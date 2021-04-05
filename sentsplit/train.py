import random
from collections import Counter
from typing import List, Set, Tuple

import pycrfsuite
from loguru import logger
from tqdm import tqdm

from .utils import read_lines

_PUNCTUATIONS = {'.', '?', '!', '\"', '\'', '”', '．', '？', '！', '。', '…'}


def train_crf_model(corpus_path: str, ngram: int, output_path: str, sample_min_length: int, crf_max_iteration: int,
                    depunctuation_ratio: float, num_depunctuation_endings: int, ending_length: int, despace_ratio: float) -> None:
    train_samples = _preprocess(corpus_path, sample_min_length, depunctuation_ratio, num_depunctuation_endings, ending_length, despace_ratio)
    X_train, y_train = _create_features(train_samples, ngram)
    _fit_model(X_train, y_train, output_path, crf_max_iteration)


def _compute_top_k_depunctuated_endings(lines: List[str], num_depunctuation_endings: int, ending_length: int) -> Set[str]:
    """
    Computes the most common endings of sentences.
    Applicable only to languages that utilize specific endings
    that can indicate the end of sentence even without the punctuations.
    """
    assert ending_length > 0 and num_depunctuation_endings > 0
    all_endings = []
    for line in lines:
        line = line.strip()
        if len(line) - 1 < ending_length or line[-1] not in _PUNCTUATIONS:
            continue
        ending = line[-ending_length - 1:-1]
        all_endings.append(ending)
    ending_counter = Counter(all_endings)
    top_endings = ending_counter.most_common(num_depunctuation_endings)
    logger.info(f"Top-{num_depunctuation_endings} endings are: {top_endings}")
    return set(ending for ending, _ in top_endings)


def _preprocess(corpus_path: str, sample_min_length: int, depunctuation_ratio:float,
                num_depunctuation_endings: int, ending_length: int, despace_ratio: float) -> List[List[Tuple[str, str]]]:
    logger.info("Preprocessing sentences..")
    assert 0.0 <= depunctuation_ratio <= 1.0
    assert 0.0 <= despace_ratio <= 1.0

    raw_lines = read_lines(corpus_path)
    random.shuffle(raw_lines)

    num_depunctuation_remainings = int(len(raw_lines) * depunctuation_ratio)
    if depunctuation_ratio > 0.0:
        depunctuated_endings = _compute_top_k_depunctuated_endings(raw_lines, num_depunctuation_endings, ending_length)

    num_despace_remainings = int(len(raw_lines) * despace_ratio)

    train_samples = []
    single_sample = []
    for line in tqdm(raw_lines):
        chars = [c for c in line.strip()]
        labels = ['O' for _ in chars[:-1]] + ['EOS']
        # Ex. 'Hello!' -> [('H', 'O'), ('e', 'O'), ('l', 'O'), ('l', 'O'), ('o', 'O'), ('!', 'EOS')]
        char_and_labels = [(char, label) for char, label in zip(chars, labels)]

        if len(single_sample) < 1:
            single_sample = char_and_labels
        else:
            if num_depunctuation_remainings > 0 and single_sample[-1][0] in _PUNCTUATIONS and \
               len(single_sample) - 1 > ending_length and \
               ''.join(char for char, _ in single_sample[-ending_length - 1:-1]) in depunctuated_endings:
                single_sample = single_sample[:-1]
                new_eos = (single_sample[-1][0], 'EOS')
                single_sample[-1] = new_eos
                num_depunctuation_remainings -= 1
            if num_despace_remainings > 0 and single_sample[-1][0] in _PUNCTUATIONS:
                single_sample += char_and_labels
                num_despace_remainings -= 1
            else:
                single_sample += [(' ', 'O')] + char_and_labels

        if len(single_sample) >= sample_min_length:
            train_samples.append(single_sample)
            single_sample = []
    return train_samples


def _create_features(samples: List[List[Tuple[str, str]]], ngram: int) -> Tuple[List[List[List[str]]], List[List[str]]]:
    logger.info("Creating features..")
    X = []
    y = []
    for sample in tqdm(samples):
        X.append(_sample_to_features(sample, ngram))
        y.append(_sample_to_labels(sample))
    return X, y


def _sample_to_features(sample: List[Tuple[str, str]], ngram: int) -> List[List[str]]:
    def _char_to_features(i: int) -> List[str]:
        char = sample[i][0]
        feats = [
            'bias',
            f'char={char}',
            f'char.isdigit={char.isdigit()}',
            f'char.isupper={char.isupper()}',
        ]
        for j in range(1, min(i, ngram) + 1):
            char_j = sample[i - j][0]
            feats.append(f'-{j}:char={char_j}')
        for j in range(1, min(len(sample) - 1 - i, ngram) + 1):
            char_j = sample[i + j][0]
            feats.append(f'+{j}:char={char_j}')
        return feats

    features = []
    for i in range(len(sample)):
        features.append(_char_to_features(i))
    return features


def _sample_to_labels(sample: List[Tuple[str, str]]) -> List[str]:
    return [label for _, label in sample]


def _fit_model(X_train: List[List[List[str]]], y_train: List[List[str]], output_path: str, crf_max_iteration: int) -> None:
    logger.info("Fitting CRF model..")
    trainer = pycrfsuite.Trainer(verbose=True)
    for xseq, yseq in zip(X_train, y_train):
        trainer.append(xseq, yseq)
    trainer.set_params({
        'c1': 1.0,   # coefficient for L1 penalty
        'c2': 1e-3,  # coefficient for L2 penalty
        'epsilon': 1e-4,
        'max_iterations': crf_max_iteration,  # stop earlier
        # include transitions that are possible, but not observed
        'feature.possible_transitions': True
    })
    trainer.train(output_path)
    logger.info(f"Done! Model saved at {output_path}")
