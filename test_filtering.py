import subprocess

import os
from os.path import dirname, join, exists, isfile, splitext, basename, isdir, relpath, getmtime, getsize, expanduser, \
    abspath

from ngs_utils.file_utils import add_suffix
from ngs_utils.testing import BaseTestCase, info, check_call, swap_output, swap_prev_symlink


class Test_varfilter(BaseTestCase):
    script = 'varfilter'

    data_dir = join(dirname(__file__), BaseTestCase.data_dir, script)
    results_dir = join(dirname(__file__), BaseTestCase.results_dir, script)
    gold_standard_dir = join(dirname(__file__), BaseTestCase.gold_standard_dir, script)
    source_dir = abspath(dirname(dirname(__file__)))

    def setUp(self):
        BaseTestCase.setUp(self)

    def _test(self, name, i_vcf=None, i_vcf2txt=None,
              sample=None, debug=True, reuse_intermediate=False,
              genome='hg19', threads=None, keep_work_dir=True, write_json=True,
              target_type=None):
        os.chdir(self.results_dir)
        o_dir = 'varfilter'
        if name: o_dir += '_' + name
        o_dir = join(self.results_dir, o_dir)
        cmdl = [self.script, '-o', o_dir]
        if i_vcf: cmdl.extend(['--vcf', join(self.data_dir, i_vcf)])
        if i_vcf2txt: cmdl.extend(['--vcf2txt', join(self.data_dir, i_vcf2txt)])

        if sample: cmdl.extend(['--sample', sample])
        if debug: cmdl.append('--debug')
        if reuse_intermediate: cmdl.append('--reuse')
        if genome: cmdl.extend(['-g', genome])
        if threads: cmdl.extend(['-t', str(threads)])
        if not write_json: cmdl.append('--no-write-json')
        if target_type:
            cmdl.extend(['--target-type', target_type])

        prev_o_dir = swap_output(o_dir)

        info('-' * 100)
        check_call(cmdl)
        info('-' * 100)
        info('')

        diff_failed = False
        variants_txt_name = 'vardict.txt'
        paths_to_check = [
            join(o_dir, variants_txt_name),
            join(o_dir, add_suffix(variants_txt_name, 'PASS')),
            join(o_dir, add_suffix(variants_txt_name, 'REJECT')),
        ]
        if write_json:
            paths_to_check.append(join(o_dir, splitext(add_suffix(variants_txt_name, 'PASS'))[0] + '.json'))
        for fpath in paths_to_check:
            try:
                self._check_file_throws(fpath)
            except (subprocess.CalledProcessError, AssertionError) as e:
                diff_failed = True
        assert not diff_failed, 'Some files are different with the gold standard'

        swap_prev_symlink(o_dir, prev_o_dir)

    def test_01(self):
        self._test('',
                   i_vcf='032269P-OVARIAN-P2mL-07-IDTUMI09_S1-vardict.anno.vcf.gz',
                   i_vcf2txt='032269P-OVARIAN-P2mL-07-IDTUMI09_S1.vardict.txt',
                   sample='032269P-OVARIAN-P2mL-07-IDTUMI09_S1',
                   genome='hg19',
                   target_type='panel')

    def test_02_with_damage(self):
        self._test('damage',
                   i_vcf='AURA-77-FFPE-vardict.anno.vcf.gz',
                   i_vcf2txt='AURA-77-FFPE.vardict.txt',
                   sample='AURA-77-FFPE',
                   genome='hg19',
                   write_json=False,
                   target_type='panel')


