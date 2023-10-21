from dynamerge.marks import MarkupParser
from dynamerge.merge_policy import MergePolicy


def test_merge_mark_parsing():
    base_dict = {"a": "A", "b": "B"}
    parser = MarkupParser(base_dict)
    result = parser.parse_tree()
    assert result.merge_policy_tree["a"] == MergePolicy()
    assert result.merge_policy_tree["b"] == MergePolicy()
