BASEDIR=dream_chr21
mv $BASEDIR $BASEDIR.bak
rsync -tavz --exclude "*.bam" --exclude "work" --exclude "input" --exclude "final_*" --exclude "final-*" chi:/Sid/vsaveliev/dream-chr21/ $BASEDIR
rm $BASEDIR/config/run_info_ExomeSeq.yaml
sed -i '' s%/Sid/vsaveliev/dream-chr21/input/%../input/%g $BASEDIR/config/dream-chr21.yaml
ln -s ../../../bams/syn3-normal-ready.bam $BASEDIR/final/syn3-normal/
ln -s ../../../bams/syn3-tumor-ready.bam $BASEDIR/final/syn3-tumor/
rm $BASEDIR/final/syn3-normal/syn3-normal-ready.bam.bai
rm $BASEDIR/final/syn3-tumor/syn3-tumor-ready.bam.bai
mkdir $BASEDIR/input
cp NGv3.chr21.4col.bed $BASEDIR/input

echo ""
echo "To compare:"
echo "diff -r --brief $BASEDIR $BASEDIR.bak"
