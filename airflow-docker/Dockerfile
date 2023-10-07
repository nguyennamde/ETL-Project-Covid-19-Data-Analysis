FROM apache/airflow:2.7.1-python3.9
USER root

# Install OpenJDK-11
RUN apt update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get install -y ant && \
    apt-get clean;

RUN curl -O https://dlcdn.apache.org/spark/spark-3.4.1/spark-3.4.1-bin-hadoop3.tgz \
    && tar zxvf spark-3.4.1-bin-hadoop3.tgz \
    && rm -rf spark-3.4.1-bin-hadoop3.tgz \
    && mv spark-3.4.1-bin-hadoop3/ /opt/spark/

# Set JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-arm64/
ENV SPARK_HOME /opt/spark/

RUN export JAVA_HOME
RUN export SPARK_HOME

USER airflow

COPY ./requirements.txt /
COPY ./drivers/mysql-connector-j-8.0.33.jar /opt/spark/jars/
RUN pip install -r /requirements.txt
