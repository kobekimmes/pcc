def assert_equals(lex, msg, one, two):
    if one != two:
        raise Error(lex, msg)

class Error(Exception):
    def __init__(self, lexer, err_msg):
        self.err_msg = err_msg
        self.lexer = lexer
        super().__init__(err_msg)

    def __str__(self):
        return f"{self.err_msg} {self.lexer}"


class ParseError(Error):
    def __init__(self, lexer, err_msg):
        super().__init__(lexer, f"Parse error: {err_msg}")


class SyntaxError(Error):
    def __init__(self, lexer, err_msg):
        super().__init__(lexer, f"Syntax error: {err_msg}")


class ValueError(Error):
    def __init__(self, lexer, err_msg):
        super().__init__(lexer, f"Value error: {err_msg}")


class RuntimeError(Error):
    def __init__(self, lexer, err_msg):
        super().__init__(lexer, f"Runtime error: {err_msg}")
        
class DebugError(Error):
    def __init__(self, lexer, err_msg):
        super().__init__(lexer, f"Debug error: {err_msg}")