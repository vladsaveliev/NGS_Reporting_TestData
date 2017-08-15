if [ -z "$1" ]; then
	echo "Usage: bash $0 path_to_bcbio_project"
else
	BASEDIR=$1
	mv $BASEDIR $BASEDIR.bak
	rsync -tavz --exclude "*.bam" --exclude "work" --exclude "input" --exclude "final_*" --exclude "final-*" \
		chi:/Sid/vsaveliev/bcbio_tests_dna/$BASEDIR/ $BASEDIR
	rm $BASEDIR/config/run_info_ExomeSeq.yaml
	sed -i '' s%/Sid/vsaveliev/$BASEDIR/input/%../input/%g $BASEDIR/config/$BASEDIR.yaml
	cp bams/syn3-tumor-ready.bam $BASEDIR/final/syn3-tumor/
	cp bams/syn3-normal-ready.bam $BASEDIR/final/syn3-normal/
	cp bams/syn3-normal-germline-ready.bam $BASEDIR/final/syn3-normal-germline/
	rm $BASEDIR/final/syn3-tumor/syn3-tumor-ready.bam.bai
	rm $BASEDIR/final/syn3-normal/syn3-normal-ready.bam.bai
	rm $BASEDIR/final/syn3-normal-germline/syn3-normal-germline-ready.bam.bai
	mkdir $BASEDIR/input
	cp NGv3.chr21.4col.bed $BASEDIR/input

	echo ""
	echo "To compare:"
	echo "diff -r --brief $BASEDIR $BASEDIR.bak"
fi