#!/usr/bin/env python3

import argparse
import queue
import os
import pathlib
import re
import signal
import sys
import threading
import urllib.request
from typing import Optional
from urllib.error import URLError, HTTPError

IMAGE_LOADER = '/img/image-loader.svg'


class ProducersManager:
    class _ConsumersManager:
        def __init__(self, task_queue: queue.Queue, producer_end, term):
            self._queue = task_queue
            self._producer_ended = producer_end
            self._term_sign = term

        def getTask(self, block=True, timeout=None):
            return self._queue.get(block, timeout)

        def task_done(self):
            self._queue.task_done()

        def is_producer_finished(self):
            return self._producer_ended.is_set()

        def is_terminate(self):
            return self._term_sign.is_set()

    def __init__(self):
        self._queue = queue.Queue()
        self._producer_ended = threading.Event()
        self._term_sign = threading.Event()

    def get_consumers_manager(self):
        return self._ConsumersManager(self._queue,
                                      self._producer_ended,
                                      self._term_sign)

    def put(self, item):
        if self._producer_ended.is_set():
            return
        self._queue.put(item)

    def produce_ended(self):
        self._producer_ended.set()

    def shutdown_signal(self):
        self._term_sign.set()
        # print('SETTED')
        self._producer_ended.set()
        try:
            while True:
                self._queue.get_nowait()
                self._queue.task_done()
        except queue.Empty:
            pass
        # print('SIGNAL')

    def is_terminate(self):
        return self._term_sign.is_set()

    def wait_job_ending(self):
        self._queue.join()


class HabrArticlesPictureLoader(threading.Thread):
    _datasrc_from_article_pattern = re.compile(
        r'<img(?: +[^ \'">/=]+ *= *(?:[^"\'][^ ]+|(?P<q>["\'])'
        r'(?(q)[^"]|[^\'])*(?P=q)))* data-src *= *(?P<q2>["\'])'
        r'(?P<src>(?(q2)[^"]|[^\'])*)(?P=q2)(?: +[^ \'">/=]+ *= *'
        r'(?:[^"\'][^ ]+|(?P<q3>["\'])(?(q3)[^"]|[^\'])*(?P=q3)))*/?>')

    _img_pattern = re.compile(
        r'<img(?: +[^ \'">/=]+ *= *(?:[^"\' ][^ ]+|"[^"]*"|\'[^\']*\'))+ */?>')
    _avatar_pattern = re.compile(
        r'class *= *(?P<q>["\'])tm-entity-image__pic(?P=q)'
    )  # по хорошему надо еще и без кавычек обрабатывать
    _datasrc_pattern = re.compile(
        r' data-src *= *(?P<q>(?P<dq>")|\')(?P<src>(?(dq)[^"]*|[^\']*))(?P=q)'
    )
    _src_pattern = re.compile(
        r' src *= *(?P<q>(?P<dq>")|\')(?P<src>(?(dq)[^"]*|[^\']*))(?P=q)'
    )

    def __init__(self, manager: ProducersManager._ConsumersManager,
                 out_dir: pathlib.Path):
        super().__init__()
        self._manager = manager
        self._out = out_dir

    def run(self) -> None:
        while True:
            try:
                if self._manager.is_terminate():
                    break
                task = self._manager.getTask(True, 1)
                try:
                    if task is not None:
                        self.work(task)
                finally:
                    self._manager.task_done()
            except queue.Empty:
                if self._manager.is_producer_finished():
                    break
                else:
                    continue

    def get_article_title(self, article: str):
        title_h1 = article.index('tm-article-snippet__title_h1')
        return article[article.index('<span>', title_h1) + 6:
                       article.index('</span>', title_h1)]

    def work(self, url):
        article = self.get_article(url)
        if article is None:
            return
        title = self.get_article_title(article)
        # print(threading.currentThread().getName(), url, title)
        article_dir = (self._out / make_valid(title))
        # print(threading.currentThread().getName(),
        #       'Create dir with name:', article_dir)
        try:
            article_dir.mkdir(parents=True, exist_ok=True)
        except Exception as err:
            # print('Can\'t crete dir', err)
            return
        for picture_uri in map(_fill_url,
                               self.picture_links_iter(article)):
            self.load_picture_to_fs(article_dir, picture_uri)
        try:
            article_dir.rmdir()
        except:
            pass
        # print(threading.currentThread().getName(), 'Job finished',)

    def load_picture_to_fs(self, directory, picture_uri: str):
        picture = load_content(picture_uri)
        if picture is None:
            return
        filename = make_valid(picture_uri[picture_uri.rindex('/') + 1:])
        # print(threading.currentThread().getName(),
        #       picture_uri, len(picture), filename)
        with (directory / filename).open(mode='wb') as fd:
            fd.write(picture)

    def get_article(self, url):
        page_bytes = load_content(url)
        # print(threading.currentThread().getName(), url)
        if page_bytes is None:
            # print(self.name, url, 'page_bytes is None')
            return None
        return extract_article(page_bytes.decode(encoding='utf8'))[0]

    def picture_links_iter(self, article):
        for img in self._img_pattern.finditer(article):
            img_node = img.group()
            if self._avatar_pattern.search(img_node):  # re pattern, WOC
                continue
            datasrc = self._datasrc_pattern.search(img_node)
            if datasrc and (len(datasrc.group('src')) > 0):
                yield datasrc.group('src')
            else:
                src = self._src_pattern.search(img_node)
                if src:
                    if len(src.group('src')) > 0:
                        yield src.group('src')
                else:
                    # print('Node without src:', img_node)
                    pass


