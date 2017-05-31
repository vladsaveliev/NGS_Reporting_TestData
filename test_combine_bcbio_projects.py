import os
from os.path import dirname, join, exists, isfile, splitext, basename, isdir, relpath, getmtime, getsize, abspath, \
    expanduser
from datetime import datetime

from ngs_utils.testing import BaseTestCase, info, check_call


class Test_combine_bcbio_projects(BaseTestCase):
    script = 'combine_bcbio_projects'

    data_dir = join(dirname(__file__), BaseTestCase.data_dir, script)
    results_dir = join(dirname(__file__), BaseTestCase.results_dir, script)
    gold_standard_dir = join(dirname(__file__), BaseTestCase.gold_standard_dir, script)
    source_dir = abspath(dirname(dirname(__file__)))

    def setUp(self):
        os.environ['PATH'] = self.source_dir + '/venv_ngs_reporting/bin:' + expanduser('~/bin') + ':/usr/local/bin:/usr/bin:/bin:/usr/sbin:' + os.environ['PATH']
        BaseTestCase.setUp(self)

    def _test(self, output_dirname, input_bcbio_dirnames=list()):
        os.chdir(self.data_dir)
        cmdl = [self.script]
        cmdl.extend([join(self.data_dir, dname) for dname in input_bcbio_dirnames])
        cmdl.extend(['-o', join(self.results_dir, output_dirname)])
        if exists(output_dirname):
            last_changed = datetime.fromtimestamp(getmtime(output_dirname))
            prev_output = output_dirname + '_' + last_changed.strftime('%Y_%m_%d_%H_%M_%S')
            os.rename(output_dirname, prev_output)

        info('-' * 100)
        check_call(cmdl)
        info('-' * 100)
        info('')

    def _check_results(self, output_txt):
        self._check_file_throws(output_txt)
        # TODO: check line numbers and some values isntead of diff?

    def test_01_simple(self):
        self._test(
            output_dirname='combined',
            input_bcbio_dirnames=[
                'Dev_0137_HiSeq4000_CRISPRexome_v0.9.9',
                'dream_chr21_v1.0.0',
            ]
        )

'''  -o  --debug --analysis-type exome
'''