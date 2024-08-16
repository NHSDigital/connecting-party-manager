test_sample = {"testing": "www.testing.com/test", "param1": "1"}

test_sample2 = {"testing": "www.testing.com/test", "param2": "2"}

test_sample3 = {"testing": "www.testing.com/test", "param3": "3"}


VALID_SQS_UPDATE_EVENT = {
    "Records": [
        {
            "messageId": "9eec100f-ee88-487a-80a7-3df7e40b780a",
            "receiptHandle": "xxx",
            "body": "body",
            "attributes": {
                "ApproximateReceiveCount": "1",
                "AWSTraceHeader": "Root=1-66605ea1-2906755913c79d1e09ac123c;Parent=2ead4ea5436a13b6;Sampled=0;Lineage=81989ed2:0",
                "SentTimestamp": "1717591754739",
                "SequenceNumber": "18886447562922735616",
                "MessageGroupId": "state_machine_group",
                "SenderId": "test",
                "MessageDeduplicationId": "155cca91-bd65-41a4-a335-922cde2edff9",
                "ApproximateFirstReceiveTimestamp": "1717591754739",
            },
            "messageAttributes": {},
            "md5OfBody": "xxx",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:eu-west-2:*:nhse-cpm--megtest--sds--input-sqs.fifo",
            "awsRegion": "eu-west-2",
        }
    ]
}

VALID_SQS_BULK_EVENT = {
    "Records": [
        {
            "messageId": "9eec100f-ee88-487a-80a7-3df7e40b780a",
            "receiptHandle": "xxx",
            "body": "VALID_SQS_BULK_MESSAGE_BODY",
            "attributes": {
                "ApproximateReceiveCount": "1",
                "AWSTraceHeader": "Root=1-66605ea1-2906755913c79d1e09ac123c;Parent=2ead4ea5436a13b6;Sampled=0;Lineage=81989ed2:0",
                "SentTimestamp": "1717591754739",
                "SequenceNumber": "18886447562922735616",
                "MessageGroupId": "state_machine_group",
                "SenderId": "test",
                "MessageDeduplicationId": "155cca91-bd65-41a4-a335-922cde2edff9",
                "ApproximateFirstReceiveTimestamp": "1717591754739",
            },
            "messageAttributes": {},
            "md5OfBody": "xxx",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:eu-west-2:*:nhse-cpm--megtest--sds--input-sqs.fifo",
            "awsRegion": "eu-west-2",
        }
    ]
}


INVALID_BODY_FIELD_EVENT = {
    "Records": [
        {
            "messageId": "9eec100f-ee88-487a-80a7-3df7e40b780a",
            "receiptHandle": "xxx",
            "body": "INVALID_BODY_FIELD_SQS_MESSAGE",
            "attributes": {
                "ApproximateReceiveCount": "1",
                "AWSTraceHeader": "Root=1-66605ea1-2906755913c79d1e09ac123c;Parent=2ead4ea5436a13b6;Sampled=0;Lineage=81989ed2:0",
                "SentTimestamp": "1717591754739",
                "SequenceNumber": "18886447562922735616",
                "MessageGroupId": "state_machine_group",
                "SenderId": "test",
                "MessageDeduplicationId": "155cca91-bd65-41a4-a335-922cde2edff9",
                "ApproximateFirstReceiveTimestamp": "1717591754739",
            },
            "messageAttributes": {},
            "md5OfBody": "xxx",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:eu-west-2:*:nhse-cpm--megtest--sds--input-sqs.fifo",
            "awsRegion": "eu-west-2",
        }
    ]
}

INVALID_BODY_JSON_SQS_MESSAGE = '{invalid_json: "value"}'
INVALID_BODY_JSON_EVENT = {
    "Records": [
        {
            "messageId": "9eec100f-ee88-487a-80a7-3df7e40b780a",
            "receiptHandle": "xxx",
            "body": INVALID_BODY_JSON_SQS_MESSAGE,
            "attributes": {
                "ApproximateReceiveCount": "1",
                "AWSTraceHeader": "Root=1-66605ea1-2906755913c79d1e09ac123c;Parent=2ead4ea5436a13b6;Sampled=0;Lineage=81989ed2:0",
                "SentTimestamp": "1717591754739",
                "SequenceNumber": "18886447562922735616",
                "MessageGroupId": "state_machine_group",
                "SenderId": "test",
                "MessageDeduplicationId": "155cca91-bd65-41a4-a335-922cde2edff9",
                "ApproximateFirstReceiveTimestamp": "1717591754739",
            },
            "messageAttributes": {},
            "md5OfBody": "xxx",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:eu-west-2:*:nhse-cpm--megtest--sds--input-sqs.fifo",
            "awsRegion": "eu-west-2",
        }
    ]
}
