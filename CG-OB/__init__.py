import datetime
import logging
import azure.functions as func
import os
import requests
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.subscription.operations import SubscriptionsOperations
from msrestazure.azure_exceptions import CloudError
import json
import sys
from azure.identity import ClientSecretCredential

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Build 060121-1704')
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

# Verify the environment variables have been set
#def verify_env_variables():
    logging.info("Verifying variables...")
    try:
        if 'CG_API_KEY' in os.environ:
            pass
        else:
            logging.info(f"ERROR : The CloudGuard API key has not been defined in environment variables")
            sys.exit(0)
        if 'CG_API_SECRET' in os.environ:
            pass
        else:
            logging.info(f"ERROR : The CloudGuard API key secret not been defined in environment variables")
            sys.exit(0)
        if 'AZURE_TENANT_ID' in os.environ:
            pass
        else:
            logging.info(f"ERROR : The Azure AD tenant ID has not been defined in environment variables")
            sys.exit(0)
        if 'AZURE_CLIENT_ID' in os.environ:
            pass
        else:
            logging.info(f"ERROR : The Azure AD application ID has not been defined in environment variables")
            sys.exit(0)
        if 'AZURE_CLIENT_SECRET' in os.environ:
            pass
        else:
            logging.info(f"ERROR : The Azure AD application secret key has not been defined in environment variables")
            sys.exit(0)
    except:
        sys.exit(0)

#verify_env_variables()

# Set Azure AD credentials from the environment variables
    credentials = ClientSecretCredential(
            client_id=os.environ['AZURE_CLIENT_ID'],
            client_secret=os.environ['AZURE_CLIENT_SECRET'],
            tenant_id=os.environ['AZURE_TENANT_ID']
        )

    # Instantiate an instance of the Azure SDK Subscription Client
    sub_client = SubscriptionClient(credentials)

    # Read in required environment variables
    cg_api_key = os.environ['CG_API_KEY']
    cg_api_secret = os.environ['CG_API_SECRET']
    az_tenant=os.environ['AZURE_TENANT_ID']
    az_appid=os.environ['AZURE_CLIENT_ID']
    az_appkey=os.environ['AZURE_CLIENT_SECRET']

    # Set header parameters for CloudGuard HTTP POST
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }

    # Set the account mode for automatic CloudGuard onboarding - values are Read (default) or Manage
    cg_operation_mode = 'Read'

# Run the subscription loop to add new or missing subscriptions to CloudGuard in read only mode
#def list_subscriptions():
    try:
        for sub in sub_client.subscriptions.list():
            logging.info(f'Subscription found:, {sub.subscription_id}, {sub.display_name}')
            payload = {'name':sub.display_name,'subscriptionId':sub.subscription_id,'tenantId':az_tenant,'credentials': {'clientId':az_appid,'clientPassword':az_appkey},'operationMode':cg_operation_mode,'vendor':'azure'}
            r = requests.post('https://api.dome9.com/v2/AzureCloudAccount', json=payload, headers=headers, auth=(cg_api_key,cg_api_secret))
            if r.status_code == 201:
                logging.info(f'Subscription successfully added to CloudGuard: {sub.subscription_id}')
            elif r.status_code == 400:
                logging.info(f'There was an error with the subscription {sub.subscription_id}, please check credentials and that it does not already exist in CloudGuard')
            elif r.status_code == 401:
                logging.info(f'Bad credentials onboarding subscription to CloudGuard: {sub.subscription_id}')
            else:
                logging.info(f'Unknown error onboarding subscription to CloudGuard: {sub.subscription_id} Status Code: {r.status_code}')
            logging.info(r.content)
        msg="Operation complete"
        return msg 
    except CloudError as e:
        logging.info(e)

#list_subscriptions()
