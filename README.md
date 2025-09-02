pcc
The Python C Compiler

pcc is a **C interpreter written in Python**.  
It takes in C source code, parses it into an abstract syntax tree (AST), performs semantic checks, and can either interpret the program directly or translate it into target code

---

## ✨ Components

- **Lexical Analysis** → custom lexer with token definitions for C syntax.  
- **Parsing** → builds an Abstract Syntax Tree (AST) for C programs.  
- **Semantic Analysis** → type checking, scoping, and environment management.  
- **Interpreter Mode** → directly executes the AST for rapid testing.   

---

## 📦 Project Structure


gcc/
├── src/
│   ├── c_lexer.py        # tokenization
│   ├── tokens.py       # token definitions
│   ├── parser.py       # parsing into AST
│   ├── ast.py          # AST node definitions
│   ├── env.py          # scope / environment logic
│   ├── interpreter.py  # AST interpreter
│   ├── codegen.py      # code generation (planned)
│   ├── errors.py       # compiler-specific exceptions
│   └── cli.py          # compiler CLI driver
├── tests/              # unit tests
└── README.md
