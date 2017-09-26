1="rnaseq_hg38_hisat2"

if [ -z "$1" ]; then
	echo "Usage: bash $0 name_of_bcbio_project"
else
	BASEDIR=$1  # BASEDIR=rnaseq_hg38_hisat2
	mv $BASEDIR $BASEDIR.bak
	rsync -tavz --exclude "*.fa" --exclude "*.bam" --exclude "work" --exclude "input" --exclude "final.*" --exclude "final_*" --exclude "final-*" \
		chi:/Sid/vsaveliev/bcbio_tests_rna/$BASEDIR/ $BASEDIR
	sed -i '' s%/Sid/vsaveliev/bcbio_tests_rna/$BASEDIR/input/%../input/%g $BASEDIR/config/$BASEDIR.yaml
	head -n 100 $BASEDIR/final/2017-08-13_$BASEDIR/tx2gene.csv > $BASEDIR/final/2017-08-13_$BASEDIR/tx2gene.csv2 && \
	         mv $BASEDIR/final/2017-08-13_$BASEDIR/tx2gene.csv2 $BASEDIR/final/2017-08-13_$BASEDIR/tx2gene.csv

	echo ""
	echo "To compare:"
	echo "diff -r --brief $BASEDIR $BASEDIR.bak"
fi
