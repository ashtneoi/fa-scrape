#!/usr/bin/env python3

import argparse
import sys
import urllib
from sys import stderr
from time import sleep

import activate
activate.activate()

import requests
from bs4 import BeautifulSoup


def ltake(s, t):
    if not s.startswith(t):
        raise ValueError("unexpected prefix")
    return s[len(t):]


def get_submission_urls(gallery_url):
    r = requests.get(gallery_url)
    if not r.ok:
        stderr.write(r.text)
        r.raise_for_status()

    doc = BeautifulSoup(r.content, 'html.parser')
    gallery = doc.find('section', id='gallery-gallery')
    for caption in gallery.find_all('figcaption'):
        href = caption.a['href']
        url = urllib.parse.urljoin(
            gallery_url,
            '/full/' + ltake(href, '/view/'),
        )
        yield url


def get_submission_info(submission_url):
    r = requests.get(submission_url)
    if not r.ok:
        stderr.write(r.text)
        r.raise_for_status()

    doc = BeautifulSoup(r.content, 'html.parser')
    image = doc.find('img', id='submissionImg')
    image_url = urllib.parse.urljoin(
        submission_url,
        image['src'],
    )

    title = doc.find('meta', property='og:title')['content']

    return title, image_url


def main(argv):
    p = argparse.ArgumentParser(prog=argv[0])
    p.add_argument('URL')
    p.add_argument('DIR')
    a = p.parse_args(argv[1:])

    for s in get_submission_urls(a.URL):
        print(get_submission_info(s))
        sleep(5)


if __name__ == '__main__':
    exit(main(sys.argv))
