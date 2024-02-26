from copy import deepcopy

from sentsplit.config import en_config
from sentsplit.segment import SentSplit


def test_default():
    splitter = SentSplit("en")
    assert splitter.segment("Hello world. This is a sentence.") == ["Hello world.", " This is a sentence."]


def test_mincut():
    splitter = SentSplit("en", mincut=13)
    assert splitter.segment("Hello world. This is a sentence.") == ["Hello world. This is a sentence."]


def test_maxcut():
    splitter = SentSplit("en", maxcut=13)
    assert splitter.segment("Hello world. This is a sentence.") == ["Hello world.", " This is a se", "ntence."]


def test_strip_spaces():
    splitter = SentSplit("en")
    assert splitter.segment("Hello world.  ") == ["Hello world.  "]
    assert splitter.segment("  Hello world.") == ["  Hello world."]
    assert splitter.segment("  Hello world.  ") == ["  Hello world.  "]

    splitter = SentSplit("en", strip_spaces=True)
    assert splitter.segment("Hello world.  ") == ["Hello world."]
    assert splitter.segment("  Hello world.") == ["Hello world."]
    assert splitter.segment("  Hello world.  ") == ["Hello world."]


def test_handle_multiple_spaces():
    splitter = SentSplit("en")
    assert splitter.segment("Hello world.  This is a sentence.") == ["Hello world.", "  This is a sentence."]

    splitter = SentSplit("en", handle_multiple_spaces=False)
    assert splitter.segment("Hello world.  This is a sentence.") == ["Hello world.  This is a sentence."]


def test_segment_regexes():
    splitter = SentSplit("en")
    assert splitter.segment("Hello world~ This is a sentence.") == ["Hello world~ This is a sentence."]

    config = deepcopy(en_config)
    config["segment_regexes"].append({"name": "tilde_ending", "regex": r"~+", "at": "end"})
    splitter = SentSplit("en", **config)
    assert splitter.segment("Hello world~ This is a sentence.") == ["Hello world~", " This is a sentence."]


def test_prevent_regexes():
    splitter = SentSplit("en")
    assert splitter.segment('"Hello world. This is a sentence."') == ['"Hello world.', ' This is a sentence."']

    config = deepcopy(en_config)
    config["prevent_regexes"].append({"name": "period_inside_quote", "regex": r'\.(?= *[^"]+")'})
    splitter = SentSplit("en", **config)
    assert splitter.segment('"Hello world. This is a sentence."') == ['"Hello world. This is a sentence."']


# TODO: Add test_prevent_word_split()
# def test_prevent_word_split():
#     pass
