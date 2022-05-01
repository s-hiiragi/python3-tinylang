import re
from typing import Optional

class TokenizeError(Exception):
    
    def __init__(self, message, lineno, columnno):
        self.args = ('{}:{}:{}'.format(lineno, columnno, message),)

class Token():
    IDENTIFER = 'ID'
    INTEGER = 'INT'
    SIGN = 'SIGN'
    EOF = 'EOF'

    def __init__(self, code: str, tag: int, line: int, column: int):
        self.code = code
        self.tag = tag
        self.line = line
        self.column = column

    def __repr__(self):
        return self.code

    def __str__(self):
        return self.code

class Tokenizer():
    
    def tokenize(self, code) -> tuple[list[Token], Optional[TokenizeError]]:
        tokens = []

        i = 0
        n = len(code)
        lineno = 1
        columnno_start = 0

        def columnno():
            return i - columnno_start + 1

        def add_token(code, tag):
            tokens.append(Token(code, tag, lineno, columnno()))

        while i < n:
            c = code[i]
            if c == '\n':
                i += 1
                lineno += 1
                columnno_start = i
            elif c == ' ' or c == '\t':
                i += 1
            elif m := re.match(r'\d+', code[i:]):
                int_ = m.group()
                add_token(int_, Token.INTEGER)
                i += len(int_)
            elif m := re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', code[i:]):
                id_ = m.group()
                add_token(id_, Token.IDENTIFER)
                i += len(id_)
            elif c in '=()+-':
                add_token(c, Token.SIGN)
                i += 1
            else:
                return [], TokenizeError(f"unexpected character '{c}'", lineno, columnno())

        add_token('', Token.EOF)

        return tokens, None
