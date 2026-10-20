# Validation record

## Automated checks

Environment: Windows, Python 3.13, Tk 8.6. Tests use the standard library only.

Verified on 2026-10-21: **19 tests passed**, including the real Tk widget tests;
no tests were skipped. Python syntax compilation and local documentation-link
checks passed. The `main.py` entry point opened its event loop and closed normally
in a bounded launch check. The GitHub workflow is configured for core checks on
Python 3.10 and 3.13; remote workflow execution has not been verified.

The core suite checks formula parsing and boundaries, known balances, exact RREF,
replay of recorded operations, nullspace vectors, integer normalization, atom
verification, exceptional system statuses, teaching output, all ten practice
exercises, and invalid/proportional/incorrect/correct practice feedback.

The Tk widget integration suite opens actual windows and invokes the controls.
It checks result invalidation after editing, row-step navigation and endpoints,
clipboard content, error messages, exceptional cases, practice progress and
assistance, retry, example switching, Enter/Tab bindings, scrolling, and resizing.
Tk callback exceptions fail the tests. GUI tests skip if no display is available.

Run:

```powershell
python -m unittest discover -s tests -v
python -m compileall -q chemmatrix main.py tests
```

## Visual review and hands-on checks

README screenshots show the actual Tkinter app rather than a mockup. Visual
inspection checks readability, spacing, matrix alignment, and visible controls.
Implementation review checked control labels against their actions, session
progress semantics, input/result invalidation, exact arithmetic, and use of
standard Tk widgets. No outstanding functional findings remained. There are no
network queries or external state to synchronize.
Widget-driven checks are automated integration checks; a human presentation
rehearsal still needs the following checks on the presentation computer:

- [ ] Launch with `python main.py` and confirm the window is usable at the display's scaling.
- [ ] Type the propane equation and balance it using the keyboard.
- [ ] Inspect every step, including the fractional-to-integer conversion.
- [ ] Copy the worked solution and paste it into a text editor.
- [ ] Resize the window and use both scroll directions on long output.
- [ ] Try malformed input and correct it; ensure old output is cleared.
- [ ] In Practice, check a wrong answer, a proportional answer, and the primitive answer.
- [ ] Try hints, retry, and reveal; verify assisted and independent progress labels.
- [ ] Close and relaunch; confirm progress starts a new session.
- [ ] Rehearse the presentation script and verify report pagination separately.

The screenshots and tests do not establish instructor topic approval, report
pagination, completed video recording, or learning effectiveness.
