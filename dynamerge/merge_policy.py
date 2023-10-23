from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MergePolicy:
    """
    Responsible for storing merge policies and directives, which control the
    behavior of merging process in various scopes.

    This object is intended to be "inherited" via duplication for each tree-level
    of the merging process, thus representing what policies should apply for a
    particular level.
    """

    merge: bool = False
    merge_unique: bool = False
    dict_id_key: str = "dynaconf_id"

    def inherit_load(self, parent_merge_policy: MergePolicy) -> MergePolicy:
        """
        Copy parent MergePolicy to self.
        Bypasses None values to allow partial override.
        """
        if parent_merge_policy.merge is not None:
            self.merge = parent_merge_policy.merge
        if parent_merge_policy.merge_unique is not None:
            self.merge_unique = parent_merge_policy.merge_unique
        if parent_merge_policy.dict_id_key is not None:
            self.dict_id_key = parent_merge_policy.dict_id_key
        return self

    def load_from_mark_list(self, mark_list: list[tuple]):
        """
        Load merge policies form mark list, where each list element is
        a tuple (mark_attr, new_value)
        """
        for mark_attr, new_value in mark_list:
            try:
                setattr(self, mark_attr, new_value)
            except AttributeError:
                print("Invalid parsed marker")
                raise


@dataclass
class MergePolicyNode:
    """Represent a merge policy at each node of a tree-like structure."""

    key: str
    merge_policy: MergePolicy
    children: list = field(default_factory=list)

    def add_child(self, child: MergePolicyNode):
        if not isinstance(child, MergePolicyNode):
            raise TypeError()

        self.children.append(child)

    def __getitem__(self, key):
        return self.children[key]
