import sys
import os
import re
import urlparse
import json
import shutil
from distutils.dir_util import mkpath

ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *x: os.path.join(ROOT, *x)

sys.path.append(path('vendor'))

import url_cache
import html5lib
from html5lib import treebuilders, treewalkers, serializer

class SiteMaker(object):
    def __init__(self, cache, storage, dist_dir, wiki_root, wiki_domain,
                 base_template):
        self.cache = cache
        self.storage = storage
        self.pages_built = []
        self.pages_to_build = set(['/'])
        self.wiki_root = wiki_root
        self.wiki_domain = wiki_domain
        self.wiki_root_re = re.compile(r'\/%s(\/.*)' % wiki_root)
        self.dist_dir = dist_dir
        self.base_template = base_template

    def make_site(self):
        while self.pages_to_build:
            pagename = self.pages_to_build.pop()
            self.pages_built.append(pagename)
            self.make_page(pagename)

    def write_page(self, name, contents):
        if not name.endswith('/'):
            name += '/'
        fullpath = os.path.join(self.dist_dir, '%sindex.html' % name[1:])
        mkpath(os.path.dirname(fullpath))
        f = open(fullpath, 'w')
        f.write(contents)
        f.close()

    def get_page(self, name):
        url = 'https://%s/index.php?title=%s%s&action=render' % (
            self.wiki_domain,
            self.wiki_root,
            name
            )
        self.cache.refresh(url, sys.stdout)
        return self.storage[url]['data']

    def make_page(self, page):
        p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
        dom_tree = p.parse(self.get_page(page))

        walker = treewalkers.getTreeWalker("dom")

        body = dom_tree.getElementsByTagName('body')[0]
        stream = walker(body)
        s = serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False)
        output_generator = s.serialize(stream)

        self.traverse(body)

        content = "".join([item.encode('utf-8')
                           for item in output_generator][1:-1])

        template = self.base_template
        template = template.replace('{{ title }}', page.encode('utf-8'))
        template = template.replace('{{ content }}', content)
        self.write_page(page, template)

    def traverse(self, node):
        if node.nodeName == 'a' and node.hasAttribute('href'):
            href = node.getAttribute('href')
            url = urlparse.urlparse(href)
            if url.netloc == self.wiki_domain:
                match = self.wiki_root_re.match(url.path)
                if match:
                    pagename = match.group(1)
                    if pagename not in self.pages_built:
                        self.pages_to_build.add(pagename)
                    node.setAttribute('href', pagename)
        elif node.nodeName == 'img' and node.hasAttribute('src'):
            src = node.getAttribute('src')
            if src.startswith('/images/'):
                node.setAttribute('src', 'https://%s%s' % (self.wiki_domain, src))
        children = [child for child in node.childNodes
                    if child.nodeType == child.ELEMENT_NODE]
        for child in children:
            self.traverse(child)

def main():
    dist_dir = path('dist')
    storage = {}
    if os.path.exists(path('cache.json')):
        storage = json.load(open(path('cache.json'), 'r'))

    cache = url_cache.UrlCache(storage)

    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.mkdir(dist_dir)
    shutil.copytree(path('..', 'static'), os.path.join(dist_dir, 'static'))

    template = open(path('..', 'template.html')).read()
    template = template.replace('{{ config }}', open(path('..', 'config.json')).read())
    
    sm = SiteMaker(storage=storage, cache=cache, dist_dir=dist_dir,
                   wiki_domain='wiki.mozilla.org', wiki_root='Badges',
                   base_template=template)
    sm.make_site()

    json.dump(storage, open(path('cache.json'), 'w'))
    print "Static site is now in %s." % dist_dir

if __name__ == '__main__':
    main()
