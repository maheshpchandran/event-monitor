# Kinesis to Redshift

## Problem statement

Events ingested into Kinesis streams should be moved to RedShift for querying/analytics. The events in Kinesis are in JSON, the architecture should allow reingestion into the RedShift warehouse which would be locationed in a different aws account/vpc. The pipeline should be based on aws services.

## Proposed Architecture

![](https://github.com/maheshpnair/event-monitor/blob/master/arch.png)

## Components/Services Used

### Kinesis Firehose Delivery Stream

It can capture data from Kinesis streams in real time and configuration/deployment is quick. Data transformation is possible using lambda functions and format of the record can be converted to **parquet/orc** , which would make it easier to run analytics on top of data generated using **Athena/presto** or **Redshift Spectrum.** Firehose can move data to S3 or directly push the data to Redshift using _ **redshift copy from s3** __._

### S3

If we are to push the data to Redshift, s3 can be used as an intermediary which would allow **re-importing data to Redshift.** A lifecycle policy can be attached to the target s3 bucket to move data to glacial storage after a fixed time.

If required, lambda can be created to perform the re-import at a later stage.

### RedShift

Redshift copy command can be used to import the data from the intermediary S3 bucket to the table. If there is no transformation to any other format, it can do an auto copy.

##


## The Pipeline

### Pushing Test Data to Kinesis Data Stream

[Simple script](https://github.com/maheshpnair/event-monitor/blob/master/push_json_kinesis_streams.py) to push data to the stream, aws config file should be present, accepts the stream name, json file and number of repeats as argument.

### Kinesis Streams and Firehose - CloudFormation

[Cloudformation script](https://github.com/maheshpnair/event-monitor/blob/master/kinesis-streams.yaml) to create the two data streams accept the following parameters.

| **Parameter** | **Description** |
| --- | --- |
| UserStreamShards | Number of shards for user stream |
| UtmStreamShards | Number of shards for utm stream |
| RedshiftClusterEndpoint | The connection string to connect to the redshift cluster |
| KinesisRoleARN | Role ARN to attach to kinesis, should have access to s3 bucket and cross account RedShift |
| S3BucketName | Bucket to be used as an intermediary |
| RedshiftUsername | username for redshift |
| RedshiftPassword | Password for redshift |
| RedshiftDatabase | database for redshift |

**Alternatively one can use this** [**script**](https://github.com/maheshpnair/event-monitor/blob/master/kinesis_IAM.yaml) **to create the IAM roles for the data, which accepts an ARN of the cross account role for RedShift, additional to the above parameters.**

### RedShift

Redshift cluster can be deployed using the [cloudformation template](https://github.com/maheshpnair/event-monitor/blob/master/redshift.yaml), accepts the following parameters. It creates a single node redshift cluster and a security group in the configured VPC which whitelists the Kinesis IP CIDR.

| **Parameter** | **Description** |
| --- | --- |
| masterUsername | master username for redshift |
| masterPassword | master password for redshift |
| myVPC | VPC ID |

### Creation of Redshift Databases/ Querying Data

[Cloudformation script](https://github.com/maheshpnair/event-monitor/blob/master/Kinesis_query_runner_lambda.yaml)can be used to create a lambda function that uses the psycopg2 library to run the queries on the redshift cluster, this can be used for

1. Creation of the initial db tables
2. Testing the presence of data after ingestion.

| Parameter | Description |
| --- | --- |
| s3bucketLambda | s3 bucket with lamda zip |
| s3keyLambda | s3 lambda zip location inside bucket |
| RedshiftQuery | Init query on redshift cluster |
| RedshiftUser | redshift cluster User |
| RedshiftEndpoint | redshift cluster endpoint |
| RedshiftPort | redshift cluster point |
| Redshiftpassword | redshift cluster password |
| RedshiftDatabase | redshift database |
| SecurityGroupId | SG |
| SubnetId1 | subnet 1 |
| SubnetId2 | subnet 2 |

The cloudformation script looks for a zip in the s3 bucket that houses the following [python code](https://github.com/maheshpnair/event-monitor/tree/master/lambda). It has the psycopg2 library for python3.7 as there is no in-built support.

## Roadblocks faced

1. Extra copy parameters for s3 to redshift copy

Delimiter not found error fixed by adding the following to copy parameters &quot;json &#39;auto&#39; TRUNCATECOLUMNS blanksasnull emptyasnull&quot;

2. Psycopg2 library is not present in the aws python3.7 lambda runtime, had to package it along with the code. This stopped me from adding the python script directly to the cloudformation template
3. I have created two versions of cloudformation templates for kinesis streams and firehose creation.
   [Kinesis\_IAM.yaml](https://github.com/maheshpnair/event-monitor/blob/master/kinesis_IAM.yaml) creates IAM roles along with the streams, this is not tested fully as I did not have access to another account to create a cross account role.
   [Kinesis\_streams.yaml](https://github.com/maheshpnair/event-monitor/blob/master/kinesis-streams.yaml) assumes you have created the IAM role.
4. If we were to create the databases using lambda along with redshift creation, the lambda primer does not end. 
   Lambda for the queries have to be triggered manually. 
