## Project Summary
## Buidling ETL Pipeline for Data Warehouse: Covid19
### Goal of the project

This project aims to building a Data Warehouse by perform ETL process

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/Outline.jpeg)

The project follows the follow steps:

Step 1: Define the Business Problem

Step 2: Define Data Requirements Gather Data from data sources

Step 3: Project Design:

- Step 3.1: Building Data Pipeline
  
- Step 3.2: Orchestration and Workflow Management

- Step 3.3: Adding Unit Test to Pipeline
  
Step 4: Conclusion

## Step 1: Define the Business Problem
### Business Problem

In this project, i will take covid19_timeseries(2020) dataset, enriching with worldometer_data dataset to create a data analytics table that can help answer questions like:

-	Compare the number of infections in countries?
-	Is there a correlation between the total population and the number of infections?

Because the impact of covid 19 was so huge in 2020 around the world, I wanted to make a chart to be able to track the spread of covid19 around the world.


For this project, I have applied what I learned on Spark, data warehouse to build an ETL pipeline for, data warehouse hosted on HDFS throught hive.

## Step 2: Define Data Requirements

- Covid19 All Over The World: Structured
- Continent, Population information: Structured 

### Data Sources

- covid19_timeseries_world(2020)
- worldometer_data
  
## Step 3: Project Design

### 3.1 Building Data Pipeline

#### Data Flow Diagram(DFD)

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/ETL%20diagram.png)

#### Description

All processing steps are orchestrated by using Airflow, and I have also Dockerized using pure Docker all services used to ensure compatibility as much as possible.

Regarding the database, I will load dataset into mysql to simulate business data, in warehouse i choose Apache Hive to save metastore and using HDFS as data warehouse, Hive can perform some queries in warehouse directly throught beeline or presto, In datalake, i will choose Hadoop(HDFS) to save raw data.

I will use Spark to extract data from MySQL and load into Datalake, Afterward, i will connect spark with datalake to extract data for further transformation and load to data warehouse.

Transformed data will be loaded into warehouse for further analysis.

My Stragery for load data is full load strategy, because load entire data into datalake/datawarehouse, so create folder structure without partitioning.

#### Architecture

In this project i will use Two-tier architecture, This architecture is called two-tier because we have 2 databases in storage layers: data lake and data warehouse.

In this case, Datalake as a object storage, and data warehouse as a analytics database(OLAP)

Two-tier architecture always consists of 2 steps ETL steps:
- Step 1: Extract from databases and load to a data lake
- Step 2: Extract from data lake, transform and load to a data warehouse

#### Data warehouse with Dimensional data modeling

- For this project, the Dimensional data model is attached as a png file. I'm using a Star Schema. A fact_covid table as the fact table and dim_location, dim_date and dim_population, dim_continent as the dimensional tables.
  
  ![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/Dimesional%20model.png)
  
- Why I choose Star schema over snowflake schema is because:
  1. Star schema is more efficient and a better way to organize the data in the data warehouse.
  2. Because they are superfast, simple design that I was looking for to combine my fact and dimension tables.
    
#### Setup the infrastructure local manually

In this project i have manually set up Bigdata Platform: Hadoop, Hive, Spark on Docker and MySQL consist of 8 container:

MySQL:

  - 1 container: mysql
    
Hadoop:

  - 3 container: hadoop-master, hadoop-slave1, hadoop-slave2
    
Spark:

  - 3 container: spark-master, spark-worker1, spark-notebook(used to run code for testing)
    
Hive:

  - 1 container: hive-server


There will now be 8 services running

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/8-container.png)

Next, i wil set up airflow on docker to orchestrate and automate ETL job: Airflow consist of 7 container:

Airflow:

  - 7 container: airflow-init, airflow-scheduler, airflow-triggerer, airflow-webserver, airflow-worker, postgres, redis

This setup i have followed the following link: [Setup Airflow On Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/airflow-container.png)

To run this project:

    git clone https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis.git
    
    cd ETL-Project-Covid-19-Data-Analysis
    
    docker network create --driver bridge bigdata
    
    docker-compose up -d
    
    cd airflow-docker

    docker-compose build
    
    docker-compose up -d


