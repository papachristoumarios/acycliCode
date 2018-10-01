#!/usr/bin/env python3

"""
	Testing routine to detect layering violations based on
	commit hashes and layer definition files

	Author: Marios Papachristou
	Usage: acyclicode.py -h for help

	This file is part of acycliCode

	Copyright (c) 2018 Marios Papachristou

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

# Imports
import collections
import sys
import os
import re
import json
import argparse
import logging

# Project-specific imports
import git_commits
from helpers import cmd

logging.basicConfig(
    format='%(levelname)s : %(message)s',
    level=logging.INFO)


def basename(x): return x.split('/')[-1]


def get_dependencies(filelist, recursive=True):
    """Get dependences for analysis using regex"""

    dependencies = set([])

    for filename in filelist:
        with open(filename) as f:
            lines = f.read().splitlines()

            for line in lines:
                if line.startswith('#include'):
                    result = re.search(r'"([A-Za-z0-9_\./\\-]*)"', line)
                    if result is not None:
                        ddir = os.path.dirname(filename)
                        source_dep = ddir + '/' + \
                            re.sub('.h', '.c', result.group(1))
                        dependencies |= {source_dep}

    # Iterate through dependencies header files
    q = collections.deque()
    visited = collections.defaultdict(bool)

    if recursive:

        # Initialize
        for d in dependencies:
            header_dep = re.sub('.c', '.h', d)
            q.append(header_dep)
            visited[header_dep] = True

        # Perform Breadth-First Search
        while q:
            current = q.popleft()

            # Visit
            dependencies |= {current}
            visited[current] = True

            # Children
            with open(filename) as f:
                lines = f.read().splitlines()

                for line in lines:
                    if line.startswith('#include'):
                        result = re.search(r'"([A-Za-z0-9_\./\\-]*)"', line)
                        if result is not None:
                            ddir = os.path.dirname(filename)
                            header_dep = ddir + '/' + result.group(1)
                            if not visited[header_dep]:
                                q.append(header_dep)

    return dependencies


def parse_flow_graph(flow_graph):
    """Parse flow graph generated with Cflow"""

    def _get_file_dep(x):
        y = x.split(' at ')[-1]
        return y.split(':')[0]

    edges = set([])

    current = _get_file_dep(flow_graph[0])
    v = None

    # Build edge set
    for line in flow_graph:
        if line.startswith('    '):
            v = _get_file_dep(line)
            e = (current, v)
            edges |= {e}
        else:
            current = _get_file_dep(line)

    return edges


def map_to_layers(edges, layers):
    """Map graph to respective layers removing excess edges"""

    result = set()

    for (u, v) in edges:
        e = (layers[u], layers[v])
        result |= {e}

    return result


def get_back_calls(edges, layers):
    """Detect back calls"""

    b_calls = []
    for u, v in edges:
        if layers[u] < layers[v]:
            b_calls.append((u, v))

    return b_calls


def get_skip_calls(edges, layers):
    """Detect skip calls"""

    sk_calls = []
    for u, v in edges:
        if layers[u] >= layers[v] and layers[u] - layers[v] > 1:
            sk_calls.append((u, v))

    return sk_calls


def get_layers_size(files, layers):
    """Get layers sizes given modules"""

    sizes = collections.defaultdict(int)

    for f in files:
        sizes[layers[f]] += 1

    return sizes


def flow_graph(files, deps, layers):
    """Generate and parse flow graph using GNU Cflow"""

    total_files = files | deps
    command = 'cflow {} -d 2'.format(' '.join(total_files))
    flow_graph_txt = cmd(command)
    edges = parse_flow_graph(flow_graph_txt)

    return edges


def count_calls(calls, layers):
    """Count total calls in layers"""

    result = collections.defaultdict(int)

    for u, v in calls:
        result[layers[u]] += 1

    return result


def calculate_violation_index(calls_count, sizes):
    """Calculate average violation index (e.g. BCVI, SCVI)"""

    total = 0
    count = 0

    for l, c in calls_count.items():
        total += c / sizes[l]
        count += 1

    return total / count


def analyze_violations(files, layers, flow_graph, _assert):
    """Analyze violations provided the flow graph"""

    # Get layer sizes
    sizes = get_layers_size(layers.keys(), layers)

    # Back calls
    back_calls = get_back_calls(flow_graph, layers)

    if back_calls != []:
        logging.warning('Back Calls')
        for u, v in back_calls:
            logging.warning(
                '{} (Layer {}) -> {} (Layer {})'.format(u, layers[u], v, layers[v]))

            # Calculate BCVI
            count = count_calls(back_calls, layers)
            bcvi = calculate_violation_index(count, sizes)

            logging.warning('Average BCVI: {}'.format(bcvi))
    else:
        logging.info('No Back Calls Found')

    # Skip calls
    skip_calls = get_skip_calls(flow_graph, layers)

    if skip_calls != []:
        logging.warning('Skip Calls')
        for u, v in skip_calls:
            logging.warning(
                '{} (Layer {}) -> {} (Layer {})'.format(u, layers[u], v, layers[v]))

        # Calculate SCVI
        count = count_calls(skip_calls, layers)
        scvi = calculate_violation_index(count, sizes)

        logging.warning('Average SCVI: {}'.format(scvi))

    else:
        logging.info('No Skip Calls Found')

    # Raise errors to testing routine
    if _assert:
        assert(back_calls == [])
        assert(skip_calls == [])


if __name__ == '__main__':

    # Initialize argparse
    parser = argparse.ArgumentParser(
        description='Testing routine to detect layering violations in git commits')

    parser.add_argument(
        '-c',
        dest='commit',
        type=str,
        default=git_commits.last_hash(),
        help='Commit hash in SHA256. If ommited defaults to last commit hash.')
    parser.add_argument(
        '-l',
        dest='layers',
        type=str,
        default='layers.json',
        help='Layer definitions file')
    parser.add_argument(
        '--assert',
        dest='_assert',
        action='store_true',
        help='Assert tests for CI testing routines')

    # Change path
    path = os.getenv('ACYCLICODE_PATH')

    if path is not None:
        os.chdir(path)

    args = parser.parse_args()

    # Open layer definition file
    with open(args.layers) as f:
        layers = json.loads(f.read())

    # Get changed files from commit
    files = set(git_commits.changed_files(args.commit)) & set(layers.keys())

    if len(files) == 0:
        exit(0)

    # Get dependences
    deps = get_dependencies(files)

    # Generate flow graph
    flow_graph = flow_graph(files, deps, layers)

    # Analyze violations
    analyze_violations(files, layers, flow_graph, _assert=args._assert)
