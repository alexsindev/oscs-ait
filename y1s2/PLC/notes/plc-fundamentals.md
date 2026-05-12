# Programming Languages & Compilers

## Language Processing Phases

```
Source Code
    ↓ Lexical Analysis (Scanner)
Token Stream
    ↓ Syntax Analysis (Parser)
Parse Tree / AST
    ↓ Semantic Analysis
Annotated AST
    ↓ Intermediate Code Generation
IR (3-address code)
    ↓ Optimisation
Optimised IR
    ↓ Code Generation
Target Code (machine / bytecode)
```

---

## Lexical Analysis

The scanner reads characters and groups them into **tokens** (terminal symbols).

**Token types:** keyword, identifier, integer literal, float literal, operator, delimiter

### Regular Expressions → DFA

1. Write RegEx for each token class
2. Build NFA via Thompson's construction
3. Convert NFA → DFA (subset construction)
4. Minimise DFA (Hopcroft's algorithm)
5. Run DFA on input; longest match wins

### PLY Lexer (Python)

```python
import ply.lex as lex

tokens = ('NUMBER', 'PLUS', 'TIMES', 'LPAREN', 'RPAREN', 'ID')

t_PLUS   = r'\+'
t_TIMES  = r'\*'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ID     = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()
```

---

## Syntax Analysis

The parser checks token sequences against the grammar and builds a parse tree.

### Grammar Classification

| Type | Parser | Examples |
|------|--------|---------|
| LL(k) | Top-down, predictive | k=1 common; recursive descent |
| LR(0) | Bottom-up, shift-reduce | Simplest SLR |
| SLR(1) | Bottom-up, follow sets | SLR |
| LALR(1) | Bottom-up, lookahead | yacc/bison default |
| Canonical LR(1) | Full LR | Most powerful, largest tables |

### LL(1) Parsing

**FIRST(α):** Set of terminals that can begin strings derived from α.
**FOLLOW(A):** Set of terminals that can appear immediately after A.

**LL(1) Parse Table:** `M[A, a]` = production to use when parsing non-terminal A
with lookahead a.

```
M[A, a] = A → α    if a ∈ FIRST(α)
M[A, a] = A → α    if ε ∈ FIRST(α) and a ∈ FOLLOW(A)
```

**A grammar is LL(1) iff** the parse table has no conflicts.

### Shift-Reduce Parsing (LR)

The parser uses a **stack** and the **remaining input**:
- **Shift:** Push next input token onto stack
- **Reduce:** Pop handle from stack; push the corresponding LHS non-terminal

**Handle:** A sentential form `αβw` where `β` is the right side of some production
and reducing `β → A` is the correct action.

```
Stack:    Action:
          Input: +*nnn
+         shift +
+*        shift *
+*n       shift n
+*E       reduce n → E (by E → n)
+E        reduce *E → E (by E → *E)... wait, need operator on right
```

**Conflicts:**
- **Shift-Reduce conflict:** Unclear whether to shift next token or reduce current handle
- **Reduce-Reduce conflict:** Two different productions could reduce the same handle

### SLR(1) Parsing

Builds on LR(0) items (marked positions in productions) using FOLLOW sets to
resolve reduce conflicts.

**Action table:** `action[s, a]` = shift to state t, reduce by production,
accept, or error.
**Goto table:** `goto[s, A]` = next state after reducing to non-terminal A.

**LR(0) Item:** Production with a dot marking parse progress:
- `E → E + • T` (expecting T next)
- `E → E + T •` (ready to reduce)

**Item closure:** Add all items derivable by the dot position.
**Goto(I, X):** Move dot past X in all items of I.

### PLY Parser (LALR(1))

```python
import ply.yacc as yacc

def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = p[1] + p[3]

def p_expression_term(p):
    'expression : term'
    p[0] = p[1]

def p_term_times(p):
    'term : term TIMES factor'
    p[0] = p[1] * p[3]

def p_factor_num(p):
    'factor : NUMBER'
    p[0] = p[1]

def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]

def p_error(p):
    print(f"Syntax error at '{p.value}'")

parser = yacc.yacc()
result = parser.parse("3 + 4 * 2")
```

---

## Abstract Syntax Trees (AST)

An AST is a condensed parse tree that omits syntactic noise (parentheses,
delimiters) and represents the program's structure.

```python
class BinOp:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class Num:
    def __init__(self, value):
        self.value = value

# 3 + 4 * 2
ast = BinOp('+', Num(3), BinOp('*', Num(4), Num(2)))

def eval_ast(node):
    if isinstance(node, Num):
        return node.value
    l = eval_ast(node.left)
    r = eval_ast(node.right)
    if node.op == '+': return l + r
    if node.op == '*': return l * r
```

---

## Type Systems

A type system assigns types to expressions and enforces type safety.

### Static vs Dynamic Typing

- **Static:** Types checked at compile time (Java, C, Haskell, Rust)
- **Dynamic:** Types checked at runtime (Python, JavaScript, Ruby)
- **Gradual:** Mix of both (TypeScript, mypy for Python)

### Type Rules

Formalised as inference rules:

```
Γ ⊢ e₁ : Int    Γ ⊢ e₂ : Int
─────────────────────────────  (T-Plus)
      Γ ⊢ e₁ + e₂ : Int
```

"In context Γ, if e₁ and e₂ have type Int, then e₁ + e₂ has type Int."

### Type Environments

`Γ = {x: Int, y: Bool, f: Int → Bool}` maps variable names to types.

Typing rules thread Γ through the derivation.

### Polymorphism

- **Parametric:** `id : ∀α. α → α` — works for any type
- **Subtype (OOP):** If `Dog` is a subtype of `Animal`, a `Dog` can be used
  where `Animal` is expected
- **Ad-hoc (overloading):** Same name, different types, different implementations

---

## Attribute Grammars

Attach **attributes** to grammar symbols to compute semantic information during parsing.

- **Synthesised attribute:** Computed from children (bottom-up)
- **Inherited attribute:** Passed down from parent/siblings (top-down)

**Example — type propagation:**
```
D → T L
T → int   { T.type = int }
T → float { T.type = float }
L → id    { L.in = D.T.type; add_to_symtable(id.name, L.in) }
L → L₁ , id { L₁.in = L.in; add_to_symtable(id.name, L.in) }
```

---

## Programming Language Concepts

### Bindings

A **binding** associates a name with an entity (value, type, location).

- **Static binding (early binding):** At compile time
- **Dynamic binding (late binding):** At runtime (needed for polymorphism)

**Binding time** affects the language's expressiveness vs performance tradeoff.

### Scope

The textual region where a binding is valid.

- **Lexical scope (static scope):** Determined by the program text; most languages
- **Dynamic scope:** Determined by the call stack at runtime; some older languages

**Closures:** A function bundled with its lexical environment — captures bindings
from the enclosing scope.

```python
def make_adder(n):
    def adder(x):
        return x + n   # closes over n
    return adder

add5 = make_adder(5)
add5(3)  # → 8
```

### Storage Allocation

- **Static allocation:** Fixed addresses; global variables, static locals
- **Stack allocation:** Activation records (frames) for function calls
- **Heap allocation:** Dynamic allocation; manual (C malloc/free) or GC (Java, Python)

### Activation Records (Stack Frames)

Each function call creates a frame on the call stack:
```
[return address]
[saved registers]
[local variables]
[temporaries]
[parameters]
← frame pointer (FP)
```
