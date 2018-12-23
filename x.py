#!/usr/bin/env python3

import argparse
import sys
import urllib
from os import path
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


def rtake(s, t):
    if not s.endswith(t):
        raise ValueError("unexpected suffix")
    return s[:-len(t)]


def get_submission_urls(gallery_url):
    r = requests.get(gallery_url)
    if not r.ok:
        stderr.write(r.text)
        r.raise_for_status()

    doc = BeautifulSoup(r.content, 'html.parser')
    gallery = doc.find('section', id='gallery-gallery')
    for caption in gallery.find_all('figcaption'):
        href = caption.a['href']
        submission_id = rtake(ltake(href, '/view/'), '/')
        url = urllib.parse.urljoin(
            gallery_url,
            f'/full/{submission_id}/',
        )
        yield submission_id, url


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

    return r.content, title, image_url


def main(argv):
    p = argparse.ArgumentParser(prog=argv[0])
    p.add_argument('URL')
    p.add_argument('DIR')
    a = p.parse_args(argv[1:])

    for submission_id, submission_url in get_submission_urls(a.URL):
        page_content, title, image_url = get_submission_info(submission_url)

        r = requests.get(image_url, stream=True)
        if not r.ok:
            stderr.write(r.text)
            r.raise_for_status()

        assert '.' in image_url
        image_out_path = path.join(
            a.DIR,
            '{} {}.{}'.format(
                submission_id,
                title,
                image_url[image_url.rfind('.')+1:],
            ),
        )
        print(image_out_path)

        with open(image_out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1<<14):
                f.write(chunk)

        page_out_path = path.join(
            a.DIR,
            f'{submission_id} {title}.html',
        )

        with open(page_out_path, 'wb') as f:
            f.write(page_content)

        sleep(3)


if __name__ == '__main__':
    exit(main(sys.argv))
