import sys
import os
import re
import urlparse
import json
import shutil

ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *x: os.path.join(ROOT, *x)

sys.path.append(path('vendor'))

import url_cache
import html5lib
from html5lib import treebuilders, treewalkers, serializer

BADGES_RE = re.compile(r'\/Badges(\/.*)')

storage = {}
if os.path.exists(path('cache.json')):
    storage = json.load(open(path('cache.json'), 'r'))

cache = url_cache.UrlCache(storage)

pages_built = []
pages_to_build = set(['/'])

def get_page(name):
    url = 'https://wiki.mozilla.org/index.php?title=Badges%s&action=render' % name
    cache.refresh(url, sys.stdout)
    return storage[url]['data']

def build(page):
    p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
    dom_tree = p.parse(get_page(page))

    walker = treewalkers.getTreeWalker("dom")

    body = dom_tree.getElementsByTagName('body')[0]
    stream = walker(body)
    s = serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False)
    output_generator = s.serialize(stream)

    traverse(body)

    content = "".join([item.encode('utf-8')
                       for item in output_generator][1:-1])

    template = open(path('..', 'template.html')).read()
    template = template.replace('{{ content }}', content)
    template = template.replace('{{ config }}', open(path('..', 'config.json')).read())
    f = open(path('dist', pathname_for_page(page)[1:]), 'w')
    f.write(template)
    f.close()

def pathname_for_page(pagename):
    if pagename.endswith('/'):
        pagename += 'index'
    return pagename + '.html'

def traverse(node):
    if node.nodeName == 'a' and node.hasAttribute('href'):
        href = node.getAttribute('href')
        url = urlparse.urlparse(href)
        if url.netloc == 'wiki.mozilla.org':
            match = BADGES_RE.match(url.path)
            if match:
                pagename = match.group(1)
                if pagename not in pages_built:
                    pages_to_build.add(pagename)
                node.setAttribute('href', pathname_for_page(pagename))
    elif node.nodeName == 'img' and node.hasAttribute('src'):
        src = node.getAttribute('src')
        if src.startswith('/images/'):
            node.setAttribute('src', 'https://wiki.mozilla.org' + src)
    children = [child for child in node.childNodes
                if child.nodeType == child.ELEMENT_NODE]
    for child in children:
        traverse(child)

if __name__ == '__main__':
    if os.path.exists(path('dist')):
        shutil.rmtree(path('dist'))
    os.mkdir(path('dist'))
    shutil.copytree(path('..', 'static'), path('dist', 'static'))

    while pages_to_build:
        pagename = pages_to_build.pop()
        pages_built.append(pagename)
        build(pagename)

    json.dump(storage, open(path('cache.json'), 'w'))
    print "Static site is now in %s." % path('dist')
