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
"""Linter using yamllint.

This test calls the flake program, see https://yamllint.readthedocs.io/en/latest/
"""
from __future__ import print_function

from cardboardlint.common import Message, run_command, matches_filefilter, flag


__all__ = ['linter_yamllint']


DEFAULT_CONFIG = {
    # Filename filter rules
    'filefilter': ['+ *.yml', '+ *.yaml'],
}


@flag(static=True, python=True)
def linter_yamllint(linter_config, files_lines):
    """Linter for checking yamllint results.

    Parameters
    ----------
    linter_config : dict
        Dictionary that contains the configuration for the linter
    files_lines : dict
        Dictionary of filename to the set of line numbers (that have been modified).
        See `run_diff` function in `carboardlinter`.

    Returns
    -------
    messages : list
        The list of messages generated by the external linter.

    """
    config = DEFAULT_CONFIG.copy()
    config.update(linter_config)

    # get yamllint version
    command = ['yamllint', '--version']
    version_info = run_command(command, verbose=False)[0]
    print('USING              : {0}'.format(version_info))

    # Get all relevant filenames
    filenames = [filename for filename in files_lines
                 if matches_filefilter(filename, config['filefilter'])]

    def has_failed(returncode, _stdout, _stderr):
        """Determine if yamllint ran correctly."""
        return not 0 <= returncode < 2

    messages = []
    if len(filenames) > 0:
        command = ['yamllint', '-f', 'parsable'] + filenames
        output = run_command(command, has_failed=has_failed)[0]
        if len(output) > 0:
            for line in output.splitlines():
                words = line.split(':')
                messages.append(Message(
                    words[0], int(words[1]), int(words[2]), words[3].strip()))
    return messages
