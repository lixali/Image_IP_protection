#!/bin/bash
echo "hi from shell script"
echo "hello from shell script"

#ssh -X ubuntu@ec2-18-213-112-144.compute-1.amazonaws.com
cd /home/ubuntu/image_ID_protection
python search.py -t ./ -a img_hash_dictionary.pickle -q ../flask-example-master/static/usr_upload/$1 -s 32 -d 10
