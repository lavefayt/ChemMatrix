# ChemMatrix: Chemical Equation Balancing Through Linear Algebra

**Group members:** [Names]

**Course and section:** [Course / Section]

**Instructor:** [Name]

**Submission date:** [Date]

*Editable report draft: target 2–3 pages after formatting. Topic acceptance remains
unconfirmed because chemistry is not one of the handout's four listed categories.*

## System description and objectives

Balancing a chemical equation requires equal atom counts for every element on
both sides. The formulas identify the substances, while their coefficients
describe relative quantities. Changing a formula would change the substance, so
the problem is to find coefficients that preserve every element simultaneously.
This makes equation balancing a practical application of a homogeneous linear
system.

ChemMatrix is an offline Python desktop prototype that connects this conservation
problem to matrix methods. It accepts an unbalanced equation, generates the
conservation matrix, displays exact row operations, derives whole-number
coefficients, and verifies the result. A practice mode provides ten exercises
with hints, retries, and atom-count feedback. The objectives are to model a
system using simultaneous linear equations, solve it through elimination, and
interpret the resulting coefficient ratios in context.

## Mathematical model

Consider the equation `C3H8 + O2 -> CO2 + H2O`. Let a, b, c, and d be the
coefficients of propane, oxygen, carbon dioxide, and water, respectively.
Conserving carbon, hydrogen, and oxygen produces three simultaneous equations:

```text
3a - c = 0
8a - 2d = 0
2b - 2c - d = 0
```

These equations have the matrix form `Ax = B`, where B is the zero vector:

```text
    [ 3  0  -1   0 ]      [ a ]       [ 0 ]
A = [ 8  0   0  -2 ]  x = [ b ]   B = [ 0 ]
    [ 0  2  -2  -1 ]      [ c ]       [ 0 ]
                         [ d ]
```

The rows correspond to elements and the columns to compound coefficients.
Reactant atom counts are positive and product counts negative. A is 3×4, x is
4×1, and B is 3×1. This is a homogeneous system because subtracting the product
counts from the reactant counts must give zero for each element.

## Solution process

ChemMatrix uses Gauss–Jordan elimination, continuing Gaussian elimination until
each pivot is 1 and the other entries in its column are zero. The program uses
exact fractions to avoid decimal-rounding errors and records a matrix snapshot
after every elementary row operation.

For the propane model, it scales R1 by 1/3, eliminates the first entry of R2,
swaps R2 and R3, and scales the new R2 by 1/2. It then scales R3 by 3/8 and
eliminates the third-column entries in R1 and R2. The reduced matrix is:

```text
[ 1  0  0  -1/4 ]
[ 0  1  0  -5/4 ]
[ 0  0  1  -3/4 ]
```

Thus a=d/4, b=5d/4, and c=3d/4. The matrix has rank 3 and one free variable,
so its nullity is 4−3=1. The general solution is
`x=t(1/4,5/4,3/4,1)`. Multiplying this basis vector by the least common multiple
of its denominators, 4, gives `(1,5,3,4)`. Its greatest common divisor is 1, so
this is the smallest positive integer ratio:

**C3H8 + 5O2 → 3CO2 + 4H2O**

There are infinitely many real solutions to the homogeneous system, including
zero. Positive integer multiples of the primitive vector also balance the
equation. The application selects the smallest ratio for a concise answer.
The matrix is rectangular, so its determinant is undefined. For square matrices,
a zero determinant establishes a nontrivial nullspace, but does not alone
guarantee that every chemical coefficient can be positive.

## Verification and interpretation

Substitution into the original equations gives `3(1)−3=0`, `8(1)−2(4)=0`, and
`2(5)−2(3)−4=0`. Independently counting atoms gives:

| Element | Reactant atoms | Product atoms |
| --- | --- | --- |
| Carbon | 3 | 3 |
| Hydrogen | 8 | 8 |
| Oxygen | 10 | 10 |

The result represents a ratio of one propane molecule to five oxygen molecules,
producing three carbon dioxide molecules and four water molecules. The same
ratio applies to moles. These equalities demonstrate conservation of atoms;
they do not establish reaction conditions, rates, or chemical feasibility.

## Prototype summary and reflection

The Balancer tab presents equation input, the mathematical model, individual
solution steps, and verification. The Practice tab asks learners to enter one
coefficient per compound and identifies mismatched element counts. Proportional
answers are recognized as balanced, with a prompt to reduce them. Hints and
reveals are marked as assisted, and progress lasts for the current session.

The prototype supports neutral formulas and parentheses. It reports invalid
notation, zero-only systems, and one-dimensional solutions that require zero or
mixed-sign coefficients. When multiple independent free variables remain, it
shows the general solution without automatically selecting a balance. It does
not support ionic or hydrate notation.

ChemMatrix illustrates how a domain rule can become a computational model:
identify quantities, express constraints, organize coefficients, solve, and
check the result against the original system. Separating parsing, matrix
arithmetic, verification, and presentation also makes the software easier to
test and explain. The prototype demonstrates these mathematical and software
connections; it does not claim measured improvement in learning outcomes.
