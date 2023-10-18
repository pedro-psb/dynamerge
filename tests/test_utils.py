from dynamerge.marks import ScopeParser
import pytest


@pytest.mark.parametrize(
    "mark,mark_attr,new_value",
    [
        ("dynaconf_merge", "merge", True),
        ("dynaconf_merge_unique", "merge_unique", True),
        ("dynaconf_merge=false", "merge", False),
        ("dynaconf_merge=False", "merge", False),
        ("dynaconf_id_key=foo", "dict_id_key", "foo"),
    ],
)
def test_parse_from_list_single(mark, mark_attr, new_value):
    sample_list = ["a", "b", 123, True, "dynaconf_abc", mark]
    mark_list = ScopeParser.parse_from_list(sample_list)
    assert len(mark_list) == 1
    assert (mark_attr, new_value) in mark_list


def test_parse_from_list_multiple():
    sample_list = [
        123,
        "abc",
        "dynaconf_merge",
        "dynaconf_merge_unique",
        "dynaconf_merge=false",
        "dynaconf_id_key=foo",
        "@empty",
    ]
    mark_list = ScopeParser.parse_from_list(sample_list)
    assert len(mark_list) == 4
