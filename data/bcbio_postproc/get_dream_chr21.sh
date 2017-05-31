BASEDIR=dream_chr21
mv $BASEDIR $BASEDIR.bak
rsync -tavz --exclude "*.bam" --exclude "work" chi:/Sid/vsaveliev/dream-chr21/ $BASEDIR
cd $BASEDIR
sed -i '' s%/Sid/vsaveliev/dream-chr21/input/%../input/%g config/dream-chr21.yaml
rm config/run_info_ExomeSeq.yaml
cp ~/googledrive/az/analysis/dream_chr21/bams/syn3-normal-ready.key_genes_cds.bam final/syn3-normal/syn3-normal-ready.bam
cp ~/googledrive/az/analysis/dream_chr21/bams/syn3-tumor-ready.key_genes_cds.bam final/syn3-tumor/syn3-tumor-ready.bam
rm final/syn3-normal/syn3-normal-ready.bam.bai
rm final/syn3-tumor/syn3-tumor-ready.bam.bai
rm input
mkdir input
cp ~/googledrive/az/analysis/dream_chr21/input/NGv3.chr21.4col.bed input

echo ""
echo "To compare:"
echo "diff -r --brief $BASEDIR $BASEDIR.bak"
