import os
from os.path import dirname, join, exists, isfile, splitext, basename, isdir, relpath, getmtime, getsize, realpath, \
    abspath, expanduser
import shutil

from ngs_utils.testing import BaseTestCase, info, check_call, swap_output


class BaseTest_prealign(BaseTestCase):
    script = 'prealign'

    data_dir = join(dirname(__file__), BaseTestCase.data_dir, script)
    results_dir = join(dirname(__file__), BaseTestCase.results_dir, script)
    gold_standard_dir = join(dirname(__file__), BaseTestCase.gold_standard_dir, script)
    source_dir = abspath(dirname(dirname(__file__)))

    def setUp(self):
        os.environ['PATH'] = self.source_dir + '/venv_ngs_reporting/bin:' + expanduser('~/bin') + ':/usr/local/bin:/usr/bin:/bin:/usr/sbin:' + os.environ['PATH']
        BaseTestCase.setUp(self)


class Test_hiseq(BaseTest_prealign):
    ds_project_name = 'TATTON_MEDI_ASIA'
    ds_sample_names = ['NA12878EnzymeFrag_20min', 'TATTON_100', 'Colo-829'],
    genome = 'hg19-chr21'

    def setUp(self):
        BaseTest_prealign.setUp(self)

    def _test(self, name, dirpath, analysis_dir=None, project_name=None,
              hiseq4000_conf=None, jira=None, bed=None, samplesheet=None,
              debug=False, reuse_intermediate=False,
              threads=None, keep_work_dir=True):
        info('Starting ' + name)

        #
        # Checking and cleaning previous runs
        #
        dirpath = realpath(dirpath)

        expected_ds_proj_dirpath = dirpath
        if 'Unaligned' not in dirpath:
            expected_ds_proj_dirpath = join(dirpath, 'Unalign', 'Project_' + self.ds_project_name)

        expected_fastq_dirpath = join(expected_ds_proj_dirpath, 'fastq')
        if not reuse_intermediate and isdir(expected_fastq_dirpath):
            shutil.rmtree(expected_fastq_dirpath)

        expected_output_dir = join(dirpath, 'prealign')
        if analysis_dir:
            expected_analysis_dir = analysis_dir
            expected_output_dir = join(analysis_dir, 'prealign')
        elif project_name:
            expected_analysis_dir = join(expected_output_dir, project_name)
        else:
            expected_analysis_dir = None

        if expected_analysis_dir and exists(expected_analysis_dir):
            swap_output(expected_analysis_dir)
        elif expected_output_dir and exists(expected_output_dir):
            swap_output(expected_output_dir)

        #
        # Running
        #
        os.chdir(self.results_dir)
        cmdl = [self.script, dirpath]
        cmdl.extend(['-g', self.genome])
        if analysis_dir:
            cmdl.extend(['-o', analysis_dir])
        if project_name:
            cmdl.extend(['--project-name', project_name])
        if hiseq4000_conf:
            cmdl.extend(['--conf', hiseq4000_conf])
        if bed:
            cmdl.extend(['--bed', bed])
        if samplesheet:
            cmdl.extend(['--samplesheet', samplesheet])
        if debug:
            cmdl.append('--debug')
        if reuse_intermediate:
            cmdl.append('--reuse')
        if jira:
            cmdl.extend(['--jira', jira])
        if threads:
            cmdl.extend(['-t', str(threads)])

        info('-' * 100)
        check_call(cmdl)
        info('-' * 100)
        info('')

        #
        # Checking results
        #
        self._check_dir_not_empty(expected_fastq_dirpath)
        self._check_dir_not_empty(expected_output_dir)
        if expected_analysis_dir: self._check_dir_not_empty(expected_analysis_dir)

        self._check_dir_not_empty(join(expected_output_dir, 'Downsample_TargQC'))
        self._check_dir_not_empty(join(expected_output_dir, 'FastQC'))
        assert exists(join(expected_fastq_dirpath, 'FastQC'))  # symlink
        assert realpath(join(expected_fastq_dirpath, 'FastQC')) == join(expected_output_dir, 'FastQC')

        self._check_file_throws(join(expected_output_dir, 'multiqc_report.html'))

        # if self.remove_work_dir_on_success and not reuse_intermediate and not reuse_output_dir:
        #     work_dir = join(output_dir, 'work')
        #     if not isdir(work_dir):
        #         info('Work dir for run ' + output_dirname + ' does not exist under ' + work_dir)
        #     else:
        #         shutil.rmtree(work_dir)

    def test_01_hiseq(self):
        self._test('hiseq',
            dirpath=join(self.data_dir, 'datasets/HiSeq/150612_D00443_0168_AHMNFGADXX'),
            analysis_dir=join(self.results_dir, 'Dev_0001_TATTON_MEDI_ASIA'),
                   )

    def test_01_hiseq_no_o(self):
        self._test('hiseq_no_o',
            dirpath=join(self.data_dir, 'datasets/HiSeq/150612_D00443_0168_AHMNFGADXX'),
            project_name='Dev_0001_TATTON_MEDI_ASIA',
                   )

    def test_01_hiseq_no_o_no_projname(self):
        self._test('hiseq_no_o_no_projname',
            dirpath=join(self.data_dir, 'datasets/HiSeq/150612_D00443_0168_AHMNFGADXX'),
                   )



