#!/bin/bash
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user
docker run -d -p 80:3000 --name metabase metabase/metabase