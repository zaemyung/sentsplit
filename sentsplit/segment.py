import math
import os
import pprint
from copy import deepcopy
from typing import Any, Dict, List, Tuple, Union

import pkg_resources
import pycrfsuite
import regex as re
from loguru import logger

from . import config, regexes
from .train import _PUNCTUATIONS, _sample_to_features
from .utils import split_keep_multiple_separators


class SentSplit():

    def __init__(self, lang: str, **kwargs: Any) -> None:
        self.lang = lang
        try:
            default_config = deepcopy(getattr(config, f'{self.lang}_config'))
        except AttributeError:
            logger.critical(f"Unsupported language: {self.lang.upper()}")
            logger.info(f"Falling back to the `base_config`. Need to provide `model` path.")
            default_config = deepcopy(getattr(config, 'base_config'))

        # override config arguments
        for k, v in kwargs.items():
            if k not in default_config:
                logger.warning(f"`{k}` not in config, skipped")
                continue
            default_config[k] = v

        self.config = default_config

        # load tagger
        model_path = self.config['model']
        if not os.path.isfile(model_path):
            model_path = pkg_resources.resource_filename('sentsplit', model_path)
        self.tagger = SentSplit._load_model(model_path)

        # fill regexes
        self._fill_regexes()

        config_string = pprint.pformat(self.config, indent=2)
        logger.info(f"SentSplit for {self.lang.upper()} loaded:\n{config_string}")

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    @staticmethod
    def _load_model(model_path: str) -> pycrfsuite.Tagger:
        tagger = pycrfsuite.Tagger()
        tagger.open(model_path)
        return tagger

    def _fill_regexes(self) -> None:
        '''
        Retrieve actual regexes from `regexes.py` by their `name`s if not given
        '''
        for rgx_index, rgx in enumerate(self.config['segment_regexes']):
            if 'regex' not in rgx:
                self.config['segment_regexes'][rgx_index] = getattr(regexes, rgx['name'])
        for rgx_index, rgx in enumerate(self.config['prevent_regexes']):
            if 'regex' not in rgx:
                self.config['prevent_regexes'][rgx_index] = getattr(regexes, rgx['name'])

    def segment(self, string: Union[str, List], strip_spaces: Union[None, bool] = None) -> List[str]:
        if strip_spaces is None:
            strip_spaces = self.config['strip_spaces']
        else:
            assert isinstance(strip_spaces, bool), "`strip_spaces` must be a boolean value"

        # for string input
        if isinstance(string, str):
            result = self._segment(string, strip_spaces)
        # for list input
        else:
            assert isinstance(string, list)
            result = [self._segment(t, strip_spaces) for t in string]
        return result

    def _segment(self, original_string: str, strip_spaces: bool) -> List[str]:
        '''This method deals with a single string'''
        # initially segment by line feeds
        strings = split_keep_multiple_separators(original_string, ['\n'])

        # list of original characters per string
        chars_strings = []
        # list of character n-gram features per string
        features_strings = []
        # list of tuples(matched_spaces, start_ind, end_ind) per string
        multiple_spaces_positions_strings = []

        for string in strings:
            # keep the original characters per string
            chars_strings.append([c for c in string])
            if self.config['handle_multiple_spaces']:
                # replace multiple spaces with a single space for better segmentation by CRF model
                preprocessed_string, multiple_spaces_positions = SentSplit._substitute_multiple_spaces(string)
                multiple_spaces_positions_strings.append(multiple_spaces_positions)
                # convert the string into character n-gram features
                features_strings.append(_sample_to_features([c for c in preprocessed_string], self.config['ngram']))
            else:
                # convert the string into character n-gram features
                features_strings.append(_sample_to_features([c for c in string], self.config['ngram']))

        # tag strings
        y_tags_strings = [self.tagger.tag(f_s) for f_s in features_strings]

        if self.config['handle_multiple_spaces']:
            # adjust y_tags_strings to account for the removed multiple spaces
            y_tags_strings = SentSplit._adjust_tags_for_multiple_spaces(y_tags_strings, multiple_spaces_positions_strings)

        y_tags_strings = SentSplit._tag_segment_regexes(y_tags_strings, strings, self.config['segment_regexes'])
        y_tags_strings = SentSplit._tag_prevent_regexes(y_tags_strings, strings, self.config['prevent_regexes'],
                                                        self.config['maxcut'], self.config['prevent_word_split'])
        results = SentSplit._segment_by_char_tag(chars_strings, y_tags_strings, strip_spaces, self.config['maxcut'], self.config['mincut'])
        return results

    @staticmethod
    def _substitute_multiple_spaces(line: str) -> Tuple[str, List[Tuple[int, int]]]:
        '''
        Substitute multiple spaces with a single space and record their indices so that they can be restored later
        multiple_spaces_positions: [(start_ind, end_ind), ..]
        '''
        rgx_multiple_spaces = r'(\s{2,})'
        multiple_spaces_positions = [(m.start(0), m.end(0)) for m in re.finditer(rgx_multiple_spaces, line)]
        if len(multiple_spaces_positions) > 0:
            line = re.sub(rgx_multiple_spaces, ' ', line)
        return line, multiple_spaces_positions

    @staticmethod
    def _adjust_tags_for_multiple_spaces(y_tags_strings: List[List[str]],
                                         multiple_spaces_positions_strings: List[List[Tuple[int, int]]]) -> List[List[str]]:
        '''
        So far y_tags_strings contains labels (tags) for the multiple-space-substituted strings
        This method adds back (`len_matched_spaces` - 1) 'O' tags after the substituted single space to restore original strings
        Note that `start_char_ind` and `end_char_ind` are character-level indices of the original strings
        Example:
            Input:
                (original) string: 'It is good.   Ha'
                preprocessed_string: 'It is good. Ha'  (after _substitute_multiple_spaces)
                y_tags_string: ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'EOS', 'O', 'O','O']
            Returns:
                (Restores the three spaces after '~ good.'
                y_tags_string: ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'EOS', 'O', 'O', 'O', 'O','O']
        '''
        assert len(y_tags_strings) == len(multiple_spaces_positions_strings)
        for string_index, multiple_spaces_positions in enumerate(multiple_spaces_positions_strings):
            y_tags = y_tags_strings[string_index]
            for start_char_ind, end_char_ind in multiple_spaces_positions:
                len_matched_spaces = end_char_ind - start_char_ind
                # y_tags already contains an 'O' for one space, hence subtract 1
                o_tags_for_matched_spaces = ['O'] * (len_matched_spaces - 1)
                # insert 'O's after the index of the substituted single space
                y_tags = y_tags[:start_char_ind + 1] + o_tags_for_matched_spaces + y_tags[start_char_ind + 1:]
            y_tags_strings[string_index] = y_tags
        return y_tags_strings

    @staticmethod
    def _tag_segment_regexes(y_tags_strings: List[List[str]], strings: List[str], segment_regexes: List[Dict]) -> List[List[str]]:
        '''
        Label either the start or end indices of the matched regex patterns with 'EOS'
        @param segment_regexes: [{'regex': '<pattern>', 'at': <'end' or 'start'>}, ..]
        '''
        for string_index, string in enumerate(strings):
            assert len(string) == len(y_tags_strings[string_index])
            for rgx in segment_regexes:
                for matched_position in re.finditer(rgx['regex'], string):
                    start = matched_position.start(0)
                    end = matched_position.end(0) - 1
                    if rgx['at'] == 'start':
                        y_tags_strings[string_index][start] = 'EOS'
                    else:
                        y_tags_strings[string_index][end] = 'EOS'
        return y_tags_strings

    @staticmethod
    def _tag_prevent_regexes(y_tags_strings: List[List[str]], strings: List[str], prevent_regexes: List[Dict],
                             maxcut: int, prevent_word_split: bool) -> List[List[str]]:
        '''
        Remove 'EOS' label for characters that are matched by prevent_regexes
        and prevent these characters from being cut due to maxcut
        @param prevent_regexes: [{'regex': '<pattern>'}, ..]
        '''
        def _tag_prevent_word_split(y_tags: List[str], curr_string: str) -> List[str]:
            '''Prevent segmentation occurring in the middle of a word'''
            assert isinstance(curr_string, str)
            for i, tag in enumerate(y_tags[:-1]):
                if tag != 'EOS':
                    continue
                char = curr_string[i]
                if char not in _PUNCTUATIONS and not char.isspace() and not curr_string[i + 1].isspace():
                    y_tags[i] = 'O'
            return y_tags

        def _get_last_segmented_index(labels: List[str], pivot: int) -> int:
            '''Return the closest previously cut index to pivot'''
            if pivot < 1:
                return -1
            for index in range(pivot - 1, -1, -1):
                if labels[index] == 'EOS':
                    return index
            return -1

        for string_index, string in enumerate(strings):
            assert len(string) == len(y_tags_strings[string_index])
            y_tags_string = y_tags_strings[string_index]
            if prevent_word_split:
                y_tags_string = _tag_prevent_word_split(y_tags_string, string)
            for rgx in prevent_regexes:
                for matched_position in re.finditer(rgx['regex'], string):
                    start = matched_position.start(0)
                    end = matched_position.end(0) - 1
                    # add 'O' at matched positions
                    for pos in range(start, end + 1):
                        y_tags_string[pos] = 'O'

                    # make sure this pattern is not maxcut later by segmenting before the pattern
                    if end < maxcut:
                        # no need to check if the pattern falls within the maxcut
                        continue
                    last_segmented_index = _get_last_segmented_index(y_tags_string, start)
                    last_segmented_plus_one = last_segmented_index + 1
                    length_to_cover = end - last_segmented_plus_one + 1  # inclusive
                    num_cuts = math.floor(length_to_cover / maxcut)
                    if num_cuts < 1:
                        num_cuts = 1
                    maxcutted_length = num_cuts * maxcut - 1
                    next_maxcut_pos = last_segmented_plus_one + maxcutted_length
                    # cut before the pattern if the next_maxcut_pos falls within the pattern
                    if start <= next_maxcut_pos < end and start - 1 > 0:
                        y_tags_string[start - 1] = 'EOS'

            y_tags_strings[string_index] = y_tags_string
        return y_tags_strings

    @staticmethod
    def _segment_by_char_tag(chars_strings: List[List[str]], y_tags_strings: List[List[str]], strip_spaces: bool, maxcut: int, mincut: int) -> List[str]:
        '''
        Loop through character-level tags and segment when 'EOS' and other conditions are met
        :param chars_strings: list of lines where each line consists of characters
        :param y_tags_strings: list of lines where each line consists of tags which are either 'O' or 'EOS'
        '''
        def _check_and_add_sentence(sent: str, str_len: int, cur_ind: int, is_leftover: bool = False) -> bool:
            '''
            Check if the given `sent` can be added to `results`.
            If so, add to `results` and return `True`; otherwise, return `False`
            '''
            if len(sent) <= mincut:
                if not is_leftover:
                    return False
                # if it is a leftover, but also an empty string, then don't add
                elif len(sent) <= 0:
                    return False
            if strip_spaces:
                sent = sent.strip()
            if len(sent) <= 0:
                return False
            # if the no. of remaining characters are less than mincut, don't add
            if not is_leftover and (str_len - cur_ind) <= mincut:
                return False
            results.append(sent)
            return True

        def _segment_maxcut_string(sent: str) -> str:
            '''
            Heuristically segment a maxcut string into two, add the first half to `results`, and return the remaining half.
            A list of heuristic regexes are applied to `sent` in decreasing order of importance.
            As soon as a matching is found, the sentence is segmented.
            '''
            rgx_punctuation_and_closing = r'(?<=[\.。︀?？!！…])[\'"’”❜❞›»❯」』)）\]］】〟]'
            rgx_closing_and_punctuation = r'(?<=[\'"’”❜❞›»❯」』)）\]］】〟])[\.。︀?？!！…]'
            rgx_space_and_dash = r'(?<=\s)\p{Pd}'
            rgx_colon = r'[:﹕：;﹔；؛⁏]'
            rgx_not_space_and_closing_and_space = r'(?<=[^\s])[\'"’”❜❞›»❯」』)）\]］】〟](?=\s)'
            rgx_comma = r'[,，﹐]'
            rgx_closing = r'[’”❜❞›»❯」』)）\]］】〟]'
            rgx_whitespace = r'\s'
            heuristics = [rgx_punctuation_and_closing, rgx_closing_and_punctuation, rgx_space_and_dash,
                          rgx_colon, rgx_not_space_and_closing_and_space, rgx_comma, rgx_closing, rgx_whitespace]
            for heu in heuristics:
                for match in re.finditer(heu, sent):
                    assert match.end() - match.start() == 1
                    first_half = sent[:match.end()]
                    if _check_and_add_sentence(first_half, len(sent), len(first_half)):
                        return sent[match.end():]
            if _check_and_add_sentence(sent, is_leftover=True):
                return ''
            raise RuntimeError(f"Cannot segment maxcut string: {sent}")

        results = []
        for char_string, tags in zip(chars_strings, y_tags_strings):
            sentence = ''
            string_length = len(char_string)
            for current_index, (current_character, tag) in enumerate(zip(char_string, tags)):
                if len(sentence) >= maxcut:
                    sentence = _segment_maxcut_string(sentence)
                if tag == 'EOS':
                    sentence += current_character
                    if _check_and_add_sentence(sentence, string_length, current_index):
                        sentence = ''
                else:
                    sentence += current_character
            if _check_and_add_sentence(sentence, string_length, current_index, is_leftover=True):
                sentence = ''
        return results

    def close(self):
        if self.tagger is not None:
            return self.tagger.close()
