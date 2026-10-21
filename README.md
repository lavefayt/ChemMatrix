# ChemMatrix

ChemMatrix is an offline Tkinter chemical-equation balancer built as a linear algebra final project. It keeps the original chemistry concept while presenting the complete matrix work in one balancer view.

## Core workflow

1. Enter an unbalanced equation or choose one from the Common equations list.
2. Select Balance or press Enter.
3. Read the conservation equations and matrix `A x = 0`.
4. Follow every elementary row operation. Each line includes the resulting matrix.
5. Check atom totals and the zero residual vector.
6. Copy the complete worked solution when needed.

The balancer uses exact fractions, Gauss-Jordan elimination, nullspace vectors, integer normalization, and independent atom verification. Supported formulas include parentheses and repeated elements. Charges, hydrates, state labels, and leading coefficients are rejected with a correction message.

## Linear algebra requirement extension

Chemical balancing is naturally homogeneous. For propane, the 3 x 4 conservation matrix has a one-dimensional nullspace, so a nonzero balance is not unique as a vector; its positive integer ratio is selected by normalization.

The same balancer view therefore includes a compact realistic chemical-production system with a unique 3 x 3 solution:

```text
2x1 + x2 + 3x3 = 130
x1 + 2x2 + x3 = 80
3x1 + x2 + 2x3 = 110
```

Here `x1`, `x2`, and `x3` are small, standard, and large chemical-product batches, while the rows represent three limited production resources. The app shows Gauss-Jordan reduction of `[A | b]`, `det(A) = -8`, the unique solution `(10, 20, 30)^T`, `Ax = b`, and `AA^-1 = I`.

The What-if section changes `b` to `(150, 80, 110)^T` and reuses `A^-1`, producing `(5/2, 35/2, 85/2)^T`. The text explains why Gauss-Jordan is the primary method, when the inverse method is useful, and why Cramer's rule is less efficient for larger systems.

## Run

Python 3.10 or newer with Tcl/Tk support is required. The project uses only the standard library; `requirements.txt` contains no third-party packages.

macOS/Linux:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python main.py
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

If Tkinter is unavailable, install Python with Tcl/Tk support. Tkinter is not installed through pip.

## Tests

```bash
./.venv/bin/python -m unittest discover -s tests -v
./.venv/bin/python -m compileall -q chemmatrix main.py tests
```

The tests cover parsing, chemical balancing, exact row-operation replay, the unique 3 x 3 system, inverse and matrix verification, the what-if result, the single-page GUI, common-equation selection, and clipboard export.

## Structure

```text
main.py
chemmatrix/
  parser.py              Formula and equation parsing
  matrix.py              Exact RREF and recorded row operations
  solver.py              Chemical conservation matrix and balancer
  linear.py              Unique 3 x 3 production model and inverse checks
  explanation.py         Continuous worked-solution text
  gui.py                 Single balancer interface
tests/                   Core and GUI tests
docs/                    Assignment and presentation material
```
