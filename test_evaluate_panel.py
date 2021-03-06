import subprocess
import traceback

import os
import sys

import shutil
from os.path import dirname, join, exists, isfile, splitext, basename, isdir, relpath, getmtime, getsize, abspath, \
    expanduser

from ngs_utils.file_utils import add_suffix
from ngs_utils.testing import BaseTestCase, info, check_call, swap_output, swap_prev_symlink


class Test_evaluate_panel(BaseTestCase):
    script = 'evaluate_panel'

    data_dir = join(dirname(__file__), BaseTestCase.data_dir, script)
    results_dir = join(dirname(__file__), BaseTestCase.results_dir, script)
    gold_standard_dir = join(dirname(__file__), BaseTestCase.gold_standard_dir, script)
    source_dir = abspath(dirname(dirname(__file__)))

    def setUp(self):
        BaseTestCase.setUp(self)

    def test(self):
        bcbio_dir = join(dirname(Test_evaluate_panel.data_dir), 'bcbio_postproc', 'dream_chr21_paired')
        assert isdir(bcbio_dir), 'data dir ' + bcbio_dir + ' not found'
        
        o_dir = join(self.results_dir, 'capture_eval')
        cmdl = [self.script, bcbio_dir, '--min-depth', '50', '-o', o_dir]
        if 'TRAVIS' in os.environ:
            cmdl.extend(['--sys-cnf', join(self.source_dir, 'az', 'configs', 'system_info_Travis.yaml')])

        prev_o_dir = swap_output(o_dir)

        info('-' * 100)
        check_call(cmdl)
        info('-' * 100)
        info('')

        self._check_file_throws(join(o_dir, 'low_panel_coverage.50.bed.gz'),
                                ignore_matching_lines=['Showing low-covered regions for project'])

        shutil.rmtree(join(o_dir, 'work'))
        
        swap_prev_symlink(o_dir, prev_o_dir)
