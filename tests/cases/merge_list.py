"""Cases using: Merger.merge_dict"""
from dataclasses import dataclass


@dataclass
class MergeCase:
    name: str
    desc: str
    old: dict | list
    new: dict | list
    expected: dict | list


cases = [
    MergeCase(
        "positional mode",
        "Merges two lists by index-match",
        {"root": {"listy": [21, 22, 23]}},
        {"root": {"listy": [91, 92, 93]}},
        {"root": {"listy": [91, 92, 93]}},
    )
]
