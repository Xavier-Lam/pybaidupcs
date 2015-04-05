#!/usr/bin/python

import sys
from argparse import ArgumentParser

p = ArgumentParser(usage='it is usage tip', description='this is a test')
p.add_argument('--one', default=1, type=int, help='the first argument')
p.add_argument('--two', default=2, type=int, help='the second argument')
p.add_argument('--docs-dir', default="./", help='document directory')

# 这个函数将认识的和不认识的参数分开放进2个变量中
args, remaining = p.parse_known_args(sys.argv)
print(args)
if not args:
    print(sys.argv[0].append("-h"))
    p.parse_known_args(sys.argv[0].append("-h"))