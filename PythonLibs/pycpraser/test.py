import pycparser as pyc

code = """
char test(char a)
{
    return ((a>2)?(b=3,c=4,d=5):(b=6,c=7,d=8));
}
"""
#_Alignas(char) const volatile static _Thread_local int a;
code = """
int func(void);
"""

parser = pyc.c_parser.CParser()
ast = parser.parse(code)
print(ast)
