#!/bin/bash

. "/opt/spark/bin/load-spark-env.sh"

if [ "$SPARK_WORKLOAD" == "master" ];
then

export SPARK_MASTER_HOST=`hostname`

cd /opt/spark/bin && ./spark-class org.apache.spark.deploy.master.Master --ip $SPARK_MASTER_HOST --port $SPARK_MASTER_PORT --webui-port $SPARK_MASTER_WEBUI_PORT >> $SPARK_MASTER_LOG

elif [ "$SPARK_WORKLOAD" == "worker" ];
then

cd /opt/spark/bin && ./spark-class org.apache.spark.deploy.worker.Worker --webui-port $SPARK_WORKER_WEBUI_PORT $SPARK_MASTER >> $SPARK_WORKER_LOG

elif [ "$SPARK_WORKLOAD" == "submit" ];
then
    echo "SPARK SUBMIT"
else
    echo "Undefined Workload Type $SPARK_WORKLOAD, must specify: master, worker, submit"
fi
# entrypoint.sh: 根据SPARK_WORKLOAD启动Master或Worker

#if [ "$SPARK_WORKLOAD" == "master" ]; then
#  echo "Starting Spark Master..."
#  ${SPARK_HOME}/sbin/start-master.sh \
#    --ip 0.0.0.0 \
#    --port 7077 \
#    --webui-port 8080
  # 阻塞以防容器退出
#  tail -f /dev/null

#elif [ "$SPARK_WORKLOAD" == "worker" ]; then
#  echo "Starting Spark Worker..."
  # 如果环境变量中没指定SPARK_MASTER地址，默认连spark-master:7077
#  if [ -z "$SPARK_MASTER" ]; then
#    SPARK_MASTER="spark://spark-master:7077"
#  fi
#  ${SPARK_HOME}/sbin/start-worker.sh \
#    $SPARK_MASTER \
#    --webui-port 8080
#  tail -f /dev/null

#else
  # 如果既不是master也不是worker，就执行传入的命令
#  echo "No SPARK_WORKLOAD specified, running default command: $@"
#  exec "$@"
#fi
