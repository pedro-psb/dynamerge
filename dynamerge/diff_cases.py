"""
Diff Cases

Because there are many and complex diff behavior cases, this module
aims to provide convenience tools for testing and documenting them.
"""
from __future__ import annotations
from dynamerge.differ import Differ
from icecream import ic

doc = """
This module shows the shallow_diff behavior of two continer object under different
configurations and cases.

ShallowDiff here refers to a diff that won't peform a full recursive diff, but
will provide enought information for future processing (and possibly future diffs inside containers).

The ShallDiff object provides some relevant information for post-processing.
The core information are @key_id and @diff_pair.

@key_id is the identify key used for comparision.
For dicts, it is simply they keys.
For lists, we can make a trick to generate a pseudo-key, which we'll call its @key_id.
There are several strategies we can use to generate this pseudo-key, such as using the index,
hashing the values, etc. We'll explore some of those here.

@diff_pair is a tuple (old_value, new_value), where 'old' refers to the data that will receive
the merge, and 'new' to the data being merged.
This tuple is related to a single @key_id, and fall intro three cases:

At key_id="a"
(old None) - old-only: only old have some value for key 'a'
(None, new) - new-only: only new have some value for key 'a'
(old, new) - conflict: both old and new have values for key 'a'
"""

def main():
    print(doc)
    list_merge_use_index_cases()
    list_merge_use_value_hash_cases()
    return 0


def diff_report(name, old, new, diff_fn, **kwargs):
    print()
    print(f"> {name}")
    ic(old)
    ic(new)
    out = list(diff_fn(old, new, **kwargs).sort().get(filter_attr="diff_pair"))
    ic(out)


def list_merge_use_index_cases():
    diff_report(
        "list mode: positional",
        [1, 2, 3, 4],
        [4, 3, 2, 1],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_index,
    )

    diff_report(
        "list mode: positional new < old",
        [1, 2, 3],
        [3, 2],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_index,
    )

    diff_report(
        "list mode: positional + old < new",
        [3, 2],
        [1, 2, 3],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_index,
    )

    diff_report(
        "list-mode: positional + dicts",
        [1, {"a": "B"}, 3],
        [3, {"a": "B"}, 1],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_index,
    )

    diff_report(
        "list-mode: positional + @empty pads",
        [1, {"a": "B"}, 3],
        ["@empty", {"a": "B"}, "@empty"],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_index,
    )


def list_merge_use_value_hash_cases():
    diff_report(
        "list-mode: value hash + hashable values only",
        [1, 2, 3],
        [2, 1, 0],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_value_hash,
    )

    diff_report(
        "list-mode: value hash + dict(annonymous)",
        [1, {"a": "B"}, 3],
        [3, {"a": "B"}, 1],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_value_hash,
    )

    diff_report(
        "list-mode: value hash + dict + dict_id_default",
        [1, 3, {"a": "B", "dynaconf_id": 1}],
        [3, {"a": "B", "dynaconf_id": 1}, 1],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_value_hash,
    )

    diff_report(
        "list-mode: value hash + dict + dict_id_mark_override",
        [1, {"a": "B", "c": "C"}, 3],
        [3, {"a": "B", "d": "D"}, 1, "@dict_id_key=a"],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_value_hash,
    )


if __name__ == "__main__":
    exit(main())
