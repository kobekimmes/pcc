# pcc
## 🐍 The Python C Compiler

pcc is a **C interpreter written in Python**.  
It takes in C source code, parses it into an abstract syntax tree (AST) and can interpret the program directly

---

## ✨ Components

- **Lexical Analysis** → custom lexer with token definitions for C syntax.  
- **Parsing** → builds an Abstract Syntax Tree (AST) for C programs.  
- **Interpreter** → type checking, scoping, environment management and evaluation. 

---

## 📦 Project Structure

```
gcc/
├── src/
│   ├── c_lexer.py        # tokenization
│   ├── c_parse.py        # parsing into AST
│   ├── c_ast.py          # AST node definitions
│   ├── c_env.py          # scope / environment logic
│   ├── c_interpreter.py  # AST interpreter
│   ├── c_codegen.py      # code generation (planned)
│   ├── c_error.py        # compiler-specific exceptions
│   └── main.py           # entry point / driver via command-line
├── tests/                # unit tests
├── .gitignore
├── pyproject.toml
└─- README.md
```

---

## 📝 Plans

1. Implement codegen to target specific IR

## Resources & References

- [Crafting Interpreters by Robert Nystrom](https://craftinginterpreters.com)
What a beautiful book, highly recommend!
