from typing import Optional
from .tokenizer import Token

class Node():
    attrs: list
    children: list

class Block(Node):

    def __init__(self, stmts):
        self.attrs = []
        self.children = stmts

class Stmt(Node):
    pass

class DeclVar(Stmt):
    
    def __init__(self, name, expr):
        self.name = name
        self.attrs = [name]
        self.children = [expr]

class CallFunc(Stmt):

    def __init__(self, name, arg):
        self.name = name
        self.attrs = []
        self.children = [arg]

class Expr(Node):
    pass

class AddExpr(Expr):

    def __init__(self, left, right):
        self.attrs = []
        self.children = [left, right]

class Term(Expr):

    def __init__(self, token):
        self.token = token
        self.attrs = [token]
        self.children = []

def print_node(node: Node, indent = 0):
    prefix = '  ' * indent
    nodename = type(node).__name__
    attr = ', '.join([str(a) for a in node.attrs])
    print(prefix, nodename, attr)
    for c in node.children:
        print_node(c, indent + 1)

class ParseError(Exception):

    def __init__(self, message, lineno, columnno):
        self.args = ('{}:{}: {}'.format(lineno, columnno, message),)

class ParseResult():

    def __init__(self, node: Node, consumed_count: int):
        self.node = node
        self.consumed_count = consumed_count

'''
def trace(f):
    def wrapper(*args, **kwargs):
        fname = f.__name__.ljust(32)
        args_ = args[1:]

        match args_:
            case [tokens, i]:
                args_ = (tokens[i:],)
            case [tokens, i, tag_or_code]:
                args_ = (tokens[i:], tag_or_code)

        print(f'TRACE: {fname}{args_}')
        return f(*args, **kwargs)
    return wrapper
'''
def trace(f):
    return f
#'''

class Parser():
    
    def parse(self, tokens: list[Token]) -> tuple[Node, Optional[ParseError]]:
        stmts = []

        i = 0
        n = len(tokens)
        while tokens[i].tag != Token.EOF:
            result = self._parse_stmt(tokens, i)
            if result is None:
                return Node(), ParseError(f'unexpected token {tokens[i]}', tokens[i].line, tokens[i].column)

            stmts.append(result.node)
            i += result.consumed_count

        ast = Block(stmts)

        return ast, None

    @trace
    def _parse_stmt(self, tokens, i) -> Optional[ParseResult]:
        
        parse_methods = [
            self._parse_declvar,
            self._parse_callfunc,
        ]

        for parse in parse_methods:
            result = parse(tokens, i)
            if result:
                return result

        return None

    @trace
    def _parse_declvar(self, tokens, i) -> Optional[ParseResult]:
        if var := self._take_tagged_token(tokens, i, Token.IDENTIFER):
            i += 1
            if self._take_token(tokens, i, '='):
                i += 1
                result = self._parse_expr(tokens, i)
                if result:
                    node = DeclVar(var.code, result.node)
                    return ParseResult(node, result.consumed_count + 2)

    @trace
    def _parse_callfunc(self, tokens, i) -> Optional[ParseResult]:
        if func := self._take_tagged_token(tokens, i, Token.IDENTIFER):
            i += 1
            if self._take_token(tokens, i, '('):
                i += 1
                result = self._parse_expr(tokens, i)
                if result:
                    i += result.consumed_count
                    if self._take_token(tokens, i, ')'):
                        node = CallFunc(func.code, result.node)
                        return ParseResult(node, result.consumed_count + 3)

    @trace
    def _parse_expr(self, tokens, i) -> Optional[ParseResult]:
        
        parse_methods = [
            self._parse_expr_add
        ]

        for parse in parse_methods:
            result = parse(tokens, i)
            if result:
                return result

        return None

    @trace
    def _parse_expr_add(self, tokens, i) -> Optional[ParseResult]:
        if term_result := self._parse_expr_term(tokens, i):
            i += 1
            if add := self._take_token(tokens, i, '+'):
                i += 1
                add_result = self._parse_expr_add(tokens, i)
                if add_result:
                    node = AddExpr(term_result.node, add_result.node)
                    return ParseResult(node, add_result.consumed_count + 2)
                else:
                    return None
            return ParseResult(term_result.node, 1)

    @trace
    def _parse_expr_term(self, tokens, i) -> Optional[ParseResult]:
        if tokens[i].tag == Token.EOF:
            return None
        else:
            node = Term(tokens[i])
            return ParseResult(node, 1)

    @trace
    def _take_token(self, tokens, i, code):
        if tokens[i].code == code:
            return tokens[i]
        return None

    @trace
    def _take_tagged_token(self, tokens, i, tag):
        if tokens[i].tag == tag:
            return tokens[i]
        return None
