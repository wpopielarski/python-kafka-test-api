import logging
import py4j.java_gateway as JG
from py4j.java_collections import MapConverter, ListConverter
from pyspark.sql import SparkSession
import pytest
import py


def test_kafka_conn(kafka: JG.JavaObject):
    try:
        # GIVEN
        kafka.createCustomTopic('testTopic', MapConverter().convert({}, kafka._gateway_client), 1, 1)
        kafka.publishToKafka('testTopic', 'Hello friend')
    
        # WHEN
        actual = kafka.consumeFirstStringMessageFrom('testTopic')
        
        # THEN
        assert actual == 'Hello friend'
    
    finally:
        kafka.deleteTopics(ListConverter().convert(['testTopic'], kafka._gateway_client))


@pytest.mark.parametrize('spark',
                         ({'spark.jars': '../jars/commons-pool2-2.6.2.jar,../jars/kafka-clients-2.8.0.jar,../jars/spark-sql-kafka-0-10_2.12-3.0.2.jar,../jars/spark-streaming-kafka-0-10_2.12-3.0.2.jar,../jars/spark-tags_2.12-3.0.2.jar,../jars/spark-token-provider-kafka-0-10_2.12-3.0.2.jar',
                           'spark.sql.streaming.forceDeleteTempCheckpointLocation': 'true'},),
                         indirect=True)
def test_spark_stream_consumer_with_kafka(kafka: JG.JavaObject, spark: SparkSession):
    try:
        # GIVEN
        default_kafka_port = 6001
        kafka.createCustomTopic('testTopic', MapConverter().convert({}, kafka._gateway_client), 1, 1)
        kafka.publishToKafka('testTopic', 'Hello friend')
        
        reader = (spark
                  .readStream
                  .format('kafka')
                  .option('kafka.bootstrap.servers', f'localhost:{default_kafka_port}')
                  .option('subscribe', 'testTopic')
                  .option('startingOffsets', 'earliest')
                  .load())
        
        stream = (reader
                  .select('*')
                  .writeStream
                  .outputMode('append')
                  .format('memory')
                  .queryName('testTopic')
                  .start())

        kafka.publishToKafka('testTopic', 'Hello kin')
        
        # WHEN
        stream.processAllAvailable()
        actual = map(lambda row: bytearray(row.value).decode(), 
                     spark
                     .sql('select * from testTopic')
                    .select('value')
                    .collect())
        
        stream.stop()
        
        # THEN
        assert set(actual) == set(['Hello friend', 'Hello kin'])
        
    finally:
        kafka.deleteTopics(ListConverter().convert(['testTopic'], kafka._gateway_client))


@pytest.mark.parametrize('spark',
                         ({'spark.jars': '../jars/commons-pool2-2.6.2.jar,../jars/kafka-clients-2.8.0.jar,../jars/spark-sql-kafka-0-10_2.12-3.0.2.jar,../jars/spark-streaming-kafka-0-10_2.12-3.0.2.jar,../jars/spark-tags_2.12-3.0.2.jar,../jars/spark-token-provider-kafka-0-10_2.12-3.0.2.jar',
                           'spark.sql.streaming.forceDeleteTempCheckpointLocation': 'true'},),
                         indirect=True)
def test_spark_stream_producer_with_kafka(kafka: JG.JavaObject, spark: SparkSession, tmpdir: py.path.local):
    spark.conf.set('spark.sql.streaming.checkpointLocation', str(tmpdir.mkdir('checkpoints')))
    try:
        # GIVEN
        default_kafka_port = 6001
        kafka.createCustomTopic('testIngressTopic', MapConverter().convert({}, kafka._gateway_client), 1, 1)    
        kafka.createCustomTopic('testEgressTopic', MapConverter().convert({}, kafka._gateway_client), 1, 1) 
        writer = (spark
                  .readStream
                  .format('kafka')
                  .option('kafka.bootstrap.servers', f'localhost:{default_kafka_port}')
                  .option('subscribe', 'testIngressTopic')
                  .option('startingOffsets', 'earliest')
                  .load())
    
        stream = (writer
                  .selectExpr("CAST(value AS STRING)")
                  .writeStream
                  .format('kafka')
                  .option('kafka.bootstrap.servers', f'localhost:{default_kafka_port}')
                  .option('topic', 'testEgressTopic')
                  .start())
        
        kafka.publishToKafka('testIngressTopic', 'Hello friend')
        
        # WHEN
        stream.processAllAvailable()
        actual = kafka.consumeFirstStringMessageFrom('testEgressTopic')       
        
        stream.stop()
        
        # THEN
        assert actual == 'Hello friend'
        
    finally:
        kafka.deleteTopics(ListConverter().convert(['testEgressTopic', 'testIngressTopic'], kafka._gateway_client))


@pytest.mark.parametrize('spark',
                         ({'spark.jars': '../jars/commons-pool2-2.6.2.jar,../jars/kafka-clients-2.8.0.jar,../jars/spark-sql-kafka-0-10_2.12-3.0.2.jar,../jars/spark-streaming-kafka-0-10_2.12-3.0.2.jar,../jars/spark-tags_2.12-3.0.2.jar,../jars/spark-token-provider-kafka-0-10_2.12-3.0.2.jar',
                           'spark.sql.streaming.forceDeleteTempCheckpointLocation': 'true'},),
                         indirect=True)
def test_spark_batch_consumer_with_kafka(kafka: JG.JavaObject, spark: SparkSession):
    try:
        # GIVEN
        default_kafka_port = 6001
        kafka.createCustomTopic('testTopic', MapConverter().convert({}, kafka._gateway_client), 1, 1)
        kafka.publishToKafka('testTopic', 'Hello friend')
        reader = (spark
                  .read
                  .format('kafka')
                  .option('kafka.bootstrap.servers', f'localhost:{default_kafka_port}')
                  .option('subscribe', 'testTopic')
                  .load())
 
        # WHEN
        actual = bytearray(reader.select('*').first().value)
        
        # THEN
        assert actual.decode() == 'Hello friend'

    finally:
        kafka.deleteTopics(ListConverter().convert(['testTopic'], kafka._gateway_client))


@pytest.mark.parametrize('spark',
                         ({'spark.jars': '../jars/commons-pool2-2.6.2.jar,../jars/kafka-clients-2.8.0.jar,../jars/spark-sql-kafka-0-10_2.12-3.0.2.jar,../jars/spark-streaming-kafka-0-10_2.12-3.0.2.jar,../jars/spark-tags_2.12-3.0.2.jar,../jars/spark-token-provider-kafka-0-10_2.12-3.0.2.jar',
                           'spark.sql.streaming.forceDeleteTempCheckpointLocation': 'true'},),
                         indirect=True)
def test_spark_batch_producer_with_kafka(kafka: JG.JavaObject, spark: SparkSession):
    try:
        # GIVEN
        default_kafka_port = 6001
        kafka.createCustomTopic('testTopic', MapConverter().convert({}, kafka._gateway_client), 1, 1)
        writer = spark.createDataFrame([['Hello friend']], schema=['value'])
        writer.show()
        (writer
         .selectExpr("CAST(value AS STRING)")
         .write
         .format('kafka')
         .option('kafka.bootstrap.servers', f'localhost:{default_kafka_port}')
         .option('topic', 'testTopic')
         .save())
 
        # WHEN
        actual = kafka.consumeFirstStringMessageFrom('testTopic')
        
        # THEN
        assert actual == 'Hello friend'

    finally:
        kafka.deleteTopics(ListConverter().convert(['testTopic'], kafka._gateway_client))
