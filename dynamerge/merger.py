"""
Module responsible for merging two structures.
"""
from __future__ import annotations
from dynamerge.differ import MergePolicy, KeyDiffer, KeyDiff, ScopeParser
from typing import Any, TypeAlias
from icecream import ic

# typing
TreePath: TypeAlias = tuple


class Terminal:
    """Terminal type"""


def main():
    ...


def use_new(parent, diff: KeyDiff, **kwargs):
    parent[diff.real_key_pair[0]] = diff.diff_pair[1]
    return parent


def use_old(parent, key_diff: KeyDiff, **kwargs):
    return parent  # no op


def use_dict_merge(parent, diff: KeyDiff, merge_policy: MergePolicy, **kwargs):
    merge_fn = Merger.merge_dict
    if merge_policy.merge is True:
        parent[diff.real_key_pair[0]] = merge_fn(*diff.diff_pair, **kwargs)
    else:
        parent[diff.real_key_pair[0]] = diff.diff_pair[1]

    return parent


def get_structural_type(value):
    """Get values structural type to be used in the Merger.action_map.
    If its not a Dict, List or None, then its a Terminal.
    """
    if type(value) in (dict, list):
        return type(value)
    elif value is None:
        return None
    else:
        return Terminal


class Merger:
    # (parent-type, old-type, new-type): action-over-parent
    action_map = {
        # specific maps
        (dict, dict, dict): use_dict_merge,
        (dict, dict, Terminal): use_new,
        (dict, Terminal, dict): use_new,
        (dict, Terminal, Terminal): use_new,
        # generic maps (TODO implement Any structural type)
        (dict, None, Terminal): use_new,
        (dict, None, dict): use_new,
        (dict, None, list): use_new,
        (dict, Terminal, None): use_old,
        (dict, list, None): use_old,
        (dict, dict, None): use_old,
    }

    @staticmethod
    def get_action(parent, diff: KeyDiff):
        parent_type = type(parent)
        old_value, new_value = diff.diff_pair

        old_type = get_structural_type(old_value)
        new_type = get_structural_type(new_value)

        return Merger.action_map[(parent_type, old_type, new_type)]

    @staticmethod
    def merge_dict(
        old: dict,
        new: dict,
        merge_policy: MergePolicy = None,
        tree_path: TreePath = None,
    ):
        merge_policy = merge_policy or MergePolicy()
        # mark_list = ScopeParser.parse_from_dict(new)
        # merge_policy.load_from_mark_list(mark_list)

        diff_list = KeyDiffer.diff_dict(old, new, merge_policy)
        parent = old  # old will be mutated in-place. e.g parent[ḱey] = new_value
        for diff in diff_list:
            # new independent merge policy for each child, bacause each has a different
            # scope and their policy should not be mixed
            child_merge_policy = MergePolicy().inherit_load(merge_policy)
            diff_marks = ScopeParser.parse_diff(diff)
            child_merge_policy.load_from_mark_list(diff_marks)

            action_fn = Merger.get_action(parent, diff)
            action_fn(parent, diff, merge_policy=child_merge_policy)
        return parent


if __name__ == "__main__":
    exit(main())
