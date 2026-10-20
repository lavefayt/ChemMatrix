# ChemMatrix presentation script

Target: approximately **4 minutes 30 seconds**. Rehearse at a comfortable pace;
timings include pauses for the demonstration. Split sections among group members
as needed. Before recording, launch `python main.py` and use a readable window
size. The title and narration describe the new chemistry concept.

## 0:00–0:30 — Introduction

**Show:** Title and the Balancer tab.

“Our project is ChemMatrix, a chemical equation balancer built with Python and
Tkinter. It demonstrates how linear algebra can solve a real-world conservation
problem. In a balanced chemical equation, every element must have the same
number of atoms on both sides. We find the coefficients while preserving the
chemical formulas.”

## 0:30–1:15 — Mathematical model

**Show:** Select Propane; open Model. Point to variables, equations, and matrix.

“Our example is propane and oxygen producing carbon dioxide and water. Let a,
b, c, and d represent the four coefficients. Carbon gives 3a minus c equals
zero. Hydrogen gives 8a minus 2d equals zero. Oxygen gives 2b minus 2c minus d
equals zero.

These equations form Ax equals zero. Each row represents an element, and each
column represents a compound. Reactant counts are positive and product counts
are negative. A is a three-by-four matrix, and x contains our four unknowns.”

## 1:15–2:10 — Solution process

**Show:** Solution Steps. Move through the seven operations; pause on the last.
Scroll to the solution beneath the final matrix.

“We use Gauss–Jordan elimination with exact fractions. The application shows
each row operation and the matrix it produces. Scaling and adding rows preserve
the solution set. We also swap rows to position a pivot.

The final matrix has three pivots. Variable d is free, so rank is three and
nullity is one. We obtain a equals d over four, b equals five d over four, and
c equals three d over four. Setting d to one gives fractional ratios. The least
common multiple of the denominators is four, so multiplying gives one, five,
three, four. Their greatest common divisor is one.

This homogeneous system has infinitely many real solutions. We select the
smallest positive integer ratio. Because the matrix is rectangular, it has no
determinant; rank and free variables explain the solution.”

## 2:10–3:25 — Prototype demonstration

**Show:** Verification, then Parentheses example; then Practice → Easy, Water formation.

“Verification counts the atoms independently: three carbon atoms, eight
hydrogen atoms, and ten oxygen atoms on each side. The matrix product Ax is
the zero vector, so the coefficients satisfy the original system.

The input also supports parentheses. Here, calcium hydroxide contributes two
oxygen atoms and two hydrogen atoms per formula unit. The program produces a
new conservation matrix and solution for this equation.

Practice mode contains ten exercises grouped by difficulty. We enter a
coefficient for every compound, including one.”

**Do:** Enter `1,1,1`; select Check atom counts. Then enter `4,2,4` and check.
Finally enter `2,1,2` and check.

“This first attempt has mismatched oxygen counts. The second balances the atoms
but can be reduced. The final answer uses the smallest whole-number ratio.
Learners can retry, request a hint, or reveal the worked solution. Assisted
exercises are marked separately in session progress.”

## 3:25–4:00 — Interpretation and limits

**Show:** Return to Propane → Verification.

“The propane coefficients describe relative quantities: one propane molecule
reacts in a ratio with five oxygen molecules, giving three carbon dioxide and
four water molecules. The ratio also applies to moles.

Balancing checks atom conservation, not whether a proposed reaction occurs.
Our version supports neutral formulas, and reports unsupported notation. It
also explains systems with only the zero solution, no strictly positive ratio,
or several independent free variables.”

## 4:00–4:30 — Conclusion

**Show:** Final balanced propane equation or closing slide.

“ChemMatrix connects a conservation rule to simultaneous equations, a matrix,
row reduction, and a verified result. The same modeling process is useful in
other systems: define unknowns, express constraints, solve, and interpret.
Our prototype makes those stages visible and gives learners a way to practice
them. Thank you.”

## Recording checklist

- Fill in names and course details in any title slide.
- Keep formulas and matrices large enough to read in the recording.
- Follow the displayed steps rather than claiming a determinant for propane.
- Allow short pauses for tab switches and coefficient entry.
- Confirm the final video is 3–5 minutes; the earlier reference video is a
  presentation-structure reference, not footage of ChemMatrix.
