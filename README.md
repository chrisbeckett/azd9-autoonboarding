What does this script do?

It logs into an Azure AD tenant, obtains a list of all subscriptions attached to it and then adds them one by one to Dome9 in read only mode. It can be used as an Azure Function to run daily to sweep up any new subscriptions not onboarded.

PRE-REQUISITES
=====
To run this script, you will need the following:-

1) You will need Python 3.6 (or newer)

2) Azure environment information
    a) Azure AD tenant ID
    b) Azure Application (Client) ID
    c) Azure Application (Client) Secret Key
    
3) Dome9 API key with admin permissions to add subscriptions
    a) Dome9 API key
    b) Dome9 API secret
    
