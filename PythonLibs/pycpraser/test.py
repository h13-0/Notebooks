import pycparser as pyc

code = """
enum enum_type { a, b, c };
enum enum_type obj;
"""

parser = pyc.c_parser.CParser()
ast = parser.parse(code)
print(ast)
