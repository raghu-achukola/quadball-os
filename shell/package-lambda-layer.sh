# To run from root of folder
mkdir python
cd ${2}
pip install -r requirements.txt -t ../python/ --platform manylinux2010_x86_64 --only-binary=:all:
cp -r . ../python/${2}/
cd ..
zip -r ${1}-layer.zip python/
aws s3 cp ${1}-layer.zip s3://quadball-os-packages/${1}.zip