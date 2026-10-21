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
