"""Cases using: KeyDiff.diff_dict"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


from dynamerge.differ import KeyDiffer, KeyDiff, MergePolicy


doc = __doc__


@dataclass
class DiffCase:
    name: str
    pseudo_id: Callable
    old: dict | list
    new: dict | list
    exp: list[KeyDiff]
    merge_policy: MergePolicy = None


case_list = [
    DiffCase(
        "different-keys",
        KeyDiffer.pseudo_id_strategies.use_index,
        {"a": "A"},
        {"b": "B"},
        [
            KeyDiff("a", ("A", None), ("a", "a")),
            KeyDiff("b", (None, "B"), ("b", "b")),
        ],
    ),
]


def main():
    ...


if __name__ == "__main__":
    exit(main())
