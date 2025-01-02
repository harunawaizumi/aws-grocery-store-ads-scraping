# AWS Grocery Store Advertisement Scraping

1. Create Lambda function

- Download a grocery store digital flyer as jpg from a website to a temp folder
- Copy the file to S3
- Get AccessID from System Manager to allow Lambda access to SNS
- Send a message to SNS
  ![lambda_chart.png](https://github.com/harunawaizumi/aws-grocery-store-ads-scraping/blob/main/lambda_chart.png)

2. Create SNS

- Send a message to a specific endpoint which is my email address

3. Set up EventBridge

- Set a crontab to run on a specific time
- Run the Lambda function on every Saturday
  ![eventbridge.png](https://github.com/harunawaizumi/aws-grocery-store-ads-scraping/blob/main/eventbridge.png)

After you run the function, you should see the result on Lambda CloudWatch.
