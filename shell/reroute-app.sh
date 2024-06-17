aws s3 cp $WEBSERVER_PEM_LOCATION pemfile.pem
chmod 400 pemfile.pem
scp   -o "StrictHostKeyChecking no" -i "pemfile.pem"  app/routing/nginx_routing.txt /tmp/nginx_routing.txt
ssh  -o "StrictHostKeyChecking no" -i "pemfile.pem" $WEBSERVER_EC2_HOST "sudo mv /tmp/nginx_routing.txt /etc/nginx/sites-available/default && sudo systemctl restart nginx"
