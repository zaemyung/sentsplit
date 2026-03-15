from __future__ import annotations

from copy import deepcopy

from typing_extensions import NotRequired, TypedDict

from sentsplit.regexes import Regex


class Config(TypedDict):
    model: NotRequired[str]

    ngram: int

    mincut: int
    maxcut: int

    strip_spaces: bool
    handle_multiple_spaces: bool

    segment_regexes: list[Regex]

    prevent_regexes: list[Regex]
    prevent_word_split: bool


base_config = Config(
    ngram=5,
    mincut=7,
    maxcut=500,
    strip_spaces=False,
    segment_regexes=[
        Regex(name="after_semicolon"),
        Regex(name="ellipsis"),
        Regex(name="newline"),
    ],
    prevent_regexes=[
        Regex(name="liberal_url"),
        Regex(name="period_followed_by_lowercase"),
    ],
    handle_multiple_spaces=True,
    prevent_word_split=True,
)

de_config = deepcopy(base_config)
de_config["model"] = "crf_models/de-default-25032021.model"

en_config = deepcopy(base_config)
en_config["model"] = "crf_models/en-default-25032021.model"

fr_config = deepcopy(base_config)
fr_config["model"] = "crf_models/fr-default-25032021.model"

it_config = deepcopy(base_config)
it_config["model"] = "crf_models/it-default-25032021.model"

ja_config = deepcopy(base_config)
ja_config["model"] = "crf_models/ja-default-05042021.model"
ja_config["mincut"] = 5
ja_config["prevent_word_split"] = False

ko_config = deepcopy(base_config)
ko_config["model"] = "crf_models/ko-default-05042021.model"
ko_config["mincut"] = 5

lt_config = deepcopy(base_config)
lt_config["model"] = "crf_models/lt-default-25032021.model"

pl_config = deepcopy(base_config)
pl_config["model"] = "crf_models/pl-default-25032021.model"

pt_config = deepcopy(base_config)
pt_config["model"] = "crf_models/pt-default-25032021.model"

ru_config = deepcopy(base_config)
ru_config["model"] = "crf_models/ru-default-25032021.model"

tr_config = deepcopy(base_config)
tr_config["model"] = "crf_models/tr-default-25032021.model"

zh_config = deepcopy(base_config)
zh_config["model"] = "crf_models/zh-default-05042021.model"
zh_config["mincut"] = 5
zh_config["prevent_word_split"] = False
