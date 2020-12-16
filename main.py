import base64
import json
import os
import requests
import sys


def notify_slack(event, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.

         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    """

    print("""This Function was triggered by messageId {} published at {}
    """.format(context.event_id, context.timestamp))

    if 'data' in event:
        print("Event was passed into function and will be processed.")
        print(event)
        print(event['attributes'])

        cluster = event['attributes']['cluster_name']
        cluster_resource = json.loads(event['attributes']['payload'])[
            'resourceType']
        current_version = json.loads(event['attributes']['payload'])[
            'currentVersion']
        location = event['attributes']['cluster_location']
        message = base64.b64decode(
            event['data']).decode('utf-8')
        project = event['attributes']['project_id']
        start_time = json.loads(event['attributes']['payload'])[
            'operationStartTime']
        target_version = json.loads(event['attributes']['payload'])[
            'targetVersion']
        title = (f"GKE Cluster Upgrade Notification :zap:")
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')

        slack_data = {
            "username": "SLACK_USERNAME",
            "icon_emoji": ":satellite:",
            "attachments": [
                {
                    "color": "#9733EE",
                    "fields": [
                        {
                          "title": title
                        },
                        {
                            "title": "Project",
                            "value": project,
                            "short": "false"
                        },
                        {
                            "title": "Cluster",
                            "value": cluster,
                            "short": "false"
                        },
                        {
                            "title": "Location",
                            "value": location,
                            "short": "false"
                        },
                        {
                            "title": "Update Type",
                            "value": cluster_resource,
                            "short": "false"
                        },
                        {
                            "title": "Current Version",
                            "value": current_version,
                            "short": "false"
                        },
                        {
                            "title": "Target Version",
                            "value": target_version,
                            "short": "false"
                        },
                        {
                            "title": "Start Time",
                            "value": start_time,
                            "short": "false"
                        },
                        {
                            "title": "Details",
                            "value": message,
                            "short": "false"
                        }
                    ]
                }
            ]
        }

        byte_length = str(sys.getsizeof(slack_data))
        headers = {'Content-Type': "application/json",
                   'Content-Length': byte_length}

        response = requests.post(
            webhook_url, data=json.dumps(slack_data), headers=headers)

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
    else:
        print("No event was passed into the function. Exiting.")
