from c_lexer import *
from c_parse import *
from c_ast import *
from c_env import *
from c_error import *

ONE_K = 1024
EIGHT_K = 8 * ONE_K
    

class Interpreter:
    
    def __init__(self, filename, debug = False):
        self.lex = Lexer(filename)
        self.parser = Parser(self.lex, debug)
        self.trace_depth = 0
        self.debug = debug
        
        self.ast = self.parser.parseFile()
        
        # Data & Code memory
        self.current_env = Environment(None, "Global")
        
        self.function_map = {}
        self.struct_map = {}
        
    def newEnvironment(self, name = ""):
        self.current_env = Environment(self.current_env, name)
        
    def declareVariable(self, name, type, value):
        (_, _, depth) = self.current_env.get_mapping(name)
        if depth == self.current_env.depth:
            raise RuntimeError(self.lex, "Illegal redeclaration in same scope")
        self.current_env.insert_mapping(name, type, value)
        
    def updateVariable(self, name, new_value):
        type = self.resolveType(new_value)
        self.current_env.update_mapping()
        
    def readVariable(self, name):
        var_info = self.current_env.get_mapping(name)
        if var_info is None:
            raise RuntimeError(self.lex, "Reading from undeclared value")
        return var_info
        
    def getTruthyFalsey(self, value):
        match value:
            case 0 | None | False:
                return False
            case _:
                return True
       
       
    def evaluateChainExpression(self, node):
        
        chain_type = node.node_type
        
        match chain_type:
            case NodeType.FunctionCall:
                return self.evaluateFunctionCall(node)
            case NodeType.Subscript:
                return self.evaluateSubscript(node)
            case NodeType.MemberSelection:
                return self.evaluateMemberSelection(node)
            case _:
                raise NotImplementedError(f"Unsupported chain component: {chain_type}")
        
       
    def evaluateFunctionCall(self, node):
        
        if node.node_type == NodeType.FunctionCall:
            function_name = node.children["Locator"].name
            args = [self.evaluateExpression(node.children[f"Arg{i+1}"]) for i in range(len(node.children))]
            
            return self.executeFunction(function_name, args)
    
    def evaluateSubscript(self, node):
        
        if node.node_type == NodeType.Subscript:
            collection_name = node.children["Locator"].name
            index = self.evaluateExpression(node.children["Index"])
            
            return self.indexLookup(collection_name, index)
    
    def evaluateMemberSelection(self, node):
        
        if node.node_type == NodeType.MemberSelection:
            
            locator = self.evaluateChainExpression(node.children["Locator"])
            member = self.evaluateChainExpression(node.children["Member"])
            
            return self.memberLookup(locator, member)
   
    @trace
    def evaluateExpression(self, node):
        if node:
            node_type = node.node_type
            name = node.name
            type = node.type
            value = node.value

            match node_type:
                case NodeType.IntLiteral | NodeType.FloatLiteral:
                    return value
                case NodeType.Identifier:
                    return self.readVariable(name, type, self.current_env.depth)
                case NodeType.BinaryOperationExpression:
                    return self.evaluateBinary(node)
                case NodeType.PrefixUnaryExpression | NodeType.PostfixUnaryExpression:
                    return self.evaluateUnary(node)
                case NodeType.Parenthetical:
                    return self.evaluateExpression(node.children["Group"])
                case NodeType.ChainExpression:
                    return self.evaluateChainExpression(node)
                case _:
                    raise NotImplementedError(f"Unsupported expression type: {node_type}")
      
    @trace
    def evaluateConditional(self, node):
        pass

    
    @trace
    def evaluateFunction(self, node):
        
        assert_equals(self.lex, "Expected function signature and body (declaration)", node.node_type, NodeType.Function)
            
        
    
    
      
    @trace
    def evaluateStatment(self, node):
        statement_type = node.node_type
        match statement_type:
            case NodeType.ExpressionStatement:
                return self.evaluateExpression(node)
            case NodeType.ConditionalStatement:
                return self.evaluateConditional(node)
            case NodeType.Declaration:
                return self.evaluateDeclaration(node)
            case NodeType.Assignment:
                return self.evaluateAssignment(node)
            case NodeType.Function:
                if self.current_env.depth != 0:
                    raise RuntimeError(self.lex, "Illegal nesting of function declarations. Function declarations only allowed at top-level")
                return self.evaluateFunction(node)
            case _:
                raise RuntimeError(self.lex, "Unrecognized statement type")
                
    @trace
    def evaluateCompoundStatement(self, node):
        self.newEnvironment()
        
        if node.node_type == NodeType.CompoundStatement:
            for i in range(len(node.children)):
                statement = node.children[f"Statement{i+1}"]
                
                self.evaluateStatement(statement)
        
    @trace
    def evaluateBooleanComparison(self, lhs, rhs, operation):
        match operation:
            case "||":
                if self.getTruthyFalsey(self.evaluateExpression(lhs)):
                    return True
                return self.getTruthyFalsey(self.evaluateExpression(rhs))
            
            case "&&":
                if not self.getTruthyFalsey(self.evaluateExpression(lhs)):
                    return False
                return self.getTruthyFalsey(self.evaluateExpression(rhs))
            
    @trace       
    def evaluateArithmeticComparison(self, lhs, rhs, operation):
        left_val = self.evaluateExpression(lhs)
        right_val = self.evaluateExpression(rhs)
        match operation:
            case "<":   return left_val < right_val
            case "<=":  return left_val <= right_val
            case ">":   return left_val > right_val
            case ">=":  return left_val >= right_val
            
    @trace        
    def evaluateArithmeticOperation(self, lhs, rhs, operation):
        left_val = self.evaluateExpression(lhs)
        right_val = self.evaluateExpression(rhs)
        match operation:
            case "+":  return left_val + right_val
            case "-":  return left_val - right_val
            case "*":  return left_val * right_val
            case "/":  return left_val / right_val
            case "%":  return left_val % right_val
            
    @trace   
    def evaluateBinary(self, node):
        if node.node_type == NodeType.BinaryOperationExpression:
            lhs = node.children["LeftOperand"]
            rhs = node.children["RightOperand"]
            operation = node.name
            
            match operation:
                case "||" | "&&":
                    return self.evaluateBooleanComparison(lhs, rhs, operation)
                case "<" | "<=" | ">" | ">=":
                    return self.evaluateArithmeticComparison(lhs, rhs, operation)
                case "+" | "-" | "*" | "/" | "%":
                    return self.evaluateArithmeticOperation(lhs, rhs, operation)
            
            raise RuntimeError(self.lex, "Invalid binary expression")
        raise RuntimeError(self.lex, "Expected binary expression")
                    
    @trace 
    def evaluatePrefixExpression(self, operand, operator):
        match operator:
            case "!":
                return not self.getTruthyFalsey(self.evaluateExpression(operand))
            case "-":
                return -(self.evaluateExpression(operand))
                
            case "*":
                return self.dereference(operand)
                
            case "&":
                return self.addressOf(operand)
                
            case "++":
                result = self.evaluate(operand) + 1
                self.updateVariable(operand, result)
                return result
                
            case "--":
                result = self.evaluate(operand) - 1
                self.updateVariable(operand, result)
                return result
                
    @trace 
    def evaluatePostfixExpression(self, operand, operator):
        match operator:
            case "++":
                result = self.evaluate(operand)
                self.updateVariable(operand, result + 1)
                return result
                
            case "--":
                result = self.evaluate(operand)
                self.updateVariable(operand, result - 1)
                return result
    
    @trace 
    def evaluateUnary(self, node):
        match node.node_type:
            case NodeType.PrefixUnaryExpression:
                operand = node.children["Operand"]
                operator = node.name
                
                return self.evaluatePrefixExpression(operand, operator)
                
            case NodeType.PostfixUnaryExpression:
                operand = node.children["Operand"]
                operator = node.name
                
                return self.evaluatePostfixExpression(operand, operator)
                
            case NodeType.UnaryOperationExpression:
                pass
                 
        raise RuntimeError(self.lex, "Invalid unary expression")
            
    
    def evalutePrimitive(self):
        pass
    
    
    def evaluateAssignment(self, node):
        
        if node.node_type == NodeType.Assignment:
            self.current_env.update_mapping()
            
        raise RuntimeError(self.lex, "Expected assignment")
    
    
    @trace
    def evaluateDeclaration(self, node):
    
        if node.node_type == NodeType.Declaration:
            
            for i in range(len(node.children)):
                declaration = node.children[f"Decl{i+1}"]
                
                match declaration.node_type:
                    case NodeType.Identifier:
                        self.declareVariable(declaration.name, node.type, None)
                    case NodeType.Assignment:
                        self.declareVariable(declaration.children["LValue"].name, node.type, self.evaluateExpression(declaration.children["RValue"]))
                        
        if self.debug: print(self.current_env)
        
        
    @trace
    def evaluateModule(self, node):
        if node.node_type == NodeType.TranslationUnit:
            
            for i in range(len(node.children)):
                statement = node.children[f"Statement{i+1}"]
                
                
            