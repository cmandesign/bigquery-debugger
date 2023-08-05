import os
import re
import argparse
import sys
import configparser

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from service.logging_service import get_logger

home_path = os.path.expanduser('~')
file_logger = get_logger()

def get_destination_table(destination_table):
    return "{}.{}.{}".format(destination_table['projectId'],destination_table['datasetId'],destination_table['tableId'] )



CREDENTIALS_PATH = os.path.join(home_path, '.config/gcloud/application_default_credentials.json')
DEFAULT_CONFIG_PATH = os.path.join(home_path, '.config/gcloud/configurations/config_default')

def read_project_id_from_config():
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_PATH)

    if "core" in config and "project" in config["core"]:
        return config["core"]["project"]
    else:
        file_logger.debug("Project ID not found in  {}".format(DEFAULT_CONFIG_PATH))
        return None


def authenticate_bigquery():
    creds = None

    # Check if the credentials file exists
    file_logger.debug("CREDENTIALS_PATH {}".format(CREDENTIALS_PATH))
    if os.path.exists(CREDENTIALS_PATH):
        file_logger.debug("CREDENTIALS_PATH Exist")
        creds = Credentials.from_authorized_user_file(CREDENTIALS_PATH)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        # else:
        #     # from google_auth_oauthlib.flow import InstalledAppFlow

        #     flow = InstalledAppFlow.from_client_secrets_file('path/to/client_secret.json', SCOPES)
        #     creds = flow.run_local_server(port=0)
        
        # # Save the credentials for the next run
        # with open(CREDENTIALS_PATH, 'w') as token:
        #     token.write(creds.to_json())
    
    project_id = read_project_id_from_config()

    return creds, project_id

