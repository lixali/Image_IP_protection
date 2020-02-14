#Spark Submit (for testing in CLI)
#./bin/spark-submit --master spark://10.0.0.11:7077 --executor-memory 6g test.py

#Initiate PySpark/Python
from pyspark.sql import SparkSession
from pyspark import SparkContext
import sys

sc = SparkContext.getOrCreate();

spark=SparkSession.builder \
    .master("spark://ip-10-0-0-6:7077") \
    .appName("PicturePerfect") \
    .getOrCreate()

#Custom Modules
sc.addFile("import_img.py")
sc.addFile("hashing.py")

from pyspark import SparkConf, SparkContext, SparkFiles
sys.path.insert(0,SparkFiles.getRootDirectory())

import import_img as impg
import hashing as hs

#Pyspark Packages
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.ml.linalg import SparseVector, DenseVector, Vectors
from pyspark.sql.functions import col
from pyspark.ml.feature import MinHashLSH, BucketedRandomProjectionLSH
from pyspark.ml.clustering import KMeans, BisectingKMeans

#Python Packages
import numpy as np
from PIL import Image
from io import BytesIO
import boto3
#import s3fs
from imutils import paths
import argparse
import time
import cv2
import os
import vptree
import pickle

#import findspark

#findspark.init()
#S3 Bucket/Folder
#bucket='openimagedata2'
#bucket='openimagedatatest'
#bucket='puretest1000'
bucket='puretest5000'
folders='./'

#Import as Spark RDD
urlsRDD=sc.textFile("s3a://"+bucket+"/urls.txt")
#llist = urlsRDD.collect()

#urlsRDD.take(100).foreach(println)
#print(urlsRDD)
#impg.read_image_from_s3(bucket, url)
#Download and acquire image vectors
img_vectors=urlsRDD.map(lambda url: (url, impg.read_image_from_s3(bucket, url)))
#img_vectors.take(5)


#dHash function
img_hash=img_vectors.map(lambda img: (img[0], hs.convert_hash(hs.dhash(img[1], 32))))

#Makes dictionary from RDD continaing dHash (key) and URLs (value)
#dHash_dict=img_hash.map(lambda (url, dHash): (dHash, url))   ### python 2 code 
dHash_dict=img_hash.map(lambda url_dHash: (url_dHash[1], url_dHash[0]))    ### python 3 code

#dHash_dict.take(5).foreach(println)


#Pickles python hash dictionary
hs.pickleHash(dHash_dict.collectAsMap())

#Converts Image dHash into Sparse Vector (Required Input for LSH)
img_sparse=img_hash.map(lambda img: (img[0], str(img[1]), hs.sparse_vectorize(img[1])))

#Converts array of sparse img vectors into dataframe
df = spark.createDataFrame(img_sparse, ["url", "dHash", "sparseHash"])

#MinHashLSH
mh = MinHashLSH(inputCol="sparseHash", outputCol="minHash", numHashTables=4, seed=69)
model = mh.fit(df)

#BucketedRandomProjectionLSH
#brp = BucketedRandomProjectionLSH(inputCol="sparseHash", outputCol="minHash", bucketLength=20.0, numHashTables=5)
#model = brp.fit(df)

#KMeans
#kmeans=KMeans(featuresCol='denseHash', predictionCol='minHash', k=12, seed=69)
#model = kmeans.fit(df)

#Transform df to model
transformed_df = model.transform(df).select("url","dHash","minHash")

#Combines LSH_minHash Arrays into List
dense_to_array_udf = F.udf(hs.dense_to_array, T.ArrayType(T.FloatType()))
minHashCombine_df = transformed_df.withColumn('minHash', dense_to_array_udf('minHash')).select("url", "dHash", "minHash")

#Repartition Data Based on Prediction (minHash)
from pyspark.sql.functions import col, countDistinct
numPartitions=str(minHashCombine_df.agg(countDistinct(col("minHash")).alias("count")).first())

numPartitions=int(''.join(filter(str.isdigit, numPartitions)))

#Repartion
repartitioned_df=minHashCombine_df.repartition(numPartitions, "minHash")

#Create list of dHash Keys in each partition
dHashList=repartitioned_df.select('dHash').rdd
partitionHashList = dHashList.glom().collect()

#Run VP-Tree on Partitions
hs.pickleTree(partitionHashList)


print("")
print('FINISED!!!')
print("")

#Stop Session
spark.stop()
