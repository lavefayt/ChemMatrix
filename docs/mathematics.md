# Mathematical model and implementation guide

## 1. Conservation of atoms gives a homogeneous system

A chemical equation specifies compounds on two sides. Balancing finds their
relative coefficients without changing any compound's formula. Each element
must have the same atom count on the reactant and product sides.

For `C3H8 + O2 -> CO2 + H2O`, let:

| Variable | Compound |
| --- | --- |
| a | C3H8 |
| b | O2 |
| c | CO2 |
| d | H2O |

The three simultaneous equations are:

```text
Carbon:    3a      - c      = 0
Hydrogen:  8a          - 2d = 0
Oxygen:        2b - 2c - d  = 0
```

The model uses the assignment's `AX = B` form with `B = 0`:

```text
          a   b   c   d
     C [  3   0  -1   0 ]        [ a ]        [ 0 ]
A =  H [  8   0   0  -2 ]    x = [ b ]    B = [ 0 ]
     O [  0   2  -2  -1 ]        [ c ]        [ 0 ]
                                [ d ]
```

A is 3×4, x is 4×1, and B is 3×1. Each matrix entry counts atoms per molecule
with a sign determined by its side. Coefficients are dimensionless ratios.

## 2. Exact Gauss–Jordan elimination

Elementary row operations preserve the solution set. ChemMatrix chooses the
first available nonzero pivot, swaps it into the current row when needed, scales
the pivot to 1, then eliminates that column in every other row. Each calculation
uses `Fraction`, so values such as 1/3 are exact rather than rounded decimals.

For propane the operations and resulting rows are:

```text
Initial:
[ 3  0  -1    0 ]
[ 8  0   0   -2 ]
[ 0  2  -2   -1 ]

R1 <- (1/3) R1:
[ 1  0  -1/3   0 ]
[ 8  0   0    -2 ]
[ 0  2  -2    -1 ]

R2 <- R2 + (-8) R1:
[ 1  0  -1/3   0 ]
[ 0  0   8/3  -2 ]
[ 0  2  -2    -1 ]

R2 <-> R3:
[ 1  0  -1/3   0 ]
[ 0  2  -2    -1 ]
[ 0  0   8/3  -2 ]

R2 <- (1/2) R2:
[ 1  0  -1/3   0   ]
[ 0  1  -1    -1/2 ]
[ 0  0   8/3  -2   ]

R3 <- (3/8) R3:
[ 1  0  -1/3   0   ]
[ 0  1  -1    -1/2 ]
[ 0  0   1    -3/4 ]

R1 <- R1 + (1/3) R3:
[ 1  0   0    -1/4 ]
[ 0  1  -1    -1/2 ]
[ 0  0   1    -3/4 ]

R2 <- R2 + (1) R3:
[ 1  0   0    -1/4 ]
[ 0  1   0    -5/4 ]
[ 0  0   1    -3/4 ]
```

The displayed matrix is A; the omitted right-hand column remains zero through
every operation. Pivot columns are a, b, c. Variable d is free.

## 3. Nullspace and smallest integer coefficients

The reduced equations are `a = d/4`, `b = 5d/4`, and `c = 3d/4`.
Rank = 3. Nullity = number of columns − rank = 4 − 3 = 1.

```text
x = t(1/4, 5/4, 3/4, 1) = s(1, 5, 3, 4)
```

There are infinitely many real solutions. Positive scalar multiples preserve the
ratio, and positive integer multiples preserve whole-number atom counts. The
zero vector is mathematically valid but is not a chemical balance.

To normalize the basis vector, orient its sign so all entries are positive,
multiply by the LCM of denominators (4), and divide by the GCD of the resulting
integers (1). The primitive positive vector is `(1, 5, 3, 4)`.

```text
C3H8 + 5O2 -> 3CO2 + 4H2O
```

An all-negative basis vector can have its sign reversed. A vector with zero or
mixed-sign entries cannot be made strictly positive by scaling. With more than
one independent free variable, the application displays one basis vector per
parameter and does not select a particular positive combination.

## 4. Verify and interpret

The verifier counts atoms again from parsed compound formulas and coefficients,
independently of the elimination steps:

| Element | Reactants | Products |
| --- | --- | --- |
| C | 1×3 = 3 | 3×1 = 3 |
| H | 1×8 = 8 | 4×2 = 8 |
| O | 5×2 = 10 | 3×2 + 4×1 = 10 |

Substitution into the original equations gives `3(1)−3=0`, `8(1)−2(4)=0`,
and `2(5)−2(3)−4=0`. Thus `Ax = (0,0,0)^T`.

One molecule of propane has the balanced ratio of five oxygen molecules to three
carbon dioxide molecules and four water molecules; the same ratio applies to
moles. This is an atom-conservation model. It does not predict reaction conditions,
rates, energy, or whether the proposed reaction occurs.

## 5. Determinants and exceptional systems

A determinant exists only for square matrices. Propane's 3×4 matrix has no
determinant; rank and nullity explain its family of solutions. For a square A:

- `det(A) != 0` means A is invertible and `Ax=0` has only `x=0`.
- `det(A) = 0` means a nontrivial nullspace exists. Strict positivity is an
  additional requirement and does not follow from the determinant alone.

Matrix inversion and Cramer's rule do not directly produce propane's balance.
Gaussian elimination, explicitly allowed by the assignment, handles rectangular
homogeneous systems. This implementation continues to reduced row echelon form.

| Example | Outcome |
| --- | --- |
| `H2 -> O2` | Rank 2, nullity 0: zero solution only. |
| `H2 + O2 -> H2` | Oxygen coefficient must be zero; cannot include all compounds. |
| `H2 + H2O -> O2` | One-dimensional family with mixed signs; cannot balance as written. |
| `C + O2 -> CO + CO2` | Nullity 2; general family shown, automatic selection unsupported. |

Every homogeneous system is consistent because zero is always a solution.
ChemMatrix therefore never describes these systems as inconsistent merely
because a chemical balance cannot be selected.

## 6. Core function contracts

The GUI imports the following independent Python functions; no service is involved:

| Function | Input and output |
| --- | --- |
| `parse_formula(formula)` | A formula string → element/count dictionary; raises `EquationError` for invalid input. |
| `parse_equation(text)` | Equation string → `Equation` with ordered reactants, products, and elements. |
| `build_matrix(equation)` | Parsed equation → rectangular tuple of `Fraction` rows. |
| `rref(values)` | Nonempty rectangular matrix → `Reduction` with final matrix, pivots, steps, free columns, and nullspace basis. |
| `balance(text)` | Equation string → `BalanceResult` with model, reduction, explicit status, message, and optional integer coefficient tuple. |
| `normalize_coefficients(vector)` | Same-sign nonzero rational entries → primitive positive integer tuple; raises `ValueError` otherwise. |
| `verify_atoms(equation, coefficients)` | One positive Python integer per compound → per-element totals; raises `ValueError` for invalid coefficients. |
| `check_answer(exercise, entries)` | Practice exercise and coefficient entries → feedback with status, message, and atom counts when valid. |

`RowStep` stores operation kind (`initial`, `swap`, `scale`, `add`), zero-based
target/source indices, exact factor, and a snapshot after the operation. These
records support replay tests, on-screen navigation, and clipboard export.

Element order follows first occurrence; compounds retain input order. The parser
recognizes all 118 element symbols but makes no chemical-valence judgment. Limits
and supported notation are listed in the README. Errors are returned to the
interface as correction messages rather than silently rewriting the equation.
