# This script logs into Azure AD and iterates through subscriptions to onboard them into CloudGuard
# Feedback to stuartg@checkpoint.com or open an issue on https://github.com/chkp-stuartgreen/azd9-autoonboarding/issues

# To run the script, you will need to set environment variables for AZURE_CLIENT_ID, AZURE_CLIENT_SECRET and AZURE_TENANT_ID



# You will also need to set environment variables for CG_API_KEY, CG_API_SECRET and CG_REGION
# Regions:
# 
# USA = default / blank (secure.dome9.com)
# Australia = AP2 (secure.ap2.dome9.com)
# Ireland = EU1 (secure.eu1.dome9.com)
# India = AP3 secure.ap3.dome9.com

# Import required libraries
import os
import requests
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.subscription.operations import SubscriptionsOperations
from msrestazure.azure_exceptions import CloudError
import json
import sys
from azure.identity import ClientSecretCredential

# Verify the environment variables have been set

def verify_env_variables():
    try:
        if 'CG_API_KEY' in os.environ:
            pass
        else:
            print("ERROR : The CloudGuard API key has not been defined in environment variables")
            sys.exit(0)
        if 'CG_API_SECRET' in os.environ:
            pass
        else:
            print("ERROR : The CloudGuard API key secret not been defined in environment variables")
            sys.exit(0)
        if 'AZURE_TENANT_ID' in os.environ:
            pass
        else:
            print("ERROR : The Azure AD tenant ID has not been defined in environment variables")
            sys.exit(0)
        if 'AZURE_CLIENT_ID' in os.environ:
            pass
        else:
            print("ERROR : The Azure AD application ID has not been defined in environment variables")
            sys.exit(0)
        if 'AZURE_CLIENT_SECRET' in os.environ:
            pass
        else:
            print("ERROR : The Azure AD application secret key has not been defined in environment variables")
            sys.exit(0)
        if 'CG_REGION' in os.environ and os.environ['CG_REGION'] in ['AP2', 'AP3', 'EU1']:
            cloudguard_endpoint_host = f"api.{os.environ['CG_REGION'].lower()}.dome9.com"
        else:
            cloudguard_endpoint_host = 'api.dome9.com'
    except:
        sys.exit(0)

verify_env_variables()

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
def list_subscriptions():
    try:
        for sub in sub_client.subscriptions.list():
            print('Subscription found:', sub.subscription_id, sub.display_name)
            payload = {'name':sub.display_name,'subscriptionId':sub.subscription_id,'tenantId':az_tenant,'credentials': {'clientId':az_appid,'clientPassword':az_appkey},'operationMode':cg_operation_mode,'vendor':'azure'}
            r = requests.post(f"https://{cloudguard_endpoint_host}/v2/AzureCloudAccount", json=payload, headers=headers, auth=(cg_api_key,cg_api_secret))
            if r.status_code == 201:
                print('Subscription successfully added to CloudGuard:',sub.subscription_id)
            elif r.status_code == 400:
                print('There was an error with the subscription, please check credentials and that it does not already exist in CloudGuard')
            elif r.status_code == 401:
                print('Bad credentials onboarding subscription to CloudGuard:',sub.subscription_id)
            else:
                print('Unknown error onboarding subscription to CloudGuard:',sub.subscription_id,'Status Code:',r.status_code)
            print(r.content)
        msg="Operation complete"
        return msg 
    except CloudError as e:
        print(e)

list_subscriptions()