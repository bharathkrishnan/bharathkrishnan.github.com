class Author:
    def __init__(self, name) -> None:
        self.name = name
        
    def safe_name(self) -> str:
        return "".join(c for c in str(self.name) if c.isalnum()).rstrip()
    
    def print_link(self) -> str:
        return '[{0}](../{1})'.format(self.name, self.safe_name())

    def print(self) -> str:
        return self.name