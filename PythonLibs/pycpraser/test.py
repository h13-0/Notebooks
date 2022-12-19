import pycparser as pyc

code = """
struct { int a; int b; } obj = { .a = 1, .b = 2 };
"""

parser = pyc.c_parser.CParser()
ast = parser.parse(code)
print(ast)
