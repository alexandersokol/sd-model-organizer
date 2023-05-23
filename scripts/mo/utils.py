import re


def is_blank(s):
    return len(s.strip()) == 0


def is_valid_url(url: str) -> bool:
    pattern = re.compile(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    return bool(pattern.match(url))


def is_valid_filename(filename: str) -> bool:
    pattern = re.compile(r'^[^\x00-\x1f\\/?*:|"<>]+$')
    return bool(pattern.match(filename))
