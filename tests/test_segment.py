from sentsplit.segment import SentSplit


def test_segment_en():
    splitter = SentSplit("en")

    assert splitter.segment("This is a test sentence. And here is another one.") == [
        "This is a test sentence.",
        " And here is another one.",
    ]


def test_segment_fr():
    splitter = SentSplit("fr")

    assert splitter.segment("Ceci est une phrase de test. Et voici une autre.") == [
        "Ceci est une phrase de test.",
        " Et voici une autre.",
    ]


def test_segment_de():
    splitter = SentSplit("de")

    assert splitter.segment("Dies ist ein Test-Satz. Und hier ist noch einer.") == [
        "Dies ist ein Test-Satz.",
        " Und hier ist noch einer.",
    ]


def test_segment_it():
    splitter = SentSplit("it")

    assert splitter.segment("Questo è una frase di prova. Ed ecco un'altra.") == [
        "Questo è una frase di prova.",
        " Ed ecco un'altra.",
    ]


def test_segment_ja():
    splitter = SentSplit("ja")

    assert splitter.segment("これはテストの文です。 ここにもう一つあります。") == [
        "これはテストの文です。",
        " ここにもう一つあります。",
    ]


def test_segment_ko():
    splitter = SentSplit("ko")

    assert splitter.segment("이것은 테스트 문장입니다. 여기에 하나 더 있습니다.") == [
        "이것은 테스트 문장입니다.",
        " 여기에 하나 더 있습니다.",
    ]


def test_segment_lt():
    splitter = SentSplit("lt")

    assert splitter.segment("Tai yra bandymo sakinys. Ir čia yra dar vienas.") == [
        "Tai yra bandymo sakinys.",
        " Ir čia yra dar vienas.",
    ]


def test_segment_pl():
    splitter = SentSplit("pl")

    assert splitter.segment("To jest zdanie testowe. A oto kolejne.") == [
        "To jest zdanie testowe.",
        " A oto kolejne.",
    ]


def test_segment_pt():
    splitter = SentSplit("pt")

    assert splitter.segment("Esta é uma frase de teste. E aqui está mais uma.") == [
        "Esta é uma frase de teste.",
        " E aqui está mais uma.",
    ]


def test_segment_ru():
    splitter = SentSplit("ru")

    assert splitter.segment("Это тестовое предложение. И вот еще одно.") == [
        "Это тестовое предложение.",
        " И вот еще одно.",
    ]


def test_segment_zh():
    splitter = SentSplit("zh")

    assert splitter.segment("这是一个测试句子。 这里还有另一个。") == [
        "这是一个测试句子。",
        " 这里还有另一个。",
    ]


def test_segment_tr():
    splitter = SentSplit("tr")

    assert splitter.segment("Bu bir test cümlesi. İşte başka bir tane.") == [
        "Bu bir test cümlesi.",
        " İşte başka bir tane.",
    ]


def test_segment_edge_cases():
    splitter = SentSplit("en")

    assert splitter.segment("This\n") == [
        "This\n"
    ]

    assert splitter.segment("This is a test sentence.\n\n And here's another one.\n") == [
        "This is a test sentence.\n", "\n", " And here's another one.\n"
    ]
