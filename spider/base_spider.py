#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import httplib
import zlib
import time

from gevent import monkey, queue
import gevent
from urlparse import urlsplit, urljoin
from bs4 import BeautifulSoup
import logging

#from common.orm.models import Page, session_scope

monkey.patch_all()

logger = logging


class BaseSpider(object):
    def __init__(self, start_url, hosts):
        '''
        :param start_url:
            从start_url开始爬
        :param hosts:
            包含一个或多个域名或ip的元组或列表；.e.g:('www.pythondoc.com', 'pythondoc.com')
        '''
        self.urls_found = set([start_url])
        self.urls_queue = queue.Queue(items=[start_url])
        self.hosts = hosts
        self.opener = urllib2.build_opener()
        self.coding = None
        self.crawling_count = 0


    def _set_header(self, host):
        self.opener.addheaders=[
            ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('Accept-Language', 'zh-CN,zh;q=0.8'),
            ('Accept-Encoding', 'gzip'),
            ('Referer', 'https://www.51job.com/s?'),
            ('Host', host),
        ]

    def crawl(self):
        while True:
            try:
                url = self.urls_queue.get(timeout=1)
            except queue.Empty:
                if self.crawling_count == 0:
                    # 取不到url，且当前没有协程正在抓取网页，就不会再有的了
                    return
            else:
                logger.debug("crawling %s" % url)
                start_time = time.time()

                self.begin_crawl_page(url)

                self.crawling_count += 1
                try:
                    html = self._get_page(url)
                    if html:
                        soup = BeautifulSoup(html, "html.parser", from_encoding=self.coding)
                        self.coding = soup.original_encoding
                        for u in self._get_urls(soup, url):
                            self.urls_queue.put(u)
                finally:
                    self.crawling_count -= 1

                self.finish_crawl_page(url, html)

                logger.debug("time expense %f" % (time.time() - start_time))


    def _get_page(self, url):
        t = time.time()
        self._set_header(urlsplit(url).netloc)
        try:
            response = self.opener.open(url)
        except urllib2.HTTPError as e:
            if e.code == 404:
                logger.debug(e)
            elif e.code == 403:
                logger.warning(e)
        except urllib2.URLError as e:
            pass
            # logger.exception(e)
        except UnicodeEncodeError as e:
            # logger.error(u"跳过中文url %s" % url)
            pass
        except httplib.BadStatusLine:
            pass
        else:
            logger.debug('%d %.2fs' % (response.getcode(),time.time()-t))

            html = response.read()
            encoding = response.headers.get('Content-Encoding')
            if encoding == 'gzip':
                try:
                    html = zlib.decompress(html, 16+zlib.MAX_WBITS)
                except Exception as e:
                    raise e
            return html

    def _get_urls(self, soup, page_url):
        page_url_split = urlsplit(page_url)

        keyword_list = ["apk","exe","dmg","rar","zip","7z"]
        html_tags_and_linkattri =[("a","href"),("script", "src"),("link","href")]

        for tag, linkattri in html_tags_and_linkattri:
            for a in soup.find_all(tag, **{linkattri:True}):
                url_ = urljoin(page_url, a[linkattri], allow_fragments=False)
                if '#' in url_:
                    url_ = url_.split('#', 1)[0]
                if url_ in self.urls_found:
                    continue
                url_split = urlsplit(url_)
                if url_split.scheme not in ('http', 'https',):
                    continue
                if url_split.netloc not in self.hosts:
                    continue
                if '.' in url_split.path and url_split.path.rsplit('.', 1)[-1].lower() in keyword_list:
                    # 如果是下载文件连接
                    continue

                self.urls_found.add(url_)
                yield url_

    def begin_crawl_page(self, url):
        pass

    def finish_crawl_page(self, url, html):
        pass



if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    spider = BaseSpider('http://www.51job.com', ['www.51job.com'])
    gevent.joinall([
        gevent.spawn(spider.crawl),
        gevent.spawn(spider.crawl),
        gevent.spawn(spider.crawl),
    ])
