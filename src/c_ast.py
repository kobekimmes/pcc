

from enum import Enum

class NodeType(str, Enum):
    BaseNode = "BaseNode"
    TranslationUnit = "TranslationUnit"
    CompoundStatement = "CompoundStatement"
    
    Expression = "Expression"
    UnaryOperationExpression = "UnaryOperationExpression"
    PostfixUnaryExpression = "PostfixUnaryExpression"
    PrefixUnaryExpression = "PrefixUnaryExpression"
    BinaryOperationExpression = "BinaryOperationExpression"
    Identifier = "Identifier"
    IntLiteral = "IntLiteral"
    FloatLiteral = "FloatLiteral"
    CharacterLiteral = "CharacterLiteral"
    StringLiteral = "StringLiteral"
    BooleanLiteral = "BooleanLiteral"
    FunctionCall = "FunctionCall"
    ArrayLiteral = "ArrayLiteral"
    Parenthetical = "Parenthetical"
    Subscript = "Subscript"
    MemberSelection = "MemberSelection"
    ChainExpression = "ChainExpression"
    
    Function = "Function"
    Struct = "Struct"
    
    Statement = "Statement"
    ReturnStatement = "ReturnStatement"
    ConditionalStatement = "ConditionalStatement"
    IfStatement = "IfStatement"
    ForStatement = "ForStatement"
    WhileStatement = "WhileStatement"
    Assignment = "Assignment"
    Declaration = "Declaration"
    ExpressionStatement = "ExpressionStatement"
    

    
    
class Node:
    def __init__(self, node_type, name = None, type = None, value = None):
        self.node_type = node_type
        self.start = (-1, -1)
        self.end = (-1, -1)
       
        self.name = name
        self.type = type
        self.value = value
        
        self.children = {} 
        
    def format_file_pos(self):
        start_line, start_col = self.start
        end_line, end_col = self.end
 
        if start_line != end_line and start_col != end_col:
            return f"ln{start_line}:{start_col}-ln{end_line}:{end_col}"

        if start_col != end_col:
            return f"ln{start_line}:{start_col}-{end_col}"
        
        return f"ln{start_line}:{start_col}"
            
    
    def assign_file_pos(self, start_line, start_col, end_line, end_col):
        self.start = (start_line, start_col)
        self.end = (end_line, end_col)
        
    def __str__(self):
        return f"{self.node_type}<{self.type}>({self.value}) @ {self.format_file_pos()}"
    
    def __repr__(self):
        return f"{self.node_type}({self.start}, {self.end}, {self.name}, {self.type}, {self.value})"
    
    def toString(self, depth):
        children = ""
        for key, value in self.children.items():
            children += f"\n{'\t' * (depth+1)}-- {key}: {value.toString(depth+1)}"
        return self.__str__() + children
    
    def add(self, key, value):
        if not value: return
        self.children[key] = value
        
    def get(self, node_type):
        if not self.children:
            return []
        results = []
        for child in self.children.values():
            if child.node_type == node_type:
                results += [child] + child.get(node_type)
        return results
    
    def get_children(self):
        if not self.children:
            return []
        results = []
        for child in self.children.values():
            results += [child] + child.get_children()
        return results
        
        
class TranslationUnit(Node):
    def __init__(self, program_name, program):
        super().__init__(NodeType.TranslationUnit, None, None, f"'{program_name}'")
        for i in range(len(program)):
            self.add(f"Statement{i+1}", program[i])

# Compound statement

class CompoundStatement(Node):
    def __init__(self, statements):
        super().__init__(NodeType.CompoundStatement)
        for i in range(len(statements)):
            self.add(f"Statement{i+1}", statements[i])
        
class Expression(Node):
    def __init__(self, node_type, name = None, type = None, value = None):
        super().__init__(node_type, name, type, value)
        
    def __str__(self):
        return f"{self.node_type}<'{self.name}'> @ {self.format_file_pos()}"
    
class Parenthetical(Expression):
    def __init__(self, internals):
        super().__init__(NodeType.Parenthetical)
        self.add("Group", internals)
        
class UnaryExpression(Expression):
    def __init__(self, node_type, operator, operand):
        super().__init__(node_type, operator)
        self.add("Operand", operand)
        
class Prefix(UnaryExpression):
    def __init__(self, operand, operator):
        super().__init__(NodeType.PrefixUnaryExpression, operator, operand)
 
class Postfix(UnaryExpression):
    def __init__(self, operand, operator):
        super().__init__(NodeType.PostfixUnaryExpression, operator, operand)

