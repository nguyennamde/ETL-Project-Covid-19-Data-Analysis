FROM ubuntu:latest

MAINTAINER Nguyennam <nguyennam250303@gmail.com>

WORKDIR /root

# install openjdk and wget
RUN apt-get update && apt-get install -y openjdk-11-jdk wget vim net-tools iputils-ping mysql-server

# install hadoop 2.7.2
RUN wget https://github.com/kiwenlau/compile-hadoop/releases/download/2.7.2/hadoop-2.7.2.tar.gz && \
    tar -xzvf hadoop-2.7.2.tar.gz && \
    mv hadoop-2.7.2 /usr/local/hadoop && \
    rm hadoop-2.7.2.tar.gz

# install hive 2.3.6
RUN wget https://archive.apache.org/dist/hive/hive-2.3.6/apache-hive-2.3.6-bin.tar.gz && \
    tar -zxvf apache-hive-2.3.6-bin.tar.gz && \
    mv apache-hive-2.3.6-bin /usr/local/hive && \
    rm apache-hive-2.3.6-bin.tar.gz

# set environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64 
ENV HADOOP_HOME=/usr/local/hadoop 

ENV HIVE_HOME=/usr/local/hive 
ENV PATH=$PATH:/usr/local/hive/bin:/usr/local/hive/sbin 

ENV CORE_CONF_fs_defaultFS=hdfs://hadoop-master:9000/

COPY conf_hive/* /tmp/
     
COPY conf_hadoop/* /tmp/

COPY drivers/* $HIVE_HOME/lib/

RUN mv /tmp/hadoop-env.sh /usr/local/hadoop/etc/hadoop/hadoop-env.sh && \
    mv /tmp/hdfs-site.xml $HADOOP_HOME/etc/hadoop/hdfs-site.xml && \ 
    mv /tmp/core-site.xml $HADOOP_HOME/etc/hadoop/core-site.xml && \
    mv /tmp/mapred-site.xml $HADOOP_HOME/etc/hadoop/mapred-site.xml && \
    mv /tmp/yarn-site.xml $HADOOP_HOME/etc/hadoop/yarn-site.xml
    

RUN mv /tmp/beeline-log4j2.properties $HIVE_HOME/conf/beeline-log4j2.properties && \
    mv /tmp/hive-env.sh $HIVE_HOME/conf/hive-env.sh && \ 
    mv /tmp/hive-exec-log4j2.properties $HIVE_HOME/conf/hive-exec-log4j2.properties && \
    mv /tmp/hive-log4j2.properties $HIVE_HOME/conf/hive-log4j2.properties && \
    mv /tmp/ivysettings.xml $HIVE_HOME/conf/ivysettings.xml && \
    mv /tmp/hive-site.xml $HIVE_HOME/conf/hive-site.xml && \
    mv /tmp/llap-daemon-log4j2.properties $HIVE_HOME/conf/llap-daemon-log4j2.properties  

ENTRYPOINT [ "sh", "-c", "service mysql start; sleep infinity"]


