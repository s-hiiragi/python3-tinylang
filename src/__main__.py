import sys
import argparse
from .tokenizer import Tokenizer
from .parser import Parser, print_node
from .code_generator import CodeGenerator

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    args = parser.parse_args()
    return args

def read_file(filename):
    with open(filename, 'r', encoding='UTF-8') as f:
        return f.read()

def main() -> int:
    args = parse_args()

    code = read_file(args.infile)

    tokens, error = Tokenizer().tokenize(code)
    if error:
        print(str(error), file=sys.stderr)
        return 1

    print('-- tokens')
    print(tokens)

    ast, error = Parser().parse(tokens)
    if error:
        print(str(error), file=sys.stderr)
        return 1

    print('-- ast')
    print_node(ast)

    lines = CodeGenerator().generate(ast)

    print('-- code')
    print('\n'.join(lines))

    return 0

if status := main():
    sys.exit(status)
