What does this script do?
-------------------------

It logs into an Azure AD tenant, obtains a list of all subscriptions attached to it and then adds them one by one to Dome9 in read only mode. It can be used as an Azure Function to run daily to sweep up any new subscriptions not onboarded.

Pre-requisites
--------------
To run this script, you will need the following:-

1) **Python 3.6** (or newer)

2) An Azure AD **Application Registration** (see *https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal*)

3) Azure environment information
    - Azure AD **tenant ID**
    - Azure **Application (Client) ID**
    - Azure **Application (Client) Secret Key**
    
4) Dome9 API key with admin permissions to add subscriptions (*https://supportcenter.checkpoint.com/supportcenter/portal?eventSubmit_doGoviewsolutiondetails=&solutionid=sk144514&partition=General&product=CloudGuard*)
    - Dome9 **API key**
    - Dome9 **API secret**
    
5) You will need the **Azure Management Group** construct configured against your Azure AD (see *https://docs.microsoft.com/en-us/azure/governance/management-groups/overview* for further information). This is so that any new subscriptions added against the Azure AD tenant are visible to the onboarding tool. **Adding the Application ID as a Contributor in the IAM Access Control blade in the Tenant Root Group will provide this capability.**

6) Clone the repository locally

7) Run **pip install -r requirements.txt** to install required Python modules
    
Setup
-----
To run the script locally, you need to set several environment variables which are then read in by the script. This prevents any secret keys being hard coded into the script. Set the following:-

- SET D9_API_KEY=xxxxxxxxxxx
- SET D9_API_SECRET=xxxxxxxxxxxx
- SET AZURE_TENANT_ID=xxxxxxxxxx
- SET AZURE_CLIENT_ID=xxxxxxxxxxx
- SET AZURE_CLIENT_SECRET=xxxxxxxxxxxxxxx

Running the script
------------------
Simply run the script **onboard.py**

[![Deploy to Azure](https://azuredeploy.net/deploybutton.png)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchrisbeckett%2Fazd9-autoonboarding%2Fmaster%2Ftemplate.json)
