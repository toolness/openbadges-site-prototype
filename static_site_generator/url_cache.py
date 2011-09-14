import urllib2
import logging

class UrlCache(object):
    def __init__(self, storage):
        self.urls = storage

    def refresh(self, url, stdout):
        req = urllib2.Request(url)
        if url in self.urls and 'lastmod' in self.urls[url]:
            req.add_header('If-Modified-Since', self.urls[url]['lastmod'])
        try:
            stdout.write('fetching %s.\n' % url)
            response = urllib2.urlopen(req)
            info = {'data': response.read().decode('utf-8')}
            if 'Last-Modified' in response.info():
                info['lastmod'] = response.info()['Last-Modified']
            self.urls[url] = info
        except urllib2.HTTPError, e:
            if e.code == 304:
                logging.debug('url not modified: %s\n' % url)
            else:
                raise
