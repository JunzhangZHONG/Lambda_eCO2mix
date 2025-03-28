# speed_layer.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, expr, when, round as spark_round
from pyspark.sql.types import StructType, StructField, FloatType
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.functions import concat, lit


# 1. 创建SparkSession，并指定Cassandra连接配置
spark = (SparkSession.builder
         .appName("SpeedLayer")
         # 替换为你的Cassandra容器主机名/IP
         .config("spark.cassandra.connection.host", "cassandra1")
         .getOrCreate())

# 2. 定义与producer_f.py发送的JSON结构对应的Schema
schema = StructType([
    StructField("fioul", FloatType(), True),
    StructField("charbon", FloatType(), True),
    StructField("gaz", FloatType(), True),
    StructField("nucleaire", FloatType(), True),
    StructField("eolien", FloatType(), True),
    StructField("solaire", FloatType(), True),
    StructField("hydraulique", FloatType(), True),
    StructField("bioenergies", FloatType(), True)
])

# 3. 从Kafka读取流数据
kafka_df = (spark
    .readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:29092")  # 替换为你的Kafka地址
    .option("subscribe", "eCO2mix")                   # 替换为你的Topic名称
    .load()
    # 这里同时选出 Kafka 自带的 offset、partition
    .selectExpr("CAST(value AS STRING) AS json_str", "offset", "partition")
)

# 4. 解析Kafka消息（JSON字符串 -> DataFrame列）
parsed_df = (kafka_df
    # 先保留 offset, partition, 以及 json_str
    .select(
        col("json_str"),
        col("offset"),
        col("partition")
    )
    # 对 json_str 做 JSON 解析
    .select(
        from_json(col("json_str"), schema).alias("data"),
        "offset",
        "partition"
    )
    # 拆分到字段
    .select("data.*", "offset", "partition")
)

# 5. 计算总发电量、可再生能源总量、可再生能源占比
#    若 total_gen=0，则可再生能源占比=0
transformed_df = (parsed_df
    .withColumn("total_gen",
        col("fioul") + col("charbon") + col("gaz") + col("nucleaire")
        + col("eolien") + col("solaire") + col("hydraulique") + col("bioenergies")
    )
    .withColumn("renewable_gen",
        col("eolien") + col("solaire") + col("hydraulique") + col("bioenergies")
    )
    .withColumn("renewable_share",
        # 当 total_gen>0 时计算占比，否则为0
        when(col("total_gen") > 0, spark_round((col("renewable_gen")/col("total_gen"))*100, 2))
        .otherwise(0)
    )
    .withColumn("record_id", concat(col("partition"), lit("-"), col("offset")))
)

final_df = transformed_df.select(
    "record_id",
    "fioul",
    "charbon",
    "gaz",
    "nucleaire",
    "eolien",
    "solaire",
    "hydraulique",
    "bioenergies",
    "total_gen",
    "renewable_gen",
    "renewable_share"
)

# 6. 将结果写入Cassandra
#    需在Cassandra中有对应表结构(见后文)
print(final_df)

query = (final_df
    .writeStream
    .format("org.apache.spark.sql.cassandra")
    .option("keyspace", "my_keyspace")   # 替换为你的Keyspace
    .option("table", "my_table")        # 替换为你的Table
    .option("checkpointLocation", "/tmp/checkpoints/speed_layer") # 为了容错，需指定checkpoint目录
    .outputMode("append")
    .start()
)



query.awaitTermination()