def _path_repl(match: re.Match):
    if match.group() in ':?!':
        return '.'
    elif match.group() == '"':
        return '\''
    elif match.group() == '*':
        return 'x'
    elif match.group() == '>':
        return 'g'
    elif match.group() == '<':
        return 'l'
    else:  # /\|
        return ''


_validate_pattern = re.compile(r"[:?!\"*<>+/\\|]")


def make_valid(path: str):
    return _validate_pattern.sub('', path)


def load_content(url: str) -> Optional[bytes]:
    try:
        return urllib.request.urlopen(url, timeout=10).read()
    except (HTTPError, URLError):
        return None


def _fill_url(parted_url: str):
    if parted_url is None:
        return None
    if parted_url.startswith('/'):
        return 'https://habr.com' + parted_url
    return parted_url


def extract_article(html: str, offset=0) -> (str, int):
    if type(html) is not str:
        raise TypeError(f'html must be a string, but its {type(html)}')
    if type(offset) is not int:
        raise TypeError('offset must be a int')
    try:
        article_start = html.index('<article ', offset)
        article_end = html.index('</article>', article_start + 9)
    except ValueError:
        return None, 0
    return html[article_start: article_end + 10], article_start


tag_pattern = re.compile(
    r'<a(?: [^ \'">/=]+ *= *(?:"[^"]*"|\'[^\']*\'|[^"\'][^ ]*))* class *'
    r'= *(?:(?P<q>["\'])(?:(?:[\w\-]+ )*tm-article-snippet__title-link'
    r'(?: [\w-]+)*|(?:[\w-]+ )*tm-megapost-snippet__card(?: [\w-]+)*)'
    r'(?P=q))(?: [^ \'">/=]+ *= *(?:"[^"]*"|\'[^\']*\'|[^"\'][^ ]*))*>'
)
href_pattern = re.compile(r'href=(?P<q>["\'])((?(q)[^"]|[^\'])*)(?P=q)')


def get_article_reference(article_html: str):
    href_tag = tag_pattern.search(article_html)
    if href_tag:
        return href_pattern.search(href_tag.group()).group(2)
    # with open('mybrokenart.html', mode='w', encoding='utf8') as fd:
    #    fd.write(article_html)
    return None


def article_generator(articles):
    source_pattern = 'https://habr.com/ru/all/page{}/'
    page_number = 1
    main_html = ''
    article, offset = None, 0
    for _ in range(articles):
        while article is None:
            html_bytes = load_content(source_pattern.format(page_number))
            if html_bytes is None:
                raise HTTPError('Can\' load page.')
            main_html = html_bytes.decode(encoding='utf8')
            page_number += 1
            article, offset = extract_article(main_html, 0)
        yield article
        article, offset = extract_article(main_html, offset + 1)


def produce_articles(manager: ProducersManager, articles: int):
    try:
        for article in article_generator(articles):
            manager.put(_fill_url(get_article_reference(article)))
    finally:
        manager.produce_ended()
        # print('Producer finished')


def run_scraper(threads: int, articles: int, out_dir: pathlib.Path) -> None:
    manager = ProducersManager()
    set_signal_handlers(lambda sig, frame: manager.shutdown_signal())
    consumer = manager.get_consumers_manager()
    for _ in range(threads - 1):
        HabrArticlesPictureLoader(consumer, out_dir).start()
    produce_articles(manager, articles)
    HabrArticlesPictureLoader(consumer, out_dir).run()
    manager.wait_job_ending()


def set_signal_handlers(action):
    signal.signal(signal.SIGINT, action)
    signal.signal(signal.SIGBREAK, action)
    signal.signal(signal.SIGTERM, action)


def main():
    script_name = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(
        usage=f'{script_name} [ARTICLES_NUMBER] THREAD_NUMBER OUT_DIRECTORY',
        description='Habr parser',
    )
    parser.add_argument(
        '-n', type=int, default=25, help='Number of articles to be processed',
    )
    parser.add_argument(
        'threads', type=int, help='Number of threads to be run',
    )
    parser.add_argument(
        'out_dir', type=pathlib.Path, help='Directory to download habr images',
    )
    args = parser.parse_args()

    run_scraper(args.threads, args.n, args.out_dir)


if __name__ == '__main__':
    main()
