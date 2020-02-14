# import the necessary packages
from imutils import paths
import argparse
import time
import sys
import cv2
import os
import numpy as np
import vptree
from pyspark.ml.linalg import Vectors
from pyspark.sql.functions import col
import pickle

def dhash(image, hashSize=8):
    # if image is colored, convert the image to grayscale
    if len(image.shape)==3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray=image

    # resize the grayscale image, adding a single column (width)
    # so we can compute the horizontal gradient
    resized = cv2.resize(gray, (hashSize + 1, hashSize))

    # compute the (relative) horizontal gradient
    # between adjacent column pixels
    diff = resized[:, 1:] > resized[:, :-1]

    #Produce dHash Integer
    dHash=sum([2**i for (i,v) in enumerate(diff.flatten()) if v])

    #binHash = diff.flatten().astype(int)
    # convert the difference image to a hash
    return dHash#, binHash

#Converts integer into sparse vector
#(had to convert things to strings because operations can't be performed on LongInt)
def sparse_vectorize(img_hash):
    index, value = [], [] #create empty vectors for index and value
    for i,v in enumerate(str(img_hash)):
        if v!="0":
            index.append(int(i))
            value.append(int(v))
    return Vectors.sparse(len(str(img_hash)), index, value)

def convert_hash(h):
    # convert the hash to NumPy's 64-bit float and then back to
    # Python's built in int
    return int(np.array(h, dtype="float64"))

def hamming(a, b):
    # compute and return the Hamming distance between the integers
    return bin(int(a) ^ int(b)).count("1")

#Pickle and Save Python Dictionary
def pickleHash(hashesRDD):
    print("[INFO] serializing hashes...")
    f = open("img_hash_dictionary.pickle", "wb")
    f.write(pickle.dumps(hashesRDD))
    f.close()

#Combines minHash Arrays into List
def dense_to_array(df):
    floatList=[float(d[0]) for d in df]
    return floatList

def pickleTree(partitionHashList):
    partitionList=len(partitionHashList) #Total number of partiitons
    singlets=[]
    p=1 #number to append to model save file (iterable)
    #f = open("hashing_image.pickle", "wb")
    for partition in partitionHashList:
        dHashList=[] #next several lines unpacks numbers from spark RDD and turns it into a list
        if len(partition)>=2:
            for dHash in partition:
                dHashList.append(dHash['dHash'])
            #Performs VPTree on partition cluster and does pickle suprise
            print('pipis: '+str(len(dHashList)))
            tree=vptree.VPTree(dHashList, hamming)
            print("[INFO] serializing VP-Tree for {partition} out of {partitionList} Partitions".format(partition=p, partitionList=partitionList))
            filer = open("vptree_{partition}.pickle".format(partition=p), "wb")
            filer.write(pickle.dumps(tree))
            filer.close()
	    
	    #f.write(pickle.dumps(dHash))
            
            p+=1
        #Deals with singlet clusters:
        elif len(partition)==1:
            print("Adding image singlet to singlet cluster")
            singlets.append(partition[0]['dHash']) #Add singlet to list of other single images
        else:
            print("Partition Empty")
    #Performs VPTree on singlet list and does pickle suprise
    tree=vptree.VPTree(singlets, hamming)
    print("[INFO] serializing VP-Tree for Remaining Singlet Images")
    filer = open("vptree_0.pickle", "wb")
    filer.write(pickle.dumps(tree))
    filer.close()
    #f.close()
