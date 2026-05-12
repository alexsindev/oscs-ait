#!/bin/bash
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user
docker run -d -p 80:5000 --name retail-data st125052/retail-data:latest-deployment