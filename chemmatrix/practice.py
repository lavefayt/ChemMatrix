"""Practice content and feedback, independent of Tkinter."""

from dataclasses import dataclass
from math import gcd
from functools import reduce

from .solver import AtomCount, balance, verify_atoms


@dataclass(frozen=True)
class Exercise:
    title: str
    difficulty: str
    equation: str
    hint: str


EXERCISES = (
    Exercise("Water formation", "Easy", "H2 + O2 -> H2O", "Match oxygen first, then hydrogen."),
    Exercise("Magnesium oxidation", "Easy", "Mg + O2 -> MgO", "Oxygen occurs in pairs on the left."),
    Exercise("Hydrogen chloride", "Easy", "H2 + Cl2 -> HCl", "Both reactants are diatomic."),
    Exercise("Iron oxidation", "Medium", "Fe + O2 -> Fe2O3", "The least common multiple of 2 and 3 is 6."),
    Exercise("Ammonia formation", "Medium", "N2 + H2 -> NH3", "Match nitrogen, then count hydrogen atoms."),
    Exercise("Propane combustion", "Medium", "C3H8 + O2 -> CO2 + H2O", "Match carbon and hydrogen before oxygen."),
    Exercise("Water decomposition", "Medium", "H2O -> H2 + O2", "There must be an even number of oxygen atoms."),
    Exercise("Calcium hydroxide", "Hard", "Ca(OH)2 + HCl -> CaCl2 + H2O", "(OH)2 contributes two O and two H atoms."),
    Exercise("Aluminum sulfate", "Hard", "Al + H2SO4 -> Al2(SO4)3 + H2", "Keep the sulfate group together when counting."),
    Exercise("Potassium chlorate", "Hard", "KClO3 -> KCl + O2", "Use six oxygen atoms on each side."),
)


@dataclass(frozen=True)
class PracticeFeedback:
    status: str
    message: str
    counts: tuple[AtomCount, ...] = ()


def check_answer(exercise: Exercise, entries) -> PracticeFeedback:
    result = balance(exercise.equation)
    entries = tuple(entries)
    try:
        if any(not str(value).isascii() or not str(value).isdigit() or len(str(value)) > 6
               for value in entries):
            raise ValueError
        values = tuple(int(value) for value in entries)
        counts = verify_atoms(result.equation, values)
    except ValueError:
        return PracticeFeedback("invalid", "Enter one positive integer (up to six digits) per compound.")
    if not all(count.matches for count in counts):
        missing = ", ".join(count.element for count in counts if not count.matches)
        return PracticeFeedback("incorrect", f"Check these elements: {missing}. Try again.", counts)
    if reduce(gcd, values) != 1:
        return PracticeFeedback("proportional", "Balanced! Divide all coefficients by their common factor for the smallest ratio.", counts)
    return PracticeFeedback("correct", "Correct — balanced in the smallest whole-number ratio!", counts)
