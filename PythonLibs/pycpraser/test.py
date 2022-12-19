import pycparser as pyc

code = """
int a, b, c;
"""

parser = pyc.c_parser.CParser()
ast = parser.parse(code)
print(ast)
