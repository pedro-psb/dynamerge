"""Cases using: Merger.merge_dict"""
from dataclasses import dataclass


@dataclass
class MergeCase:
    name: str
    old: dict | list
    new: dict | list
    expected: dict | list
    notes: str = ""


cases = [
    MergeCase(
        "(0,0) when no marks should merge at root",
        {"root": {"a": "A", "b": "B"}},
        {"root": {"a": "A*", "c": "C"}},
        {"root": {"a": "A*", "b": "B", "c": "C"}},
    ),
    MergeCase(
        "(0,0) when mark-false should replace in root",
        {"root": {"a": "A", "b": "B"}},
        {"root": {"a": "A*", "dynaconf_merge": False}},
        {"root": {"a": "A*"}},
        notes="""\
        By the general way scope-marks are interpreted, that is, by taking effect
        in the scope they are located and in all descendents, this is the
        expected behavior.

        Nevertheless, root-level in dynaconf has special behavior.
        This is a matter of priority and precedence. This test case states that:
        - root-level-rules (priority) < mark (priority)
        """,
    ),
    MergeCase(
        "(1,1) when no marks should replace",
        {"root": {"nested": {"a": "A", "b": "B"}}},
        {"root": {"nested": {"c": "C"}}},
        {"root": {"nested": {"c": "C"}}},
    ),
    MergeCase(
        "(1,1) when no marks should replace variation",
        {"root": {"a": "A", "b": {"c": "C", "d": "D"}}, "foo": True},
        {"root": {"a": "A*", "b": {"c": "C*", "e": "E"}}},
        {"root": {"a": "A*", "b": {"c": "C*", "e": "E"}}, "foo": True},
    ),
    MergeCase(
        "(2,2) when mark-true(lvl-0) should apply for descendents",
        {"root": {"a": "A", "b": {"c": "C", "d": {"e": "E", "f": "F"}}}},
        {"root": {"b": {"d": {"f": "F*"}}, "dynaconf_merge": True}},
        {
            "root": {
                "a": "A",
                "b": {"c": "C", "d": {"e": "E", "f": "F*"}},
            }
        },
    ),
    MergeCase(
        "(3,3) when mark-false(level-0) should replace",
        {
            "root": {
                "a": "A",
                "b": {"c": "C", "d": {"e": "E", "f": {"g": "G", "h": "H"}}},
            }
        },
        {"root": {"b": {"d": {"f": {"g": "G*"}}}, "dynaconf_merge": False}},
        {"root": {"b": {"d": {"f": {"g": "G*"}}}}},
    ),
    MergeCase(
        "(1,1) when no marks should replace",
        {"root": {"a": "A", "b": {"c": "C"}}},
        {"root": {"b": {"d": "D"}}},
        {"root": {"a": "A", "b": {"d": "D"}}},
    ),
    MergeCase(
        "(1,1) when merge-true(lvl-1) mark should merge",
        {"root": {"a": "A", "b": {"c": "C"}}},
        {"root": {"b": {"d": "D", "dynaconf_merge": True}}},
        {"root": {"a": "A", "b": {"c": "C", "d": "D"}}},
    ),
    MergeCase(
        "(2,2) when no marks should replace",
        {"root": {"a": "A", "b": {"c": {"d": "D"}}}},
        {"root": {"b": {"c": {"x": "X"}}}},
        {"root": {"a": "A", "b": {"c": {"x": "X"}}}},
    ),
    MergeCase(
        "(2,2) when merge-true(lvl-2) mark should merge",
        {"root": {"a": "A", "b": {"c": {"d": "D"}}}},
        {"root": {"b": {"c": {"x": "X", "dynaconf_merge": True}}}},
        {"root": {"a": "A", "b": {"c": {"d": "D", "x": "X"}}}},
    ),
]


def main():
    ...


if __name__ == "__main__":
    exit(main())
