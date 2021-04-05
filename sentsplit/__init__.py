import argparse
import json

import sentsplit.cli
import sentsplit.meta_data
import sentsplit.segment
import sentsplit.train


def str_to_bool(v):
  return str(v).lower() in ('yes', 'true', 't', '1')


def main(*args: str) -> None:
    parser = argparse.ArgumentParser(description=sentsplit.meta_data.description)
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {sentsplit.meta_data.version}')
    parser.set_defaults(func=lambda x: parser.print_usage())
    subparsers = parser.add_subparsers()

    # train a new CRF model
    subparser_train = subparsers.add_parser('train', help='train a new CRF model')
    subparser_train.add_argument('-l', '--lang', required=True, help='ISO language code, e.g. "ko" for Korean, "en" for English')
    subparser_train.add_argument('-c', '--corpus', required=True, help='path to input corpus file, where one line is one sentence')
    subparser_train.add_argument('-n', '--ngram', type=int, default=5, help='maximum ngram features for CRF model')
    subparser_train.add_argument('-o', '--output', type=str, help='path to output CRF model')
    subparser_train.add_argument('--sample_min_length', type=int, default=450, help='minimum number of characters of an input sample for CRF model')
    subparser_train.add_argument('--crf_max_iteration', type=int, default=50, help='maximum number of CRF iteration for training')
    subparser_train.add_argument('--depunctuation_ratio', type=float, default=0.0,
                                 help='ratio of training samples with no punctuation; only appropriate for certain languages '\
                                      '(e.g. "ko", "ja") that have specific endings for sentences; '\
                                      'top-`num_depunctuation_endings` most common endings are computed from `corpus`; '\
                                      '1.0 means 100%% of the samples are depunctuated')
    subparser_train.add_argument('--num_depunctuation_endings', type=int, default=100, help='number of sentence endings to extract and use')
    subparser_train.add_argument('--ending_length', type=int, default=3, help='length of a sentence ending counted from reverse, excluding any punctuation')
    subparser_train.add_argument('--despace_ratio', type=float, default=0.0,
                                 help='ratio of training samples without whitespaces inbetween the sentences; '\
                                      '1.0 means 100%% of the samples are despaced')
    subparser_train.set_defaults(func=sentsplit.cli.sentsplit_train)

    # segment a given text file
    subparser_segment = subparsers.add_parser('segment', aliases=['split'],
                                              help='segment an input file into sentences;'\
                                                   'optional arguments can override the default values defined in the `config.py`')
    subparser_segment.add_argument('-l', '--lang', required=True, help='ISO language code, e.g. "ko", "en"')
    subparser_segment.add_argument('-i', '--input', required=True, help='path to input file to segment')
    subparser_segment.add_argument('-o', '--output', help='path to output file, default is `{input}.split`')
    subparser_segment.add_argument('-m', '--model', help='path to the CRF model')
    subparser_segment.add_argument('--ngram', type=int, help='maximum ngram for both training and segmentation')
    subparser_segment.add_argument('--mincut', type=int, help='does not segment a line if its character length is shorter than the mincut')
    subparser_segment.add_argument('--maxcut', type=int, help='segment a line if its character length exceeds the maxcut')
    subparser_segment.add_argument('--strip_spaces', type=str_to_bool, default=False,
                                   help='trim (if any) whitespaces of segmented sentences at the head and tail')
    subparser_segment.add_argument('--handle_multiple_spaces', type=str_to_bool, default=True,
                                   help='substitute multiple spaces with a single space, segment, and recover the original spaces')
    subparser_segment.add_argument('--prevent_word_split', type=str_to_bool, default=True,
                                   help='prevent from splitting a word where word boundary is denoted by white spaces; '\
                                        'ignored if the splitting position is at a punctuation')
    subparser_segment.add_argument('--segment_regexes', nargs='?', type=json.loads,
                                   help='segment at either start or end indices of the matched regex patterns defined by `segment_regexes` in JSON;'\
                                        'e.g. \'[{"name": "custom", "regex": "\\\\w+봐유~+", "at": "end"}]\'')
    subparser_segment.add_argument('--prevent_regexes', nargs='?', type=json.loads,
                                   help='do not segment at characters that are matched by `prevent_regexes` regex(es) in JSON;'\
                                        'e.g. \'[{"name": "custom", "regex": "\\\\.["\\\\\'”] "}]\'')
    subparser_segment.add_argument('--cores', type=int, default=1, help='number of CPU cores to use; default is 1 (single core)')
    subparser_segment.set_defaults(func=sentsplit.cli.sentsplit_segment)

    args = parser.parse_args()
    args.func(args)
