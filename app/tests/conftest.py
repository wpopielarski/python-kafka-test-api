import os
from pyspark.sql import SparkSession
import py4j.java_gateway as G
import pytest
import shutil
import wpopiel.shared.py4j_tools as JavaTools
import logging

"""
Place holder for fixtures used by ``pytest`` testing framework.
"""


dbpath = 'metastore_db'
logpath = 'derby.log'


@pytest.fixture(scope='module', autouse=True)
def remove_db_lock():
    yield

    if os.path.exists(dbpath) and os.path.isdir(dbpath):
        import glob
        lcklist = glob.glob(os.path.join(dbpath, '*.lck'))
        for lck in lcklist:
            os.remove(lck)


@pytest.fixture(scope='module', autouse=True)
def remove_db():
    if os.path.exists(dbpath):
        assert os.path.isdir(dbpath), '%s is not a directory' % dbpath
        shutil.rmtree(dbpath)
    if os.path.exists(logpath):
        assert os.path.isfile(logpath), '%s is not a file' % logpath
        os.remove(logpath)


@pytest.fixture(scope="module")
def spark(request):
    additional_configuration = dict()
    try:
        additional_configuration = request.param
    except:
        pass
    builder = SparkSession.builder
    for key, value in additional_configuration.items():
        logging.warning('%s: %s', key, value)
        builder.config(key, value)
    logging.warning(builder._options)
    session = (builder
               .enableHiveSupport()
               .master('local[2]')
               .config('spark.ui.enabled', False)
               .config('spark.sql.catalogImplementation', 'hive')
               .config('spark.hadoop.hive.exec.dynamic.partition.mode', 'nonstrict')
               .getOrCreate())

    yield session

    session.stop()


@pytest.fixture(scope='module')
def kafka():
    gateway = G.JavaGateway.launch_gateway(classpath=os.path.join('tests',
                                                                  'test-jars',
                                                                  'kafka-test-api-1.0-SNAPSHOT',
                                                                  'lib',
                                                                  '*'))
    j_embedded = JavaTools.ref_scala_object(gateway.jvm, 'tesco.test.kafka.Py4jEmbeddedKafkaApi')
    j_embedded.start()
    
    yield j_embedded
    
    j_embedded.stop()
    gateway.shutdown()
