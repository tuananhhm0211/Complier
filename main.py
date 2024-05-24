from lexer.main import generate_token
from parser.parser_ast import LL1_parser, print_ast
import os

if __name__ == "__main__":
    file = "sample_psgeneric"
    generate_token(file)
    ast = LL1_parser(file)
    ast = ast.remove_parent(ast)
    os.makedirs(f"output/{file}", exist_ok=True)
    out = open(f"output/{file}/out_ast_bracket.vcps", "w")
    out1 = open(f"output/{file}/out_ast.vcps", "w")
    out.write(print_ast(ast, 0))
    out1.write(ast.__repr__())

    out.close()
    out1.close()