# batch_layer.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, expr, when, round as spark_round
from pyspark.sql.types import StructType, StructField, FloatType
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.functions import concat, lit

def main():
    spark = (SparkSession.builder
             .appName("BatchLayer")
             .config("spark.hadoop.fs.defaultFS", "hdfs://hadoop-namenode:8020") 
             # 这里可以指定 HDFS 地址，也可使用 Kafka/Cassandra 作为数据源
             .getOrCreate())

    # 1. 读取历史数据：比如从 HDFS 中读取
    #   也可以从 Kafka 的存档主题读取，或从 Cassandra/Hive 中拉取历史数据
    df = spark.read.parquet("hdfs://hadoop-namenode:8020/root/eco2mix-national-tr.parquet")
    
    # 2. 批处理逻辑：比如做某些聚合/清洗
    transformed_df = (df
        .withColumn("total_gen",
            col("fioul") + col("charbon") + col("gaz") + col("nucleaire")
            + col("eolien") + col("solaire") + col("hydraulique") + col("bioenergies")
        )
        .withColumn("renewable_gen",
            col("eolien") + col("solaire") + col("hydraulique") + col("bioenergies")
        )
        .withColumn("renewable_share",
            when(col("total_gen") > 0, spark_round((col("renewable_gen")/col("total_gen"))*100, 2))
            .otherwise(0)
        )
        # 使用 monotonically_increasing_id() 生成唯一的 record_id，并转换为字符串
        .withColumn("record_id", monotonically_increasing_id().cast("string"))
    )
    
    # 最终选择要写入Cassandra的字段
    final_df = transformed_df.select(
        "record_id",
        col("fioul").cast("float").alias("fioul"),
        col("charbon").cast("float").alias("charbon"),
        col("gaz").cast("float").alias("gaz"),
        col("nucleaire").cast("float").alias("nucleaire"),
        col("eolien").cast("float").alias("eolien"),
        col("solaire").cast("float").alias("solaire"),
        col("hydraulique").cast("float").alias("hydraulique"),
        col("bioenergies").cast("float").alias("bioenergies"),
        col("total_gen").cast("float").alias("total_gen"),
        col("renewable_gen").cast("float").alias("renewable_gen"),
        col("renewable_share").cast("float").alias("renewable_share")
    )
    
    # 例如，将结果写入Cassandra的my_keyspace.my_table（确保表结构已创建）
    (final_df.write
     .format("org.apache.spark.sql.cassandra")
     .option("keyspace", "my_keyspace")
     .option("table", "batch_table")
     .mode("append")
     .save())
    
    spark.stop()

if __name__ == "__main__":
    main()
