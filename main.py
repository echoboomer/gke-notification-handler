#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : github.com/echoboomer
# =============================================================================
"""
This script processes GKE cluster upgrade-related notifications as part of a
GCP Cloud Function.
"""
# =============================================================================
# Imports
# =============================================================================
import base64
import json
import os
import requests
import sys


def process_event(slack_data, webhook_url):
    byte_length = str(sys.getsizeof(slack_data))
    headers = {
        "Content-Type": "application/json",
        "Content-Length": byte_length,
    }
    response = requests.post(webhook_url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)


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

    print(
        """This Function was triggered by messageId {} published at {}
    """.format(
            context.event_id, context.timestamp
        )
    )

    if "data" in event:
        # Print the event at the beginning for easier debug.
        print("Event was passed into function and will be processed.")
        print(event)

        # Shared Variables
        cluster = event["attributes"]["cluster_name"]
        cluster_resource = json.loads(event["attributes"]["payload"])["resourceType"]
        location = event["attributes"]["cluster_location"]
        message = base64.b64decode(event["data"]).decode("utf-8")
        project = event["attributes"]["project_id"]
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")

        # UpgradeEvent
        if "UpgradeEvent" in event["attributes"]["type_url"]:
            # UpgradeEvent Variables
            current_version = json.loads(event["attributes"]["payload"])[
                "currentVersion"
            ]
            start_time = json.loads(event["attributes"]["payload"])[
                "operationStartTime"
            ]
            target_version = json.loads(event["attributes"]["payload"])["targetVersion"]
            title = f"GKE Cluster Upgrade Notification :zap:"
            slack_data = {
                "username": "Platform Notifications",
                "icon_emoji": ":satellite:",
                "attachments": [
                    {
                        "color": "#9733EE",
                        "fields": [
                            {"title": title},
                            {
                                "title": "Project",
                                "value": project,
                                "short": "false",
                            },
                            {
                                "title": "Cluster",
                                "value": cluster,
                                "short": "false",
                            },
                            {
                                "title": "Location",
                                "value": location,
                                "short": "false",
                            },
                            {
                                "title": "Update Type",
                                "value": cluster_resource,
                                "short": "false",
                            },
                            {
                                "title": "Current Version",
                                "value": current_version,
                                "short": "false",
                            },
                            {
                                "title": "Target Version",
                                "value": target_version,
                                "short": "false",
                            },
                            {
                                "title": "Start Time",
                                "value": start_time,
                                "short": "false",
                            },
                            {
                                "title": "Details",
                                "value": message,
                                "short": "false",
                            },
                        ],
                    }
                ],
            }
            process_event(slack_data, webhook_url)
        # UpgradeAvailableEvent
        elif "UpgradeAvailableEvent" in event["attributes"]["type_url"]:
            if os.Getenv("SEND_UPGRADE_AVAILABLE_NOTIFICATIONS") == "enabled":
                # UpgradeAvailableEvent Variables
                available_version = json.loads(event["attributes"]["payload"])[
                    "version"
                ]
                title = f"GKE Cluster Upgrade Available Notification :zap:"
                slack_data = {
                    "username": "Platform Notifications",
                    "icon_emoji": ":satellite:",
                    "attachments": [
                        {
                            "color": "#9733EE",
                            "fields": [
                                {"title": title},
                                {
                                    "title": "Project",
                                    "value": project,
                                    "short": "false",
                                },
                                {
                                    "title": "Cluster",
                                    "value": cluster,
                                    "short": "false",
                                },
                                {
                                    "title": "Location",
                                    "value": location,
                                    "short": "false",
                                },
                                {
                                    "title": "Eligible Resource",
                                    "value": cluster_resource,
                                    "short": "false",
                                },
                                {
                                    "title": "Eligible Version",
                                    "value": available_version,
                                    "short": "false",
                                },
                                {
                                    "title": "Details",
                                    "value": message,
                                    "short": "false",
                                },
                            ],
                        }
                    ],
                }
                process_event(slack_data, webhook_url)
            else:
                pass
        else:
            print(
                "Event was neither UpgradeEvent or UpgradeAvailableEvent, so it will be skipped."
            )
            exit(0)
    else:
        print("No event was passed into the function. Exiting.")
        exit(0)
