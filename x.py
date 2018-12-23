#!/usr/bin/env python3

import argparse
import sys
from sys import stderr

import activate
activate.activate()

from bs4 import BeautifulSoup


def main(argv):
    p = argparse.ArgumentParser(prog=argv[0])
    p.add_argument('URL')
    p.add_argument('DIR')
    a = p.parse_args(argv[1:])


if __name__ == '__main__':
    exit(main(sys.argv))
