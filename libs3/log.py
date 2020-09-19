#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''
Log in color from

https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python

usage : 

 import log
    log.info("Hello World")
    log.err("System Error")

'''
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = "\033[1m"

def disable():
    HEADER = ''
    OKBLUE = ''
    OKGREEN = ''
    WARNING = ''
    FAIL = ''
    ENDC = ''

def infog( msg):
    print(OKGREEN + msg + ENDC)

def info( msg):
    print(OKBLUE + msg + ENDC)

def warn( msg):
    print(WARNING + msg + ENDC)

def err( msg):
    print(FAIL + msg + ENDC)
