#!/usr/bin/env python
"""A Python tool and a library for blaming Python code

Currently supports only git and HEAD revision and blaming tests.

Usage:
    python-blame [<path>]...
"""
import os
import sys
from collections import Counter
from contextlib import suppress
from enum import Enum
from typing import List, Dict, Callable, Tuple

import astroid
import plumbum
import poetry_version
from docopt import docopt
from pathlib import Path

from plumbum import ProcessExecutionError
from ruamel.yaml import YAML


class NodeFilterType(Enum):
    FUNCTION = 'function'
    TEST = 'test'


NodeFilterFunction = Callable[[astroid.node_classes.NodeNG], bool]
NodeFilter = List[NodeFilterType]

TEST_NODE_FILTER = [NodeFilterType.FUNCTION, NodeFilterType.TEST]


def get_paths(paths: List[Path]) -> List[Path]:
    result = []
    for path in paths:
        if path.is_dir():
            result += path.rglob('*.py')
        else:
            result += [path]
    result = [path.absolute() for path in result]
    return result


def git_blame(path: Path) -> List[str]:
    git = plumbum.local['git']
    result = []
    try:
        git_output = git('blame', '--line-porcelain', str(path))
    except ProcessExecutionError:
        return result
    for line in git_output.splitlines():
        author_prefix = 'author '
        if line.startswith(author_prefix):
            author = line.replace(author_prefix, '')
            result.append(author)
    return result


def get_node_filter_function(node_filter: NodeFilter) -> NodeFilterFunction:
    node_filter_functions = []
    for node_filter_type in node_filter:
        if node_filter_type == NodeFilterType.FUNCTION:
            node_filter_functions.append(lambda node: node.is_function)
        elif node_filter_type == NodeFilterType.TEST:
            node_filter_functions.append(lambda node: node.name.startswith('test_'))

    def result(node: astroid.node_classes.NodeNG) -> bool:
        return all(node_filter_function(node) for node_filter_function in node_filter_functions)

    return result


def python_extract_nodes(path: Path, node_filter: NodeFilter) -> Dict[str, Tuple[int, int]]:
    node_filter_function = get_node_filter_function(node_filter)
    source = open(str(path)).read()
    result = {}
    try:
        tree = astroid.parse(source)
    except astroid.AstroidSyntaxError:
        return result
    for node in tree.body:
        if node_filter_function(node):
            result[node.name] = (node.lineno, node.tolineno)
    return result


def blame(paths: List[Path], node_filter: NodeFilter) -> Dict[str, Dict[str, str]]:
    old_cwd = os.getcwd()
    paths = get_paths(paths)
    result = {}
    for path in paths:
        file_result = {}
        os.chdir(str(path.parent.absolute()))
        git_blame_output = git_blame(path)
        nodes = python_extract_nodes(path, node_filter)
        for node_name, (node_first_line, node_last_line) in nodes.items():
            counts = Counter(git_blame_output[node_first_line - 1:node_last_line])
            with suppress(IndexError):
                author = counts.most_common(1)[0][0]
                file_result[node_name] = author
        result[str(path)] = file_result
    os.chdir(old_cwd)
    return result


def main() -> None:
    args = docopt(__doc__, version=poetry_version.extract(source_file=__file__))
    paths = [Path(path) for path in args.get('<path>', ['.'])]
    result = blame(paths, TEST_NODE_FILTER)
    yaml = YAML()
    yaml.dump(result, stream=sys.stdout)


if __name__ == '__main__':
    main()
