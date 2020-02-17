# Image IP Protection
> ***find and retrieve similar or identical images***

This is a project I completed during the Insight Data Engineering program.
Visi www.data-engineering.xyz to see to upload a picture and find out if there is similar picture in the database (the images source is from Image-net.org)

***

This project aims at creating a pipeline that users can do generate a database of existing pictures and run query on whether a new uploaded picture(or similar picture) can be found in the database. 

A lot of companies has proprietary pictures and they might be used by other organization without permission (e.g companies' logo or ). This pipeline employs both Vantage Point approach (pixel based compaision) and Deep Ranking model (CNN model https://arxiv.org/abs/1404.4661) to make the search faster and more accurate.

The following two pictures show what it looks like when uploading a picture on the website www.data-eningeering.xyz and a similar picture is found. 

![alt text](https://github.com/lixali/Image_IP_protection/blob/master/flask-app/static/Screen%20Shot%202020-02-17%20at%204.49.46%20PM.png "Image_IP_Protection Screenshot Upload Picture")

![alt text](https://github.com/lixali/Image_IP_protection/blob/master/flask-app/static/Screen%20Shot%202020-02-17%20at%204.59.47%20PM.png "Image_IP_Protection Screenshot Similar Picture Found")

Pipeline
-----------------

![alt text](https://github.com/lixali/Image_IP_protection/blob/master/flask-app/static/Screen%20Shot%202020-02-17%20at%205.13.32%20PM.png "Image_IP_Protection Pipeline Indexing")
![alt text](https://github.com/lixali/Image_IP_protection/blob/master/flask-app/static/Screen%20Shot%202020-02-17%20at%205.13.55%20PM.png "Image_IP_Protection Pipeline Query ")
![alt text](https://github.com/lixali/Image_IP_protection/blob/master/flask-app/static/Screen%20Shot%202020-02-17%20at%205.14.56%20PM.png "Image_IP_Protection Pipeline Deep Ranking Model Feature extraction")
![alt text](https://github.com/lixali/Image_IP_protection/blob/master/flask-app/static/Screen%20Shot%202020-02-17%20at%205.16.11%20PM.png "Image_IP_Protection Pipeline Deep Ranking Query ")

***Batch Job***: 100 million pictures (100G) from Image-net.org are ingested from S3 bucket into Spark, which computes will 
(1)generate VP-trees(store in the pickle file format), hash table(stored in txt file format);  
(2)Use trained model "model_w_weight.h5" to create vectors tables and saves the result into the PostgreSQL database.

***Query***: User upload an image, which computes will 
(1)generate VP-trees(store in the pickle file format), hash table(stored in txt file format);  
(2)Use trained model "model_w_weight.h5" to create vectors tables and saves the result into the PostgreSQL database.

### Data Sources
  1. Image-net.org: needs to create an account and request access to the image database with a non-commercial email account.


### Environment Setup

Install and configure [AWS CLI](https://aws.amazon.com/cli/) and [Pegasus](https://github.com/InsightDataScience/pegasus) on your local machine, and clone this repository using
`git clone https://github.com/lixali/Image_IP_protection`.

> AWS Tip: Add your local IP to your AWS VPC inbound rules

> Pegasus Tip: In $PEGASUS_HOME/install/download_tech, change Zookeeper version to 3.4.12, and follow the notes in docs/pegasus_setup.odt to configure Pegasus

#### CLUSTER STRUCTURE:

To reproduce my environment, 11 m4.large AWS EC2 instances are needed:

- (4 nodes) Spark Cluster - Batch
- Postgres Node
- Flask Node

To create the clusters, put the appropriate `master.yml` and `workers.yml` files in each `cluster_setup/<clustername>` folder (following the template in `cluster_setup/dummy.yml.template`), list all the necesary software in `cluster_setup/<clustername>/install.sh`, and run the `cluster_setup/create-clusters.sh` script.



##### PostgreSQL setup
The PostgreSQL database sits on the master node of *spark-stream-cluster*.
Follow the instructions in `docs/postgres_install.txt` to download and setup access to it.

##### Configurations
Configuration settings for Kafka, PostgreSQL, AWS S3 bucket, as well as the schemas for the data are stored in the respective files in `config/` folder.
> Replace the settings in `config/s3config.ini` with the names and paths for your S3 bucket.


## Running Image_IP_protection

### Indexing
go to "Image_IP_protection/" folder and run the following command "spark-submit --packages com.amazonaws:aws-java-sdk:1.7.4,org.apache.hadoop:hadoop-aws:2.7.6 --master spark://ip-10-0-0-6:7077 image_IP_protect.py"

### Using Deep ranking model
go to "Image_IP_protection/deep_ranking/" folder and run the following command "spark-submit --packages com.amazonaws:aws-java-sdk:1.7.4,org.apache.hadoop:hadoop-aws:2.7.6 --master spark://ip-10-0-0-6:7077 spark_deploy_model.py"


### Flask
go to "Image_IP_protection" folder, and run `sudo screen python3 app.py` to start the Flask server.
