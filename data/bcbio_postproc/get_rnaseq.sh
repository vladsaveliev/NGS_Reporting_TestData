BASEDIR=rnaseq
mv $BASEDIR $BASEDIR.bak
rsync -tavz --exclude "work" chi:/Sid/vsaveliev/RIA_0017/rnaseq_1_0_2a/ $BASEDIR
cd $BASEDIR
sed -i '' s%/Sid/vsaveliev/RIA_0017/rnaseq_1_0_2a/input/%../input/%g config/rnaseq_1_0_2a.yaml
rm -rf final/*/sailfish
head -n 100 final/2017-02-28_rnaseq_1_0_2a/combined.sf > final/2017-02-28_rnaseq_1_0_2a/combined.sf2 && mv final/2017-02-28_rnaseq_1_0_2a/combined.sf2 final/2017-02-28_rnaseq_1_0_2a/combined.sf

echo ""
echo "To compare:"
echo "diff -r --brief $BASEDIR $BASEDIR.bak"
