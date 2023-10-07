from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format, year, month, dayofmonth, concat, lower
import datetime as dt
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')
def createSparkSession():
    try:
        spark = SparkSession.\
                            builder.\
                            appName("Spark ETL").\
                            master("spark://spark-master:7077").\
                            config("hive.metastore.uris", "thrift://hive-server:9083").\
                            config("spark.sql.warehouse.dir", "hdfs://hadoop-master:9000/user/hive/warehouse").\
                            enableHiveSupport().\
                            getOrCreate()
        logging.info("SparkSession was be created successfully")
    except Exception:
        logging.error("Fail to create SparkSession")
    return spark


def extract_covid19_timeseries_mysql(spark):
    try:
        df_covid19_timeseries = spark.read \
                                     .format("jdbc") \
                                     .option("driver", "com.mysql.cj.jdbc.Driver") \
                                     .option("url", "jdbc:mysql://c-mysql:3306/covid19") \
                                     .option("dbtable", "covid19_timeseries") \
                                     .option("user", "root") \
                                     .option("password", "123") \
                                     .load()
        logging.info("Read covid19_timeseries from mysql successfully")
    except Exception:
        logging.warning("Couldn't read covid19_timeseries from mysql")
        
    return df_covid19_timeseries
def extract_worldometer_mysql(spark):
    try:
        df_worldometer = spark.read \
                              .format("jdbc") \
                              .option("driver", "com.mysql.cj.jdbc.Driver") \
                              .option("url", "jdbc:mysql://c-mysql:3306/covid19") \
                              .option("dbtable", "worldometer") \
                              .option("user", "root") \
                              .option("password", "123") \
                              .load()
        logging.info("Read worldometer from mysql successfully")
    except Exception:
        logging.warning("Couldn't read worldometer from mysql")
    return df_worldometer
def load_to_datalake(raw_data, name_table):
    try:
        raw_data.write \
         .format("parquet") \
         .mode("overwrite") \
         .save(f"hdfs://hadoop-master:9000/datalake/{name_table}")
        logging.info(f"load {name_table} to datalake successfully")
    except Exception:
        logging.warning(f"Couldn't load {name_table} to datalake")
    
    


def extract_datalake(spark, name_table):
    try:
        df = spark.read \
                  .format("parquet") \
                  .load(f"hdfs://hadoop-master:9000/datalake/{name_table}")
        logging.info(f"Read {name_table} from datalake successfully")
    except Exception:
        logging.warning(f"Couldn't read {name_table} from datalake")
    return df



def transform(df_covid19_timeseries, df_worldometer):
    cleaned_worldometer = df_worldometer.select(col("country") \
                                           , col("continent") \
                                           , col("2020_population"))

    
    cleaned_covid19_timeseries = df_covid19_timeseries \
                            .filter((col("confirmed") != 0) \
                                    | (col("deaths") != 0) \
                                    | (col("active") != 0))
    cleaned_covid19_timeseries = cleaned_covid19_timeseries.withColumn("date", col("date") \
                                           .cast("date"))
    cleaned_covid19_timeseries = cleaned_covid19_timeseries.withColumn("date_id" \
                                           , date_format(col("date"), "yyyyMMdd"))
    cleaned_covid19_timeseries = cleaned_covid19_timeseries.withColumn("year", year(col("date"))) \
                               .withColumn("month", month(col("date"))) \
                               .withColumn("day", dayofmonth(col("date")))
    cleaned_covid19_timeseries = cleaned_covid19_timeseries.drop("date")
    cleaned_covid19_timeseries = cleaned_covid19_timeseries.withColumn("who_id", lower(col("who_region")) \
                                                                       .substr(0,3))
    
    cleaned_data = cleaned_covid19_timeseries.join(cleaned_worldometer, "country", "inner")
    cleaned_data = cleaned_data.withColumn("pop_loc_id", lower(concat(col("country").substr(0,2) \
                           , col("lat_").cast("int") \
                           , col("long_").cast("int"))))
    return cleaned_data

def create_fact_table(cleaned_data):
    fact_covid = cleaned_data.select(col("uuid") \
                                    , col("date_id") \
                                    , col("who_id") \
                                    , col("pop_loc_id") \
                                    , col("confirmed") \
                                    , col("deaths") \
                                    , col("recovered") \
                                    , col("active"))
    return fact_covid
def create_dimensional_table(cleaned_data):
    dim_date = cleaned_data.select(col("date_id") \
                                     , col("year") \
                                     , col("month") \
                                     , col("day")) \
                        .dropDuplicates()
    
    dim_who_region = cleaned_data.select(col("who_id") \
                                  , col("who_region")) \
                             .dropDuplicates()
    
    dim_location = cleaned_data.select(col("pop_loc_id") \
                                  , col("country") \
                                  , col("continent") \
                                  , col("lat_") \
                                  , col("long_")) \
                             .dropDuplicates()
    
    dim_population = cleaned_data.select(col("pop_loc_id") \
                                  , col("2020_population")) \
                             .dropDuplicates()
    
    return dim_date, dim_who_region, dim_location, dim_population





def load_to_warehouse(fact_covid, dim_date, dim_who_region, dim_location, dim_population):
    fact_covid = fact_covid.repartition(3)
    dim_date = dim_date.repartition(3)
    dim_who_region = dim_who_region.repartition(3)
    dim_location = dim_location.repartition(3)
    dim_population = dim_population.repartition(3)
    # spark.sql("create database if not exists covid19;")
    fact_covid.write \
              .format("hive") \
              .mode("overwrite") \
              .saveAsTable("covid19.fact_covid")
    dim_date.write \
              .format("hive") \
              .mode("overwrite") \
              .saveAsTable("covid19.dim_date")
    dim_who_region.write \
              .format("hive") \
              .mode("overwrite") \
              .saveAsTable("covid19.dim_who_region")
    dim_location.write \
              .format("hive") \
              .mode("overwrite") \
              .saveAsTable("covid19.dim_location")
    dim_population.write \
              .format("hive") \
              .mode("overwrite") \
              .saveAsTable("covid19.dim_population")


if __name__ == "__main__":
    spark = createSparkSession()
    # print("Extracting data from mysql...")
    df_covid19_timeseries = extract_covid19_timeseries_mysql(spark)
    df_worldometer = extract_worldometer_mysql(spark)
    # print("Loading raw data to datalake...")
    load_to_datalake(df_covid19_timeseries, "covid19_timeseries")
    load_to_datalake(df_worldometer, "worldometer")
    # print("Running ETL process...")
    raw_covid19_timeseries = extract_datalake(spark, "covid19_timeseries")
    raw_worldometer = extract_datalake(spark, "worldometer")
    cleaned_data = transform(raw_covid19_timeseries, raw_worldometer)
    fact_covid = create_fact_table(cleaned_data)
    dim_date, dim_who_region, dim_location, dim_population = create_dimensional_table(cleaned_data)
    load_to_warehouse(fact_covid, dim_date, dim_who_region, dim_location, dim_population)
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%m:%S")
    print("-"*50)
    print("|" + " "*49 + "|")
    print("|              Finish ETL Process" + " " * (50-33) + "|")
    print(f"|        Running At: {now}" + " " * (50-40) + "|")
    print("|" + " "*49 + "|")
    print("-"*50)

