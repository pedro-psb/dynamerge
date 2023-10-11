"""Cases using: Merger.merge_dict"""
from dataclasses import dataclass


@dataclass
class MergeCase:
    name: str
    old: dict | list
    new: dict | list
    expected: dict | list


case_list = [
    MergeCase(
        "un-nested dicts",
        {"root": {"a": "A", "b": "B"}},
        {"root": {"a": "A*", "c": "C"}},
        {"root": {"a": "A*", "b": "B", "c": "C"}},
    ),
    MergeCase(
        "nested dicts: new-old overrides common keys",
        {"root": {"a": "A", "b": {"c": "C", "d": "D"}}},
        {"root": {"a": "A*", "b": {"c": "C*", "e": "E"}}},
        {"root": {"a": "A*", "b": {"c": "C*", "d": "D", "e": "E"}}},
    ),
    # fmt: off
    MergeCase(
        "nested dicts: new-only merges different key",
        {"root":
            {"a": "A", "b": {"c": "C", "d": {"e": "E", "f": {"g": "G", "h": "H"}}}}},
        {"root":
            {"b": {"d": {"f": {"g": "G*"}}}}},
        {"root":
            {"a": "A", "b": {"c": "C", "d": {"e": "E", "f": {"g": "G*", "h": "H"}}}}},
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
