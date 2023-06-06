from typing_extensions import TypedDict


class Regex(TypedDict, total=False):
    name: str
    regex: str
    at: str


"""
`segment_regexes`: make sure a string is segmented at either the start or end of the matching group(s)
"""
newline = Regex(name="newline", regex=r"\n", at="end")
ellipsis = Regex(name="ellipsis", regex=r"…(?![\!\?\.．？！])", at="end")
after_semicolon = Regex(name="after_semicolon", regex=r" *;", at="end")


"""
`prevent_regexes`: make sure a string is not segmented at characters that fall within the matching group(s)
"""
liberal_url = Regex(
    name="liberal_url",
    # ref. https://gist.github.com/gruber/249502#gistcomment-1328838
    regex=r'\b((?:[a-z][\w\-]+:(?:\/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]|\((?:[^\s()<>]|(?:\([^\s()<>]+\)))*\))+(?:\((?:[^\s()<>]|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
)
period_followed_by_lowercase = Regex(name="period_followed_by_lowercase", regex=r"\.(?= *[a-z])")
