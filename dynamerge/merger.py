"""
Module responsible for merging two structures.
"""
from __future__ import annotations
from dynamerge.differ import MergePolicy, KeyDiffer, KeyDiff
from dynamerge.marks import ScopeParser
from typing import Any, TypeAlias, Callable
from icecream import ic
from dataclasses import dataclass
from functools import partial

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
    merge_fn = Merger.merge_containers
    parent[diff.real_key_pair[0]] = merge_fn(*diff.diff_pair, merge_policy, **kwargs)
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
        ("default",): {
            # dict
            (dict, dict, dict): (
                ("merge", True, use_merge),
                ("merge", False, subscribe_new),
            ),
            (dict, dict, Terminal): (
                ("merge", True, subscribe_new),
                ("merge", False, subscribe_new),
            ),
            (dict, Terminal, dict): (
                ("merge", True, subscribe_new),
                ("merge", False, subscribe_new),
            ),
            (dict, Terminal, Terminal): (
                ("merge", True, subscribe_new),
                ("merge", False, subscribe_new),
            ),
            # list
            (dict, list, list): (
                # ("merge_unique", True, "merge", True, use_merge),
                ("merge", True, use_merge),
                ("merge", False, use_merge),
            ),
            (list, Terminal, Terminal): (
                ("merge", True, subscribe_new),
                ("merge", False, subscribe_new),
            ),
            # one side only
            (dict, None, Terminal): (
                ("merge", True, subscribe_new),
                ("merge", False, subscribe_new),
            ),
            (dict, None, dict): (
                ("merge", True, subscribe_new),
                ("merge", False, subscribe_new),
            ),
            (dict, None, list): (
                ("merge", True, subscribe_new),
                ("merge", False, subscribe_new),
            ),
            (dict, Terminal, None): (
                ("merge", True, keep_old),
                ("merge", False, keep_old),
            ),
            (dict, list, None): (
                ("merge", True, keep_old),
                ("merge", False, keep_old),
            ),
            (dict, dict, None): (
                ("merge", True, keep_old),
                ("merge", False, keep_old),
            ),
        },
    }

    @staticmethod
    def get_action(
        parent: dict | list,
        diff: KeyDiff,
        merge_policy: MergePolicy,
        tree_path: tuple[str] = None,
    ):
        """
        Action that will use to process old/new-values in relation to parent container.
        """
        parent_type = type(parent)
        old_value, new_value = diff.diff_pair

        old_type = get_structural_type(old_value)
        new_type = get_structural_type(new_value)

        action_submap = Merger.action_map[("default",)][
            (parent_type, old_type, new_type)
        ]

        for policy_attr, policy_value, action_fn in action_submap:
            if getattr(merge_policy, policy_attr, None) == policy_value:
                action = action_fn
                break

        # should we have some path-based map here?
        # try:
        #     action_map = Merger.action_map[tree_path][(parent_type, old_type, new_type)]
        # except KeyError:
        #     action_map = Merger.action_map[("default",)][
        #         (parent_type, old_type, new_type)
        #     ]

        return action

    # The idea of this is that policies defined for a given /path are
    # used only in /path level and are not inherited by its children.
    tmp_path_based_policies = {
        ("root",): MergePolicy(merge=True, merge_unique=True),
    }

    @staticmethod
    def merge_containers(
        old: dict | list,
        new: dict | list,
        merge_policy: MergePolicy = None,
        parent_path: TreePath = None,
    ):
        merge_policy = merge_policy or MergePolicy()
        parent_path = parent_path or tuple()

        diff_list = KeyDiffer.diff_container(old, new, merge_policy)
        parent = old  # alias
        for diff in diff_list:
            this_path = parent_path + (diff.id_key,)

            # new independent merge policy for each child, bacause each has a different
            # scope and their policy should not be mixed
            child_merge_policy = MergePolicy().inherit_load(merge_policy)

            # tmp_merge includes path-specific policies (e.g, for /root),
            # so it is used only for this diff case and it is not passed forward.
            path_based_policy = Merger.tmp_path_based_policies.get(this_path)
            tmp_merge_policy = MergePolicy().inherit_load(merge_policy)
            if path_based_policy:
                tmp_merge_policy.inherit_load(path_based_policy)

            # parse new-value only. Old should never contain markers
            diff_marks = ScopeParser.parse_container(diff.diff_pair[1])
            child_merge_policy.load_from_mark_list(diff_marks)
            tmp_merge_policy.load_from_mark_list(diff_marks)

            action_fn = Merger.get_action(parent, diff, tmp_merge_policy, this_path)
            action_fn(parent, diff, merge_policy=child_merge_policy)
        return parent


if __name__ == "__main__":
    exit(main())
