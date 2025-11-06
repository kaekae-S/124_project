import re
from typing import List, Dict

# List of multi-word keywords (order matters: longer/multi-word first)
_MULTIWORD_KEYWORDS = [
    r"I\s+HAS\s+A",
    r"SUM\s+OF",
    r"DIFF\s+OF",
    r"PRODUKT\s+OF",
    r"QUOSHUNT\s+OF",
    r"MOD\s+OF",
    r"BIGGR\s+OF",
    r"SMALLR\s+OF",
    r"BOTH\s+OF",
    r"EITHER\s+OF",
    r"WON\s+OF",
    r"ALL\s+OF",
    r"ANY\s+OF",
    r"BOTH\s+SAEM",
    r"DIFFRINT",
    r"IS\s+NOW\s+A",
    r"IM\s+IN\s+YR",
    r"IM\s+OUTTA\s+YR",
    r"HOW\s+IZ\s+I",
    r"FOUND\s+YR",
    r"IF\s+U\s+SAY\s+SO",
    r"SUM\s+OF",
]

# Single-word keywords and punctuation-words (escape question marks)
_SINGLEWORD_KEYWORDS = [
    r"HAI", r"KTHXBYE", r"WAZZUP", r"BUHBYE", r"BTW", r"OBTW", r"TLDR",
    r"ITZ", r"R", r"SMOOSH", r"MAEK", r"A", r"VISIBLE", r"GIMMEH",
    r"O\s+RLY\?", r"YA\s+RLY", r"MEBBE", r"NO\s+WAI", r"OIC",
    r"WTF\?", r"OMG", r"OMGWTF",
    r"UPPIN", r"NERFIN", r"YR", r"TIL", r"WILE",
    r"GTFO", r"I\s+IZ", r"MKAY"
]

# Combine and order: YARN first, multiword keywords, single-word keywords, TROOF, NUMBAR, NUMBR, IDENTIFIER
class Lexer:
    def __init__(self, ignore_case: bool = True):
        flags = re.IGNORECASE if ignore_case else 0

        # YARN literal must be matched first because it can contain spaces
        self.yarn_re = re.compile(r'^"([^"\\]*(?:\\.[^"\\]*)*)"', flags)

        # Build ordered token patterns (anchored with ^ for matching at the current position)
        self.ordered_patterns = []

        # Multi-word keywords
        for kw in _MULTIWORD_KEYWORDS:
            pat = rf'^{kw}\b'
            self.ordered_patterns.append(("KEYWORD", re.compile(pat, flags)))

        # Single-word keywords / punctuation-words
        for kw in _SINGLEWORD_KEYWORDS:
            pat = rf'^{kw}\b'
            self.ordered_patterns.append(("KEYWORD", re.compile(pat, flags)))

        # TROOF (WIN/FAIL)
        self.ordered_patterns.append(("TROOF_LITERAL", re.compile(r'^(WIN|FAIL)\b', flags)))

        # NUMBAR then NUMBR (NUMBAR has a decimal point)
        # Allow optional leading minus sign
        self.ordered_patterns.append(("NUMBAR_LITERAL", re.compile(r'^-?\d+\.\d+\b', flags)))
        self.ordered_patterns.append(("NUMBR_LITERAL", re.compile(r'^-?\d+\b', flags)))

        # Identifiers (variable/function/loop identifiers share same pattern in spec)
        self.ordered_patterns.append(("IDENTIFIER", re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*\b', flags)))

        # Single-line comment (BTW...) — we'll handle comments specially at line start or inline
        self.comment_re = re.compile(r'\bBTW\b', flags)
        # Multiline comment markers
        self.obtw_re = re.compile(r'^\s*OBTW\b', flags)
        self.tldr_re = re.compile(r'^\s*TLDR\b', flags)

        # Generic word fallback (to ensure we parse every chunk)
        self.fallback_re = re.compile(r'^\S+')

    def tokenize(self, code: str) -> List[Dict]:
        """
        Tokenize the given source code into a list of token dicts:
        {"type": <TYPE>, "value": <lexeme>, "line": <line_no>, "col": <col_index>}
        """
        tokens = []
        in_multiline_comment = False
        lines = code.splitlines()

        for line_num, raw_line in enumerate(lines, start=1):
            line = raw_line.rstrip('\n')
            pos = 0
            length = len(line)

            # Check multiline comment start (OBTW) anywhere in line but rules state it must be alone on line,
            # however we handle robustly.
            if self.obtw_re.match(line):
                in_multiline_comment = True
                tokens.append({"type": "COMMENT_START", "value": "OBTW", "line": line_num, "col": 0})
                continue

            if self.tldr_re.match(line):
                in_multiline_comment = False
                tokens.append({"type": "COMMENT_END", "value": "TLDR", "line": line_num, "col": 0})
                continue

            if in_multiline_comment:
                # emit the line as part of comment (optional)
                tokens.append({"type": "COMMENT_CONTENT", "value": line, "line": line_num, "col": 0})
                continue

            # Walk through the line left-to-right
            while pos < length:
                # Skip whitespace
                if line[pos].isspace():
                    pos += 1
                    continue

                remaining = line[pos:]

                # Check for inline single-line comment start 'BTW' (it and the rest of line are a comment)
                m_comment = self.comment_re.search(remaining)
                if m_comment and m_comment.start() == 0:
                    # the rest of the line is comment
                    comment_text = remaining
                    tokens.append({"type": "COMMENT", "value": comment_text, "line": line_num, "col": pos})
                    pos = length
                    break
                elif m_comment and m_comment.start() > 0:
                    # there is a BTW later in the remaining text; but we should match tokens up to that point
                    # We'll allow normal matching until pos reaches that index.
                    pass

                # YARN literal (must be checked first)
                myarn = self.yarn_re.match(remaining)
                if myarn:
                    lex = myarn.group(0)
                    tokens.append({"type": "YARN_LITERAL", "value": lex, "line": line_num, "col": pos})
                    pos += len(lex)
                    continue

                # Try ordered patterns (multi-word + single-word keywords, TROOF, numbers, identifier)
                matched = False
                for tok_type, cre in self.ordered_patterns:
                    m = cre.match(remaining)
                    if m:
                        lex = m.group(0)
                        tokens.append({"type": tok_type, "value": lex, "line": line_num, "col": pos})
                        pos += len(lex)
                        matched = True
                        break
                if matched:
                    continue

                # Fallback: take next non-space chunk so we never skip words
                mf = self.fallback_re.match(remaining)
                if mf:
                    lex = mf.group(0)
                    tokens.append({"type": "UNKNOWN", "value": lex, "line": line_num, "col": pos})
                    pos += len(lex)
                    continue

                # If nothing matched (shouldn't happen), advance one char to avoid infinite loop
                pos += 1

        return tokens
