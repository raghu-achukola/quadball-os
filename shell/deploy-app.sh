aws s3 cp $WEBSERVER_PEM_LOCATION pemfile.pem
chmod 400 pemfile.pem
cd app
# todo -> this only works while we only add/modify files, we need to handle deletes
# replace folder (what about the venv we have there?) 
scp   -o "StrictHostKeyChecking no" -i "../pemfile.pem"  -r . "${WEBSERVER_EC2_HOST}:/home/ubuntu/qviewer"
# Find a more permanent solution than disabling StrictHostKeyChecking
ssh  -o "StrictHostKeyChecking no" -i "../pemfile.pem" $WEBSERVER_EC2_HOST "sudo systemctl restart qviewer"