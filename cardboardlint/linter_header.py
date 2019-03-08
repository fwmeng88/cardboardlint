# -*- coding: utf-8 -*-
# Cardboardlint is a cheap lint solution for pull requests.
# Copyright (C) 2011-2017 The Cardboardlint Development Team
#
# This file is part of Cardboardlint.
#
# Cardboardlint is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Cardboardlint is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
"""Linter for source file headers.

This linter checks if the headers of source files are correctly formatted. The header
is read in from some file and it is expected that the source files contain this header
as a comment at the start of the file. Options can be used to allow other lines to be
present, such as a shebang line or a mode line.
"""
from __future__ import print_function

import codecs
from typing import List

from cardboardlint.common import Message, Linter


__all__ = ['linter_header']


DEFAULT_CONFIG = {
    # Filename filter rules
    'filefilter': ['+ *.py', '+ *.pyx', '+ *.pxd'],
    # The path to the header file'
    'header': 'HEADER',
    # Comments start with:
    'comment': '# ',
    # Format of the shebang line, only checked if a shebang line is present
    'shebang': '#!/usr/bin/env python',
    # Some extra lines that should be inserted above the header (but under the shebang if
    # present)
    'extra': ['# -*- coding: utf-8 -*-'],
}


def run_header(config, filenames):
    """Linter for checking source file headers.

    Parameters
    ----------
    config : dict
        Dictionary that contains the configuration for the linter
    filenames : list
        A list of filenames to check

    Returns
    -------
    messages : list
        The list of messages generated by the external linter.

    """
    # Load the header file as a set of lines
    header_lines = list(config['extra'])
    with codecs.open(config['header'], encoding='utf-8') as f:
        for line in f:
            header_lines.append((config['comment'] + line).strip())

    # Loop all files and check in the header each file.
    messages = []
    for filename in filenames:
        try:
            _check_file(filename, config, header_lines, messages)
        except UnicodeDecodeError as err:
            messages.append(Message(filename, None, None, str(err)))
    return messages


def _check_file(filename: str, config: dict, header_lines: List[str],
                messages: List[str]):
    """Look for bad filename headers.

    Parameters
    ----------
    filename
        File to be checked
    config
        Dictionary with configuration of the linters.
    header_lines
        The expected header.
    messages
        A list of messages to append to. (output arg)

    """
    with codecs.open(filename, encoding='utf-8') as f:
        iterator = iter(enumerate(f))
        header_counter = 0
        while header_counter < len(header_lines):
            try:
                lineno, line = next(iterator)
            except StopIteration:
                break
            if lineno == 0 and line.startswith('#!') and config['shebang'] is not None:
                if line[:-1] != config['shebang']:
                    messages.append(Message(
                        filename, lineno + 1, None,
                        'Shebang line should be {}.'.format(config['shebang'])))
            else:
                expected = header_lines[header_counter]
                if line[:-1] != expected:
                    messages.append(Message(
                        filename, lineno + 1, None, 'Line should be: {}'.format(expected)))
                header_counter += 1

# pylint: disable=invalid-name
linter_header = Linter('header', run_header, DEFAULT_CONFIG)
