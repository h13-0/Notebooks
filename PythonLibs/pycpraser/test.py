import pycparser as pyc

code = """
int a = 1, b = 2, c = 3;
a = a == 1 ? 0 : 0;
"""

parser = pyc.c_parser.CParser()
ast = parser.parse(code)
print(ast)
