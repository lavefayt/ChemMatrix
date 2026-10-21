"""Parse bounded, neutral chemical formulas without external dependencies."""

from collections import Counter
from dataclasses import dataclass
import re


ELEMENTS = frozenset("""
H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu
Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba
La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi
Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt
Ds Rg Cn Nh Fl Mc Lv Ts Og
""".split())

MAX_LENGTH = 500
MAX_COMPOUNDS = 12
MAX_ELEMENTS = 12
MAX_DEPTH = 4
MAX_SUBSCRIPT = 999


class EquationError(ValueError):
    """An input error suitable for showing directly to the learner."""


@dataclass(frozen=True)
class Compound:
    formula: str
    atoms: dict[str, int]


@dataclass(frozen=True)
class Equation:
    reactants: tuple[Compound, ...]
    products: tuple[Compound, ...]
    elements: tuple[str, ...]

    @property
    def compounds(self) -> tuple[Compound, ...]:
        return self.reactants + self.products

    @property
    def text(self) -> str:
        return " + ".join(c.formula for c in self.reactants) + " -> " + " + ".join(
            c.formula for c in self.products
        )


def parse_formula(formula: str) -> dict[str, int]:
    """Read an element/group sequence, accumulating repeated element counts."""
    if not formula or len(formula) > MAX_LENGTH:
        raise EquationError("Enter a formula of 1–500 characters.")
    if formula[0].isdigit():
        raise EquationError("Remove leading coefficients; enter H2O rather than 2H2O.")
    if re.search(r"\((?:s|l|g|aq)\)", formula):
        raise EquationError("Remove physical-state labels such as (s), (l), (g), or (aq).")
    if any(char in formula for char in ".·[]{}^+-"):
        raise EquationError("Use neutral formulas only; ions, hydrates, and brackets are unsupported.")
    if not re.fullmatch(r"[A-Za-z0-9()]+", formula):
        raise EquationError("Use case-sensitive element symbols, ordinary digits, and parentheses only.")
    position = 0

    def subscript() -> int:
        nonlocal position
        start = position
        while position < len(formula) and formula[position].isdigit():
            position += 1
        if start == position:
            return 1
        token = formula[start:position]
        if token.startswith("0") or len(token) > 3:
            raise EquationError("Subscripts must be integers from 1 to 999, without leading zeros.")
        value = int(token)
        if not 1 <= value <= MAX_SUBSCRIPT:
            raise EquationError("Subscripts must be integers from 1 to 999.")
        return value

    def group(depth: int) -> Counter:
        nonlocal position
        counts: Counter = Counter()
        terms = 0
        while position < len(formula) and formula[position] != ")":
            char = formula[position]
            if char == "(":
                if depth >= MAX_DEPTH:
                    raise EquationError("Use at most four nested parenthesis levels.")
                position += 1
                inner = group(depth + 1)
                if position >= len(formula) or formula[position] != ")":
                    raise EquationError("A closing parenthesis is missing.")
                position += 1
                multiplier = subscript()
                for element, count in inner.items():
                    counts[element] += count * multiplier
            elif "A" <= char <= "Z":
                start = position
                position += 1
                if position < len(formula) and "a" <= formula[position] <= "z":
                    position += 1
                element = formula[start:position]
                if element not in ELEMENTS:
                    raise EquationError(f"Unknown element symbol '{element}'. Check capitalization.")
                counts[element] += subscript()
            else:
                raise EquationError(f"Unexpected '{char}' in {formula}. Check symbols and subscripts.")
            terms += 1
        if not terms:
            raise EquationError("Empty parentheses are not allowed.")
        return counts

    atoms = group(0)
    if position != len(formula):
        raise EquationError("An opening parenthesis is missing.")
    if len(atoms) > MAX_ELEMENTS:
        raise EquationError("Use at most 12 distinct elements.")
    return dict(atoms)


def _strip_coefficient(term: str) -> str:
    """Drop a leading whole-number coefficient (2H2O or 2 H2O); the balancer recomputes it."""
    match = re.fullmatch(r"(\d+)\s*(.*)", term)
    if not match:
        return term
    if int(match.group(1)) < 1:
        raise EquationError("Coefficients must be positive whole numbers.")
    return match.group(2)


def parse_equation(text: str) -> Equation:
    """Accept exactly two nonempty sides separated by ->, →, or =."""
    if not text.strip():
        raise EquationError("Enter an equation, for example C3H8 + O2 -> CO2 + H2O.")
    if len(text) > MAX_LENGTH:
        raise EquationError("Use at most 500 characters.")
    sides = re.split(r"->|→|=", text)
    if len(sides) != 2:
        raise EquationError("Use exactly one separator: ->, →, or =.")
    raw_sides = [[part.strip() for part in side.split("+")] for side in sides]
    if any(not part for side in raw_sides for part in side):
        raise EquationError("Each side needs compounds separated by +. Remove empty terms or ionic charges.")
    if sum(map(len, raw_sides)) > MAX_COMPOUNDS:
        raise EquationError("Use at most 12 compounds in total.")
    raw_sides = [[_strip_coefficient(part) for part in side] for side in raw_sides]
    parsed = [tuple(Compound(part, parse_formula(part)) for part in side) for side in raw_sides]
    elements = tuple(dict.fromkeys(e for side in parsed for c in side for e in c.atoms))
    if len(elements) > MAX_ELEMENTS:
        raise EquationError("Use at most 12 distinct elements in the equation.")
    return Equation(parsed[0], parsed[1], elements)