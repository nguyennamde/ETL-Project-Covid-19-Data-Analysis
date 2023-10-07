#!/bin/bash



# start hive container
sudo docker rm -f hive-server &> /dev/null
echo "start hive container..."
sudo docker run -itd \
                --net=hadoop \
                -p 10002:10002 \
                --name hive-server \
                --hostname hive-server \
                nguyennam/hive:v1 &> /dev/null

sudo docker exec -it hive-server bash
