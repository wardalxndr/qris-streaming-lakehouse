"""Referensi Spark Structured Streaming: logika silver yang sama, versi cluster.
Jalan: spark-submit spark/spark_streaming_job.py  (butuh PySpark + Java)
Lokal default tetap pipeline/run_pipeline.py (tanpa cluster).
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count

RAW = "data/bronze/qris_raw.csv"

spark = (SparkSession.builder.appName("qris-silver")
         .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true")
         .getOrCreate())
spark.sparkContext.setLogLevel("WARN")

bronze = (spark.readStream.format("csv").option("header", True)
           .option("maxFilesPerTrigger", 1).schema(
               "txn_id STRING, ts TIMESTAMP, user_id STRING, merchant_id STRING,"
               "merchant_cat STRING, amount INT, city STRING, device_id STRING,"
               "channel STRING, is_fraud INT, fraud_type STRING")
           .load("data/bronze_stream/"))

clean = bronze.dropDuplicates(["txn_id"]).filter(col("amount") > 0)

velocity = (clean
            .withWatermark("ts", "15 minutes")
            .groupBy(col("user_id"), window(col("ts"), "10 minutes"))
            .agg(count("*").alias("n"))
            .filter(col("n") >= 5))

q = velocity.writeStream.outputMode("complete").format("console").start()
q.awaitTermination()
