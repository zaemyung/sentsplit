# sentsplit
A flexible sentence segmentation library using CRF model and regex rules

This library allows splitting of text paragraphs into sentences. It is built with the following desiderata:
- Be able to extend to new languages or "types" of sentences from data alone by learning a conditional random field (CRF) model.
- Also provide functionality to segment (or not to segment) lines based on regular expression rules (referred as `segment_regexes` and `prevent_regexes`, respectively).
- Be able to reconstruct the exact original text paragraphs from joining the segmented sentences.

All in all, the library aims to benefit from the best of both worlds: data-driven and rule-based approaches.

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
- `add_depunctuated_samples`: when set to `True`, randomly (30% chance) remove the punctuation of the current sentence before concatenation; default is `False`. May only be suitable for languages (e.g. Korean, Japanese) that have specific endings for sentences.
- `add_despaced_samples`: when set to `True`, with 35% chance, current sentence is concatenated to input sample without a prepending white space; default is `False`.

### Setting Configuration
Refer to the `base_config` in `config.py`. Append a new config to the file, adjusting the arguments accordingly if needed.

A newly created model can also be called directly in codes by passing the kwargs accordingly:
```python
from sentsplit.segment import SentSplit

sent_splitter = SentSplit(lang_code, model='path/to/model', ...)
```