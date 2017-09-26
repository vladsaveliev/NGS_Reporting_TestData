import traceback
import os
import sys
from os.path import dirname, join, exists, isfile, splitext, basename, isdir, relpath, getctime, getsize, abspath, expanduser
from datetime import datetime
import shutil
import subprocess

from ngs_utils.testing import BaseTestCase, info, check_call
from ngs_utils.utils import is_az, is_local, is_travis


REUSE = False      # Run on top of existing latest results
ONLY_DIFF = False   # Do not run, just diff the latest results against the gold standard

# Find and parse all elements containing json data, put data into a list and dumps the result.
# The resulting text is unique per json data, so we can run simple `diff` on them.
html_wrapper = [
    'grep', '-A1', '<div id=".*_json">', '|', 'grep', '-v', '<div id=".*_json">', '|',
    'python', '-c',
        'import sys, json; '
        'sys.stdout.write(json.dumps([json.loads(el) for el in sys.stdin.read().split(\'--\')], '
                                     'indent=2, sort_keys=True))'
]

vcf_ignore_lines = [
    'bcftools_annotateVersion',
    'bcftools_annotateCommand',
    '^##INFO=',
    '^##FILTER=',
    '^##contig=',
]


class Test_bcbio_postproc(BaseTestCase):
    script = 'bcbio_postproc'

    data_dir = join(dirname(__file__), BaseTestCase.data_dir, script)
    results_dir = join(dirname(__file__), BaseTestCase.results_dir, script)
    gold_standard_dir = join(dirname(__file__), BaseTestCase.gold_standard_dir, script)

    def setUp(self):
        if is_local():
            info('Running locally: setting up PATH')
            os.environ['PATH'] = '/Users/vlad/miniconda3/envs/ngs_reporting/bin:' + expanduser('~/bin') + ':/usr/local/bin:/usr/bin:/bin:/usr/sbin:' + os.environ['PATH']
            info('PATH = ' + os.environ['PATH'])
        BaseTestCase.setUp(self)

    def _run_postproc(self, bcbio_dirname, eval_panel=False, parallel=False, debug=True):
        results_dir = join(self.results_dir, bcbio_dirname)
        run_with_error = False

        if not ONLY_DIFF:
            bcbio_dir = join(self.data_dir, bcbio_dirname)
            assert isdir(bcbio_dir), 'data dir ' + bcbio_dir + ' not found'

            if not REUSE:
                if exists(results_dir):
                    last_changed = datetime.fromtimestamp(getctime(results_dir))
                    prev_run = results_dir + '_' + last_changed.strftime('%Y_%m_%d_%H_%M_%S')
                    os.rename(results_dir, prev_run)
                shutil.copytree(bcbio_dir, results_dir, symlinks=True)

            cmdl = [self.script, results_dir]
            if eval_panel:
                cmdl.append('--eval-panel')
            if not parallel:
                cmdl.extend(['-t', '1'])
            if debug:
                cmdl.append('-d')

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

        return results_dir, run_with_error

    def _check_file(self, diff_failed, path, ignore_matching_lines=None, wrapper=None, check_diff=True):
        try:
            self._check_file_throws(path, ignore_matching_lines=ignore_matching_lines, wrapper=wrapper, check_diff=check_diff)
        except subprocess.CalledProcessError as e:
            sys.stderr.write('Error: ' + str(e) + '\n')
            return True
        except AssertionError as e:
            sys.stderr.write('Error: ' + str(e) + '\n')
            return True
        return diff_failed

    def _check_var_in_datestamp(self, failed, datestamp_dir, caller):
        failed = self._check_file(failed, join(datestamp_dir, caller + '.PASS.txt'))
        failed = self._check_file(failed, join(datestamp_dir, 'var', caller + '.PASS.txt'))
        failed = self._check_file(failed, join(datestamp_dir, 'var', caller + '.txt'))
        failed = self._check_file(failed, join(datestamp_dir, 'var', caller + '.REJECT.txt'))
        failed = self._check_file(failed, join(datestamp_dir, 'var', caller + '.PASS.json'))
        if caller != 'freebayes':  # cannot merge using `bcftools merge`: > Incorrect number of AD fields (3) at chr21:11049225, cannot merge.
            failed = self._check_file(failed, join(datestamp_dir, 'var', caller + '.vcf.gz'), vcf_ignore_lines)
        return failed

    def _check_var_in_sample(self, failed, sample_dir, sample, caller):
        failed = self._check_file(failed, join(sample_dir, 'varAnnotate', sample + '-' + caller + '.anno.vcf.gz'), vcf_ignore_lines)
        failed = self._check_file(failed, join(sample_dir, 'varFilter', sample + '-' + caller + '.anno.filt.vcf.gz'), vcf_ignore_lines)
        failed = self._check_file(failed, join(sample_dir, 'varFilter', sample + '-' + caller + '.anno.filt.PASS.vcf.gz'), vcf_ignore_lines)
        failed = self._check_file(failed, join(sample_dir, 'varFilter', caller + '.PASS.json'), check_diff=False)
        failed = self._check_file(failed, join(sample_dir, 'varFilter', caller + '.PASS.txt'))
        failed = self._check_file(failed, join(sample_dir, 'varFilter', caller + '.txt'))
        failed = self._check_file(failed, join(sample_dir, 'varFilter', caller + '.REJECT.txt'))
        return failed

    def _test_dream_chr20(self, name, callers, parallel=False, eval_panel=False):
        bcbio_proj_dir, run_with_error = self._run_postproc(bcbio_dirname=name, parallel=parallel, eval_panel=eval_panel)

        datestamp_name = '2014-08-13_' + name
        datestamp_dir = join(bcbio_proj_dir, 'final', datestamp_name)

        failed = False
        failed = self._check_file(failed, join(bcbio_proj_dir, 'config', 'run_info_ExomeSeq.yaml'))
        failed = self._check_file(failed, join(datestamp_dir, 'NGv3.chr21.4col.clean.sorted.bed'))
        failed = self._check_file(failed, join(datestamp_dir, 'report.html'), check_diff=False)
        failed = self._check_file(failed, join(datestamp_dir, 'reports', 'call_vis.html'), wrapper=html_wrapper, check_diff=False)
        failed = self._check_file(failed, join(datestamp_dir, 'cnv', 'seq2c.tsv'), wrapper=['sort'])
        failed = self._check_file(failed, join(datestamp_dir, 'cnv', 'seq2c.filt.tsv'), wrapper=['sort'])
        failed = self._check_file(failed, join(datestamp_dir, 'cnv', 'seq2c-coverage.tsv'), wrapper=['sort'])
        failed = self._check_file(failed, join(datestamp_dir, 'cnv', 'seq2c_mapping_reads.txt'))
        failed = self._check_file(failed, join(datestamp_dir, 'cnv', 'cnvkit.tsv'), wrapper=['sort'])
        failed = self._check_file(failed, join(datestamp_dir, 'cnv', 'cnvkit.filt.tsv'), wrapper=['sort'])
        for caller, samples in callers.items():
            if all(s.endswith('-germline') for s in samples):
                failed = self._check_var_in_datestamp(failed, datestamp_dir, caller + '-germline')
            else:
                failed = self._check_var_in_datestamp(failed, datestamp_dir, caller)
            for sample in samples:
                failed = self._check_file(failed, join(datestamp_dir, 'reports', sample + '.html'), wrapper=html_wrapper, check_diff=False)
                sample_dir = join(bcbio_proj_dir, 'final', sample)
                self._check_var_in_sample(failed, sample_dir, sample, caller)

        assert not run_with_error, 'post-processing finished with error'
        assert not failed, 'some of file checks have failed'

        if exists(join(bcbio_proj_dir, 'work')):
            shutil.rmtree(join(bcbio_proj_dir, 'work'))

    def test_01_paired(self):
        self._test_dream_chr20('dream_chr21_paired',
                               callers={'vardict': ['syn3-tumor']}, eval_panel=True)

    def test_02_unpaired(self):
        self._test_dream_chr20('dream_chr21_unpaired',
                               callers={'freebayes': ['syn3-tumor', 'syn3-normal']}, parallel=True)

    def test_03_paired_with_germline(self):
        self._test_dream_chr20('dream_chr21_paired_with_germline',
                               callers={'vardict': ['syn3-tumor'], 'gatk-haplotype': ['syn3-normal-germline']})

    def test_04_rnaseq(self):
        bcbio_proj_dir, run_with_error = self._run_postproc(bcbio_dirname='rnaseq_hg38_hisat2')

        datestamp_name = '2017-08-13_rnaseq_hg38_hisat2'
        sample_name = 'brain100-1-1'
        datestamp_dir = join(bcbio_proj_dir, 'final', datestamp_name)
        sample_dir = join(bcbio_proj_dir, 'final', sample_name)

        failed = False
        failed = self._check_file(failed, join(datestamp_dir, 'tx2gene.csv'))
        failed = self._check_file(failed, join(datestamp_dir, 'expression', 'combined.counts'))
        failed = self._check_file(failed, join(datestamp_dir, 'expression', 'html', 'counts.html'), wrapper=['grep', '<td metric='])
        failed = self._check_file(failed, join(datestamp_dir, 'report.html'), check_diff=False)

        assert not run_with_error, 'post-rpocessing finished with error'
        assert not failed, 'some of the diffs have failed'

        if exists(join(bcbio_proj_dir, 'work')):
            shutil.rmtree(join(bcbio_proj_dir, 'work'))


