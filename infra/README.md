## Prerequisites

- Azure CLI
- Bicep CLI

## Deployment Steps

0. Ensure you have configured the certificates on your machine

if applicable

1. Login to Azure

```sh
az login --tenant <your-tenant-id>
```

2. Set the subscription

```sh
az account set --subscription <your-subscription-id>
```

3. Deploy the Bicep template

Create resource group(s) on Azure

Create resource(s) within an existing resource group
```sh
export RESOURCE_GROUP_NAME="ragdemo"
export TEMPLATE_FILEPATH="main.bicep"
export PARAMETERS_FILEPATH="main.bicepparam"
az deployment group create --name $RESOURCE_GROUP_NAME'-'$(date +"%Y-%b-%d") --resource-group $RESOURCE_GROUP_NAME --template-file $TEMPLATE_FILEPATH --parameters $PARAMETERS_FILEPATH 
```