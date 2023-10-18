"""Cases using: Merger.merge_dict"""
from dataclasses import dataclass


@dataclass
class MergeCase:
    name: str
    old: dict | list
    new: dict | list
    expected: dict | list


cases = [
    MergeCase(
        "un-nested dicts on root should merge",
        {"root": {"a": "A", "b": "B"}},
        {"root": {"a": "A*", "c": "C"}},
        {"root": {"a": "A*", "b": "B", "c": "C"}},
    ),
    MergeCase(
        "nested dicts outside root shouldnt merge",
        {"root": {"nested": {"a": "A", "b": "B"}}},
        {"root": {"nested": {"c": "C"}}},
        {"root": {"nested": {"c": "C"}}},
    ),
    MergeCase(
        "mixed nested and unested dicts should behave consistently",
        {"root": {"a": "A", "b": {"c": "C", "d": "D"}}, "foo": True},
        {"root": {"a": "A*", "b": {"c": "C*", "e": "E"}}},
        {"root": {"a": "A*", "b": {"c": "C*", "e": "E"}}, "foo": True},
    ),
    # fmt: off
    MergeCase(
        "dynaconf_merge=true should apply for subsequent nesting levels",
        {"root": {
            "a": "A",
            "b": {"c": "C", "d": {"e": "E", "f": "F"}}}},
        {"root": {
            "b": {"d": {"f": "F*"}}, "dynaconf_merge": True}},
        {
            "root": {
                "a": "A",
                "b": {"c": "C", "d": {"e": "E", "f": "F*"}},
            }
        },
    ),
    # fmt: on
    MergeCase(
        "merge_false: simple",
        {"root": {"a": "A", "b": "B"}},
        {"root": {"a": "A*", "dynaconf_merge": False}},
        {"root": {"a": "A*"}},
    ),
    MergeCase(
        "merge_false: nested",
        {
            "root": {
                "a": "A",
                "b": {"c": "C", "d": {"e": "E", "f": {"g": "G", "h": "H"}}},
            }
        },
        {"root": {"b": {"d": {"f": {"g": "G*"}}}, "dynaconf_merge": False}},
        {"root": {"b": {"d": {"f": {"g": "G*"}}}}},
    ),
]


def main():
    ...


if __name__ == "__main__":
    exit(main())
