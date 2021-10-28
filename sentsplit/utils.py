from functools import reduce
from typing import List

import regex as re


def read_lines(file_path: str) -> List[str]:
    lines = []
    with open(file_path, 'r') as inf:
        for line in inf:
            lines.append(line.rstrip('\n'))
    return lines


def write_lines(lines: List[str], file_path: str) -> None:
    with open(file_path, 'w') as outf:
        for line in lines:
            outf.write(f'{line}\n')


def split_keep_multiple_separators(string: str, separators: List[str]) -> List[str]:
    '''
    Split `string` on separator(s) but also keep the separator(s)
    Modified from `http://programmaticallyspeaking.com/split-on-separator-but-keep-the-separator-in-python.html`
    to extend to multiple separators.
    '''
    rgx_multiple_separators = '|'.join([re.escape(sep) for sep in separators])
    rgx_multiple_separators = '(' + rgx_multiple_separators + ')'
    return reduce(lambda acc, elem: acc[:-1] + [acc[-1] + elem] if (elem in separators) else acc + [elem], re.split(rgx_multiple_separators, string), [])
