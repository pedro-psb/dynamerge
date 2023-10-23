from dynamerge.marks import MarkupParser, TokenParser
from dynamerge.merge_policy import MergePolicy
import pytest
from icecream import ic


def test_merge_mark_parsing():
    base_dict = {"a": "A", "b": "B"}
    parser = MarkupParser(base_dict)
    result = parser.parse_tree()
    assert result.merge_policy_tree["a"].merge_policy == MergePolicy()
    assert result.merge_policy_tree["b"].merge_policy == MergePolicy()


@pytest.mark.parametrize(
    "string,output",
    [
        ("@foo", [("foo", "")]),
        ("@foo bar spam eggs", [("foo", "bar spam eggs")]),
        ("@foo bar @spam eggs", [("foo", "bar"), ("spam", "eggs")]),
    ],
)
def test_token_parser(string, output):
    assert TokenParser.parse(string) == output
