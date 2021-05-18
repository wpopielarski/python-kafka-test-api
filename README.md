The repository contains sample code showing how to process JSON message using Spark and Kafka (and to be more specific using Spark Structured Streaming and Kafka).

Below you can find descriptions of different files stored in the repository.

### kafka_json_producer.py
Creates sample JSONs and stores it to kafka topic or filesystem directory.

### file_triggered_spark_kafka_streaming.py
Monitors a directory and when it finds a new file in that directory it sends it to kafka topic.

### spark_kafka_streaming.py
It monitors a kafka topic. When it finds a new message there it consumes it, does some processing and stores a new message to a new kafka topic.

## Usage

### Prerequisites
* create the topics where you want to produce to / consumer from (unless auto-creation is enabled)
* create required directories where the json files are going to be stored

### Producing sample messages

```
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
python3 json_producer.py --destination dir --output-dir json-input-path
ls -ltr json-input-path/
````
After the messages you can send it to HDFS directory, which is going to be used as input directory for the spark job.

### Running the spark job
```
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
export SPARK_MAJOR_VERSION=2
spark-submit --master yarn \
--jars spark-sql-kafka-0-10_2.11-2.3.0.jar,kafka-clients-1.0.0.jar \
--conf "spark.driver.extraJavaOptions=-Djava.security.auth.login.config=kafka-jaas.conf" \
--conf "spark.executor.extraJavaOptions=-Djava.security.auth.login.config=kafka-jaas.conf" \
--files kafka-jaas.conf,svc-ds-prod.keytab \
file_triggered_spark_kafka_streaming.py  --input-path json-input-path --bootstrap-servers pphdpkafka007xx.global.tesco.org:6667 --topic PRD.DATA.AIM.MarkdownResult.JSON.V1_0
```

### Running kafka-console-consumer to test if the spark job produced messages to the output topic
```
export KAFKA_OPTS="-Djava.security.auth.login.config=/home/svc-ds-prod/lgaza/kafka-jaas.conf"
./confluent-4.0.0/bin/kafka-console-consumer --bootstrap-server pphdpkafka007xx.global.tesco.org:6667 --topic PRD.DATA.AIM.MarkdownResult.JSON.V1_0 --from-beginning --consumer.config consumer.properties
```


## Kerberos stuff

### kafka-jaas.conf

```
KafkaClient {
    com.sun.security.auth.module.Krb5LoginModule required
    doNotPrompt=true
    useTicketCache=true
    principal="svc-ds-prod@GLOBAL.TESCO.ORG"
    useKeyTab=true
    renewTicket=true
    serviceName="kafka"
    keyTab="svc-ds-prod.keytab"
    client=true;
};
Client {
  com.sun.security.auth.module.Krb5LoginModule required
  useTicketCache=false
  useKeyTab=true
  principal="serviceaccount@DOMAIN.COM"
  keyTab="serviceaccount.headless.keytab"
  renewTicket=true
  storeKey=true
  serviceName="zookeeper";
};
```

### consumer.properties

```
group.id=test-consumer-group2
security.protocol=SASL_PLAINTEXT
```
