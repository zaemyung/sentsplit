from copy import deepcopy

from sentsplit.config import en_config
from sentsplit.segment import SentSplit


def test_default():
    """Test default English segmentation behavior."""
    splitter = SentSplit("en")
    assert splitter.segment("Hello world. This is a sentence.") == [
        "Hello world.", 
        " This is a sentence."
    ]


def test_mincut():
    """Test segmentation when mincut prevents splitting short segments."""
    splitter = SentSplit("en", mincut=13)
    assert splitter.segment("Hello world. This is a sentence.") == [
        "Hello world. This is a sentence."
    ]


def test_maxcut():
    """Test segmentation when maxcut forces splitting long segments."""
    splitter = SentSplit("en", maxcut=13)
    assert splitter.segment("Hello world. This is a sentence.") == [
        "Hello world.", 
        " This is a se", 
        "ntence."
    ]


def test_strip_spaces():
    """Test behavior of strip_spaces option during segmentation."""
    splitter = SentSplit("en")
    assert splitter.segment("Hello world.  ") == ["Hello world.  "]
    assert splitter.segment("  Hello world.") == ["  Hello world."]
    assert splitter.segment("  Hello world.  ") == ["  Hello world.  "]

    splitter = SentSplit("en", strip_spaces=True)
    assert splitter.segment("Hello world.  ") == ["Hello world."]
    assert splitter.segment("  Hello world.") == ["Hello world."]
    assert splitter.segment("  Hello world.  ") == ["Hello world."]


def test_handle_multiple_spaces():
    """Test handling of multiple spaces with and without collapsing."""
    splitter = SentSplit("en")
    assert splitter.segment("Hello world.  This is a sentence.") == [
        "Hello world.", 
        "  This is a sentence."
    ]

    splitter = SentSplit("en", handle_multiple_spaces=False)
    assert splitter.segment("Hello world.  This is a sentence.") == [
        "Hello world.  This is a sentence."
    ]


def test_segment_regexes():
    """Test custom segmentation regexes for splitting by tilde (~)."""
    splitter = SentSplit("en")
    assert splitter.segment("Hello world~ This is a sentence.") == [
        "Hello world~ This is a sentence."
    ]

    config = deepcopy(en_config)
    config["segment_regexes"].append({"name": "tilde_ending", "regex": r"~+", "at": "end"})
    splitter = SentSplit("en", **config)
    assert splitter.segment("Hello world~ This is a sentence.") == [
        "Hello world~", 
        " This is a sentence."
    ]


def test_prevent_regexes():
    """Test prevent_regexes to stop splitting inside quotes."""
    splitter = SentSplit("en")
    assert splitter.segment('"Hello world. This is a sentence."') == [
        '"Hello world.', 
        ' This is a sentence."'
    ]

    config = deepcopy(en_config)
    config["prevent_regexes"].append({
        "name": "period_inside_quote", 
        "regex": r'\.(?= *[^"]+")'
    })
    splitter = SentSplit("en", **config)
    assert splitter.segment('"Hello world. This is a sentence."') == [
        '"Hello world. This is a sentence."'
    ]


# TODO: Add test_prevent_word_split()
# def test_prevent_word_split():
#     """Test prevention of word-level splits (placeholder)."""
#     pass