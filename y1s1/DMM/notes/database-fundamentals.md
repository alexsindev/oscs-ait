# Database Fundamentals

## Data Models

A **data model** defines how data is structured, queried, and constrained.

| Model | Structure | Query Language | Example Systems |
|-------|-----------|---------------|-----------------|
| Relational | Tables (relations) | SQL | MySQL, PostgreSQL, SQLite |
| Document | JSON/BSON documents | MQL / aggregation | MongoDB, CouchDB |
| Graph | Nodes + edges | Cypher, Gremlin | Neo4j, Amazon Neptune |
| Key-Value | Hash map | GET/SET/DEL | Redis, DynamoDB |
| Column-Family | Wide rows | CQL | Cassandra, HBase |

---

## Entity-Relationship (ER) Modeling

ER diagrams capture real-world entities, their attributes, and relationships
before translating to a relational schema.

**Cardinalities:**
- One-to-One (1:1)
- One-to-Many (1:N)
- Many-to-Many (M:N) — requires a junction table

**Participation:**
- Total (every entity must participate) — double line
- Partial (participation is optional) — single line

**Weak Entities:** Entities that cannot be uniquely identified without a
related "owner" entity. Depend on a partial key + owner's primary key.

### ER → Relational Translation Rules

1. Each entity becomes a table; primary key maps directly.
2. A 1:N relationship: add a foreign key on the "many" side.
3. A M:N relationship: create a junction table holding both PKs.
4. A 1:1 relationship: add FK on the side with total participation (or merge).
5. Multi-valued attributes become a separate table with FK back to owner.

---

## Normalisation

Normal forms eliminate data anomalies (insert / update / delete).

### Functional Dependencies

`A → B` means: knowing A uniquely determines B.

- **Full FD:** B depends on all of A (not a proper subset of A).
- **Partial FD:** B depends on only part of a composite key.
- **Transitive FD:** A → B and B → C (so A → C transitively).

### Normal Forms

**1NF:** All attributes are atomic (no repeating groups, no nested arrays).

**2NF:** 1NF + no partial dependencies (all non-key attributes depend on the
whole primary key).

**3NF:** 2NF + no transitive dependencies (non-key attributes do not depend on
other non-key attributes).

**BCNF (Boyce-Codd):** For every non-trivial FD `X → Y`, X must be a
superkey. Stricter than 3NF; eliminates anomalies involving prime attributes.

**Decomposition:** Split a relation to remove a violation. Must preserve:
1. Lossless join (can reconstruct original relation)
2. Dependency preservation (FDs enforceable without joins)

---

## SQL

### DDL (Data Definition Language)

```sql
CREATE TABLE people (
    person_id   INT          AUTO_INCREMENT PRIMARY KEY,
    first_name  VARCHAR(100) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    department_id INT,
    FOREIGN KEY (department_id)
        REFERENCES departments(department_id) ON DELETE SET NULL,
    INDEX idx_email (email)
);

ALTER TABLE people ADD COLUMN phone VARCHAR(20);

DROP TABLE IF EXISTS temp_table;
```

### DML (Data Manipulation Language)

```sql
-- Insert
INSERT INTO departments (name, code) VALUES ('Computer Science', 'CS');

-- Select with joins
SELECT p.first_name, p.email, d.department_name
FROM   people p
JOIN   departments d ON p.department_id = d.department_id
WHERE  p.person_type = 'Faculty'
ORDER  BY p.last_name;

-- Aggregate
SELECT d.department_name, COUNT(*) AS headcount
FROM   people p
JOIN   departments d ON p.department_id = d.department_id
GROUP  BY d.department_name
HAVING COUNT(*) > 3;

-- Subquery
SELECT title FROM projects
WHERE project_id IN (
    SELECT project_id FROM project_fundings
    WHERE funding_amount > 500000
);

-- Update
UPDATE projects
SET    project_status = 'Completed'
WHERE  contract_end_date < CURRENT_DATE
  AND  project_status = 'Active';

-- Delete
DELETE FROM student_assignments
WHERE  assignment_status = 'Terminated'
  AND  end_date < '2023-01-01';
```

### Joins

```
INNER JOIN   — rows matching both sides
LEFT JOIN    — all left rows; NULL for unmatched right
RIGHT JOIN   — all right rows; NULL for unmatched left
FULL OUTER JOIN — all rows from both; NULLs where no match
CROSS JOIN   — Cartesian product
SELF JOIN    — table joined with itself (aliased)
```

### Window Functions

```sql
SELECT
    person_id,
    department_id,
    salary,
    RANK()   OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank,
    AVG(salary) OVER (PARTITION BY department_id) AS dept_avg
FROM people;
```

### Indexes

An index is a data structure (usually a B+-Tree) that speeds up lookups
at the cost of extra writes and storage.

```sql
-- Single column
CREATE INDEX idx_status ON projects(project_status);

-- Composite (useful for queries filtering on both columns)
CREATE INDEX idx_dates ON projects(contract_start_date, contract_end_date);

-- Unique constraint also creates an index
CREATE UNIQUE INDEX idx_email ON people(email);
```

