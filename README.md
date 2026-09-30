# Python koans

A path of lessons for Aayush: comfortable in JavaScript, learning Java, learning Python. The goal is a language model you can use at SDE-1 and SDE-2 — names, objects, protocols, and attribute lookup.

Each value is an object. A name is a binding to an object. `==` asks for value. `is` asks whether two names refer to the same object. Attribute lookup walks the instance, then the method resolution order. The lessons exist to make those sentences feel obvious, including where JavaScript or Java taught a different model.

Requires Python 3.10 or newer.

## How to run

Install once. The command then works from any directory, because it uses the installed package rather than the current folder.

```bash
pip install -r requirements.txt
pip install -e .
python-koans start
```

If pip installs the command outside your `PATH`, run the path it prints, or `python -m koans start`.

`python-koans start` continues the journey: it walks the lessons in order and stops at the first failure. The same walk is `python path_to_enlightenment.py` from this repository.

`python-koans start --restart` puts you back at the first koan, including mid-journey. It overwrites the lesson files and `koans/student_work.py` from the pristine copies in `koans/pristine/`, prints `Journey reset.`, and starts the walk. Edit the lessons under `koans/`, not the files in `koans/pristine/`. The flag is the confirmation. Without `--restart`, `start` does not touch your edits.

`python-koans list` prints every topic in path order, one row each. A tick means that lesson is finished. A cross means it is not. A lesson is finished when no fill-in `__` remains (`__eq__` and similar names are not blanks). `about_transfer` also needs `koans/student_work.py` implemented: `NotImplementedError` or a body that is only `pass` is not finished.

The report is drawn with Cleo: a loader while the lessons load, then the lesson and the koan. A stop says why the path stopped and what to do next. An unfilled `__` is the next koan, not a crash: the report names the file, line, and test, and tells you to replace `__` with the value you predict. If `because(__)` on that test is still blank, it asks for one sentence naming the mechanism, and prints the hint when the test has one. A `because()` that misses the mechanism says so and prints the hint, not the required words. A prediction that fails says it did not match. The report does not print the answer. Color is on in a terminal and plain text when stdout is not a terminal. The last line is how many koans passed.

There is no answer key.

## Lesson shape

Each lesson file starts with an axiom: the mechanism, in a sentence or two.

1. **Predict.** Replace `__` with the value you expect.
2. **Because.** Call `self.because(__)` and replace `__` with one sentence that names the mechanism.
3. **Discriminating case.** At least one test in the file fails under the model JavaScript or Java usually installs. A short comment names that mismatch.
4. **Transfer.** The last lesson is already written as tests. You implement `Playlist` in `koans/student_work.py`. `because()` is still yours to write.

`__` is not `None` and not a placeholder value. Comparisons and iteration fail until you replace it, with the message `fill in the blank`.

`because()` checks the concept stems on that test (`@expects(...)`, or `requires=`). The stems are short words, not a sentence to copy. Matching is case-insensitive: each required stem must appear in your sentence. If you pass alternatives, one whole group is enough. Leaving `__` fails with `state the mechanism in one line`. A sentence that misses the mechanism fails without the stems being printed back to you. A hint points at what to name.

## Path

1. `koans/about_asserts.py` — how the path works
2. `koans/about_objects.py` — identity, type, value
3. `koans/about_names.py` — binding and rebinding
4. `koans/about_mutability.py` — aliasing, list versus tuple
5. `koans/about_equality.py` — `==` versus `is`
6. `koans/about_calls.py` — arguments are assignment
7. `koans/about_functions.py` — first-class functions, default arguments evaluated once
8. `koans/about_scope.py` — LEGB, closures, late binding in loops
9. `koans/about_sequences.py` — the sequence protocol, unpacking as binding
10. `koans/about_mappings.py` — dict keys, equality, and a stable hash
11. `koans/about_iteration.py` — iterable versus iterator
12. `koans/about_comprehensions.py` — list comprehensions and generator expressions
13. `koans/about_exceptions.py` — exception objects and propagation
14. `koans/about_classes.py` — the class body executes, instance `__dict__`
15. `koans/about_attributes.py` — lookup order and the MRO
16. `koans/about_inheritance.py` — `super()` follows the MRO
17. `koans/about_protocols.py` — `__iter__`, `__len__`, `__eq__`, context managers
18. `koans/about_modules.py` — import executes the module once
19. `koans/about_transfer.py` — implement a small sequence

## Retro days

On a retro day, ask the agent to use the `koan-retro` skill at `.cursor/skills/koan-retro/SKILL.md`. For example: "Use the koan-retro skill."

The quiz only asks about lessons you have already completed. It does not preview later lessons.
