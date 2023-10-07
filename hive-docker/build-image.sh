#!/bin/bash

echo ""

echo -e "\nbuild docker hadoop image\n"
sudo docker build -t nguyennam/hive:v1 .

echo ""