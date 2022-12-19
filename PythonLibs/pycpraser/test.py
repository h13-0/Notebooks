import pycparser as pyc

code = """
char test(char a)
{
    return ((a>2)?(b=3,c=4,d=5):(b=6,c=7,d=8));
}
"""

code = """
static _Thread_local int a = 0;
"""

parser = pyc.c_parser.CParser()
ast = parser.parse(code)
print(ast)
