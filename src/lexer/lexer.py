import re

class Lexer:
    """
    Lexical Analyzer for LOLCODE
    
    Converts LOLCODE source code into a stream of tokens.
    Handles keywords (single and multi-word), literals (numbers, strings, booleans),
    identifiers, and comments (single-line BTW and multi-line OBTW...TLDR).
    
    Key Design Principles:
    - Multi-word keywords are matched BEFORE single-word keywords (longest-first pattern)
    - Comments are completely excluded from the token stream
    - Comments cannot be confused with keywords or identifiers due to early detection
    """
    
    def __init__(self):
        """
        Initialize the Lexer with token patterns and comment patterns.
        
        Token patterns are ordered by precedence (longest patterns first) to ensure
        multi-word keywords like "I HAS A" are matched before single-word "I".
        
        Attributes:
            token_patterns (list): Regex patterns for token recognition, ordered by priority
            comment_single (re.Pattern): Pattern for BTW single-line comments
            comment_start (re.Pattern): Pattern for OBTW multi-line comment start
            comment_end (re.Pattern): Pattern for TLDR multi-line comment end
        """
        # Ordered patterns (longest first — ensures multiword keywords are caught first)
        self.token_patterns = [
            # Multi-word keywords
            # CRITICAL: These must appear FIRST to take precedence over single-word keywords
            ("Keyword", r"\b(I HAS A|SUM OF|DIFF OF|PRODUKT OF|QUOSHUNT OF|MOD OF|BIGGR OF|SMALLR OF|"
                        r"BOTH SAEM|DIFFRINT|BOTH OF|EITHER OF|WON OF|ALL OF|ANY OF|IM IN YR|"
                        r"IM OUTTA YR|HOW IZ I|FOUND YR|IS NOW A|IF U SAY SO)\b"),

            # Single-word keywords
            # Includes all LOLCODE language keywords
            ("Keyword", r"\b(HAI|KTHXBYE|WAZZUP|BUHBYE|BTW|OBTW|TLDR|ITZ|R|VISIBLE|GIMMEH|"
                        r"O RLY\?|YA RLY|MEBBE|NO WAI|OIC|WTF\?|OMG|OMGWTF|"
                        r"UPPIN|NERFIN|YR|TIL|WILE|GTFO|I IZ|MKAY|AN|A|MAEK|SMOOSH)\b"),

            # Literals (must precede Identifiers to match before generic identifier pattern)
            ("NUMBAR", r"-?\d+\.\d+"),      # floating-point numbers: 3.14, -2.5
            ("NUMBR", r"-?\d+"),            # integer numbers: 42, -7
            ("TROOF", r"\b(WIN|FAIL)\b"),   # boolean values: WIN (true), FAIL (false)
            ("YARN", r'"[^"]*"'),           # strings: "hello", "3.14"
            ("NOOB", r"\bNOOB\b"),          # uninitialized / null-like literal

            # Identifiers (variables, functions, loop labels)
            # Matches: [A-Za-z][A-Za-z0-9_]*
            ("Identifier", r"[A-Za-z][A-Za-z0-9_]*"),
        ]

        # Comment patterns (compiled for efficiency)
        # BTW comments: entire line treated as comment
        self.comment_single = re.compile(r"BTW.*")
        # OBTW...TLDR: multi-line comment block markers
        self.comment_start = re.compile(r"OBTW")
        self.comment_end = re.compile(r"TLDR")

    def tokenize(self, code: str):
        """
        Tokenize LOLCODE source code into a stream of tokens.
        
        Processes the source code line by line, identifying tokens via pattern matching.
        Completely removes comments (BTW single-line and OBTW...TLDR multi-line) from
        the token stream, so comments cannot be confused with keywords or identifiers.
        
        Algorithm:
        1. Process each non-empty line
        2. Check for multi-line comment boundaries (OBTW/TLDR); skip lines between them
        3. Skip lines that are single-line comments (match "BTW...")
        4. For remaining code, match token patterns left-to-right in order
        5. Multi-word keywords are checked first to prevent mismatches (e.g., "I HAS A" 
           matched before "I")
        6. Return list of token dictionaries with type, value, and line number
        
        Args:
            code (str): LOLCODE source code (may contain multiple lines)
        
        Returns:
            list[dict]: List of token dictionaries, each containing:
                - 'type' (str): Token type (Keyword, Identifier, NUMBR, NUMBAR, YARN, TROOF, NOOB)
                - 'value' (str): Token value (the matched text)
                - 'line' (int): Line number in source (1-indexed)
        
        Example:
            >>> lexer = Lexer()
            >>> code = 'HAI\\nVISIBLE "Hello"\\nKTHXBYE'
            >>> tokens = lexer.tokenize(code)
            >>> tokens[1]
            {'type': 'Keyword', 'value': 'VISIBLE', 'line': 2}
        """
        tokens = []
        in_multiline_comment = False

        for line_num, line in enumerate(code.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue

            # Handle multi-line comments: OBTW...TLDR block
            # Set flag when encountering OBTW; clear when encountering TLDR
            if self.comment_start.search(line):
                in_multiline_comment = True
                continue
            if self.comment_end.search(line):
                in_multiline_comment = False
                continue
            if in_multiline_comment:
                continue

            # Skip single-line comments (BTW ...)
            # Any line starting with BTW is completely ignored
            if self.comment_single.match(line):
                continue

            # Tokenize the code line
            # Match patterns in order; multi-word keywords are tried first
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
                    # Skip unmatched character (error recovery)
                    pos += 1  

        return tokens
