"""Cases using: KeyDiff.diff_list"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


from dynamerge.differ import KeyDiffer, KeyDiff, MergePolicy


doc = __doc__


@dataclass
class DiffCase:
    name: str
    about: str
    pseudo_id: Callable
    old: dict | list
    new: dict | list
    exp: list[KeyDiff]
    merge_policy: MergePolicy = None


case_list = [
    DiffCase(
        "mode-positional",
        "...",
        KeyDiffer.pseudo_id_strategies.use_index,
        [1, 2, 3, 4],
        [4, 3, 2, 1],
        [
            KeyDiff(0, (1, 4), (0, 0)),
            KeyDiff(1, (2, 3), (1, 1)),
            KeyDiff(2, (3, 2), (2, 2)),
            KeyDiff(3, (4, 1), (3, 3)),
        ],
    ),
    DiffCase(
        "mode-positional--with-list",
        "...",
        KeyDiffer.pseudo_id_strategies.use_index,
        [1, {"a": "A", "b": "B"}, 3],
        [1, {"a": "A", "b": "B"}, 3],
        [
            KeyDiff(0, (1, 1), (0, 0)),
            KeyDiff(1, ({"a": "A", "b": "B"}, {"a": "A", "b": "B"}), (1, 1)),
            KeyDiff(2, (3, 3), (2, 2)),
        ],
    ),
    DiffCase(
        "mode-positional: old longer",
        "...",
        KeyDiffer.pseudo_id_strategies.use_index,
        [1, 2, 3],
        [3, 2],
        [
            KeyDiff(0, (1, 3), (0, 0)),
            KeyDiff(1, (2, 2), (1, 1)),
            KeyDiff(2, (3, None), (2, None)),
        ],
    ),
    DiffCase(
        "mode-positional: old shorter",
        "...",
        KeyDiffer.pseudo_id_strategies.use_index,
        [1, 2],
        [3, 2, 1],
        [
            KeyDiff(0, (1, 3), (0, 0)),
            KeyDiff(1, (2, 2), (1, 1)),
            KeyDiff(2, (None, 1), (None, 2)),
        ],
    ),
    DiffCase(
        "mode-positional: None (empty) pads",
        """\
        The diff is not responsible for parsing marks. This should be processed before
        """,
        KeyDiffer.pseudo_id_strategies.use_index,
        [1, 2, 3],
        ["@empty", 2, "@empty"],
        [
            KeyDiff(0, (1, "@empty"), (0, 0)),
            KeyDiff(1, (2, 2), (1, 1)),
            KeyDiff(2, (3, "@empty"), (2, 2)),
        ],
    ),
    DiffCase(
        "mode-unique: hashable values only",
        "...",
        KeyDiffer.pseudo_id_strategies.use_value_hash,
        [91, 92, 93],
        [92, 91, 90],
        [
            KeyDiff(90, (None, 90), (None, 2)),
            KeyDiff(91, (91, 91), (0, 1)),
            KeyDiff(92, (92, 92), (1, 0)),
            KeyDiff(93, (93, None), (2, None)),
        ],
    ),
    DiffCase(
        "mode-unique--without-dict-id",
        "...",
        KeyDiffer.pseudo_id_strategies.use_value_hash,
        [1, {"a": "A"}, 3],
        [3, {"a": "A"}, 1],
        [
            KeyDiff(1, (1, 1), (0, 2)),
            KeyDiff(3, (3, 3), (2, 0)),
            KeyDiff("__old_0__", ({"a": "A"}, None), (1, None)),
            KeyDiff("__new_0__", (None, {"a": "A"}), (None, 1)),
        ],
    ),
    DiffCase(
        "mode-unique: dict with default key_id (=dynaconf_id)",
        """\
        "dynaconf_id" is kept here because it not a special mark that should be popped.

        It is merely a default key that will be looked up internally to find a dict
        identify within a list, when value_hash strategy is being used.
        """,
        KeyDiffer.pseudo_id_strategies.use_value_hash,
        [91, 93, {"a": "A", "dynaconf_id": 1}],
        [93, {"a": "A", "dynaconf_id": 1}, 91],
        [
            KeyDiff(91, (91, 91), (0, 2)),
            KeyDiff(93, (93, 93), (1, 0)),
            KeyDiff(
                "dynaconf_id_1",
                ({"a": "A", "dynaconf_id": 1}, {"a": "A", "dynaconf_id": 1}),
                (2, 1),
            ),
        ],
    ),
    DiffCase(
        "mode-unique: dict with custom key_id",
        "...",
        KeyDiffer.pseudo_id_strategies.use_value_hash,
        [91, 93, {"a": "A", "c": "C"}],
        [93, {"a": "A", "d": "D"}, 91],
        [
            KeyDiff(91, (91, 91), (0, 2)),
            KeyDiff(93, (93, 93), (1, 0)),
            KeyDiff("a_A", ({"a": "A", "c": "C"}, {"a": "A", "d": "D"}), (2, 1)),
        ],
        merge_policy=MergePolicy(dict_id_key="a"),
    ),
]


def main():
    ...


if __name__ == "__main__":
    exit(main())
