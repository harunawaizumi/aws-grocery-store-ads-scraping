import requests
import boto3
import logging
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import os
from aws_lambda_powertools.utilities import parameters


# static info
image_url = "https://www.bicrise.com/flyer/jiyugaoka-01.jpg"
Filename = "/tmp/aoba.jpg"
Bucket = "harunawaizumi.supermarket"
Objectname = "aoba.jpg"
region = "ap-northeast-1"
parameter_name = "access-id"
logger = logging.getLogger(__name__)


def upload_file(file_name, bucket, object_name=None):
    """ """

    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client("s3")
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def publish_message(topic, message, attributes):
    """
    Publishes a message, with attributes, to a topic. Subscriptions can be filtered
    based on message attributes so that a subscription receives messages only
    when specified attributes are present.

    :param topic: The topic to publish to.
    :param message: The message to publish.
    :param attributes: The key-value attributes to attach to the message. Values
                        must be either `str` or `bytes`.
    :return: The ID of the message.
    """
    try:
        att_dict = {}
        for key, value in attributes.items():
            if isinstance(value, str):
                att_dict[key] = {"DataType": "String", "StringValue": value}
            elif isinstance(value, bytes):
                att_dict[key] = {"DataType": "Binary", "BinaryValue": value}
        response = topic.publish(Message=message, MessageAttributes=att_dict)
        message_id = response["MessageId"]
        logger.info(
            "Published message with attributes %s to topic %s.",
            attributes,
            topic.arn,
        )
    except ClientError:
        logger.exception("Couldn't publish message to topic %s.", topic.arn)
        raise
    else:
        return message_id


def get_parameter_value(parameter_name, region):
    # Create a Systems Manager client
    ssm = boto3.client("ssm", region_name=region)

    try:
        # Get the parameter
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)

        # Extract and return the parameter value
        return response["Parameter"]["Value"]
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def lambda_handler(event, context):
    # download aoba pdf to save it as aoba.jpgs
    img_data = requests.get(image_url).content

    with open("/tmp/aoba.jpg", "wb") as handler:
        handler.write(img_data)

    # upload aoba pdf to S3 bukcet called harunawaizumi.space
    load_dotenv()
    client = boto3.client("s3")

    # get accessid from system manager
    accessid = get_parameter_value(parameter_name, region)

    upload_file(Filename, Bucket, Objectname)

    # Create an SNS client
    sns = boto3.resource("sns")

    # Replace with your SNS topic ARN
    topic_arn = f"arn:aws:sns:ap-northeast-1:{accessid}:NewFileUploadedToS3Demo"
    print("Topic ARC: {}".format(topic_arn))

    # Get the topic object
    topic = sns.Topic(topic_arn)

    publish_message(
        topic,
        """https://s3.ap-northeast-1.amazonaws.com/harunawaizumi.supermarket/aoba.jpg
        New File is uploaded.""",
        {"Version": '{DataType: "Number", StringValue: "1"}'},
    )

    return {"statusCode": 200}