class Binary(Expression):
    def __init__(self, lhs, rhs, operator):
        super().__init__(NodeType.BinaryOperationExpression, operator)
        self.add("LeftOperand", lhs)
        self.add("RightOperand", rhs)

class Identifier(Expression):
    def __init__(self, symbol_name):
        super().__init__(NodeType.Identifier, symbol_name)
    
class PrimitiveLiteral(Expression):
    def __init__(self, node_type, primitive_type, primitive_value):
        super().__init__(node_type, None, primitive_type, primitive_value)
        
    def __str__(self):
        return f"{self.node_type}<'{self.type}'>({self.value}) @ {self.format_file_pos()}"

class ObjectLiteral(Expression):
    pass
    
class NumericLiteral(PrimitiveLiteral):
    def __init__(self, node_type, numeric_type, numeric_value):
        super().__init__(node_type, numeric_type, numeric_value)
        
class FloatLiteral(NumericLiteral):
    def __init__(self, value):
        super().__init__(NodeType.FloatLiteral, "float", value)
    
class IntLiteral(NumericLiteral):
    def __init__(self, value):
        super().__init__(NodeType.IntLiteral, "int", value)
        
class BooleanLiteral(PrimitiveLiteral):
    def __init__(self, boolean_value):
        super().__init__(NodeType.BooleanLiteral, "bool", boolean_value)
        
class CharacterLiteral(PrimitiveLiteral):
    def __init__(self, character_value):
        super().__init__(NodeType.CharacterLiteral, "char", character_value)
        
class StringLiteral(ObjectLiteral):
    def __init__(self, string_value):
        super().__init__(NodeType.StringLiteral, None, "string", string_value)
        
class ArrayLiteral(ObjectLiteral):
    def __init__(self, type, elements):
        super().__init__(NodeType.ArrayLiteral, None, type, elements)
        
class ChainExpression(Expression):
    def __init__(self, head, chain):
        super().__init__(NodeType.ChainExpression)
        head.add("Callable", chain)
        self.add("Chain", head)

class FunctionInvocation(Expression):
    def __init__(self, arguments):
        super().__init__(NodeType.FunctionCall)
        for i in range(len(arguments)):
            self.add(f"Arg{i+1}", arguments[i])
            
class Subscript(Expression):
    def __init__(self, index):
        super().__init__(NodeType.Subscript)
        self.add("Index", index)

        
class MemberSelection(Expression):
    def __init__(self, member, access_type):
        super().__init__(NodeType.MemberSelection, access_type)
        self.access_type = access_type
        self.add("Member", member)
        

class Statement(Node):
    def __init__(self, node_type, type = None, value = None, side_effects = None):
        super().__init__(node_type, type, value)
        self.side_effects = side_effects
        
class ExpressionStatement(Statement):
    def __init__(self, expr):
        super().__init__(NodeType.ExpressionStatement)
        self.add("Expression", expr)

class Conditional(Statement):
    def __init__(self, if_true, then, otherwise, is_loop):
        super().__init__(NodeType.ConditionalStatement)
        self.add("If", if_true)
        self.add("Then", then)
        self.add("Else", otherwise)
            
        self.is_loop = is_loop
        
class Declaration(Statement):
    def __init__(self, type, declarations):
        super().__init__(NodeType.Declaration, type)
        for i in range(len(declarations)):
            self.add(f"Decl{i+1}", declarations[i])
        

class Assignment(Statement):

    def __init__(self, symbol, assignment_operator, value):
        super().__init__(NodeType.Assignment, assignment_operator)
        self.add("LValue", symbol)
        self.add("RValue", value)

class Function(Statement):

    def __init__(self, return_type, function_name, arguments, body):
        super().__init__(NodeType.Function, function_name, return_type, arguments)
        self.return_type = return_type
        self.arguments = arguments
        self.add(body)

class Struct(Statement):
    def __init__(self, struct_name, attributes):
        super().__init__(NodeType.Struct)
        self.attributes = attributes
        
class Return(Statement):
    def __init__(self, return_value):
        super().__init__(NodeType.ReturnStatement)
        self.add("Ret", return_value)
    
       
def toString(tree, depth):
    children = ""
    for child in tree.children:
        children += f"\n{'\t' * (depth+1)}{toString(child, depth+1)}"
    return tree.__repr__() + children
    
    
def displayAst(tree):
    print("Displaying nodal representation of program:\n" +
          "---------------------------------------------")
    print(tree.toString(0))
    
def precedence(node_type):
    pass

 # type: ignore