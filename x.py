#!/usr/bin/env python3

import argparse
import sys
from sys import stderr

import activate
activate.activate()

import requests
from bs4 import BeautifulSoup


def get_submission_urls(gallery_url):
    r = requests.get(gallery_url)
    if not r.ok:
        stderr.write(r.text)
        r.raise_for_status()

    doc = BeautifulSoup(r.content, 'html.parser')
    gallery = doc.find('section', id='gallery-gallery')
    for caption in gallery.find_all('figcaption'):
        yield caption.a['href']


def main(argv):
    p = argparse.ArgumentParser(prog=argv[0])
    p.add_argument('URL')
    p.add_argument('DIR')
    a = p.parse_args(argv[1:])

    for url in get_submission_urls(a.URL):
        print(url)


if __name__ == '__main__':
    exit(main(sys.argv))
