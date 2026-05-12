# Knowledge Representation and Reasoning (KRR)

## Overview

KRR is the field of AI concerned with how to formally represent knowledge
about the world in a way that a computer system can reason about it.

---

## Logic Foundations

### Propositional Logic

Atomic propositions connected by:
- `¬` (negation), `∧` (and), `∨` (or), `→` (implication), `↔` (biconditional)

**Satisfiability:** An interpretation (assignment of T/F to all atoms) that makes
a formula true. A formula is a **tautology** if true under all interpretations.

**Normal forms:**
- **CNF** (Conjunctive Normal Form): conjunction of clauses (disjunctions of literals)
- **DNF** (Disjunctive Normal Form): disjunction of conjunctions of literals

### First-Order Logic (FOL)

Extends propositional logic with:
- **Constants, variables, function symbols** in terms
- **Predicate symbols** for relations: `Teaches(alice, cs)`, `Parent(x, y)`
- **Quantifiers:** ∀ (for all), ∃ (there exists)

**Example:**
```
∀x (Student(x) → ∃y (Course(y) ∧ EnrolledIn(x, y)))
```
"Every student is enrolled in at least one course."

**Limitations of FOL for practical KRR:**
- Undecidable in general (semi-decidable)
- Open-World Assumption (OWA): absence of info ≠ falsity

---

## Description Logics (DL)

Description Logics are decidable fragments of FOL used for ontology representation.

### Key Constructors (ALC — Attributive Language with Complements)

| Constructor | Syntax | Semantics |
|-------------|--------|-----------|
| Top | ⊤ | All individuals |
| Bottom | ⊥ | Empty set |
| Atomic concept | A | A set of individuals |
| Negation | ¬C | Complement of C |
| Conjunction | C ⊓ D | Intersection |
| Disjunction | C ⊔ D | Union |
| ∃ restriction | ∃r.C | Individuals related via r to some C |
| ∀ restriction | ∀r.C | Individuals related via r only to C instances |

### TBox and ABox

- **TBox** (terminological): general knowledge about concepts and roles
  - `Professor ⊑ ∀teaches.Course` ("professors only teach courses")
- **ABox** (assertional): facts about specific individuals
  - `Professor(alice)`, `teaches(alice, cs_intro)`

### Reasoning Tasks

- **Satisfiability:** Is a concept non-empty? Can it have an instance?
- **Subsumption:** Does `C ⊑ D` follow from the TBox? (Is C a subclass of D?)
- **Instance checking:** Is individual `a` an instance of concept `C`?
- **Retrieval:** Which individuals are instances of `C`?

### OWL (Web Ontology Language)

OWL is the W3C standard for ontologies, based on DLs:
- **OWL Lite** ≈ SHIF(D)
- **OWL DL** ≈ SHOIN(D)
- **OWL 2** ≈ SROIQ(D)

**Open World Assumption (OWA):** In OWL, if something is not stated, it is
*unknown*, not false. This contrasts with databases (Closed World Assumption).

---

## Argumentation Theory

Argumentation formalises reasoning under uncertainty and conflict by representing
arguments and the attacks between them.

### Abstract Argumentation (Dung 1995)

An **argumentation framework** is a pair `AF = (A, Attacks)` where:
- `A` is a set of arguments
- `Attacks ⊆ A × A`; `(a, b) ∈ Attacks` means argument a attacks argument b

**Semantics — sets of "acceptable" arguments:**

| Semantics | Definition |
|-----------|-----------|
| **Conflict-free** | No argument in S attacks another in S |
| **Admissible** | Conflict-free + defends all its members |
| **Complete** | Admissible + contains all arguments it defends |
| **Grounded** | Least fixed point — most sceptical complete extension |
| **Preferred** | Maximal admissible sets |
| **Stable** | Conflict-free S that attacks every argument outside S |

### Defeasible Reasoning

Extends classical logic with defeasible (presumptive) rules that can be defeated
by more specific or stronger rules.

**Structure of an argument:**
- **Support:** set of facts and rules used
- **Claim:** the conclusion the argument supports
- **Defeat:** one argument defeats another if it attacks an assumption or rule used

### Actual Causation (Halpern-Pearl Model)

A formal model to determine whether event `C` was an *actual cause* of `E`
in a given context.

`C` is an actual cause of `E` iff there exists a contingency `W` such that:
1. `C` and `E` both occurred in the actual world
2. Under contingency `W`, if `C` had not occurred, `E` would not have occurred
   (counterfactual dependence)
3. `C` is minimal (no subset is also a cause)
