import pycparser as pyc

code = """
int a, b, c;
a = 1, b = 0, c = 2;
"""

parser = pyc.c_parser.CParser()
ast = parser.parse(code)
print(ast)
