#!/bin/bash

set -euo pipefail

# Keep the model the same, but allow the diff to be reduced before it is sent
# to the model. These can be overridden when experimenting with a local model.
MODEL="${OLLAMA_COMMIT_MODEL:-gemma4:12b}"
DIRECT_DIFF_LIMIT_BYTES="${COMMIT_MSG_DIRECT_DIFF_LIMIT_BYTES:-24000}"
SUMMARY_CHUNK_BYTES="${COMMIT_MSG_SUMMARY_CHUNK_BYTES:-12000}"
FINAL_SUMMARY_LIMIT_BYTES="${COMMIT_MSG_FINAL_SUMMARY_LIMIT_BYTES:-20000}"
FINAL_METADATA_LIMIT_BYTES="${COMMIT_MSG_FINAL_METADATA_LIMIT_BYTES:-8000}"
SUMMARY_MAX_CHARS=600

TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/generate-commit-msg.XXXXXX")
trap 'rm -rf "$TEMP_DIR"' EXIT

DIFF_FILE="$TEMP_DIR/diff"
git diff > "$DIFF_FILE"

if [ ! -s "$DIFF_FILE" ]; then
    echo "No changes staged for commit" >&2
    exit 1
fi

run_model() {
    ollama run "$MODEL" --hidethinking
}

write_direct_prompt() {
    printf '%s\n\n' \
        'Based on this git diff, write a clear and concise commit message that follows conventional commit format (type: subject). The message should be in present tense and describe what the changes do. Only describe changes if a file has changed. For changes in data.json describe new books being added or removed, ratings or completion percentages being updated.'
    cat "$1"
}

DIFF_SIZE=$(wc -c < "$DIFF_FILE" | tr -d '[:space:]')

# Preserve the original one-pass behavior for normal-sized changes.
if [ "$DIFF_SIZE" -le "$DIRECT_DIFF_LIMIT_BYTES" ]; then
    write_direct_prompt "$DIFF_FILE" | run_model
    exit $?
fi

summarize_chunks() {
    local input_file="$1"
    local output_file="$2"
    local prefix="$3"
    local instruction="$4"
    local part
    local summary
    local part_number=0

    : > "$output_file"
    # macOS and GNU split both support byte-sized chunks; -C is not
    # available on the BSD split shipped with macOS.
    split -b "$SUMMARY_CHUNK_BYTES" -a 6 "$input_file" "$TEMP_DIR/$prefix"

    for part in "$TEMP_DIR/$prefix"*; do
        [ -f "$part" ] || continue
        part_number=$((part_number + 1))

        if ! summary=$(
            {
                printf '%s\n\n' "$instruction"
                cat "$part"
            } | run_model
        ); then
            echo "Failed to summarize diff part $part_number" >&2
            exit 1
        fi

        # Keep the intermediate file bounded even if the model ignores the
        # requested summary length.
        if [ "${#summary}" -gt "$SUMMARY_MAX_CHARS" ]; then
            summary="${summary:0:SUMMARY_MAX_CHARS}…"
        fi

        printf '\n--- Summary %d ---\n%s\n' "$part_number" "$summary" >> "$output_file"
    done
}

DIFF_SUMMARIES="$TEMP_DIR/diff-summaries"
summarize_chunks "$DIFF_FILE" "$DIFF_SUMMARIES" "diff-part-" \
    'You are summarizing one part of a large git diff. Extract only concrete changes that are visible in this part. Preserve filenames, book titles, counts, ratings, and progress values when visible. Return at most three concise bullet points and no more than 400 characters. Do not write a commit message. The diff part follows:'

# A very large diff can produce more summaries than fit in the final prompt.
# Reduce those summaries in additional passes, still using the same model.
CURRENT_SUMMARIES="$DIFF_SUMMARIES"
SUMMARY_PASS=1
while [ "$(wc -c < "$CURRENT_SUMMARIES" | tr -d '[:space:]')" -gt "$FINAL_SUMMARY_LIMIT_BYTES" ]; do
    NEXT_SUMMARIES="$TEMP_DIR/reduced-summaries-$SUMMARY_PASS"
    summarize_chunks "$CURRENT_SUMMARIES" "$NEXT_SUMMARIES" "reduce-$SUMMARY_PASS-" \
        'Condense these summaries of a large git diff into the concrete changes they describe. Keep filenames, book titles, counts, ratings, and progress values when available. Return at most three concise bullet points and no more than 400 characters. Do not write a commit message. The summaries follow:'
    CURRENT_SUMMARIES="$NEXT_SUMMARIES"
    SUMMARY_PASS=$((SUMMARY_PASS + 1))
done

CHANGED_FILES="$TEMP_DIR/changed-files"
DIFF_STAT="$TEMP_DIR/diff-stat"
git diff --name-status > "$CHANGED_FILES"
git diff --stat > "$DIFF_STAT"

write_bounded_file() {
    local input_file="$1"
    local input_size

    input_size=$(wc -c < "$input_file" | tr -d '[:space:]')
    if [ "$input_size" -gt "$FINAL_METADATA_LIMIT_BYTES" ]; then
        head -c "$FINAL_METADATA_LIMIT_BYTES" "$input_file"
        printf '\n[metadata truncated]\n'
    else
        cat "$input_file"
    fi
}

{
    printf '%s\n\n' \
        'Write one clear, concise commit message in conventional commit format (type: subject), in present tense. Return only the message, with no quotes, markdown, explanation, or extra lines. Use the change summaries and diff metadata below. For data.json, describe new books being added or removed, ratings or completion percentages being updated when that information is available.'
    printf '\nChanged files:\n'
    write_bounded_file "$CHANGED_FILES"
    printf '\nDiff stat:\n'
    write_bounded_file "$DIFF_STAT"
    printf '\nChange summaries:\n'
    cat "$CURRENT_SUMMARIES"
} | run_model
