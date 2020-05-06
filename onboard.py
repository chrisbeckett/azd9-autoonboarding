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
                print('Subscription successfully added to Dome9:',sub.subscription_id)
            elif r.status_code == 400:
                print('There was an error with the subscription, please check credentials and that it does not already exist in Dome9')
            elif r.status_code == 401:
                print('Bad credentials onboarding subscription to Dome9:',sub.subscription_id)
            else:
                print('Unknown error onboarding subscription to Dome9:',sub.subscription_id,'Status Code:',r.status_code)
            print(r.content)
        msg="Operation complete"
        return msg 
    except CloudError as e:
        print(e)

list_subscriptions()