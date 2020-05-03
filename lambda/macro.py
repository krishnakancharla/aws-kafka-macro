import os

PREFIX = "Boto3::"

LAMBDA_ARN = os.environ["LAMBDA_ARN"]

def handle_template(request_id, template):
    for name, resource in template.get("Resources", {}).items():
        if resource["Type"].startswith(PREFIX):
            resource.update({
                "Type": "Custom::Boto3",
                "Version": "1.0",
                "Properties": {
                    "ServiceToken": LAMBDA_ARN,
                    "Mode": resource.get("Mode", ["Create", "Update"]),
                    "Action": resource["Type"][len(PREFIX):],
                    "Properties": resource.get("Properties", {}),
                },
            })

            if "Mode" in resource:
                del resource["Mode"]

    return template

def handler(event, context):
    fragment = event["fragment"]
    status = "success"

    try:
        fragment = handle_template(event["requestId"], event["fragment"])
    except Exception as e:
        status = "failure"

    return {
        "requestId": event["requestId"],
        "status": status,
        "fragment": fragment,
    }
