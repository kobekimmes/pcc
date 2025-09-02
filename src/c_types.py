

from enum import Enum

TYPE_KEYWORDS = ["int", "float", "char", "void", "bool"]
STATEMENT_KEYWORDS = ["return", "struct", "if", "while", "for"]


class PrimitiveType(Enum):
    INT = 1
    FLOAT = 2
    BOOL = 3
    CHAR = 4
    VOID = 5
    
class PointerType():
    INT_POINTER = 1
    FLOAT_POINTER = 2
    BOOL_POINTER = 3
    CHAR_POINTER = 4
    VOID_POINTER = 5
    
class ObjectType():
    
    pass
    
    
# class ConditionalType(Enum):
#     IF = 1
#     IF_ELSE = 2
#     WHILE = 3
#     FOR = 4
    
    
def getTypeFromString(type):
    match type:
        case "int":
            return PrimitiveType.INT
        case "float":
            return PrimitiveType.FLOAT
        case "bool":
            return PrimitiveType.BOOL
        case "char":
            return PrimitiveType.CHAR
        case "void":
            return PrimitiveType.VOID
    return 0
    
def getNoneType(type):
    match type:
        case PrimitiveType.INT | PrimitiveType.FLOAT | PrimitiveType.CHAR:
            return 0
        case PrimitiveType.VOID:
            return 
        case "bool":
            return PrimitiveType.BOOL
        case "char":
            return PrimitiveType.CHAR
        case "void":
            return PrimitiveType.VOID
        case _:
            return 0
    