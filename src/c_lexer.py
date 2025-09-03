
from c_error import *


class Lexer:

    def __init__(self, filename):
        
        self.filename = filename

        try:
            self.source_code = preprocess(open(filename, "r").read())
        except FileNotFoundError:
            raise ParseError(f"Unable to open {filename}")

        self.eof = len(self.source_code)
        
        self.new_lines = []
        self.file_pos = 0
        
        self.state = []
        
    def __str__(self):
        return (
            f"\n\n----- Lexer Debug ----------\n"
            f"Lexer @ ln{self.get_line()}:{self.get_column()}\n"
            f"File position: {self.file_pos}\n\n"
            f"```\n"
            f"{self.source_code[self.new_lines[-1] if len(self.new_lines) > 0 else 0:min(self.file_pos + 20, self.eof)]}\n"
            f"```\n"
            f"----------------------------\n"
        )
        
    def get_line(self):
        return len(self.new_lines) + 1
    
    def get_column(self):
        return (self.file_pos % (len(self.new_lines) + 1)) + 1
    
    def save_state(self):
        self.state.append({
            "file_pos" : self.file_pos,
            "line_no" : self.get_line(),
            "col_no" : self.get_column(),
        })
        
        
    def resume_state(self):
        current_state = self.state.pop()
        self.file_pos = current_state["file_pos"]
        self.line_no = current_state["line_no"]
        self.col_no = current_state["col_no"]
        

    def is_eof(self):
        return self.file_pos == self.eof


    def has_next(self, n=0):
        return self.file_pos + n < self.eof


    def next(self, n=1):
        if self.has_next(n-1):
            tmp = self.source_code[self.file_pos:self.file_pos+n]
            
            for ch in tmp:
                if ch == '\n':
                    self.new_lines.append(self.file_pos)
                self.file_pos += 1
            
            return tmp
        return None


    def peek(self, n=1):
        if self.has_next(n-1):
            return self.source_code[self.file_pos:self.file_pos+n]
        return None
    
    
    def match(self, string):
        n = len(string)
        actual = self.peek(n)
        return actual == string
    
    
    def match_any(self, strings):
        for s in strings:
            if self.match(s):
                return s
        return None


    def expect(self, string):
        n = len(string)
        actual = self.peek(n)
        if actual != string:
            raise ParseError(self, f"Expected '{string}', got '{actual}' @ ln{self.get_line()}:{self.get_column()} (position: {self.file_pos})")
        self.next(n)


    def expect_any(self, strings):
        for s in strings:
            try:
                self.expect(s)
                return s
            except ParseError:
                continue       
        else:
            raise ParseError(self, f"Expected one of {[f'{s}' for s in strings]} @ ln{self.get_line()}:{self.get_column()} (position: {self.file_pos})")
        
        
    def eat_while(self, func, fail_on=None):
        res = ""
        self.skip_whitespace()
        while self.peek() and func(self.peek()):
            if self.is_eof():
                raise ParseError(self, "Reached EOF unexpectedly")
            res += self.next()
            if fail_on:
                fail_on(self)
                
        self.skip_whitespace()
        return res


    def eat_until(self, string, fail_on=None):
        res = ""
        length = len(string)
        self.skip_whitespace()
        while self.peek(length) and self.peek(length) != string:
            if self.is_eof():
                raise ParseError(self, "Reached EOF unexpectedly")
            res += self.next()
            if fail_on:
                fail_on(self)
            
        self.skip_whitespace()
        return res
        

    def skip_whitespace(self):
        while self.peek() and whitespace(self.peek()):
            self.next()
            
    def token(self):
        token = self.eat_while(alphanum)
        if token and numeric(token[0]):
            raise SyntaxError(self, f"'{token}', identifiers cannot start with a number.")
        if len(token) == 0:
            raise ParseError(self, "Empty value")
        return token
    
    def number(self):
        number = self.eat_while(numeric)
        if "." not in number and len(number) > 1 and number[0] == '0':
            raise ValueError(self, f"Non-decimals cannot begin with zero.")
        return number
            
    def string(self):
        self.expect("\"")
        string =  self.eat_until("\"", fail_on_new_line)
        self.expect("\"")
        return string
    
    def character(self):
        self.expect("'")
        char = self.eat_until("'", fail_on_new_line)
        
        if len(char) != 1:
            raise ValueError(self, "Character literal expected")
            
        self.expect("'")
        
        return char
        
        
        
def whitespace(char):
    return char.isspace()

def alphanum(char):
    return char.isalnum() or char == "_"

def alpha(char):
    return char.isalpha()

def numeric(char):
    return char.isnumeric() or char == "."

def fail_on_new_line(lexer):
    if lexer.peek() == "\n":
        raise ParseError(lexer, "Encountered EOL unexpectedly")
    

def preprocess(source_code):
    '''
    1. Remove comments
    2. Inject macros
    3. More stuff maybe
    '''
    return source_code