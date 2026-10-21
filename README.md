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

The tests cover parsing, chemical balancing, exact row-operation replay, the single-page GUI, common-equation selection, and clipboard export.

## Structure

```text
main.py
chemmatrix/
  parser.py              Formula and equation parsing
  matrix.py              Exact RREF and recorded row operations
  solver.py              Chemical conservation matrix and balancer
  explanation.py         Continuous worked-solution text
  gui.py                 Single balancer interface
tests/                   Core and GUI tests
docs/                    Assignment and presentation material
```
