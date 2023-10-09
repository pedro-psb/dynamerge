"""
Diff Cases

Because there are many and complex diff behavior cases, this module aims to provide
convenience tools for testing and documenting them.

KeyDiff here refers to a diff that won't peform a full recursive diff, but
will provide enought information for future processing (and possibly future diffs
inside containers).

The ShallDiff object provides some relevant information for post-processing. The
core information are @key_id and @diff_pair.

@key_id is the identify key used for comparision:
* For dicts, it is simply they keys.
* For lists, we can make a trick to generate a pseudo-key, which we'll call its @key_id.

There are several strategies we can use to generate this pseudo-key, such as using the index,
hashing the values, etc. We'll explore some of those here.

@diff_pair is a tuple (old_value, new_value), where 'old' refers to the data that will receive
the merge, and 'new' to the data being merged.
This tuple is related to a single @key_id, and fall intro three cases:

At key_id="a"
(old None) - old-only: only old have some value for key 'a'
(None, new) - new-only: only new have some value for key 'a'
(old, new) - conflict: both old and new have values for key 'a'


Examples
    # list merge [pseudo-key.use_index]
    # uses positional comparision (by index)
    [1, {...}, 3]
    [3, {...}, 1]
    ------------------
    Diff(0,    diff_pair=(1, 3),            real_key_pair=(0, 0))
    Diff(1,    diff_pair=({...}, {...}),    real_key_pair=(1, 1))
    Diff(2,    diff_pair=(3, 1),            real_key_pair=(2, 2))

    # list merge [pseudo-key.use_value_hash]
    # - generates id_key from value_hash.
    # - uses random uuid4 for unhashable values.
    [1, {...}, 3]
    [3, {...}, 1]
    ------------------
    Diff(id_key=1,        diff_pair=(1, 1),            real_key_pair=(0, 2))
    Diff(id_key=3,        diff_pair=(3, 3),            real_key_pair=(2, 0))
    Diff(id_key=uuid-a,   diff_pair=({...}, EMPTY),    real_key_pair=(a, a))
    Diff(id_key=uuid-b,   diff_pair=(EMPTY, {...}),    real_key_pair=(a, a))

    # list merge [pseudo-key.use_value_hash + special dict-id]
    # - generates id_key from value_hash
    # - uses id_mark inside dict to produce it's pseudo id_key
    [1, {id_mark=x, ...}, 3]
    [3, {id_mark=x, ...}, 1]
    ------------------
    Diff(id_key=1,    diff_pair=(1, 1),            real_key_pair=(0, 2))
    Diff(id_key=3,    diff_pair=(3, 3),            real_key_pair=(2, 0))
    Diff(id_key=x,    diff_pair=({...}, {...}),    real_key_pair=(a, a))

"""
from __future__ import annotations
from dynamerge.differ import KeyDiffer
from icecream import ic

doc = __doc__


def main():
    print(doc)
    case_list_diff_use_index_cases()
    case_list_diff_use_value_hash_cases()
    case_dict_diff()
    return 0


def diff_report(name, old, new, diff_fn, **kwargs):
    print()
    print(f"> {name}")
    ic(old)
    ic(new)
    # out = list(
    #     diff_fn(old, new, **kwargs).sort().get(filter_attr_pair=("id_key", "diff_pair"))
    # )
    diff_list = diff_fn(old, new, **kwargs)
    out = {
        k: v for k, v in diff_list.sort().get(filter_attr_pair=("id_key", "diff_pair"))
    }
    ic(out)


def case_list_diff_use_index_cases():
    diff_report(
        "list mode: positional",
        [1, 2, 3, 4],
        [4, 3, 2, 1],
        KeyDiffer.diff_list,
        pseudo_id_strategy=KeyDiffer.pseudo_id_strategies.use_index,
    )

    diff_report(
        "list mode: positional new < old",
        [1, 2, 3],
        [3, 2],
        KeyDiffer.diff_list,
        pseudo_id_strategy=KeyDiffer.pseudo_id_strategies.use_index,
    )

    diff_report(
        "list mode: positional + old < new",
        [3, 2],
        [1, 2, 3],
        KeyDiffer.diff_list,
        pseudo_id_strategy=KeyDiffer.pseudo_id_strategies.use_index,
    )

    diff_report(
        "list-mode: positional + dicts",
        [1, {"a": "B"}, 3],
        [3, {"a": "B"}, 1],
        KeyDiffer.diff_list,
        pseudo_id_strategy=KeyDiffer.pseudo_id_strategies.use_index,
    )

    diff_report(
        "list-mode: positional + @empty pads",
        [1, {"a": "B"}, 3],
        ["@empty", {"a": "B"}, "@empty"],
        KeyDiffer.diff_list,
        pseudo_id_strategy=KeyDiffer.pseudo_id_strategies.use_index,
    )


def case_list_diff_use_value_hash_cases():
    diff_report(
        "list-mode: value hash + hashable values only",
        [1, 2, 3],
        [2, 1, 0],
        KeyDiffer.diff_list,
        pseudo_id_strategy=KeyDiffer.pseudo_id_strategies.use_value_hash,
    )

    diff_report(
        "list-mode: value hash + dict(annonymous)",
        [1, {"a": "B"}, 3],
        [3, {"a": "B"}, 1],
        KeyDiffer.diff_list,
        pseudo_id_strategy=KeyDiffer.pseudo_id_strategies.use_value_hash,
    )

    diff_report(
        "list-mode: value hash + dict + dict_id_default",
        [1, 3, {"a": "B", "dynaconf_id": 1}],
        [3, {"a": "B", "dynaconf_id": 1}, 1],
        KeyDiffer.diff_list,
        pseudo_id_strategy=KeyDiffer.pseudo_id_strategies.use_value_hash,
    )

    diff_report(
        "list-mode: value hash + dict + dict_id_mark_override",
        [1, {"a": "B", "c": "C"}, 3],
        [3, {"a": "B", "d": "D"}, 1, "dynaconf_id_key=a"],
        KeyDiffer.diff_list,
        pseudo_id_strategy=KeyDiffer.pseudo_id_strategies.use_value_hash,
    )

def case_dict_diff():
    diff_report(
        "dict merge",
        {"a": "A", "b": "B"},
        {"a": "A", "b": "B"},
        KeyDiffer.diff_dict,
    )
    diff_report(
        "dict merge",
        {"a": "A", "b": "B"},
        {"a": "A", "c": "C"},
        KeyDiffer.diff_dict,
    )
    diff_report(
        "dict merge",
        {"a": 123, "b": "B"},
        {"a": "A", "b": False},
        KeyDiffer.diff_dict,
    )
    diff_report(
        "dict merge",
        {"a": [1,2,3,4], "b": "B"},
        {"a": {"m": "M", "n": "N", "p": "P"}, "b": "Not B"},
        KeyDiffer.diff_dict,
    )

if __name__ == "__main__":
    exit(main())