class Test_variants(BaseTestCase):
    script = 'variants'
    
    data_dir = join(dirname(__file__), BaseTestCase.data_dir, script)
    results_dir = join(dirname(__file__), BaseTestCase.results_dir, script)
    gold_standard_dir = join(dirname(__file__), BaseTestCase.gold_standard_dir, script)
    source_dir = abspath(dirname(dirname(__file__)))

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_01(self):
        inp_vcf = join(self.data_dir, 'syn3-vardict.vcf.gz')
        o_dir = join(self.results_dir, 'variants')
        cmdl = 'variants -o {o_dir} -g hg19 {inp_vcf} -t 1 -d'.format(**locals())
        os.chdir(self.results_dir)

        prev_o_dir = swap_output(o_dir)
        info('-' * 100)
        check_call(cmdl)
        info('-' * 100)
        info('')

        paths_to_check = [
            join(o_dir, 'vardict.txt'),
            join(o_dir, 'vardict.PASS.txt'),
            join(o_dir, 'vardict.REJECT.txt'),
        ]
        failed = False
        for fpath in paths_to_check:
            try:
                self._check_file_throws(fpath)
            except (subprocess.CalledProcessError, AssertionError) as e:
                failed = True
        assert not failed, 'Some files are not found'

        swap_prev_symlink(o_dir, prev_o_dir)


class Test_vardict2mut(BaseTestCase):
    script = 'vardict2mut'

    results_re = '{}.PASS.txt'
    json_results_re = '{}.PASS.json'
    reject_results_re = '{}.REJECT.txt'

    genome = 'hg19'

    data_dir = join(dirname(__file__), BaseTestCase.data_dir, script)
    results_dir = join(dirname(__file__), BaseTestCase.results_dir, script)
    gold_standard_dir = join(dirname(__file__), BaseTestCase.gold_standard_dir, script)

    def setUp(self):
        BaseTestCase.setUp(self)

    def _test(self, name, variants_txt, output_txt=None,
              debug=True, genome='hg19', threads=None, save_rejected=False,
              extra_opts=None, target_type=None):
        os.chdir(self.results_dir)
        cmdl = [self.script, join(self.data_dir, variants_txt)]

        base_name = splitext(basename(variants_txt))[0]

        output_txt = add_suffix(self.results_re.format(base_name), name)
        output_fpath = join(self.results_dir, output_txt)
        cmdl.extend(['-o', output_fpath])

        reject_fpath, json_results_fpath = None, None
        if save_rejected:
            reject_txt = add_suffix(self.reject_results_re.format(base_name), name)
            reject_fpath = join(self.results_dir, reject_txt)
            cmdl.extend(['--o-reject', reject_fpath])

        if debug: cmdl.append('--debug')
        if genome: cmdl.extend(['-g', genome])
        if threads: cmdl.extend(['-t', str(threads)])
        if extra_opts: cmdl.extend(extra_opts)
        if target_type: cmdl.extend(['--target-type', target_type])

        prev_output_fpath = swap_output(output_fpath)
        prev_reject_fpath, prev_json_results_fpath = None, None
        if reject_fpath:
            prev_reject_fpath = swap_output(reject_fpath)

        info('-' * 100)
        check_call(cmdl)
        info('-' * 100)
        info('')

        paths_to_check = [output_fpath] + ([reject_fpath] if reject_fpath else [])
        failed = False
        for fpath in paths_to_check:
            try:
                self._check_file_throws(fpath)
            except (subprocess.CalledProcessError, AssertionError) as e:
                failed = True
        assert not failed, 'Some files are not found'

        # if self.remove_work_dir_on_success and not reuse_intermediate and not reuse_output_dir:
        #     work_dir = join(output_dir, 'work')
        #     if not isdir(work_dir):
        #         info('Work dir for run ' + output_dirname + ' does not exist under ' + work_dir)
        #     else:
        #         shutil.rmtree(work_dir)

        swap_prev_symlink(output_fpath, prev_output_fpath)
        if reject_fpath and prev_reject_fpath:
            swap_prev_symlink(reject_fpath, prev_reject_fpath)

    def test_01(self):
        self._test('',
                   variants_txt='vardict.txt',
                   save_rejected=True,
                   target_type='panel')

    def test_02_keep_hla(self):
        self._test('keep_hla',
                   variants_txt='vardict.txt',
                   extra_opts=['--keep-hla'],
                   target_type='panel')

    def test_03_keep_intronic(self):
        self._test('keep_intronic',
                   variants_txt='vardict.txt',
                   extra_opts=['--keep-utr-intronic'],
                   target_type='panel')

    # def test_04_hg38(self):
    #     self._test('hg38',
    #                variants_txt='TCGA-FF-A7CQ-10A-01D-A385-10.txt',
    #                genome='hg38',
    #                save_rejected=True)


