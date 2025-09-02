import sys
from c_lex import *
from src.c_ast import *     # type: ignore
from c_parse import *
from src.c_interpreter import *


def main():
    argv = sys.argv
    argc = len(argv)

    if not 1 < argc < 3:
        print("Usage: pcc <filename>")
        sys.exit()
        
    interp = Interpreter("test.c", True)
    
    print(interp.evaluateDeclaration(interp.ast))
    
    
if __name__ == "__main__":
    main()




