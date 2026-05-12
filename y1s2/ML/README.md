# Machine Learning (ML)

## Course Overview

Covers the theory and practice of supervised and unsupervised machine learning
algorithms, from mathematical foundations through to implementation and evaluation.

## Topics

- Introduction: ML problem types, bias-variance tradeoff, generalisation
- Linear models: linear regression, logistic regression, regularisation (L1/L2)
- Model evaluation: train/val/test split, cross-validation, confusion matrix, ROC/AUC
- Dimensionality reduction: PCA, explained variance, reconstruction error
- Neural networks: perceptron, backpropagation, activation functions, SGD
- Naive Bayes classifier: Bayes theorem, class-conditional independence, Laplace smoothing
- Ensemble methods: bagging, boosting, random forests
- Reinforcement learning: MDP, Q-learning, value iteration

## Contents

```
ML/
├── notes/
│   └── ml-fundamentals.md
└── labs/
    ├── naive-bayes/            Lab 9 — Naive Bayes classifier (Jupyter notebook)
    ├── gamma-ray-eda/          MAGIC dataset EDA (gamma vs hadron classification)
    └── titanic-eda/            Titanic survival EDA
```

## Labs

### Naive Bayes (`labs/naive-bayes/`)

Implements a Gaussian Naive Bayes classifier from scratch and compares it with
`sklearn.naive_bayes.GaussianNB`. Applied to a text/numeric classification task.

### MAGIC Gamma-Ray Dataset (`labs/gamma-ray-eda/`)

Exploratory data analysis on the MAGIC Gamma Telescope dataset (UCI ML Repository).
Binary classification: signal (gamma ray) vs background (hadron).
- 19,020 instances, 10 continuous features
- EDA: class distribution, feature distributions, correlation heatmap, boxplots

### Titanic Survival (`labs/titanic-eda/`)

EDA on the classic Titanic dataset.
- Feature analysis: age, fare, sex, passenger class, embarkation port
- Survival rate by each demographic variable
- Correlation analysis
