if [ ! -z "$1" ]; then
	DIR=$1
	rm -r $DIR/input $DIR/work $DIR/final/*/log/multiqc_bcbio/multiqc_report.html $DIR/final/*/*.bam*
	rm -r $DIR/final/*/cnv/*-cnvkit.{cnr,vcf}
else
	echo "Usage: bash $0 path_to_bcbio_project"
fi
