#!/usr/bin/env python3
from urllib.request import urlopen
import re
from urllib.parse import quote, unquote
from urllib.error import URLError, HTTPError


def get_content(name):
    try:
        with urlopen('http://ru.wikipedia.org/wiki/' + quote(name)) as page:
            file = page.read().decode('utf-8', errors='ignore')
    except (URLError, HTTPError):
        return None
    return file


def extract_content(page):
    if page is None:
        return 0, 0
    start_file = re.search(r'<div id="mw-content-text"', page).start()
    finish_file = re.search(r'<div id="mw-navigation">', page).start()
    return start_file, finish_file - 1


def extract_links(page, begin, end):
    regular_expression = re.compile(r'["\']/wiki/([\w%]+?)["\']', re.IGNORECASE)
    refs = re.finditer(regular_expression, page[begin:end])
    output = []
    for ref in refs:
        if not ref.group(1) in output:
            output.append(unquote(ref.group(1)))
    return output


def find_chain(start, finish):
    title = start
    transitions = []
    if start == finish:
        return [start]
    while finish not in transitions:
        page = get_content(title)
        if page is None:
            return None
        else:
            transitions.append(title)
        begin, end = extract_content(page)
        refs = extract_links(page, begin, end)
        if finish in refs:
            transitions.append(finish)
            return transitions
        else:
            for ref in refs:
                if ref in transitions:
                    continue
                else:
                    title = ref
                    break


if __name__ == '__main__':
    pass
