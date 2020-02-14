# import the necessary packages
import hashing as hs
from imutils import paths
import argparse
import pickle
import vptree
import time
import json
import cv2

#Walk through VPTree directory and unpack models
import glob
import pickle

f = open("result_search.txt", "wb")   #Lixiang

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--tree", required=True, type=str, help="path to pre-constructed VP-Tree")
ap.add_argument("-a", "--hashes", required=True, type=str, help="path to hashes dictionary")
ap.add_argument("-q", "--query", required=True, type=str, help="path to input query image")
ap.add_argument("-d", "--distance", type=int, default=10, help="maximum hamming distance")
# ^^^^ ADJUST THIS METRIC FOR QUERY THRESHOLD (larger distance=more images to compare [longer runtime])
ap.add_argument("-s", "--size", required=False, type=str, help="image resize (default is 8x8)")
args = vars(ap.parse_args())

# load the input query image
image = cv2.imread(args["query"])
#cv2.imshow("Query", image)

# compute the hash for the query image, then convert it
queryHash = hs.dhash(image, int(args["size"]))
queryHash = hs.convert_hash(queryHash)
print("the query image hash value is", queryHash)

# load the VP-Tree and hashes dictionary
print("[INFO] loading VP-Tree and hashes...")
#tree=pickle.loads(open(args["tree"], "rb").read())
hashes=pickle.loads(open(args["hashes"], "rb").read())

start = time.time()
resultsList=[] #Adds results of image query to this list
for pickleTree in glob.glob(args["tree"]+"/vptree_*.pickle"):
    print("[INFO] loading VP-Tree: {pickle}".format(pickle=pickleTree))
    with open(pickleTree,'rb') as f:
        tree=pickle.load(f)
    #tree=pickle.loads(open(pickleTree, "rb").read())

    #Perform search in VPTree
    print("[INFO] performing search on {pickle}".format(pickle=pickleTree))
    results = tree.get_all_in_range(queryHash, args["distance"])
    results = sorted(results)

    #Loop through reults and add to resultsList
    counter=0 #nNsure that only top 10 results are used
    for i, result in enumerate(results):
        resultsList.append(result)
        if i>=1:
            break #Grabs first result (modifiable), moves on to next tree
        else:
            i+=1
#Sort final list of all resutls
resultsList=sorted(resultsList)
end = time.time()
no_images=len(set(hashes))
print("[INFO] search took {} seconds to search {} images".format(end - start, no_images))
print("resultslist is", resultsList)  #Lixiang

# loop over the results (Performed on flask UI??)
for (d, h) in resultsList:
    #grab all image paths in our dataset with the same hash
    resultPaths = [hashes.get(int(h), [])]
    print("[INFO] {} total images(s) with d: {}, h:{}".format(len(resultPaths), d, h))
    # loop over the result paths
    for resultPath in resultPaths:
        # load the result image and display it to our screen
        result = cv2.imread(resultPath)
        #print 's3://puretest1000/' + resultPath
        print(resultPath)
        #cv2.imshow("Result", result)
        cv2.waitKey(0) #THIS WAITS FOR USER INPUT (PROBABLY WON'T WORK IN SQL SEARCH))
