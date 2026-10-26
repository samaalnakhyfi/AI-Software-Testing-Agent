import pytest

from agent.test_generator import SUPPORTED_TEST_TYPES, generate_test_cases, parse_test_cases


def test_parses_reply_wrapped_in_code_fence():
    reply = '```json\n[{"name": "Title", "test_type": "page_title"}]\n```'
    assert parse_test_cases(reply) == [{"name": "Title", "test_type": "page_title"}]


def test_parses_reply_with_surrounding_text():
    reply = 'Here you go:\n[{"name": "HTTPS", "test_type": "https_security"}]\nGood luck!'
    assert parse_test_cases(reply)[0]["test_type"] == "https_security"


def test_drops_unsupported_and_incomplete_cases():
    reply = """[
        {"name": "Login", "test_type": "login"},
        {"test_type": "page_load"},
        {"name": "Load", "test_type": "page_load"}
    ]"""
    assert parse_test_cases(reply) == [{"name": "Load", "test_type": "page_load"}]


@pytest.mark.parametrize("reply", [
    "Sorry, I cannot do that.",
    "[not valid json]",
    '[{"name": "Login", "test_type": "login"}]',
])
def test_rejects_unusable_replies(reply):
    with pytest.raises(ValueError):
        parse_test_cases(reply)


def test_fallback_cases_use_supported_types():
    for test_case in generate_test_cases("https://example.com"):
        assert test_case["test_type"] in SUPPORTED_TEST_TYPES
