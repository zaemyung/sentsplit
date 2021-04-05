import os
import pprint
import subprocess
import sys
from argparse import Namespace
from copy import deepcopy
from datetime import datetime
from multiprocessing import Pool
from typing import List

from loguru import logger
from tqdm import tqdm

from sentsplit import config
from sentsplit.segment import SentSplit
from sentsplit.train import train_crf_model
from sentsplit.utils import write_lines


def sentsplit_train(args: Namespace) -> None:
    lang = args.lang
    corpus_path = args.corpus
    ngram = args.ngram
    output_path = args.output
    sample_min_length = args.sample_min_length
    crf_max_iteration = args.crf_max_iteration
    depunctuation_ratio = args.depunctuation_ratio
    num_depunctuation_endings = args.num_depunctuation_endings
    ending_length = args.ending_length
    despace_ratio = args.despace_ratio

    args_string = pprint.pformat(vars(args), indent=2)
    logger.info(f"Training a new CRF model:\n{args_string}")

    if output_path is None:
        corpus_basename = os.path.basename(corpus_path)
        today_str = datetime.today().strftime('%d%m%Y')
        output_path = f'./{corpus_basename}.{lang}-{ngram}-gram-{today_str}.model'

    train_crf_model(corpus_path, ngram, output_path, sample_min_length, crf_max_iteration, depunctuation_ratio, num_depunctuation_endings, ending_length, despace_ratio)


def call_sentsplit_batch(line: str) -> List[str]:
    return sentsplit.segment(line.rstrip('\n'))


def sentsplit_segment(args: Namespace) -> None:
    lang = args.lang
    input_file = args.input
    output_file = args.output
    assert os.path.isfile(input_file)
    if output_file is None:
        output_file = f'{input_file}.segment'

    override_options = vars(args)
    cores = override_options['cores']
    del override_options['cores']
    try:
        default_config = deepcopy(getattr(config, '{}_config'.format(lang)))
    except AttributeError:
        logger.critical(f"Unsupported language: {lang.upper()}")
        sys.exit(1)

    for k, v in default_config.items():
        if override_options[k] is not None:
            default_config[k] = override_options[k]

    global sentsplit
    sentsplit = SentSplit(lang, **default_config)

    num_lines = int(subprocess.check_output(['wc', '-l', input_file]).decode('utf8').split()[0])
    with open(input_file, 'r') as inf, open(output_file, 'w') as outf:
        cnt = 0
        if cores <= 1:
            for line in tqdm(inf, total=num_lines):
                line = line.rstrip('\n')
                segments = sentsplit.segment(line)
                for segment in segments:
                    outf.write(f"{segment}\n")
                cnt += len(segments)
        else:
            with Pool(processes=cores) as p:
                pooled_results = list(tqdm(p.imap(call_sentsplit_batch, inf, chunksize=700), total=num_lines))
            sentences = [item for sublist in pooled_results for item in sublist]
            cnt = len(sentences)
            write_lines(sentences, output_file)

        logger.info(f"{num_lines} lines are segmented into {cnt} sentences, and saved at {output_file}")
    sentsplit.close()
