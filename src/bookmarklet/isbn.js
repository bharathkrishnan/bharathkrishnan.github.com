javascript:(
    function() {    
        function getISBN() {
            const detailBullets = document.querySelectorAll("#detailBullets_feature_div .a-list-item");
            let isbn10 = null;
            let isbn13 = null;
            detailBullets.forEach(item => {
                if (item.innerText.includes("ISBN-13")) {
                    isbn13 = item.innerText.split("ISBN-13")[1].replace(":", "").replace(/\u200f/g, '').replace("‎", '').trim();
                } else if (item.innerText.includes("ISBN-10")) {
                    isbn10 = item.innerText.split("ISBN-10")[1].replace(":", "").replace(/\u200f/g, '').replace("‎", '').trim();
                }});
                return "\"ISBN13\": \"" + isbn13 + "\",\n\"ISBN10\": \"" + isbn10+"\"";
            }
            const isbn = getISBN();
            if (isbn) {
                navigator.clipboard.writeText(isbn).then(() => {
                    alert("ISBN copied: " + isbn);
                }).catch(err => {
                    alert("Error copying ISBN: " + err);
                });
            } else {
                alert("ISBN not found on this page.");
            }}
        )();
