using './main.bicep'

@description('Name of the resource group')
param rgName = 'ragdemo'

@description('Location for all resources')
param rLocation = 'swedencentral'

@description('Publisher name for API Management')
param publisherName = 'ragdemo'

@description('Publisher email for API Management')
param publisherEmail = 'foo@bar.buz'

@description('The OpenAPI document to be used for the API Management service')
param openapi = loadTextContent('./openapi.json')
