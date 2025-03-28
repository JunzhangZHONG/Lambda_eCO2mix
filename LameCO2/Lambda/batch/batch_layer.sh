#!/bin/bash

spark-submit \
  --master spark://spark-master:7077 \
  --packages com.datastax.spark:spark-cassandra-connector_2.12:3.3.0 \
  --conf spark.cassandra.connection.host=cassandra1 \
  --conf spark.cassandra.connection.port=9042 \
  --conf spark.eventLog.dir=file:/opt/spark/logs/spark-events \
  --conf spark.executor.memory=1G \
  --conf spark.driver.memory=1G \
  batch_layer.py
