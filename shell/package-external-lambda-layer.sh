mkdir python
pip install \
    --platform manylinux2014_x86_64 \
    --target=python/lib/python3.9/site-packages \
    --implementation cp \
    --python-version 3.9 \
    --only-binary=:all: --upgrade \
    -r ${2}/requirements.txt -t python/
zip -r ${1}-layer.zip python
aws s3 cp ${1}-layer.zip s3://quadball-os-packages/${1}.zip
rm -r python
rm ${1}-layer.zip