Run hive service:

    docker exec -it hive-server mysql

    create user "hiveuser"@"%" identified by "nguyennam";
    grant all privileges on *.* to "hiveuser"@"%";
    exit

    # initialize schema for mysql as metastore
    docker exec -it hive-server schematool -initSchema --dbType mysql

    # run hiveserver2 in background
    docker exec -it hive-server nohup hiveserver2 &

    # run metastore in background
    docker exec -it hive-server nohup hive --service metastore &


Create user spark and airflow in group spark in hadoop:

    docker exec -it hadoop-master groupadd hadoop
    docker exec -it hadoop-master useradd -m -G hadoop spark
    docker exec -it hadoop-master useradd -m -G hadoop airflow

Create spark-logs in hdfs to save log history of spark:

    docker exec -it hadoop-master hdfs dfs -mkdir /spark-logs

Create datalake in hdfs:

    docker exec -it hadoop-master hdfs dfs -mkdir /datalake

grant permission for group spark:

    docker exec -it hadoop-master hdfs dfs -chown -R :hadoop /spark-logs
    docker exec -it hadoop-master hdfs dfs -chown -R :hadoop /datalake

    docker exec -it hadoop-master hdfs dfs -chmod -R 775 /spark-logs
    docker exec -it hadoop-master hdfs dfs -chmod -R 775 /datalake


First, i will import dataset covid19_timeseries_world(2020), worldometer_data (csv format) into mySQL:
  
  Enter mysql cli
  
    docker exec -it c-mysql mysql --local-infile=1 -u root -p123

    create database covid19;

    SET GLOBAL local_infile=true;
    -- Check if local_infile is turned on 
    SHOW VARIABLES LIKE "local_infile"; 
    exit

  Copy cleaned_data and load_dataset folder into /tmp/ of c-mysql

    docker cp ./data/cleaned_data c-mysql:/tmp/
    docker cp ./load_dataset_mysql c-mysql:/tmp/

Second, Initialize the Schema for covid19 and worldometer table and load data in MySQL

    docker exec -it c-mysql mysql --local-infile=1 -u root -p123 covid19 -e"source /tmp/load_dataset_mysql/mysql_create_schema.sql"
    docker exec -it c-mysql mysql --local-infile=1 -u root -p123 covid19 -e"source /tmp/load_dataset_mysql/mysql_load_dataset.sql"

    # Check whether data is loaded into table

    docker exec -it c-mysql mysql -u root -p123 covid19 -e"select * from covid19_timeseries limit 5; select * from worldometer limit 5;"


Third, Create Database in Hive and grant privileges

    docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000 -e"create database if not exists covid19;"

    docker exec -it hadoop-master hdfs dfs -chown -R :hadoop /user/hive/warehouse
    docker exec -it hadoop-master hdfs dfs -chmod -R 775 /user/hive/warehouse


#### Detailed code walkthrough

##### EL to Datalake

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/EL%20to%20datalake.png)

##### ETL to Data Warehouse

###### Extract

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/extract.png)

###### Transform

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/transform.png)

###### Load

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/load.png)

### 3.1 Orchestration and Workflow Management

First, Write dag script in python to automate ETL task using SparkSubmitOperator

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/dag_script.png)

Second, create connection between airflow and spark

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/create_connection_airflow_spark.png)

Last, Trigger dag to run

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/output-airflow.png)

Result in warehouse

<img width="1373" alt="image" src="https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/assets/95016684/0f80c943-0682-44bf-9e9a-613d7988792b">

### Adding Unit Test to Pipeline

Write python script to test dag airflow

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/unit_test_dag.png)


Run unit test

    docker exec -it airflow-docker-airflow-webserver-1 bash

    cd tests

    pytest

## Step 4: Conclusion

After setting up data pipeline sucessfully, I'm going to answer some questions that I've made a previous question

I'm going to use SparkSQL to query directly in warehouse

### Map tracking the spread of covid19 worldwide

Join the necessary tables to draw the map

<img width="648" alt="image" src="https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/assets/95016684/5b950616-7978-4446-b14b-cba964194497">

Creating map

<img width="799" alt="image" src="https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/assets/95016684/bd268095-08b1-4801-bb44-18315c9c2ba6">

Result

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/map_covid19.png)

![image](https://github.com/nguyennamde/ETL-Project-Covid-19-Data-Analysis/blob/main/assets/map_covid2.png)


#### This project helped me to understand better how ETL process works and have experience to build ETL Pipeline, Data Warehouse Thanks for reading my project!!!


