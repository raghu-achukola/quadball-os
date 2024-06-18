mkdir python
pip install -r ${2}/requirements.txt -t python/
zip -r ${1}-layer.zip python/*
aws s3 cp ${1}-layer.zip s3://quadball-os-packages/${1}.zip
rm -r python
rm ${1}-layer.zip