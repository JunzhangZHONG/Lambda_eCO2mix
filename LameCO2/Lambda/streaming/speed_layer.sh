#spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,com.datastax.spark:spark-cassandra-connector_2.12:3.3.0 speed_layer.py
#spark-submit \
#  --master spark://spark-master:7077 \
#  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,com.datastax.spark:spark-cassandra-connector_2.12:3.3.0 \
#  speed_layer.py

spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0 \
  --conf spark.cassandra.connection.host=cassandra1 \
  --conf spark.cassandra.connection.port=9042 \
  --conf spark.eventLog.dir=file:/opt/spark/logs/spark-events \
  --conf spark.executor.memory=1G \
  --conf spark.driver.memory=1G \
  speed_layer.py eCO2mix