import traceback
import os
import sys
from os.path import dirname, join, exists, isfile, splitext, basename, isdir, relpath, getctime, getsize, abspath, expanduser
from datetime import datetime
import shutil
import subprocess

from ngs_utils.testing import BaseTestCase, info, check_call
from ngs_utils.utils import is_az, is_local, is_travis


class Test_bcbio_postproc(BaseTestCase):
    script = 'bcbio_postproc'

    data_dir = join(dirname(__file__), BaseTestCase.data_dir, script)
    results_dir = join(dirname(__file__), BaseTestCase.results_dir, script)
    gold_standard_dir = join(dirname(__file__), BaseTestCase.gold_standard_dir, script)

    def setUp(self):
        if is_local():
            info('Local - setting up PATH')
            os.environ['PATH'] = '/Users/vlad/miniconda3/envs/ngs_reporting/bin:' + expanduser('~/bin') + ':/usr/local/bin:/usr/bin:/bin:/usr/sbin:' + os.environ['PATH']
            info('PATH =  ' + os.environ['PATH'])
        BaseTestCase.setUp(self)

    def _run_postproc(self, bcbio_dirname):
        bcbio_dir = join(self.data_dir, bcbio_dirname)
        assert isdir(bcbio_dir), 'data dir ' + bcbio_dir + ' not found'
        bcbio_proj_dir = join(self.results_dir, bcbio_dirname)
        
        if exists(bcbio_proj_dir):
            last_changed = datetime.fromtimestamp(getctime(bcbio_proj_dir))
            prev_run = bcbio_proj_dir + '_' + last_changed.strftime('%Y_%m_%d_%H_%M_%S')
            os.rename(bcbio_proj_dir, prev_run)
        shutil.copytree(bcbio_dir, bcbio_proj_dir, symlinks=True)

        cmdl = [self.script, bcbio_proj_dir, '--eval-panel']  # '-d', '-t', '1'

        run_with_error = False
        info('-' * 100)
        try:
            check_call(cmdl)
        except subprocess.CalledProcessError:
            sys.stderr.write(self.script + ' finished with error:\n')
            sys.stderr.write(traceback.format_exc() + '\n')
            run_with_error = True
        info('-' * 100)
        info('')
        return bcbio_proj_dir, run_with_error

    def _check_file(self, diff_failed, path, ignore_matching_lines=None, wrapper=None,
                    check_diff=True, json_diff=False):
        try:
            self._check_file_throws(path, ignore_matching_lines=ignore_matching_lines, wrapper=wrapper,
                                    check_diff=check_diff, json_diff=json_diff)
        except subprocess.CalledProcessError as e:
            sys.stderr.write('Error: ' + str(e) + '\n')
            return True
        except AssertionError as e:
            sys.stderr.write('Error: ' + str(e) + '\n')
            return True
        return diff_failed

    def test_01_dream_chr21(self):
        bcbio_proj_dir, run_with_error = self._run_postproc(bcbio_dirname='dream_chr21')

        datestamp_name = '2014-08-13_dream-chr21'
        sample_name = 'syn3-tumor'
        datestamp_dir = join(bcbio_proj_dir, 'final', datestamp_name)
        sample_dir = join(bcbio_proj_dir, 'final', sample_name)

        VCF_IGNORE_LINES = [
            'bcftools_annotateVersion',
            'bcftools_annotateCommand',
            '^##INFO=',
            '^##FILTER=',
        ]
        failed = False
        failed = self._check_file(failed, join(bcbio_proj_dir, 'config', 'run_info_ExomeSeq.yaml'))
        failed = self._check_file(failed, join(datestamp_dir, 'vardict.PASS.txt'))
        failed = self._check_file(failed, join(datestamp_dir, 'var', 'vardict.PASS.txt'))
        failed = self._check_file(failed, join(datestamp_dir, 'var', 'vardict.txt'))
        failed = self._check_file(failed, join(datestamp_dir, 'var', 'vardict.REJECT.txt'))
        failed = self._check_file(failed, join(datestamp_dir, 'var', 'vardict.PASS.json'))
        failed = self._check_file(failed, join(datestamp_dir, 'var', 'vardict.vcf.gz'), VCF_IGNORE_LINES)
        failed = self._check_file(failed, join(datestamp_dir, 'cnv', 'seq2c.tsv'), wrapper=['sort'])
        failed = self._check_file(failed, join(datestamp_dir, 'cnv', 'seq2c.filt.tsv'), wrapper=['sort'])
        failed = self._check_file(failed, join(datestamp_dir, 'cnv', 'seq2c-coverage.tsv'), wrapper=['sort'])
        failed = self._check_file(failed, join(datestamp_dir, 'cnv', 'seq2c_mapping_reads.txt'))
        failed = self._check_file(failed, join(datestamp_dir, 'reports', 'call_vis.html'),
                                  check_diff=False)
                                  # wrapper=['grep', '-A1', '<div id=".*_json">', '|', 'grep', '-v', '<div id=".*_json">'],
                                  # json_diff=True)
        failed = self._check_file(failed, join(datestamp_dir, 'report.html'), check_diff=False)
        failed = self._check_file(failed, join(sample_dir, 'varAnnotate', 'syn3-tumor-vardict.anno.vcf.gz'), VCF_IGNORE_LINES)
        failed = self._check_file(failed, join(sample_dir, 'varFilter', 'syn3-tumor-vardict.anno.filt.vcf.gz'), VCF_IGNORE_LINES)
        failed = self._check_file(failed, join(sample_dir, 'varFilter', 'syn3-tumor-vardict.anno.filt.PASS.vcf.gz'), VCF_IGNORE_LINES)
        failed = self._check_file(failed, join(sample_dir, 'varFilter', 'vardict.PASS.json'), check_diff=False)
        failed = self._check_file(failed, join(sample_dir, 'varFilter', 'vardict.PASS.txt'))
        failed = self._check_file(failed, join(sample_dir, 'varFilter', 'vardict.txt'))
        failed = self._check_file(failed, join(sample_dir, 'varFilter', 'vardict.REJECT.txt'))
        failed = self._check_file(failed, join(datestamp_dir, 'reports', sample_name + '.html'),
                                  check_diff=False)
                                  # wrapper=['grep', '-A1', '<div id=".*_json">', '|', 'grep', '-v', '<div id=".*_json">'],
                                  # json_diff=True)

        assert not run_with_error, 'post-processing finished with error'
        assert not failed, 'some of file checks have failed'
        shutil.rmtree(join(bcbio_proj_dir, 'work'))

    def test_02_rnaseq(self):
        bcbio_proj_dir, run_with_error = self._run_postproc(bcbio_dirname='rnaseq')

        datestamp_name = '2017-02-28_rnaseq_1_0_2a'
        sample_name = 'PI3Ksign2_E001006_CD4Tcells_AZ4943_NS_KT_15'
        datestamp_dir = join(bcbio_proj_dir, 'final', datestamp_name)
        sample_dir = join(bcbio_proj_dir, 'final', sample_name)

        failed = False
        failed = self._check_file(failed, join(datestamp_dir, 'annotated_combined.counts'))
        failed = self._check_file(failed, join(datestamp_dir, 'tx2gene.csv'))
        failed = self._check_file(failed, join(datestamp_dir, 'expression', 'counts.tsv'))
        failed = self._check_file(failed, join(datestamp_dir, 'expression', 'dexseq.tsv'))
        failed = self._check_file(failed, join(datestamp_dir, 'expression', 'gene.sf.tpm.tsv'))
        failed = self._check_file(failed, join(datestamp_dir, 'expression', 'isoform.sf.tpm.tsv'))
        failed = self._check_file(failed, join(datestamp_dir, 'expression', 'html', 'counts.html'), wrapper=['grep', '<td metric='])
        failed = self._check_file(failed, join(datestamp_dir, 'expression', 'html', 'dexseq.html'), wrapper=['grep', '<td metric='])
        failed = self._check_file(failed, join(datestamp_dir, 'expression', 'html', 'gene.sf.tpm.html'), wrapper=['grep', '<td metric='])
        failed = self._check_file(failed, join(datestamp_dir, 'expression', 'html', 'isoform.sf.tpm.html'), wrapper=['grep', '<td metric='])
        failed = self._check_file(failed, join(datestamp_dir, 'report.html'), check_diff=False)

        assert not run_with_error, 'post-rpocessing finished with error'
        assert not failed, 'some of the diffs have failed'
        shutil.rmtree(join(bcbio_proj_dir, 'work'))
