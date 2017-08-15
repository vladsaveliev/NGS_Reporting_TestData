if [ -z "$1" ]; then
	echo "Usage: bash $0 name_of_bcbio_project"
else
	BASEDIR=$1  # BASEDIR=rnaseq_hg19_star
	mv $BASEDIR $BASEDIR.bak
	rsync -tavz --exclude "work" chi:/Sid/vsaveliev/bcbio_tests_rna/$BASEDIR/ $BASEDIR
	cd $BASEDIR
	sed -i '' s%/Sid/vsaveliev/bcbio_tests_rna/$BASEDIR/input/%../input/%g config/$BASEDIR.yaml
	rm -rf final/*/sailfish/*
	head -n 100 final/2017-02-28_$BASEDIR/combined.sf > final/2017-02-28_$BASEDIR/combined.sf2 && \
	         mv final/2017-02-28_$BASEDIR/combined.sf2 final/2017-02-28_$BASEDIR/combined.sf

	echo ""
	echo "To compare:"
	echo "diff -r --brief $BASEDIR $BASEDIR.bak"
fi
