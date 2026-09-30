---
name: koan-retro
description: Use when it is a retro day, or when the user wants to be quizzed and graded on Python koans they have already finished in this repo.
---

# Koan retro

## Overview

Quiz only lessons whose blanks are already filled. Grade the language model: names, objects, protocols, lookup. One question at a time.

## When to use

Use on a retro day, or when the user asks to be quizzed or graded on finished Python koans.

Do not use this to teach the next unfilled lesson or to walk the path.

## What counts as completed

Read `path_to_enlightenment.py`, then the koan files in that order.

A lesson is completed only when no identifier `__` remains as a value to fill in. `__ = blank` only publishes the sentinel. Longer names such as `__eq__`, `__iter__`, and `__dict__` are not blanks. A remaining `because(__)` or comparison against `__` means the lesson is not done.

Stop at the first incomplete file. Do not open later lesson files.

`koans/about_transfer.py` counts only when its blanks are filled and `koans/student_work.py` is implemented. `NotImplementedError` or a body that is only `pass` is not an implementation. A docstring is not one either.

If none are completed, say so and stop. Do not preview later lessons, and do not quote their axioms, snippets, stems, or bridge comments.

## Quiz

Ask about five questions, one at a time. Wait for the answer before the next.

Use completed lessons only. Prefer older ones and the discriminating case (the comment that names the JavaScript or Java habit). Do not replay a filled blank. Invent a nearby case that needs the same mechanism.

Mix all three:

- Predict a novel snippet.
- Name the mechanism in one sentence.
- Catch a JavaScript or Java habit that installs the wrong model.

Language-model level only: names, objects, protocols, attribute lookup. No bytecode, refcounting, or interning puzzles. Small-int identity is an accident, not a rule. Do not grade it.

## Grade

Score each answer before the next question: 0 wrong model, 1 partial, 2 the model is right.

On 0 or 1, name the lesson file to revisit. Do not reveal how an uncompleted lesson comes out.

Then give a final score out of 10 and the lessons to revisit.

## Red flags

- Quizzing a file that still has a fill-in `__` (ignore `__ = blank` and longer dunder names)
- Opening a lesson after the first incomplete one
- Repeating a filled blank, or asking the next question before grading
- Explaining CPython internals

| Excuse | Reality |
| --- | --- |
| "One peek at the next lesson makes a better question" | That is a preview. Stop at the first incomplete file. |
| "I can tell it is done without the blanks being filled" | Completed means the fill-in `__` is gone. |
| "Replaying the blank confirms memory" | Ask a novel snippet that needs the same mechanism. |
| "Transfer is done because the tests exist" | The student module must be implemented, and its blanks filled. |
