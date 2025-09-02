from c_lex import *
from src.c_ast import *
from c_types import *


def trace(function):
    def wrapper(self, *args, **kwargs):
        self.lex.skip_whitespace()
        if not self.debug: 
            return function(self, *args, **kwargs)
        
        indent = " " * self.trace_depth
        print(f"{indent}→ Entering {function.__name__}()")
        self.trace_depth += 1
        result = None
        try:
            result = function(self, *args, **kwargs)
            return result
        except Error as e:
            print(f"{indent}← (fail) Exiting {function.__name__}() with error: {e}")
            raise
        finally:
            self.trace_depth -= 1
            if result is not None:
                print(f"{indent}← (success) Exiting {function.__name__}() with result: {result}")
            self.lex.skip_whitespace()
    return wrapper


def capture(parse_function):
    def wrapper(self, *args, **kwargs):
        
        try:
            start_line_number = self.lex.get_line()
            start_column_number = self.lex.get_column()
            
            result = parse_function(self, *args, **kwargs)
            
            end_line_number = self.lex.get_line()
            end_column_number = self.lex.get_column()
            
            if result is not None:
                result.assign_file_pos(start_line_number, start_column_number, end_line_number, end_column_number)
            return result
        
        except Error:
            raise
        
    return wrapper
        
        

# Expression parsing

