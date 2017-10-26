#!/usr/bin/env python
"""Prepare paired end fastq files from a chromosome region in an aligned input BAM file.
Useful for preparing test or other example files with subsets of aligned data.
Usage:
  bam_to_fastq_region.py <YAML config> <BAM input> <chromosome> <start> <end>
"""
import os
import sys
import contextlib

import yaml
import pysam
from Bio import Seq


def main(in_file, chrom, start, end):
    target_region = (chrom, int(start), int(end))
    for pair in [1, 2]:
        out_file = "%s_%s-%s.fastq" % (os.path.splitext(os.path.basename(in_file))[0],
                                       pair, target_region[0])
        with open(out_file, "w") as out_handle:
            for name, seq, qual in bam_to_fastq_pair(in_file, target_region, pair):
                out_handle.write("@%s/%s\n%s\n+\n%s\n" % (name, pair, seq, qual))

def bam_to_fastq_pair(in_file, target_region, pair):
    """Generator to convert BAM files into name, seq, qual in a region.
    """
    space, start, end = target_region
    bam_file = pysam.Samfile(in_file, "rb")
    for read in bam_file:
        if (not read.is_unmapped and not read.mate_is_unmapped
                and bam_file.getrname(read.tid) == space
                and bam_file.getrname(read.mrnm) == space
                and read.pos >= start and read.pos <= end
                and read.mpos >= start and read.mpos <= end
                and not read.is_secondary
                and read.is_paired and getattr(read, "is_read%s" % pair)):
            seq = Seq.Seq(read.seq)
            qual = list(read.qual)
            if read.is_reverse:
                seq = seq.reverse_complement()
                qual.reverse()
            yield read.qname, str(seq), "".join(qual)

def bam_to_fastq(in_file, runner):
    out_file = "%s.fastq" % os.path.splitext(in_file)[0]
    opts = [("INPUT", in_file),
            ("FASTQ", out_file)]
    runner.run("SamToFastq", opts)

if __name__ == "__main__":
    main(*sys.argv[1:])
