import os
import pprint
import subprocess
import sys
from argparse import Namespace
from copy import deepcopy
from datetime import datetime

from loguru import logger
from tqdm import tqdm

from sentsplit import config
from sentsplit.segment import SentSplit
from sentsplit.train import train_crf_model


def sentsplit_train(args: Namespace) -> None:
    lang = args.lang
    corpus_path = args.corpus
    ngram = args.ngram
    output_path = args.output
    sample_min_length = args.sample_min_length
    crf_max_iteration = args.crf_max_iteration
    add_depunctuated_samples = args.add_depunctuated_samples
    add_despaced_samples = args.add_despaced_samples

    args_string = pprint.pformat(vars(args), indent=2)
    logger.info(f"Training a new CRF model:\n{args_string}")

    if output_path is None:
        corpus_basename = os.path.basename(corpus_path)
        today_str = datetime.today().strftime('%Y%m%d')
        output_path = f'./{corpus_basename}.{lang}-{ngram}-gram-{today_str}.model'

    train_crf_model(corpus_path, ngram, output_path, sample_min_length, crf_max_iteration, add_depunctuated_samples, add_despaced_samples)


def sentsplit_segment(args: Namespace) -> None:
    lang = args.lang
    input_file = args.input
    output_file = args.output
    assert os.path.isfile(input_file)
    if output_file is None:
        output_file = f'{input_file}.segment'

    override_options = vars(args)
    try:
        default_config = deepcopy(getattr(config, '{}_config'.format(lang)))
    except AttributeError:
        logger.critical(f"Unsupported language: {lang.upper()}")
        sys.exit(1)

    for k, v in default_config.items():
        if override_options[k] is not None:
            default_config[k] = override_options[k]

    sentsplit = SentSplit(lang, **default_config)

    num_lines = int(subprocess.check_output(['wc', '-l', input_file]).decode('utf8').split()[0])
    with open(input_file, 'r') as inf, open(output_file, 'w') as outf:
        cnt = 0
        for line in tqdm(inf, total=num_lines):
            line = line.rstrip('\n')
            segments = sentsplit.segment(line)
            for segment in segments:
                outf.write(f"{segment}\n")
            cnt += len(segments)

        logger.info(f"{num_lines} lines are segmented into {cnt} sentences, and saved at {output_file}")
    sentsplit.close()
