from dynamerge.merger import Merger
from icecream import ic
from functools import wraps

from dataclasses import dataclass
from typing import Callable


@dataclass
class MergeCase:
    name: str
    old: dict | list
    new: dict | list
    expected: dict | list


def main():
    for case in merge_cases():
        merge_report(case)
    # case_merge_dicts()
    # case_merge_false()


def merge_report(case: MergeCase):
    name = case.name
    old = {"r": case.old}
    new = {"r": case.new}
    exp = {"r": case.expected}
    print("\n> ", name)
    ic(old)
    ic(new)
    out = Merger.merge_dict(old, new)
    ic(out)
    ic(exp)


def merge_cases():
    return [
        MergeCase(
            "un-nested dicts",
            {"a": "A", "b": "B"},
            {"a": "A*", "c": "C"},
            {"a": "A*", "b": "B", "c": "C"},
        ),
        MergeCase(
            "nested dicts: new-old overrides common keys",
            {"a": "A", "b": {"c": "C", "d": "D"}},
            {"a": "A*", "b": {"c": "C*", "e": "E"}},
            {"a": "A*", "b": {"c": "C*", "d": "D", "e": "E"}},
        ),
        MergeCase(
            "nested dicts: new-only merges different key",
            {"a": "A", "b": {"c": "C", "d": {"e": "E", "f": {"g": "G", "h": "H"}}}},
            {"b": {"d": {"f": {"g": "G*"}}}},
            {"a": "A", "b": {"c": "C", "d": {"e": "E", "f": {"g": "G*", "h": "H"}}}},
        ),
        MergeCase(
            "merge_false: simple",
            {"a": "A", "b": "B"},
            {"a": "A*", "dynaconf_merge": False},
            {"a": "A*"},
        ),
        MergeCase(
            "merge_false: nested",
            {"a": "A", "b": {"c": "C", "d": {"e": "E", "f": {"g": "G", "h": "H"}}}},
            {"b": {"d": {"f": {"g": "G*"}}}, "dynaconf_merge": False},
            {"b": {"d": {"f": {"g": "G*"}}}},
        ),
    ]


if __name__ == "__main__":
    exit(main())
