# ChemMatrix Mathematical Model

## Chemical balancer

For `C3H8 + O2 -> CO2 + H2O`, let `x = (a, b, c, d)^T` be the compound coefficients. Conservation of carbon, hydrogen, and oxygen gives:

```text
3a - c       = 0
8a      - 2d = 0
     2b - 2c - d = 0
```

This is `A x = 0` with a 3 x 4 matrix. Gauss-Jordan elimination records every swap, scale, and row-add operation. The nullspace vector is `(1/4, 5/4, 3/4, 1)^T`; clearing denominators gives the smallest positive integer ratio `(1, 5, 3, 4)`.

The system is homogeneous by nature. Therefore zero is always a solution and a nonzero balance is a nullspace direction rather than a unique ordinary solution. Atom verification independently confirms that the residual vector is zero.

## Unique 3 x 3 application

To satisfy the unique-system requirement without changing the chemical focus, the balancer also models a chemical production plant. Let `x1`, `x2`, and `x3` be small, standard, and large product batches. Three resource constraints give:

```text
2x1 + x2 + 3x3 = 130
x1 + 2x2 + x3 = 80
3x1 + x2 + 2x3 = 110
```

With

```text
A = [ 2  1  3 ]    b = [ 130 ]
    [ 1  2  1 ]        [  80 ]
    [ 3  1  2 ]        [ 110 ]
```

The app reduces `[A | b]` to `[I | (10, 20, 30)^T]`. Since `det(A) = -8`, `A` is invertible and the solution is unique. It verifies both `Ax = b` and `AA^-1 = I` using exact fractions.

For the what-if case `b_new = (150, 80, 110)^T`, the same inverse gives:

```text
x_new = A^-1 b_new = (5/2, 35/2, 85/2)^T
```

Gauss-Jordan is primary because its elementary operations are visible and it works directly on the augmented matrix. The inverse method is useful when the coefficient matrix is reused for many right-hand sides. Cramer's rule is appropriate for a small nonsingular square system, but it requires three replacement determinants and scales poorly.