class Parser:
    
    def __init__(self, lex, debug = False):
        self.lex = lex
        self.debug = debug
        self.trace_depth = 0

    
    def attempt(self, parseFuncs):
        call_stack = []
        for func in parseFuncs:
            try:  
                self.lex.save_state()
                call_stack.append(func.__name__)
                parsed = func()
                return parsed
            except Error:
                self.lex.resume_state()
                continue
        else:
            raise ParseError(self.lex, "\n".join(call_stack))
    
    @capture
    @trace
    def parseParenthetical(self):
        self.lex.expect("(")
        self.lex.skip_whitespace()
        internals = self.attempt([
            self.parseExpression,
        ])
        self.lex.skip_whitespace()
        self.lex.expect(")")
        
        return Parenthetical(internals)

    @capture
    @trace
    def parseBooleanLiteral(self):
        bool = self.lex.expect_any(["true", "false"])
        return BooleanLiteral(bool == "true")

    @capture
    @trace
    def parseNumericLiteral(self):
        
        number = self.lex.number()
        
        try:
            if "." in number:
                f = FloatLiteral(float(number))
                return f
            else:
                i = IntLiteral(int(number))
                return i
        except Exception:
            raise ParseError(self.lex, "Could not parse non-numeric when expected numeric value")
    
    @capture
    @trace
    def parseCharacterLiteral(self):
        char = self.lex.character()
        return CharacterLiteral(char)
        
    @capture
    @trace
    def parseIdentifier(self):
        identifier = self.lex.token()
        return Identifier(identifier)
        
    @capture
    @trace
    def parseSubscript(self):
        self.lex.expect("[")
        index = self.parseExpression()
        self.lex.skip_whitespace()
        self.lex.expect("]")
            
        return Subscript(index)
    
    @capture
    @trace
    def parseMemberSelection(self):
        self.lex.skip_whitespace()
        access_type = self.lex.expect_any([".", "->"])
        self.lex.skip_whitespace()
        
        member = self.parseSymbol()
        
        return MemberSelection(member, access_type)
    
    @capture
    @trace
    def parseFunctionInvocation(self):
        self.lex.expect("(")
        self.lex.skip_whitespace()
        args = self.parseArguments()
        self.lex.skip_whitespace()
        self.lex.expect(")")
            
        return FunctionInvocation(args)
    
    @capture
    @trace
    def parseChainExpression(self):
        symbol = self.parseIdentifier()
        
        while self.lex.match_any([".", "->", "[", "("]) is not None:
            chain = self.attempt([
                self.parseMemberSelection,
                self.parseSubscript,
                self.parseFunctionInvocation
            ])
            chain.add("Locator", symbol)
            symbol = chain
            
        return symbol
    
    @capture
    @trace
    def parseSymbol(self):
        char = self.lex.match_any(["(", "*"])
        match char:
            case "(":
                return self.parseParenthetical()
            case "*":
                self.lex.expect("*")
                reference = self.parseSymbol()
                return Prefix(reference, char)
            case None:
                return self.parseChainExpression()
        raise ParseError(self, "Unexpected symbol")
                     
    @capture
    @trace
    def parsePrimitive(self):
        self.lex.skip_whitespace()
        
        match_with = self.lex.match_any(["true", "false", "'" ])
        
        match match_with:
            case "true" | "false":
                return self.parseBooleanLiteral()
            case "'":
                return self.parseCharacterLiteral()
            case _:
                return self.attempt([ 
                    self.parseNumericLiteral,
                    self.parseSymbol
                ])
        
    @capture
    @trace  
    def parseUnary(self):
        self.lex.skip_whitespace()
        
        if self.lex.match_any(["--", "!", "&", "++", "-"]) is not None:
            prefix_operator = self.lex.expect_any(["--", "!", "&", "++", "-"])
            
            match prefix_operator:
                case "--" | "++":
                    unary_operand =  self.attempt([
                        self.parseParenthetical,
                        self.parseSymbol,
                        self.parseNumericLiteral
                    ])
                case "!":
                    unary_operand = self.attempt([
                        self.parseParenthetical,
                        self.parseSymbol,
                        self.parseBooleanLiteral
                    ])
                case "&":
                    unary_operand =  self.attempt([
                        self.parseParenthetical,
                        self.parseSymbol
                    ])
                case "-":
                    unary_operand =  self.attempt([
                        self.parseParenthetical,
                        self.parseSymbol,
                        self.parseNumericLiteral
                    ])
            
            return Prefix(unary_operand, prefix_operator)
        
        expr = self.parsePrimitive()
        
        self.lex.skip_whitespace()
        if self.lex.match_any(["++", "--"]) is not None:
            postfix_operator = self.lex.expect_any(["++", "--"])
            
            return Postfix(expr, postfix_operator)
        
        return expr
       
    @capture
    @trace
    def parseFactor(self):
        expr = self.parseUnary()
        self.lex.skip_whitespace()
        
        while self.lex.match_any(["*", "/", "%"]) is not None:
            arithmetic_operator = self.lex.expect_any(["*", "/", "%"])
            self.lex.skip_whitespace()
            rhs = self.parseUnary()
        
            expr = Binary(expr, rhs, arithmetic_operator)
            self.lex.skip_whitespace()
        
        return expr
        
    @capture
    @trace  
    def parseTerm(self):
        expr = self.parseFactor()
        self.lex.skip_whitespace()
        
        while self.lex.match_any(["+", "-"]) is not None:
            arithmetic_operator = self.lex.expect_any(["+", "-"])
            self.lex.skip_whitespace()
            rhs = self.parseFactor()
        
            expr = Binary(expr, rhs, arithmetic_operator)
            self.lex.skip_whitespace()
        
        return expr
        
    @capture
    @trace   
    def parseComparison(self):
        expr = self.parseTerm()
        self.lex.skip_whitespace()
        
        while self.lex.match_any([">", ">=", "<", "<="]) is not None:
            comparison_operator = self.lex.expect_any([">", ">=", "<", "<="])
            self.lex.skip_whitespace()
            rhs = self.parseTerm()
        
            expr = Binary(expr, rhs, comparison_operator)
            self.lex.skip_whitespace()
        
        return expr
        
    @capture
    @trace   
    def parseEquality(self):
        expr = self.parseComparison()
        self.lex.skip_whitespace()
        
        while self.lex.match_any(["!=", "=="]) is not None:
            equality_operator = self.lex.expect_any(["!=", "=="])
            self.lex.skip_whitespace()
            rhs = self.parseComparison()
            
            expr = Binary(expr, rhs, equality_operator)
            self.lex.skip_whitespace()
        
        return expr
    
    @capture
    @trace
    def parseAnd(self):
        expr = self.parseEquality()
        self.lex.skip_whitespace()
        
        while self.lex.match("&&"):
            self.lex.expect("&&")
            self.lex.skip_whitespace()
            rhs = self.parseEquality()
            
            expr = Binary(expr, rhs, "&&")
            self.lex.skip_whitespace()
        
        return expr
    
    @capture
    @trace
    def parseOr(self):
        expr = self.parseAnd()
        self.lex.skip_whitespace()
        
        while self.lex.match("||"):
            self.lex.expect("||")
            self.lex.skip_whitespace()
            rhs = self.parseAnd()
            
            expr = Binary(expr, rhs, "||")
            self.lex.skip_whitespace()
        
        return expr
    
    @capture
    @trace   
    def parseBinary(self):
        return self.parseOr()
    
    @capture
    @trace
    def parseExpression(self):
        return self.parseBinary()
        
    @capture
    @trace
    def parseStringLiteral(self):
        return StringLiteral(self.lex.string())
     

    # Multi-line scope
    #   used in several statement bodies
    @capture
    @trace
    def parseCompoundStatement(self):
        statements = []
        self.lex.skip_whitespace()
        self.lex.expect("{")
        self.lex.skip_whitespace()
        while not self.lex.is_eof() and not self.lex.match("}"):
            self.lex.skip_whitespace()
            statements.append(self.parseStatement())
            self.lex.skip_whitespace()
        self.lex.skip_whitespace()
        self.lex.expect("}")
        self.lex.skip_whitespace()
            
        return CompoundStatement(statements)


    # Function arguments
    #   referenced in a function definition

    @trace
    def parseArguments(self):
        args_list = []

        while not self.lex.match(")"):
            args_list.append(self.parseExpression())
            
            if self.lex.match(")"):
                break
            
            self.lex.skip_whitespace()
            self.lex.expect(",")
            self.lex.skip_whitespace()

        return args_list

    # Function parameters:
    #   passed when executing a function call
    @trace
    def parseParameters(self):
        params_list = []

        while not self.lex.match(")"):
            params_list.append(self.parseVariable())
            
            if self.lex.match(")"):
                break
            
            self.lex.skip_whitespace()
            self.lex.expect(",")
            self.lex.skip_whitespace()

        return params_list

    # Function declaration/definition
    @capture
    @trace
    def parseFunction(self):
        return_type = self.lex.token()
        name = self.lex.token()
        self.lex.expect("(")
        self.lex.skip_whitespace()
        params = self.parseParameters()
        self.lex.skip_whitespace()
        self.lex.expect(")")
        
        self.lex.skip_whitespace()
        is_definition = self.lex.match_any(["{", ";"]) == "{"
        function_body = None
        
        if is_definition:
            function_body = self.parseCompoundStatement()

        return Function(return_type, name, params, function_body)
        
    @capture
    @trace
    def parseAssignment(self):
        lvalue = self.parseSymbol()
        self.lex.skip_whitespace()
        
        if self.lex.match_any(["=", "-=", "+=", "*=", "/=", "<<=", ">>=", "&=", "^=", "|="]) is not None:
            assignment_operator = self.lex.expect_any(["=", "-=", "+=", "*=", "/=", "<<=", ">>=", "&=", "^=", "|="])
            self.lex.skip_whitespace()
            rvalue = self.parseExpression()
            self.lex.skip_whitespace()
            return Assignment(lvalue, assignment_operator, rvalue)
        
        return lvalue
        
    @capture
    @trace    
    def parseDeclaration(self):
        self.lex.skip_whitespace()
        type = self.lex.token() # self.parseType()
        declarations = []
        
        while not self.lex.match(";"):
            declarations.append(self.parseAssignment())
            self.lex.skip_whitespace()
            
            if self.lex.match(";"):
                break
            
            self.lex.skip_whitespace()
            self.lex.expect(",")
            self.lex.skip_whitespace()
            
        self.lex.expect(";")
            
        return Declaration(type, declarations)
            
        
    @capture
    @trace
    def parseIf(self):
        self.lex.expect("if")
        self.lex.skip_whitespace()
        self.lex.expect("(")
        self.lex.skip_whitespace()
        if_true_condition = self.parseExpression()
        self.lex.skip_whitespace()
        self.lex.expect(")")
        self.lex.skip_whitespace()
        then_body = self.parseCompoundStatement()
        
        else_statement = None
        if self.lex.match("else"):
            self.lex.expect("else")
            self.lex.skip_whitespace()
            if self.lex.match("if"):
                else_statement = self.parseIf()
            else:
                self.lex.skip_whitespace()
                if self.lex.match("{"):
                    else_statement = self.parseCompoundStatement()
                else:
                    else_statement = None
        
        return Conditional(if_true_condition, then_body, else_statement, False)
                
    @capture
    @trace
    def parseFor(self):
        self.lex.expect("for")
        self.lex.skip_whitespace()
        self.lex.expect("(")
        iterator = self.parseDeclaration()
        self.lex.expect(";")
        cond = self.parseExpression()
        self.lex.expect(";")
        step = self.parseExpressionStatement()
        self.lex.expect(")")
        self.lex.skip_whitespace()
        
        body = self.parseCompoundStatement()
        
        return Conditional(cond, body, True)

    @capture
    @trace
    def parseWhile(self):
        self.lex.expect("while")
        self.lex.skip_whitespace()
        self.lex.expect("(")
        cond = self.parseExpression()
        self.lex.expect(")")
        self.lex.skip_whitespace()

        body = self.parseCompoundStatement()
        
        return Conditional(cond, body, True)

    @capture
    @trace
    def parseReturn(self):
        self.lex.expect("return")
        self.lex.skip_whitespace()
        return_value = self.parseExpression()
        self.lex.skip_whitespace()
        self.lex.expect(";")
        
        return Return(return_value)

    
    @capture
    @trace
    def parseExpressionStatement(self):
        
        self.lex.skip_whitespace()
        standalone_expression = self.attempt([
            self.parseAssignment
        ])
        self.lex.skip_whitespace()
        self.lex.expect(";")
        self.lex.skip_whitespace()
        
        return ExpressionStatement(standalone_expression)
        
    @capture
    @trace
    def parseStatement(self):
        self.lex.skip_whitespace()
        deterministic_parse = self.lex.match_any(["if", "for", "while", "return", "{"])
                   
        match deterministic_parse:
            case "if":
                return self.parseIf()
            case "for":
                return self.parseFor()
            case "while":
                return self.parseWhile()
            case "return":
                return self.parseReturn()
            case "{":
                return self.parseCompoundStatement()
            case None:
                return self.attempt([
                    self.parseExpressionStatement,
                    self.parseDeclaration
                ])
        
    @capture
    @trace   
    def parseStatements(self):
        
        program = []
        while not self.lex.is_eof():
            self.lex.skip_whitespace()
            program.append(self.parseStatement())
            self.lex.skip_whitespace()
            
        self.lex.skip_whitespace()
            
        return TranslationUnit(self.lex.filename, program)
    
         
    def parseFile(self):
        program = self.parseStatements()
        
        if self.debug: displayAst(program)
        return program
    



    def parseTypedef(self):
        pass


    def parseStruct(self):
       pass
   
   
    @capture
    @trace  
    def parseArrayLiteral(self):
        self.lex.expect("{")
        self.lex.skip_whitespace()
        
        self.lex.eat_until("}")
        pass
        
    @capture
    @trace
    def parseType(self):
        type = self.lex.token()
        
        # Struct
        if type == "struct":
            struct_name = self.lex.token()
        
        option = self.lex.expect_any(["[]", "*", ""])
        
        
        
        self.lex.skip_whitespace()
        
        return None
    
    
    @capture
    @trace
    def parseRValue(self):
        '''
            All LValues
            
        '''
        pass
    
    
    @capture
    @trace
    def parseLValue(self):
        '''
            [x] - Identifiers
            [x] - Member selections ('dot' or 'pointer')
            [x] - Array indexing aka subscripting 
            [ ] - Dereferenced variable
            [ ] - All of the aboves while grouped (i.e enclosed within '(' ')')
        '''
        pass