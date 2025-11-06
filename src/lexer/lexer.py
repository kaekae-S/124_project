import re

class Lexer:
    def __init__(self):
        # Ordered patterns (longest first — ensures multiword keywords are caught first)
        self.token_patterns = [
            # Multi-word keywords
            ("Keyword", r"\b(I HAS A|SUM OF|DIFF OF|PRODUKT OF|QUOSHUNT OF|MOD OF|BIGGR OF|SMALLR OF|"
                        r"BOTH SAEM|DIFFRINT|BOTH OF|EITHER OF|WON OF|ALL OF|ANY OF|IM IN YR|"
                        r"IM OUTTA YR|HOW IZ I|FOUND YR|IS NOW A|IF U SAY SO)\b"),

            # Single-word keywords
            ("Keyword", r"\b(HAI|KTHXBYE|WAZZUP|BUHBYE|BTW|OBTW|TLDR|ITZ|R|VISIBLE|GIMMEH|"
                        r"O RLY\?|YA RLY|MEBBE|NO WAI|OIC|WTF\?|OMG|OMGWTF|"
                        r"UPPIN|NERFIN|YR|TIL|WILE|GTFO|I IZ|MKAY|AN|A|MAEK|SMOOSH)\b"),

            # Literals
            ("NUMBAR", r"-?\d+\.\d+"),      # floating-point
            ("NUMBR", r"-?\d+"),            # integer
            ("TROOF", r"\b(WIN|FAIL)\b"),   # boolean
            ("YARN", r'"[^"]*"'),           # string
            ("NOOB", r"\bNOOB\b"),          # uninitialized / null-like literal

            # Identifiers (variables, functions, loops)
            ("Identifier", r"[A-Za-z][A-Za-z0-9_]*"),
        ]

        # Comment patterns
        self.comment_single = re.compile(r"BTW.*")
        self.comment_start = re.compile(r"OBTW")
        self.comment_end = re.compile(r"TLDR")

    def tokenize(self, code: str):
        """Tokenizes LOLCODE source code into a list of token dictionaries."""
        tokens = []
        in_multiline_comment = False

        for line_num, line in enumerate(code.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue

            # Handle multi-line comments
            if self.comment_start.search(line):
                in_multiline_comment = True
                continue
            if self.comment_end.search(line):
                in_multiline_comment = False
                continue
            if in_multiline_comment:
                continue

            # Skip single-line comments
            if self.comment_single.match(line):
                continue

            pos = 0
            while pos < len(line):
                match = None
                for token_type, pattern in self.token_patterns:
                    regex = re.compile(pattern)
                    match = regex.match(line, pos)
                    if match:
                        value = match.group().strip()
                        tokens.append({
                            "type": token_type,
                            "value": value,
                            "line": line_num
                        })
                        pos = match.end()
                        break
                if not match:
                    pos += 1  # skip unmatched characters

        return tokens
