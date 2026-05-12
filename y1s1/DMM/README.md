# Database Modeling & Management (DMM)

## Course Overview

Covers relational database design, SQL, NoSQL (document and graph databases),
indexing structures (B-Trees), and transaction management. Mini-projects apply
these concepts on a research project management domain (RMPO).

## Topics

- Entity-Relationship (ER) modeling and normalisation (1NF–BCNF)
- Relational algebra and SQL (DDL, DML, transactions, views, indexes)
- B-Tree and B+-Tree index structures
- NoSQL: document model (MongoDB), graph model (Neo4j / Cypher)
- Transaction management: ACID, isolation levels, concurrency control
- Query optimisation: explain plans, index strategies

## Contents

```
DMM/
├── notes/
│   └── database-fundamentals.md   Study notes
└── projects/
    ├── rmpo-schema.sql             Full relational schema + seed data (MySQL)
    ├── transactions.sql            Example transaction patterns
    ├── mysql-docker-compose.yml    MySQL container setup
    └── neo4j-docker-compose.yml    Neo4j container setup
```

## Projects

### RMPO — Research Project Management Office

A fully normalised relational database for managing university research projects,
personnel, funding, milestones, and outputs. Entities include:

- `projects`, `departments`, `people`, `donor_sponsors`
- `project_personnels`, `project_fundings`, `project_departments`
- `student_assignments`, `milestones`, `research_outputs`, `budget_installments`

See [projects/rmpo-schema.sql](projects/rmpo-schema.sql) for the full DDL + seed data.
