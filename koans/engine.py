"""The blank sentinel and the because() check.

Stems live on the test, as short mechanism words. They are not a sentence
to copy. A failing sentence is rejected without repeating those words.
"""

from __future__ import annotations

import unittest
from collections.abc import Callable, Sequence
from typing import TypeVar

FILL_IN_THE_BLANK = "fill in the blank"
STATE_THE_MECHANISM = "state the mechanism in one line"
DOES_NOT_NAME = "The reason does not name the mechanism."
DEFAULT_HINT = "Name what Python did, in one sentence."

F = TypeVar("F", bound=Callable[..., object])
StemGroups = tuple[tuple[str, ...], ...]


class Blank:
    """A stand-in that is not a value. Replace it."""

    def _refuse(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError(FILL_IN_THE_BLANK)

    __eq__ = _refuse
    __ne__ = _refuse
    __lt__ = _refuse
    __le__ = _refuse
    __gt__ = _refuse
    __ge__ = _refuse
    __iter__ = _refuse
    __contains__ = _refuse
    __getitem__ = _refuse
    __bool__ = _refuse
    __len__ = _refuse
    __add__ = _refuse
    __radd__ = _refuse
    __sub__ = _refuse
    __rsub__ = _refuse
    __hash__ = None

    def __repr__(self) -> str:
        return "__"

    def __str__(self) -> str:
        return "__"


blank = Blank()


def _groups_of(
    stems: tuple[str, ...],
    any_of: tuple[tuple[str, ...], ...] | None,
) -> StemGroups:
    if any_of is not None:
        if stems:
            raise TypeError("Pass stems or any_of, not both")
        groups = tuple(tuple(group) for group in any_of)
    else:
        groups = (tuple(stems),)
    if not groups or any(len(group) == 0 for group in groups):
        raise TypeError("expects() needs at least one stem in every group")
    return groups


def expects(
    *stems: str,
    any_of: tuple[tuple[str, ...], ...] | None = None,
    hint: str | None = None,
) -> Callable[[F], F]:
    """Attach concept stems to a test. The sentence must contain each stem in a group.

    One group means every stem is required. any_of means one whole group is enough.
    Matching is a case-insensitive substring. The hint must not contain a stem.
    """
    groups = _groups_of(stems, any_of)
    if hint:
        folded_hint = hint.casefold()
        for group in groups:
            for stem in group:
                if stem.casefold() in folded_hint:
                    raise ValueError(f"hint contains stem {stem!r}")

    def decorator(fn: F) -> F:
        fn._koan_groups = groups  # type: ignore[attr-defined]
        fn._koan_hint = hint  # type: ignore[attr-defined]
        return fn

    return decorator


def _matches(reason: str, groups: StemGroups) -> bool:
    folded = reason.casefold()
    return any(all(stem.casefold() in folded for stem in group) for group in groups)


class Koan(unittest.TestCase):
    def because(self, reason: object, requires: Sequence[str] | None = None) -> None:
        """Accept one sentence that names the mechanism.

        Stems come from the test's expects() decorator, or from requires=.
        requires= is every stem, all required. Leaving the blank asks for the sentence.
        """
        if reason is blank or (isinstance(reason, str) and reason.strip() in {"", "__"}):
            self.fail(STATE_THE_MECHANISM)
        if not isinstance(reason, str):
            self.fail(STATE_THE_MECHANISM)

        hint = DEFAULT_HINT
        if requires is not None:
            groups = _groups_of(tuple(requires), None)
        else:
            method = getattr(self, self._testMethodName)
            groups = getattr(method, "_koan_groups", None)
            hint = getattr(method, "_koan_hint", None) or DEFAULT_HINT
            if not groups:
                self.fail("This koan has no concept stems.")

        if not _matches(reason, groups):
            self.fail(f"{DOES_NOT_NAME} Hint: {hint}")
