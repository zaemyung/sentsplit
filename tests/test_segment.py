import os
import tempfile
import pytest
from unittest.mock import patch
from sentsplit.segment import SentSplit


class TestUnsupportedLanguageInitialization:
    """Tests for SentSplit initialization with unsupported languages and custom models."""

    def test_no_model_raises_value_error(self):
        """Unsupported language without model should raise ValueError."""
        with pytest.raises(ValueError, match="Model path is required"):
            SentSplit("ht")  # Haitian Creole - unsupported language

    def test_nonexistent_model_raises_file_not_found(self):
        """Unsupported language with non-existent model should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Model file not found"):
            SentSplit("ht", model="/nonexistent/path/model.model")

    def test_valid_custom_model_initializes(self):
        """Unsupported language with valid custom model should initialize successfully."""
        with tempfile.NamedTemporaryFile(suffix='.model', delete=False) as tmp_model:
            tmp_model.write(b'CRFSuite model file v0.1\n')  # Minimal CRFSuite header
            tmp_model_path = tmp_model.name

        try:
            with patch.object(SentSplit, '_load_model') as mock_load:
                mock_load.return_value = "mock_tagger"

                splitter = SentSplit("ht", model=tmp_model_path)

                assert splitter.lang == "ht"
                assert splitter.tagger == "mock_tagger"
                assert splitter.config["model"] == tmp_model_path
                mock_load.assert_called_once_with(tmp_model_path)
        finally:
            if os.path.exists(tmp_model_path):
                os.unlink(tmp_model_path)


def test_segment_en():
    """Test English sentence segmentation."""
    splitter = SentSplit("en")
    assert splitter.segment("This is a test sentence. And here is another one.") == [
        "This is a test sentence.",
        " And here is another one.",
    ]


def test_segment_fr():
    """Test French sentence segmentation."""
    splitter = SentSplit("fr")
    assert splitter.segment("Ceci est une phrase de test. Et voici une autre.") == [
        "Ceci est une phrase de test.",
        " Et voici une autre.",
    ]


def test_segment_de():
    """Test German sentence segmentation."""
    splitter = SentSplit("de")
    assert splitter.segment("Dies ist ein Test-Satz. Und hier ist noch einer.") == [
        "Dies ist ein Test-Satz.",
        " Und hier ist noch einer.",
    ]


def test_segment_it():
    """Test Italian sentence segmentation."""
    splitter = SentSplit("it")
    assert splitter.segment("Questo è una frase di prova. Ed ecco un'altra.") == [
        "Questo è una frase di prova.",
        " Ed ecco un'altra.",
    ]


def test_segment_ja():
    """Test Japanese sentence segmentation."""
    splitter = SentSplit("ja")
    assert splitter.segment("これはテストの文です。 ここにもう一つあります。") == [
        "これはテストの文です。",
        " ここにもう一つあります。",
    ]


def test_segment_ko():
    """Test Korean sentence segmentation."""
    splitter = SentSplit("ko")
    assert splitter.segment("이것은 테스트 문장입니다. 여기에 하나 더 있습니다.") == [
        "이것은 테스트 문장입니다.",
        " 여기에 하나 더 있습니다.",
    ]


def test_segment_lt():
    """Test Lithuanian sentence segmentation."""
    splitter = SentSplit("lt")
    assert splitter.segment("Tai yra bandymo sakinys. Ir čia yra dar vienas.") == [
        "Tai yra bandymo sakinys.",
        " Ir čia yra dar vienas.",
    ]


def test_segment_pl():
    """Test Polish sentence segmentation."""
    splitter = SentSplit("pl")
    assert splitter.segment("To jest zdanie testowe. A oto kolejne.") == [
        "To jest zdanie testowe.",
        " A oto kolejne.",
    ]


def test_segment_pt():
    """Test Portuguese sentence segmentation."""
    splitter = SentSplit("pt")
    assert splitter.segment("Esta é uma frase de teste. E aqui está mais uma.") == [
        "Esta é uma frase de teste.",
        " E aqui está mais uma.",
    ]


def test_segment_ru():
    """Test Russian sentence segmentation."""
    splitter = SentSplit("ru")
    assert splitter.segment("Это тестовое предложение. И вот еще одно.") == [
        "Это тестовое предложение.",
        " И вот еще одно.",
    ]


def test_segment_zh():
    """Test Chinese sentence segmentation."""
    splitter = SentSplit("zh")
    assert splitter.segment("这是一个测试句子。 这里还有另一个。") == [
        "这是一个测试句子。",
        " 这里还有另一个。",
    ]


def test_segment_tr():
    """Test Turkish sentence segmentation."""
    splitter = SentSplit("tr")
    assert splitter.segment("Bu bir test cümlesi. İşte başka bir tane.") == [
        "Bu bir test cümlesi.",
        " İşte başka bir tane.",
    ]


def test_segment_edge_cases():
    """Test segmentation of edge cases like line breaks and spacing."""
    splitter = SentSplit("en")
    assert splitter.segment("This\n") == ["This\n"]
    assert splitter.segment("This is a test sentence.\n\n And here's another one.\n") == [
        "This is a test sentence.\n", "\n", " And here's another one.\n"
    ]