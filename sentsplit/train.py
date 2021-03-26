import random
from typing import List, Tuple

import pycrfsuite
from loguru import logger
from tqdm import tqdm

from .utils import read_lines

_PUNCTUATIONS = {'.', '?', '!', '\"', '\'', '”', '．', '？', '！', '。'}


def train_crf_model(corpus_path: str, ngram: int, output_path: str, sample_min_length: int,
                    crf_max_iteration: int, add_depunctuated_samples: bool, add_despaced_samples: bool) -> None:
    train_samples = _preprocess(corpus_path, sample_min_length, add_depunctuated_samples, add_despaced_samples)
    X_train, y_train = _create_features(train_samples, ngram)
    _fit_model(X_train, y_train, output_path, crf_max_iteration)


def _preprocess(corpus_path: str, sample_min_length: int, add_depunctuated_samples: bool, add_despaced_samples: bool) -> List[List[Tuple[str, str]]]:
    logger.info("Preprocessing sentences..")

    raw_lines = read_lines(corpus_path)
    random.shuffle(raw_lines)

    depunctuated_prob = 0.30 if add_depunctuated_samples else 0.0
    depunctuated_tosses = random.choices([True, False], [depunctuated_prob, 1 - depunctuated_prob], k=len(raw_lines))

    despaced_prob = 0.35 if add_despaced_samples else 0.0
    despaced_tosses = random.choices([True, False], [despaced_prob, 1 - despaced_prob], k=len(raw_lines))

    train_samples = []
    single_sample = []
    for i, line in enumerate(tqdm(raw_lines)):
        chars = [c for c in line.strip()]
        labels = ['O' for c in chars[:-1]] + ['EOS']
        char_and_labels = [(char, label) for char, label in zip(chars, labels)]

        if len(single_sample) < 1:
            single_sample = char_and_labels
        else:
            if depunctuated_tosses[i] and single_sample[-1][0] in _PUNCTUATIONS:
                single_sample = single_sample[:-1]
                new_eos = (single_sample[-1][0], 'EOS')
                single_sample[-1] = new_eos
            if despaced_tosses[i] and single_sample[-1][0] in _PUNCTUATIONS:
                single_sample += char_and_labels
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
