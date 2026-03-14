from __future__ import annotations

import regex as re


def read_lines(file_path: str) -> list[str]:
    lines = []
    with open(file_path) as inf:
        for line in inf:
            lines.append(line.rstrip("\n"))
    return lines


def write_lines(lines: list[str], file_path: str) -> None:
    with open(file_path, "w") as outf:
        for line in lines:
            outf.write(f"{line}\n")


def split_keep_multiple_separators(string: str, separators: list[str]) -> list[str]:
    """
    Split `string` on separator(s) but also keep the separator(s)
    Modified from `http://programmaticallyspeaking.com/split-on-separator-but-keep-the-separator-in-python.html`
    to extend to multiple separators.
    """
    rgx_multiple_separators = "(" + "|".join([re.escape(sep) for sep in separators]) + ")"

    parts = re.split(rgx_multiple_separators, string)
    sentences = [parts[0]]

    for part in parts[1:]:
        if part in separators:
            sentences[-1] += part
            continue
        sentences.append(part)

    return sentences
