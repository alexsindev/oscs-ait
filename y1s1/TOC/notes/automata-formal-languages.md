# Automata Theory and Formal Languages

## Formal Language Hierarchy (Chomsky)

```
Type 0  Recursively Enumerable   Turing Machines           (unrestricted grammars)
Type 1  Context-Sensitive        Linear-Bounded Automata
Type 2  Context-Free             Pushdown Automata          (CFG)
Type 3  Regular                  Finite Automata / RegEx
```

Each class is a strict subset of the one above it.

---

## Regular Languages

### Deterministic Finite Automata (DFA)

A DFA is a 5-tuple `M = (Q, Σ, δ, q₀, F)` where:
- `Q` — finite set of states
- `Σ` — input alphabet
- `δ: Q × Σ → Q` — transition function (total)
- `q₀ ∈ Q` — start state
- `F ⊆ Q` — set of accepting states

A string `w` is **accepted** iff the computation starting from `q₀` ends in a
state in `F`.

### Nondeterministic Finite Automata (NFA)

Same tuple but `δ: Q × (Σ ∪ {ε}) → 2^Q` — transitions can be to a *set* of states
and ε-transitions (moving without consuming input) are allowed.

**NFA → DFA (subset construction):**
Each DFA state is a *set* of NFA states. Start with ε-closure of q₀.
For each input symbol, compute ε-closure of the union of all reachable NFA states.

The languages accepted by DFAs = NFAs = regular expressions (all define regular languages).

### Regular Expressions

Built from:
- `∅` (empty language), `ε` (empty string), `a` (single symbol)
- `r₁ | r₂` (union), `r₁ · r₂` (concatenation), `r*` (Kleene star)

**RegEx → NFA (Thompson's construction):** Build NFA inductively.
**NFA → RegEx:** State elimination method.

### Closure Properties of Regular Languages

Regular languages are closed under:
- Union, intersection, complement
- Concatenation, Kleene star
- Reversal, homomorphism, inverse homomorphism

### Pumping Lemma for Regular Languages

If `L` is regular, there exists `p` (pumping length) such that any string
`w ∈ L` with `|w| ≥ p` can be split as `w = xyz` where:
1. `|xy| ≤ p`
2. `|y| ≥ 1`
3. `xy^i z ∈ L` for all `i ≥ 0`

**Use:** To *disprove* regularity by showing no valid split exists.

*Classic example:* `L = {aⁿbⁿ | n ≥ 0}` is not regular.

---

## Context-Free Languages

### Context-Free Grammar (CFG)

A CFG is `G = (V, Σ, R, S)` where:
- `V` — non-terminal variables
- `Σ` — terminal alphabet
- `R` — production rules of the form `A → α` where `A ∈ V`, `α ∈ (V ∪ Σ)*`
- `S ∈ V` — start symbol

Derivation: `S ⇒* w` by repeatedly replacing non-terminals using rules.

**Leftmost derivation:** always expand the leftmost non-terminal.

**Parse tree:** tree where root is `S`, internal nodes are variables, leaves are terminals.

### Chomsky Normal Form (CNF)

Every CFG can be converted to CNF where all rules are:
- `A → BC` (two variables)
- `A → a` (one terminal)
- `S → ε` (only if ε ∈ L)

CNF is required by the CYK algorithm.

### CYK Algorithm

Dynamic programming algorithm to decide if `w ∈ L(G)` in O(n³ |G|) time.

**Input:** Grammar in CNF, string `w = a₁a₂…aₙ`

**Table:** `T[i][j]` = set of variables that derive `w[i..j]`

```
Base case: T[i][i] = { A | A → aᵢ ∈ R }

Recursive:
T[i][j] = { A | A → BC ∈ R,
                 B ∈ T[i][k],
                 C ∈ T[k+1][j],
                 for some k: i ≤ k < j }

Accept if S ∈ T[1][n]
```

### Pushdown Automata (PDA)

A PDA extends an NFA with an unbounded stack: `M = (Q, Σ, Γ, δ, q₀, Z₀, F)`
- `Γ` — stack alphabet
- `Z₀` — initial stack symbol
- `δ: Q × (Σ ∪ {ε}) × Γ → 2^(Q × Γ*)` — (state, input, stack top) → set of (new state, stack replacement)

PDAs accept context-free languages (CFG ↔ PDA equivalence).

### Pumping Lemma for Context-Free Languages

If `L` is CFL, there exists `p` such that any `w ∈ L` with `|w| ≥ p` can be split
`w = uvxyz` where:
1. `|vxy| ≤ p`
2. `|vy| ≥ 1`
3. `uvⁱxyⁱz ∈ L` for all `i ≥ 0`

*Classic example:* `L = {aⁿbⁿcⁿ | n ≥ 0}` is not context-free.

### Closure Properties of CFLs

CFLs are closed under: union, concatenation, Kleene star.
CFLs are **not** closed under: intersection, complement (in general).
CFL ∩ Regular = CFL (closed under intersection with regular languages).

---

## Turing Machines

A TM is `M = (Q, Σ, Γ, δ, q₀, q_accept, q_reject)` where:
- `Γ` — tape alphabet (`Σ ⊆ Γ`, blank symbol `⊔ ∈ Γ`)
- `δ: Q × Γ → Q × Γ × {L, R}` — (state, tape symbol) → (new state, write symbol, move head)

The tape is infinite in both directions. Computation halts when it reaches `q_accept` or `q_reject`.

**Configurations:** `(q, tape, head position)`. Language is **Turing-recognizable** if some TM accepts every string in it (may loop on strings not in L). **Decidable** if TM always halts.

### Church-Turing Thesis

Any effectively computable function can be computed by a Turing machine.
(Informal — not provable, but universally accepted.)

### Decidability

A language `L` is **decidable** if there is a TM that always halts and correctly
accepts/rejects every input.

**Undecidable problems:**
- **Halting Problem:** Does TM `M` halt on input `w`? — Undecidable (diagonal argument).
- `A_TM = {⟨M,w⟩ | M accepts w}` — Recognizable but not decidable.
- Post Correspondence Problem (PCP)

**Reduction:** If `A ≤_m B` (A reduces to B) and B is decidable, then A is decidable.
Contrapositive: if A is undecidable and A ≤_m B, then B is undecidable.

---

## Complexity Theory

### Time Complexity

`TIME(f(n))` — class of languages decidable in `O(f(n))` time.

- **P** = ⋃_k TIME(n^k) — problems solvable in polynomial time
- **NP** — problems verifiable in polynomial time (or decidable by nondeterministic TM in poly time)
- **NP-complete** — in NP, and every NP problem reduces to it in poly time
- **NP-hard** — every NP problem reduces to it (not necessarily in NP itself)

```
P ⊆ NP ⊆ PSPACE ⊆ EXPTIME
```

**P vs NP:** Is P = NP? One of the most important open problems in CS. Most believe P ≠ NP.

### Cook-Levin Theorem

SAT (Boolean satisfiability) is NP-complete.
Every NP problem can be reduced to SAT in polynomial time.

### NP-Complete Examples

- SAT, 3-SAT
- Graph Colouring (k ≥ 3)
- Hamiltonian Path / Cycle
- Clique, Independent Set, Vertex Cover
- Subset Sum, Knapsack (decision version)
- Travelling Salesman Problem (decision version)

### Reductions

To show problem `B` is NP-complete:
1. Show `B ∈ NP` (give a polynomial verifier).
2. Choose a known NP-complete problem `A`.
3. Show `A ≤_P B` (poly-time reduction from A to B).
