#!/usr/bin/env python3 
"""
	Return git commands results through Python using subprocess

	Author: Marios Papachristou

	Copyright (c) 2018 Marios Papachristou

	This file is part of acycliCode. 

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.
"""

from helpers import *


def area_commits(area):
    # Area commits
    _cmd = "git log --pretty='%H' master -- {}".format(area)
    l = cmd(_cmd)
    return set(l)


def areas_violations(*areas):
    # Area violations
    assert(len(areas) >= 1)
    result = area_commits(areas[0])
    for area in areas[1:]:
        result &= area_commits(area)
    return result


def changed_files(_hash):
    # Show changed files in a list
    _cmd = 'git show --pretty="format:" --name-only ' + _hash
    l = cmd(_cmd)
    return l


def commit_message(_hash):
    # Get commit message
    _cmd = 'git show -s --format=%B ' + _hash
    l = cmd(_cmd)
    return l


def last_hash():
    _cmd = 'git show -s --format=%H HEAD'
    l = cmd(_cmd)
    return l[0]


def get_unique_commits(areas):
    # Get unique area commits
    unique_commits = {}

    for area in areas:
        print(area)
        unique_commits[area] = area_commits(area)

    # TODO Improve complexity
    for area in areas:
        for aarea in areas:
            if aarea != area:
                unique_commits[area] -= unique_commits[aarea]

    return unique_commits
