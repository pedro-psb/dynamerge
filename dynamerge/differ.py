"""
KeyDiffer module.

Responsible for creating diff objects from
container, such as dicts and lists.
"""
from __future__ import annotations

from typing import NamedTuple, Literal
from dynamerge.merge_policy import MergePolicy


class PseudoIdStrategies:
    @staticmethod
    def use_index(unique_name: str, container: list, *args, **kwargs) -> dict:
        return {i: i for i, e in enumerate(container)}

    @staticmethod
    def use_value_hash(
        unique_name: str,
        container: list,
        dict_key_override: str | None = None,
        **kwargs,
    ) -> dict:
        """
        Use value-hash as element id.
        If value is a dict, use the following heuristics:
        - lookup for id markup inside it. e.g. [1, {dynaconf_id="foo", ...}, 3]
          or custom @dict_key_id provided by the user.
        - use incremental id (__@unique_name_i__, i=0; i++) (unique inside scope)
        """
        return_dict = {}
        dict_key_name = "dynaconf_id"
        pop_key_id = True
        if dict_key_override is not None:
            dict_key_name = dict_key_override
            pop_key_id = False

        incremental_id_counter = 0
        incremental_id_template = "__{name}_{counter}__"
        for i, e in enumerate(container):
            if isinstance(e, dict):
                pseudo_id_name = e.get(dict_key_name)
                if pop_key_id:
                    e.pop(dict_key_name, None)

                if pseudo_id_name is not None:
                    return_dict[f"{dict_key_name}_{pseudo_id_name}"] = i
                else:
                    return_dict[
                        incremental_id_template.format(
                            name=unique_name, counter=incremental_id_counter
                        )
                    ] = i
            else:
                return_dict[e] = i

        return return_dict


class KeyDiffer:
    """
    Provide function to diff containers by key only (no value compare).

    This is mostly usefull for generalizing compares among list and dicts and
    providing a flexible way of mapping their key-diffs with custom value compares
    or merging strategies.
    """

    pseudo_id_strategies = PseudoIdStrategies

    @staticmethod
    def diff_container(
        old: dict,
        new: dict,
        merge_policy: MergePolicy = None,
        **kwargs,
    ) -> list[KeyDiff]:
        """Return a KeyDiff lists from containers (lists or dicts types)."""
        if isinstance(old, dict) and isinstance(new, dict):
            return KeyDiffer.diff_dict(old, new, merge_policy, **kwargs)
        elif isinstance(old, list) and isinstance(new, list):
            return KeyDiffer.diff_list(old, new, merge_policy, **kwargs)
        else:
            raise TypeError("Can diff only dicts or lists togheter")

    @staticmethod
    def diff_dict(
        old: dict,
        new: dict,
        merge_policy: MergePolicy = None,
    ) -> list[KeyDiff]:
        """Return a KeyDiff lists (old,new)."""
        merge_policy = merge_policy or MergePolicy()
        diffs = []

        union_keys = old.keys() | new.keys()
        for id_key in union_keys:
            diff_pair = (old.get(id_key), new.get(id_key))
            real_key_pair = (id_key, id_key)  # this is usefull only for lists

            diff_object = KeyDiff(id_key, diff_pair, real_key_pair)
            diffs.append(diff_object)
        return diffs

    @staticmethod
    def diff_list(
        old: list,
        new: list,
        merge_policy: MergePolicy = None,
        pseudo_id_strategy=None,
    ) -> list[KeyDiff]:
        """Return a KeyDiff lists (old,new)."""
        pseudo_id_mapper = pseudo_id_strategy or PseudoIdStrategies.use_index
        merge_policy = merge_policy or MergePolicy()
        diffs = []

        # maps {old.pseudo_id -> old.index},
        # - pseudo_id is a generated id from the list-item (for identify comparision)
        # - index is the address of the item in the original list
        old_pseudo_id_map = pseudo_id_mapper(
            "old", old, dict_key_override=merge_policy.dict_id_key
        )
        new_pseudo_id_map = pseudo_id_mapper(
            "new", new, dict_key_override=merge_policy.dict_id_key
        )

        union_keys = old_pseudo_id_map.keys() | new_pseudo_id_map.keys()
        for id_key in union_keys:
            # get index from pseudo_id
            old_index_key = old_pseudo_id_map.get(id_key, None)
            new_index_key = new_pseudo_id_map.get(id_key, None)

            # get value from index
            old_value = old[old_index_key] if old_index_key is not None else None
            new_value = new[new_index_key] if new_index_key is not None else None

            # populate KeyDiff
            diff_pair = (old_value, new_value)
            real_key_pair = (old_index_key, new_index_key)

            diff_object = KeyDiff(id_key, diff_pair, real_key_pair)
            diffs.append(diff_object)
        return diffs


class KeyDiff(NamedTuple):
    """
    A key-based diff representation of containers (dicts and lists).
    It contain the representaiton of keys or pseudo-keys (for lists) conflicts only.

    The purpose of this is to allow a future diff-interpreter to apply different
    meanings to a key-conflict, providing more fine-control of the merging process.

    For example, it could take Diff(id_key="a", diff_pair=(1,1)) and merge that
    into "a" as  [1,1] or 2 ("a": [1,2] or "a": [1,2]).

    Args:
        identity_key: The key used for id comparision (is a pseudo-key for list items)
        diff_pair: A pair of (old, new) values
        real_key_pair: A pair of (old-real-key, new-real-key).
            In lists, it's the index. It may differ from identity_key, dependening
            on the pseudo-key generation strategy.

    Examples:
        {a: A, b: B}
        {a: A, b: B, c: C}
        ------------------
        Diff(a,    diff_pair=(A, A),        real_key_pair=(a, a))
        Diff(b,    diff_pair=(B, B),        real_key_pair=(a, a))
        Diff(c,    diff_pair=(EMPTY, B),    real_key_pair=(a, a))
    """

    id_key: str
    diff_pair: tuple
    real_key_pair: tuple


class DiffUtils:
    def __init__(self, *key_diff: KeyDiff):
        self._diff_list: list = list(key_diff) if key_diff else []

    def append(self, diff: KeyDiff):
        self._diff_list.append(diff)

    def get(
        self,
        filter_attr: Literal["id_key"]
        | Literal["diff_pair"]
        | Literal["real_key_pair"] = None,
        filter_attr_pair: tuple[str, str] = None,
    ):
        """
        Return list of KeyDiff, optionally with a single or pari attr filter.

        Args:
            filter_attr: return only the specified diff.attr from the diffs
            filter_attr_pair: return tuple pair with (diff.attr1, diff.attr2)
        """
        if filter_attr is not None:
            return (getattr(diff, filter_attr) for diff in self._diff_list)
        if filter_attr_pair is not None:
            attr_key, attr_value = filter_attr_pair
            return (
                (getattr(diff, attr_key), getattr(diff, attr_value))
                for diff in self._diff_list
            )
        return self._diff_list

    @staticmethod
    def sort_diff_list(
        diff_list: list[KeyDiff], by_attr: str = "id_key", by_attr_secondary: str = None
    ):
        """Sort this diff_list in-place by key"""
        _diff_list = diff_list.copy()
        _diff_list.sort(key=lambda item: str(getattr(item, by_attr)))
        return _diff_list

    def __iter__(self):
        return (n for n in self._diff_list)
