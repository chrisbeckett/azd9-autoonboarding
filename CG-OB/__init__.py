import datetime
import logging

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

# This script logs into Azure AD and iterates through subscriptions to onboard them into Dome9
# Feedback to chrisbe@checkpoint.com or open an issue on https://github.com/chrisbeckett/azd9-autoonboarding/issues

# To run the script, you will need to set environment variables for AZURE_CLIENT_ID, AZURE_CLIENT_SECRET and AZURE_TENANT_ID

# You will also need to set environment variables for D9_API_KEY and D9_API_SECRET

# Import required libraries
import os
import azure.common
import requests
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.subscription.operations import SubscriptionsOperations
from msrestazure.azure_exceptions import CloudError
from azure.common.credentials import ServicePrincipalCredentials
from requests.auth import HTTPBasicAuth
import json
import sys

# Verify the environment variables have been set

def verify_env_variables():
    try:
        if 'D9_API_KEY' in os.environ:
            pass
        else:
            logging.info("ERROR : The Dome9 API key has not been defined in environment variables")
            sys.exit(0)
        if 'D9_API_SECRET' in os.environ:
            pass
        else:
            logging.info("ERROR : The Dome9 API key secret not been defined in environment variables")
            sys.exit(0)
        if 'AZURE_TENANT_ID' in os.environ:
            pass
        else:
            logging.info("ERROR : The Azure AD tenant ID has not been defined in environment variables")
            sys.exit(0)
        if 'AZURE_CLIENT_ID' in os.environ:
            pass
        else:
            logging.info("ERROR : The Azure AD application ID has not been defined in environment variables")
            sys.exit(0)
        if 'AZURE_CLIENT_SECRET' in os.environ:
            pass
        else:
            logging.info("ERROR : The Azure AD application secret key has not been defined in environment variables")
            sys.exit(0)
    except:
        sys.exit(0)

verify_env_variables()

# Set Azure AD credentials from the environment variables
credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )

# Instantiate an instance of the Azure SDK Subscription Client
sub_client = SubscriptionClient(credentials)

# Read in required environment variables
d9_api_key = os.environ['D9_API_KEY']
d9_api_secret = os.environ['D9_API_SECRET']
az_tenant=os.environ['AZURE_TENANT_ID']
az_appid=os.environ['AZURE_CLIENT_ID']
az_appkey=os.environ['AZURE_CLIENT_SECRET']

# Set header parameters for Dome9 HTTP POST
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

# Set the account mode for automatic Dome9 onboarding - values are Read (default) or Manage
d9_operation_mode = 'Read'

# Run the subscription loop to add new or missing subscriptions to Dome9 in read only mode
def list_subscriptions():
    try:
        for sub in sub_client.subscriptions.list():
            print('Subscription found:', sub.subscription_id, sub.display_name)
            payload = {'name':sub.display_name,'subscriptionId':sub.subscription_id,'tenantId':az_tenant,'credentials': {'clientId':az_appid,'clientPassword':az_appkey},'operationMode':d9_operation_mode,'vendor':'azure'}
            r = requests.post('https://api.dome9.com/v2/AzureCloudAccount', json=payload, headers=headers, auth=(d9_api_key,d9_api_secret))
            if r.status_code == 201:
                logging.info('Subscription successfully added to Dome9:',sub.subscription_id)
            elif r.status_code == 400:
                logging.info('There was an error with the subscription, please check credentials and that it does not already exist in Dome9')
            elif r.status_code == 401:
                logging.info('Bad credentials onboarding subscription to Dome9:',sub.subscription_id)
            else:
                logging.info('Unknown error onboarding subscription to Dome9:',sub.subscription_id,'Status Code:',r.status_code)
            logging.info(r.content)
        msg="Operation complete"
        return msg 
    except CloudError as e:
        logging.info(e)

list_subscriptions()
