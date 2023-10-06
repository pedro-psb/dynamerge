from main import MergePolicy
import pytest


@pytest.mark.parametrize(
    "mark,merge_policy_attr,initial_value, expected_value",
    [
        ("dynaconf_merge", "merge", False, True),
        ("dynaconf_merge_unique", "merge_unique", False, True),
        ("dynaconf_merge=false", "merge", True, False),
        ("@dict_id_key=foo", "dict_id_key_override", "dynaconf_id", "foo"),
    ],
)
def test_pop_and_load_list_scope(
    mark, merge_policy_attr, initial_value, expected_value
):
    merge_policy = MergePolicy()
    list_data = [1, 2, 3, mark]
    setattr(merge_policy, merge_policy_attr, initial_value)
    merge_policy.pop_and_load_list_scope(list_data)
    assert getattr(merge_policy, merge_policy_attr) == expected_value
    assert list_data == [1, 2, 3]
