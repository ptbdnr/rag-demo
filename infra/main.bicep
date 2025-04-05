targetScope = 'resourceGroup'


//********************************************
// Parameters
//********************************************

@description('Location for all resources')
param rLocation string

@description('OpenAPI specification')
param openapi string


//********************************************
// Variables
//********************************************

var rNamePrefix = 'ragdemo'
var rNameSuffix = guid(rNamePrefix)

func addPrefixAndSuffix(name string) string => '${main.rgNamePrefix}-${name}-${rNameSuffix}'
func nohyphen(input string) string => toLower(replace(input, '-', ''))

var funcSaContainerName = 'func-package-${rNameSuffix}'
var funcAppName = addPrefixAndSuffix('func')

//********************************************
// Azure resources
//********************************************


// Container Registry
// ref https://learn.microsoft.com/en-us/azure/templates/microsoft.containerregistry/registries?pivots=deployment-language-bicep#resource-format
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: nohyphen(addPrefixAndSuffix('acr'))
  location: rLocation
  sku: {
    name: 'Standard'
  }
  properties: {
    adminUserEnabled: true
  }
}

// Storage Account 
// with Container for Function App
resource saBack 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: nohyphen(addPrefixAndSuffix('sa'))
  location: rLocation
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    dnsEndpointType: 'Standard'
    minimumTlsVersion: 'TLS1_2'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
    publicNetworkAccess: 'Enabled'
    defaultToOAuthAuthentication: false
  }
  resource blobServices 'blobServices' = {
    name: 'default'
    properties: {
      deleteRetentionPolicy: {}
    }
    resource deploymentContainer 'containers' = {
      name: funcSaContainerName
      properties: {
        publicAccess: 'None'
      }
    }
  }
}