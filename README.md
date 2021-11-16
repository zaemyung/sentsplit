# sentsplit
A flexible sentence segmentation library using CRF model and regex rules

This library allows splitting of text paragraphs into sentences. It is built with the following desiderata:
- Be able to extend to new languages or "types" of sentences from data alone by learning a conditional random field (CRF) model.
- Also provide functionality to segment (or not to segment) lines based on regular expression rules (referred as `segment_regexes` and `prevent_regexes`, respectively).
- Be able to reconstruct the exact original text paragraphs from joining the segmented sentences.

All in all, the library aims to benefit from the best of both worlds: data-driven and rule-based approaches.

You can try out the library [here](https://share.streamlit.io/zaemyung/sentsplit/main).

## Installation
Supports Python 3.6+

```bash
# stable
pip install sentsplit

# bleeding-edge
pip install git+https://github.com/zaemyung/sentsplit
```

Uses [python-crfsuite](https://github.com/scrapinghub/python-crfsuite), which, in turn, is built upon [CRFsuite](https://github.com/chokkan/crfsuite).

## Segmentation
### CLI
```bash
$ sentsplit segment -l lang_code -i /path/to/input_file  # outputs to /path/to/input_file.segment
$ sentsplit segment -l lang_code -i /path/to/input_file -o /path/to/output_file

$ sentsplit segment -h  # prints out the detailed usage
```

### Python Library
```python
from sentsplit.segment import SentSplit

# use default setting
sent_splitter = SentSplit(lang_code)

# override default setting - see "Features" for detail
sent_splitter = SentSplit(lang_code, **overriding_kwargs)

# segment a single line
sentences = sent_splitter.segment(line)

# can also segment a list of lines
sentences = sent_splitter.segment([lines])
```

## Features
The behavior of segmentation can be adjusted by the following arguments:
- `mincut`: a line is not segmented if its character-level length is smaller than `mincut`, preventing too short sentences.
- `maxcut`: a line is segmented if its character-level length is greater or equal to `maxcut`, preventing too long sentences.
- `strip_spaces`: trim any white spaces in front and end of a sentence; does not guarantee exact reconstruction of original passages.
- `handle_multiple_spaces`: substitute multiple spaces with a single space, perform segmentation, and recover the original spaces.
- `segment_regexes`: segment at either `start` or `end` index of the matched group defined by the regex patterns.
- `prevent_regexes`: a line is not segmented at characters that fall within the matching group(s) captured by the regex patterns.
- `prevent_word_split`: a line is not segmented at characters that are within a word where the word boundary is denoted by white spaces around it or a punctuation;
may not be suitable for languages (e.g. Chinese, Japanese, Thai) that do not use spaces to differentiate words.

Segmentation is performed by first applying a trained CRF model to a line, where each character in the line is labelled as either `O` or `EOS`.
`EOS` label indicates the position for segmentation.

Note that `prevent_regexes` is applied *after* `segment_regexes`, meaning that the segmentation positions captured by `segment_regexes` can be *overridden* by `prevent_regexes`.

### An Example
Let's suppose we want to segment sentences that end with a tilde (`~` or `〜`) which is often used in some East Asian countries to convey a sense of friendliness, silliness, whimsy or flirtatiousness.
We can devise a regex that looks something like this: `(?<=[다요])~+(?= )`, where `다` and `요` are the most common characters that finish the sentences in the polite/formal form.
This regex can be added to `segment_regexes` to take effect:
```python
from copy import deepcopy
from sentsplit.config import ko_config
from sentsplit.segment import SentSplit

my_config = deepcopy(ko_config)
my_config['segment_regexes'].append({'name': 'tilde_ending', 'regex': r'(?<=[다요])~+(?= )', 'at': 'end'})
sent_splitter = SentSplit('ko', **my_config)

sent_splitter.segment('안녕하세요~ 만나서 정말 반갑습니다~~ 잘 부탁드립니다!')

# results with the regex: ['안녕하세요~', ' 만나서 정말 반갑습니다~~', ' 잘 부탁드립니다!']
# results without the regex: ['안녕하세요~ 만나서 정말 반갑습니다~~ 잘 부탁드립니다!']
```
To learn more about the regular expressions, this [website](https://www.regular-expressions.info/tutorial.html) provides a good tutorial.

## Creating a New SentSplit Model
Creating a new model involves first training a CRF model on a dataset of clean sentences, followed by (optionally) adding or modifying the feature arguments for better performance.

### Training a CRF Model
First, prepare a corpus file where a single line corresponds to a single sentence.
Then, a CRF model can be trained by running a command:
```bash
sentsplit train -l lang_code -c corpus_file_path  # outputs to {corpus_file_path}.{lang_code}-{ngram}-gram-{YearMonthDate}.model

sentsplit train -h  # prints out the detailed usage
```

The following arguments are used to set the training setting:
- `ngram`: maximum ngram features used for CRF model; default is `5`.
- `crf_max_iteration`: maximum number of CRF iteration for training; default is `50`.
- `sample_min_length`: when preparing an input sample for CRF model, gold sentences are concatenated to form a longer sample with a length greater than `sample_min_length`; default is `450`.
- `depunctuation_ratio`: ratio of training samples with no punctuation inbetween the sentences.
May only be suitable for certain languages (e.g. "ko", "ja") that have specific endings for sentences.
The top-`num_depunctuation_endings` most common endings are computed from `corpus`.
1.0 means 100% of the training samples are depunctuated.
- `num_depunctuation_endings`: number of most common sentence endings to extract and use.
- `ending_length`: length of sentence endings counted from reverse, exclusing any punctuation.
- `despace_ratio`: ratio of training samples without whitespaces inbetween the sentences.
1.0 means 100% of the training samples are despaced. For languages that do not often use whitespaces, set this to a high value ~1.0.

### Setting Configuration
Refer to the `base_config` in `config.py`. Append a new config to the file, adjusting the arguments accordingly if needed.

A newly created model can also be called directly in codes by passing the kwargs accordingly:
```python
from sentsplit.segment import SentSplit

sent_splitter = SentSplit(lang_code, model='path/to/model', ...)
```

## Supported Languages
Currently supported languages are:
- English (`en`)
- French (`fr`)
- German (`de`)
- Italian (`it`)
- Japanese (`ja`)
- Korean (`ko`)
- Lithuanian (`lt`)
- Polish (`pl`)
- Portuguese (`pt`)
- Russian (`ru`)
- Simplified Chinese (`zh`)
- Turkish (`tr`)

Please note that many of these languages are trained with openly available sentences gathered from bilingual corpora for machine translations.
The training sentences for European languages are mostly from the [Europarl](https://www.statmt.org/europarl/) corpora, so the default models may not handle colloquial sentences effectively.
We can either train a new CRF model with more gold sentences from the target domain, or devise a set of domain-specific regex rules if need be.

## License
`sentsplit` is licensed under MIT license, as found in [LICENSE](https://github.com/zaemyung/sentsplit/blob/main/LICENSE) file.