# get rnaseq data:
'''
BED=/group/ngs/src/az.reporting-2.3/NGS_Reporting/ngs_reporting/reference_data/az_key_genes_plus_cosmic_census.hg38.bed.gz
PROJ=/gpfs/ngs/oncology/Analysis/dev/Dev_0354__Illumina_RNASeq_WTS_Brain-Jurkat_series/rnaseq_hg38/final
sambamba view $PROJ/brain100-1-1_S1/brain100-1-1_S1-ready.bam   -L <(gunzip -c $BED) -o brain100-1-1.bam  -f bam -F "not unmapped and proper_pair"
sambamba view $PROJ/jurkat100-1-5_S5/jurkat100-1-5_S5-ready.bam -L <(gunzip -c $BED) -o jurkat100-1-5.bam -f bam -F "not unmapped and proper_pair"
# samtools sort -n jurkat100-1-5.bam -O BAM > jurkat100-1-5.sorted.bam
bedtools bamtofastq -i jurkat100-1-5.bam -fq jurkat100-1-5_R1.fq -fq2 jurkat100-1-5_R2.fq
bedtools bamtofastq -i brain100-1-1.bam -fq brain100-1-1_R1.fq -fq2 brain100-1-1_R2.fq
'''

# Removed in gold standard:
'''
bash clean.sh dream_chr21_paired
'''