**When NOT to index:** Columns with low cardinality (e.g. boolean), small tables,
columns updated very frequently.

---

## B-Tree and B+-Tree

### B-Tree

A self-balancing tree where each node can hold multiple keys and children.
Used as the underlying structure for most database indexes.

Properties for a B-Tree of order `m`:
- Every node has at most `m` children
- Every non-leaf node (except root) has at least ⌈m/2⌉ children
- All leaves at the same depth (balanced)
- Keys in a node are sorted; subtrees between keys contain values in that range

**Search:** Start at root, follow correct child pointer → O(log n)

**Insert:** Find correct leaf, insert key; if node overflows, **split** and
push median key up to parent (cascade if parent also overflows).

**Delete:** Find key; if in internal node, replace with in-order successor from
leaf. If leaf underflows, **merge** or **redistribute** from sibling.

### B+-Tree (more common in databases)

- Internal nodes hold only keys (routing keys); **all data** lives in leaves.
- Leaf nodes are linked in a doubly-linked list → efficient range scans.
- Same insert/delete/split/merge rules as B-Tree.

**Benefit:** Full table scan = follow leaf linked list; no need to visit
internal nodes.

---

## Transactions

A transaction is a sequence of operations treated as a single logical unit.

### ACID Properties

| Property | Meaning |
|----------|---------|
| **Atomicity** | All operations succeed or all are rolled back |
| **Consistency** | DB moves from one valid state to another |
| **Isolation** | Concurrent transactions appear sequential |
| **Durability** | Committed changes survive crashes (write-ahead log) |

### Transaction Control in SQL

```sql
START TRANSACTION;

UPDATE accounts SET balance = balance - 500 WHERE id = 1;
UPDATE accounts SET balance = balance + 500 WHERE id = 2;

-- If both succeeded:
COMMIT;

-- If something went wrong:
ROLLBACK;
```

### Isolation Levels

| Level | Dirty Read | Non-repeatable Read | Phantom Read |
|-------|-----------|--------------------|----|
| Read Uncommitted | ✓ possible | ✓ | ✓ |
| Read Committed | ✗ | ✓ possible | ✓ |
| Repeatable Read | ✗ | ✗ | ✓ possible |
| Serializable | ✗ | ✗ | ✗ |

- **Dirty read:** Reading an uncommitted write from another transaction.
- **Non-repeatable read:** Same row read twice gives different values.
- **Phantom read:** A range query run twice returns different sets of rows.

### Concurrency Issues

- **Lost update:** Two transactions read-modify-write the same row; one
  overwrites the other's change.
- **Deadlock:** T1 holds lock A, waits for B; T2 holds B, waits for A.
  DBs detect cycles and roll back one participant.

---

## NoSQL

### Document Model (MongoDB)

Documents are JSON-like objects with flexible schemas.

```javascript
// Insert
db.projects.insertOne({
  title: "AI Research",
  status: "Active",
  team: ["alice", "bob"],
  budget: { amount: 500000, currency: "USD" }
})

// Query
db.projects.find({ status: "Active", "budget.amount": { $gt: 100000 } })

// Aggregation pipeline
db.projects.aggregate([
  { $match: { status: "Active" } },
  { $group: { _id: "$research_area", total: { $sum: "$budget.amount" } } },
  { $sort: { total: -1 } }
])
```

**When to use:** Hierarchical / nested data, variable schemas, rapid iteration.

### Graph Model (Neo4j / Cypher)

Nodes represent entities; edges (relationships) represent connections.
Both can carry properties.

```cypher
-- Create nodes and relationship
CREATE (alice:Person {name: "Alice"})
CREATE (proj:Project {title: "AI Research"})
CREATE (alice)-[:WORKS_ON {role: "PI"}]->(proj)

-- Query: Find everyone working on a project in CS dept
MATCH (p:Person)-[:WORKS_ON]->(proj:Project)<-[:HOSTS]-(d:Department {code: "CS"})
RETURN p.name, proj.title

-- Variable-length paths (e.g. collaboration chains)
MATCH path = (a:Person)-[:COLLABORATES*1..3]-(b:Person)
RETURN a.name, b.name, length(path)
```

**When to use:** Heavily connected data, relationship traversal, social networks,
knowledge graphs, recommendation engines.

---

## Query Optimisation

**Explain plan** shows how the database executes a query:

```sql
EXPLAIN SELECT * FROM projects WHERE project_status = 'Active';
-- Look for: type=ALL (full scan) vs type=ref/range (index used)
```

**Key optimisation rules:**
1. Filter early — push WHERE conditions as close to the table scan as possible
2. Use covering indexes — index includes all columns the query needs
3. Avoid functions on indexed columns in WHERE: `WHERE YEAR(date) = 2024`
   prevents index use; rewrite as `WHERE date BETWEEN '2024-01-01' AND '2024-12-31'`
4. Use LIMIT for pagination; avoid OFFSET on large datasets (keyset pagination)
5. Avoid SELECT * — fetch only needed columns
