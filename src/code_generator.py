from .tokenizer import Token
from .parser import Node, Block, DeclVar, CallFunc, AddExpr, Term

class CodeGenerator():

    def generate(self, ast: Node):
        self._initialize()

        if isinstance(ast, Block):
            return self._generate_block(ast)

        return []

    def _initialize(self):
        self._sp = 0
        self._bp = 0
        self._varaddrs = {}

    def _generate_block(self, block: Block):
        lines = []

        for stmt in block.children:
            lines += self._generate_stmt(stmt)

        return lines

    def _generate_stmt(self, stmt: Node):
        if isinstance(stmt, DeclVar):
            return self._generate_declvar(stmt)
        elif isinstance(stmt, CallFunc):
            return self._generate_callfunc(stmt)
        return []

    def _generate_declvar(self, stmt: DeclVar):
        lines = [
            '# var {} = {}'.format(stmt.name, stmt.children[0]),
        ]

        # 式をコード化する
        lines.extend(self._generate_expr(stmt.children[0]))

        lines.extend([
            'pushq %rax',
        ])
        self._sp += 1

        varaddr = self._sp - self._bp
        self._varaddrs[stmt.name] = varaddr

        lines.extend([
            '#   変数のアドレス = -{}(%rbp)'.format(varaddr)
        ])

        return lines

    def _generate_callfunc(self, stmt: CallFunc):
        lines = [
            '# {}({})'.format(stmt.name, stmt.children[0]),
        ]

        # 引数をコード化する
        lines.extend(self._generate_expr(stmt.children[0]))

        # 引数をスタックに積む
        lines.extend([
            'pushq %rax',
        ])
        self._sp += 1

        lines.extend([
            'callq 0xDEADBEAF <{}>'.format(stmt.name),
        ])

        return lines

    def _generate_expr(self, expr: Node):
        if isinstance(expr, AddExpr):
            return self._generate_expr_add(expr)
        elif isinstance(expr, Term):
            return self._generate_expr_term(expr)
        else:
            # あり得ないケース
            return []

    def _generate_expr_add(self, expr: AddExpr):
        lines = []

        lines.extend(self._generate_expr(expr.children[0]))
        lines.extend([
            'movq %rax, %rdx',
        ])
        lines.extend(self._generate_expr(expr.children[1]))
        lines.extend([
            'addq %rdx, %rax',
        ])

        return lines

    def _generate_expr_term(self, expr: Term):
        tok = expr.token

        if tok.tag == Token.IDENTIFER:
            return [
                # 変数を読み込む
                'movq -{}(%rbp), %rax'.format(self._varaddrs[tok.code]),
            ]
        elif tok.tag == Token.INTEGER:
            return [
                # 整数をレジスタに読み込む
                'movq ${}, %rax'.format(tok.code),
            ]
        else:
            # あり得ないケース
            return []
