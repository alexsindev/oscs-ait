# Programming Languages & Compilers (PLC)

## Course Overview

Covers the theory and implementation of programming languages and compilers —
from formal definitions of syntax and semantics through lexical analysis, parsing,
type systems, and code generation.

## Topics

- Programming language concepts: values, types, storage, bindings, scope
- Type systems: static vs dynamic typing, type checking, type inference
- Lexical analysis (scanning): regular expressions, DFA, lexer generators (PLY lex)
- Syntax analysis (parsing): CFGs, LL(1), LR(0), SLR(1), canonical LR(1) parsing
- Shift-reduce parsing: stack-based, handles, conflict resolution
- Semantic analysis: attribute grammars, synthesised and inherited attributes
- Intermediate representation, code generation
- Abstraction mechanisms: procedures, closures, higher-order functions

## Contents

```
PLC/
├── notes/
│   └── plc-fundamentals.md
└── projects/
    ├── sr-parser/               Shift-reduce parser implementation (Python)
    │   ├── parser.py
    │   └── grammar.txt
    └── compiler-starter/        Propositional logic evaluator (PLY + PySide6 GUI)
        └── src/
            ├── example/         Example language interpreter
            └── prop_evaluator/  Propositional formula evaluator
```

## Projects

### Shift-Reduce Parser (`projects/sr-parser/`)

A backtracking shift-reduce parser implemented from scratch in Python.
Reads a grammar from a text file and parses an input string, printing the
shift/reduce steps and detecting ambiguity (multiple valid reductions).

**Run:**
```bash
python parser.py
```

**Grammar format (`grammar.txt`):**
```
E -> E+T
E -> T
T -> T*n
T -> n
```

### Compiler Starter — Propositional Logic Evaluator (`projects/compiler-starter/`)

Uses PLY (Python Lex-Yacc) to build a lexer + LALR(1) parser for:
1. **Example language:** arithmetic expressions with variables
2. **Propositional logic evaluator:** parse and evaluate logical formulas with
   AND, OR, NOT, implication — includes a PySide6 GUI

**Run:**
```bash
uv run python src/prop_evaluator/main.py
```
