"""
Module responsible for merging two structures.
"""
from __future__ import annotations
from dynamerge.differ import MergePolicy, KeyDiffer, KeyDiff, ScopeParser
from typing import Any, TypeAlias
from icecream import ic
from dataclasses import dataclass

# typing
TreePath: TypeAlias = tuple


class Terminal:
    """Terminal type"""


def main():
    ...


def subscribe_new(parent, diff: KeyDiff, **kwargs):
    parent[diff.real_key_pair[0]] = diff.diff_pair[1]
    return parent


def append_new(parent: list, diff: KeyDiff, **kwargs):
    parent.append(diff.diff_pair[1])
    return parent


def inset_new_at(parent: list, diff: KeyDiff, **kwargs):
    try:
        insert_index = kwargs.pop("insert_index")
    except KeyError:
        raise

    parent.insert(insert_index, diff.diff_pair[1])
    return parent


def keep_old(parent, key_diff: KeyDiff, **kwargs):
    return parent  # no op


def use_merge(parent, diff: KeyDiff, merge_policy: MergePolicy, **kwargs):
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


@dataclass
class PolicyDispatch:
    merge_true = keep_old
    merge_false = keep_old
    merge_unique = keep_old


class Merger:
    # (parent-type, old-type, new-type): action-over-parent
    action_map = {
        ("_default",): {
            # dict
            (dict, dict, dict): PolicyDispatch(
                merge_true=subscribe_new,
                merge_false=subscribe_new,
            ),
            (dict, dict, Terminal): subscribe_new,
            (dict, Terminal, dict): subscribe_new,
            (dict, Terminal, Terminal): subscribe_new,
            # list
            (dict, list, list): use_merge,
            (list, Terminal, Terminal): subscribe_new,
            # one side only
            (dict, None, Terminal): subscribe_new,
            (dict, None, dict): subscribe_new,
            (dict, None, list): subscribe_new,
            (dict, Terminal, None): keep_old,
            (dict, list, None): keep_old,
            (dict, dict, None): keep_old,
        },
        ("default",): {
            # dict
            (dict, dict, dict): subscribe_new,
            (dict, dict, Terminal): subscribe_new,
            (dict, Terminal, dict): subscribe_new,
            (dict, Terminal, Terminal): subscribe_new,
            # list
            (dict, list, list): use_merge,
            (list, Terminal, Terminal): subscribe_new,
            # one side only
            (dict, None, Terminal): subscribe_new,
            (dict, None, dict): subscribe_new,
            (dict, None, list): subscribe_new,
            (dict, Terminal, None): keep_old,
            (dict, list, None): keep_old,
            (dict, dict, None): keep_old,
        },
        ("root",): {
            (dict, dict, dict): use_merge,
            (dict, dict, Terminal): subscribe_new,
            (dict, Terminal, dict): subscribe_new,
            (dict, Terminal, Terminal): subscribe_new,
            (dict, None, Terminal): subscribe_new,
            (dict, None, dict): subscribe_new,
            (dict, None, list): subscribe_new,
            (dict, Terminal, None): keep_old,
            (dict, list, None): keep_old,
            (dict, dict, None): keep_old,
        },
    }

    @staticmethod
    def get_action(parent, diff: KeyDiff, tree_path: tuple[str] = None):
        """
        Action that will use to process old/new-values in relation to parent conainer.
        """
        parent_type = type(parent)
        old_value, new_value = diff.diff_pair

        old_type = get_structural_type(old_value)
        new_type = get_structural_type(new_value)

        try:
            action_map = Merger.action_map[tree_path][(parent_type, old_type, new_type)]
        except KeyError:
            action_map = Merger.action_map[("default",)][
                (parent_type, old_type, new_type)
            ]

        return action_map

    @staticmethod
    def merge_dict(
        old: dict | list,
        new: dict | list,
        merge_policy: MergePolicy = None,
        tree_path: TreePath = None,
    ):
        merge_policy = merge_policy or MergePolicy()
        tree_path = tree_path or tuple()

        diff_list = KeyDiffer.diff_container(old, new, merge_policy)
        parent = old  # alias
        for diff in diff_list:
            # new independent merge policy for each child, bacause each has a different
            # scope and their policy should not be mixed
            child_merge_policy = MergePolicy().inherit_load(merge_policy)

            # parse new-value only. Old should never contain markers
            diff_marks = ScopeParser.parse_container(diff.diff_pair[1])
            child_merge_policy.load_from_mark_list(diff_marks)

            new_path = tree_path + (diff.id_key,)
            action_fn = Merger.get_action(parent, diff, new_path)
            action_fn(parent, diff, merge_policy=child_merge_policy)
        return parent


if __name__ == "__main__":
    exit(main())
