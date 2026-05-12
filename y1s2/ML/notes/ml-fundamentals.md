# Machine Learning Fundamentals

## Types of Machine Learning

| Type | Description | Examples |
|------|-------------|---------|
| **Supervised** | Learn from labelled examples `(x, y)` | Classification, Regression |
| **Unsupervised** | Discover patterns without labels | Clustering, PCA, Autoencoders |
| **Reinforcement** | Learn by interacting with environment | Q-learning, Policy Gradient |
| **Semi-supervised** | Small labelled set + large unlabelled set | Self-training |

---

## Key Concepts

### Bias-Variance Tradeoff

**Expected error = Bias² + Variance + Irreducible noise**

- **High bias (underfitting):** Model too simple, systematically wrong even on training data
- **High variance (overfitting):** Model too complex, fits noise, fails to generalise
- Goal: find the sweet spot via model selection and regularisation

### Regularisation

Adds a penalty term to the loss to constrain model complexity:

- **L2 (Ridge):** `Loss + λ||w||²` — shrinks all weights towards 0
- **L1 (Lasso):** `Loss + λ||w||₁` — drives some weights exactly to 0 (sparse models)
- **Elastic Net:** combination of L1 and L2

### Train / Validation / Test Split

```
All data → [Train 60%] [Validation 20%] [Test 20%]
```

- **Train:** Fit model parameters
- **Validation:** Tune hyperparameters, pick best model
- **Test:** Final unbiased evaluation (use only once)

**k-Fold Cross-Validation:** Split training data into k folds; train on k-1, validate on 1;
repeat k times and average scores. Expensive but uses all data for validation.

---

## Linear Models

### Linear Regression

Predict continuous output: `ŷ = wᵀx + b`

**Loss:** Mean Squared Error (MSE) = `(1/n) Σ (yᵢ - ŷᵢ)²`

**Closed-form solution (OLS):** `w = (XᵀX)⁻¹ Xᵀy`

**Gradient descent update:**
```
w ← w - α · ∂L/∂w
b ← b - α · ∂L/∂b
```

### Logistic Regression

Binary classification using the sigmoid function:

`σ(z) = 1 / (1 + e⁻ᶻ)`,  `ŷ = σ(wᵀx + b)`

**Loss:** Binary Cross-Entropy = `-Σ [y log(ŷ) + (1-y) log(1-ŷ)]`

Decision boundary: `ŷ ≥ 0.5 ↔ wᵀx + b ≥ 0`

---

## Model Evaluation Metrics

### Classification

```
               Predicted Positive   Predicted Negative
Actual Positive      TP                   FN
Actual Negative      FP                   TN
```

| Metric | Formula | Meaning |
|--------|---------|---------|
| Accuracy | (TP+TN)/(TP+TN+FP+FN) | Fraction correct |
| Precision | TP/(TP+FP) | Of predicted positives, how many are truly positive |
| Recall (Sensitivity) | TP/(TP+FN) | Of actual positives, how many did we catch |
| F1-Score | 2·P·R/(P+R) | Harmonic mean of precision and recall |
| Specificity | TN/(TN+FP) | True negative rate |

**ROC Curve:** Plots TPR vs FPR at all thresholds.
**AUC:** Area under ROC curve; 1.0 = perfect, 0.5 = random.

### Regression

- **MSE:** Mean squared error (penalises large errors)
- **MAE:** Mean absolute error (more robust to outliers)
- **R²:** Proportion of variance explained by model (0 to 1)

---

## Principal Component Analysis (PCA)

PCA finds orthogonal directions of maximum variance in the data.

**Algorithm:**
1. Standardise data (mean=0, std=1)
2. Compute covariance matrix `Σ`
3. Compute eigenvectors/eigenvalues of `Σ`
4. Sort eigenvectors by eigenvalue (descending)
5. Project data onto top k eigenvectors

**Explained variance ratio:** `λᵢ / Σλⱼ` for component i.

**Choosing k:** Keep components that explain e.g. 95% of total variance.

**Reconstruction error:** Project to k-dim space and back; compute MSE.

**Note:** PCA is a linear method. For non-linear manifolds, consider t-SNE or UMAP.

---

## Neural Networks

### Perceptron (Single Neuron)

`output = activation(Σ wᵢxᵢ + b)`

**Activation functions:**

| Function | Formula | Use |
|----------|---------|-----|
| Sigmoid | `1/(1+e⁻ˣ)` | Binary output (output layer) |
| Tanh | `(eˣ-e⁻ˣ)/(eˣ+e⁻ˣ)` | Zero-centred, hidden layers |
| ReLU | `max(0, x)` | Standard hidden layer activation |
| Leaky ReLU | `max(αx, x)` | Fixes dying ReLU |
| Softmax | `eˣⁱ / Σeˣʲ` | Multi-class output |

### Backpropagation

**Forward pass:** Compute predictions layer by layer.
**Loss:** Compare prediction to ground truth.
**Backward pass:** Chain rule — compute ∂L/∂w for each weight.
**Update:** `w ← w - α · ∂L/∂w`

```python
# PyTorch example
optimizer.zero_grad()
output = model(X)
loss = criterion(output, y)
loss.backward()      # compute gradients
optimizer.step()     # update weights
```

### Overfitting Mitigations

- **Dropout:** Randomly zero out neurons during training (rate p)
- **Batch Normalisation:** Normalise layer activations across a mini-batch
- **Early stopping:** Monitor validation loss; stop when it starts rising
- **Data augmentation:** Artificially expand training set (flips, crops, noise)

---

## Naive Bayes Classifier

Applies Bayes' theorem with the naive assumption that features are
conditionally independent given the class.

**Bayes' theorem:**
```
P(y | x₁,...,xₙ) ∝ P(y) · Π P(xᵢ | y)
```

**Gaussian Naive Bayes:** Assumes `P(xᵢ | y)` follows a Gaussian:
```
P(xᵢ | y) = (1/√(2πσ²)) · exp(-(xᵢ - μ)² / 2σ²)
```
where μ and σ² are estimated from training data per class per feature.

**Laplace smoothing (for discrete features):**
```
P(xᵢ = v | y) = (count(xᵢ=v, y) + α) / (count(y) + α·|V|)
```
Prevents zero probabilities for unseen feature values.

**Prediction:**
```
ŷ = argmax_y log P(y) + Σ log P(xᵢ | y)
```
(Log-sum for numerical stability)

---

## Reinforcement Learning

### Markov Decision Process (MDP)

`MDP = (S, A, P, R, γ)`:
- `S` — state space
- `A` — action space
- `P(s'|s,a)` — transition probability
- `R(s,a)` — reward function
- `γ` — discount factor (0 < γ < 1)

**Policy `π(a|s)`:** Probability of taking action a in state s.

**Value function:** `V^π(s) = E[Σ γᵗ Rₜ | s₀=s, π]`

**Q-function:** `Q^π(s,a) = E[Σ γᵗ Rₜ | s₀=s, a₀=a, π]`

### Bellman Equations

```
V*(s) = max_a [ R(s,a) + γ · Σ P(s'|s,a) · V*(s') ]
Q*(s,a) = R(s,a) + γ · Σ P(s'|s,a) · max_a' Q*(s',a')
```

### Q-Learning (Off-policy TD)

```python
Q[s][a] += α * (reward + γ * max(Q[s']) - Q[s][a])
```

- **ε-greedy exploration:** With prob ε, take random action; else take argmax Q.
- Model-free: does not require knowing P or R.
- Converges to optimal Q* under mild conditions.
