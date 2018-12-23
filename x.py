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


def _get_submission_urls(gallery_url, gallery):
    for caption in gallery.find_all('figcaption'):
        href = caption.a['href']
        submission_id = rtake(ltake(href, '/view/'), '/')
        url = urllib.parse.urljoin(
            gallery_url,
            f'/full/{submission_id}/',
        )
        yield submission_id, url


def get_submission_urls(gallery_url):
    r = requests.get(gallery_url)
    if not r.ok:
        stderr.write(r.text)
        r.raise_for_status()

    doc = BeautifulSoup(r.content, 'html.parser')
    gallery = doc.find('section', id='gallery-gallery')
    next_gallery_a = doc.select_one('a.button-link.right')
    if next_gallery_a is None:
        next_gallery_url = None
    else:
        next_gallery_url = urllib.parse.urljoin(
            gallery_url,
            next_gallery_a['href'],
        )
    return next_gallery_url, _get_submission_urls(gallery_url, gallery)


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
    p.add_argument('DELAY')
    a = p.parse_args(argv[1:])

    delay = int(a.DELAY)

    gallery_url = a.URL
    while gallery_url is not None:
        print(gallery_url)
        next_gallery_url, submissions = get_submission_urls(gallery_url)

        for submission_id, submission_url in submissions:
            sleep(delay)

            print(submission_url)
            page_content, title, image_url = get_submission_info(submission_url)
            title = title.replace('/', '%')

            sleep(delay)

            print(image_url)
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

            with open(image_out_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1<<14):
                    f.write(chunk)

            page_out_path = path.join(
                a.DIR,
                f'{submission_id} {title}.html',
            )

            with open(page_out_path, 'wb') as f:
                f.write(page_content)

        gallery_url = next_gallery_url
        sleep(delay)


if __name__ == '__main__':
    exit(main(sys.argv))
