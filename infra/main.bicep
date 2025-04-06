targetScope = 'resourceGroup'


//********************************************
// Parameters
//********************************************

@description('Name of the resource group')
param rgName string

@description('Location for all resources')
param rLocation string

@description('OpenAPI specification')
param openapi string

@description('Logic App schema')
param logicAppSchema string

@description('Publisher name for API Management')
param publisherName string

@description('Publisher email for API Management')
param publisherEmail string


//********************************************
// Variables
//********************************************

var rNamePrefix = rgName
var rNameSuffix = take(guid(rNamePrefix, 'ptbdnr'),8)

func addPrefixAndSuffix(name string) string => '${rNamePrefix}-${name}-${rNameSuffix}'
func nohyphen(input string) string => toLower(replace(input, '-', ''))

// Define the IDs of the roles we need to assign to our managed identities.
var storageBlobDataOwnerRoleId  = 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b'
var storageBlobDataContributorRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
var monitoringMetricsPublisherId = '3913510d-42f4-4e42-8a64-420c390055eb'

var funcDocLoaderAppName = addPrefixAndSuffix('func-docloader')
var funcDocSplitterAppName = addPrefixAndSuffix('func-docsplitter')
var funcEncoderAppName = addPrefixAndSuffix('func-encoder')

var funcDocLoaderSaContainerName = 'func-docloader-package-${rNameSuffix}'
var funcDocSplitterSaContainerName = 'func-docsplitter-package-${rNameSuffix}'
var funcEncoderSaContainerName = 'func-encoder-package-${rNameSuffix}'

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
resource sa 'Microsoft.Storage/storageAccounts@2024-01-01' = {
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
    resource deploymentDocLoaderContainer 'containers' = {
      name: funcDocLoaderSaContainerName
      properties: {
        publicAccess: 'None'
      }
    }
    resource deploymentDocSplitterContainer 'containers' = {
        name: funcDocSplitterSaContainerName
        properties: {
          publicAccess: 'None'
        }
    }
    resource deploymentEncoderContainer 'containers' = {
        name: funcEncoderSaContainerName
        properties: {
            publicAccess: 'None'
        }
    }
  }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
    name: addPrefixAndSuffix('log-analytics')
    location: rLocation
    properties: any({
        retentionInDays: 30
        features: {
        searchVersion: 1
        }
        sku: {
        name: 'PerGB2018'
        }
    })
}
  
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
    name: addPrefixAndSuffix('appi')
    location: rLocation
    kind: 'web'
    tags: {
        'hidden-link:${resourceId('Microsoft.Web/sites', funcDocLoaderAppName)}': 'Resource'
        'hidden-link:${resourceId('Microsoft.Web/sites', funcDocSplitterAppName)}': 'Resource'
        'hidden-link:${resourceId('Microsoft.Web/sites', funcEncoderAppName)}': 'Resource'
    }
    properties: {
        Application_Type: 'web'
        WorkspaceResourceId: logAnalytics.id
        DisableLocalAuth: true
    }
}

//********************************************
// Identity
//********************************************

// User Assigned Identity
resource funcUAI 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
    name: addPrefixAndSuffix('uai')
    location: rLocation
  }
  
// Role Assignments
// Assign the User Assigned Identity to the Storage Account
resource roleAssignmentBlobDataOwner 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
    name: guid(subscription().id, sa.id, funcUAI.id, 'Storage Blob Data Owner')
    scope: sa
    properties: {
        roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataOwnerRoleId)
        principalId: funcUAI.properties.principalId
        principalType: 'ServicePrincipal'
    }
}

// Assign the User Assigned Identity to the Storage Account
resource roleAssignmentBlob 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
    name: guid(subscription().id, sa.id, funcUAI.id, 'Storage Blob Data Contributor')
    scope: sa
    properties: {
        roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
        principalId: funcUAI.properties.principalId
        principalType: 'ServicePrincipal'
    }
}

resource roleAssignmentAppInsights 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
    name: guid(subscription().id, applicationInsights.id, funcUAI.id, 'Monitoring Metrics Publisher')
    scope: applicationInsights
    properties: {
        roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', monitoringMetricsPublisherId)
        principalId: funcUAI.properties.principalId
        principalType: 'ServicePrincipal'
    }
}

//********************************************
// App Service Plan and Function App definitions
//********************************************

// App Service Plan for Function App
resource asp 'Microsoft.Web/serverfarms@2024-04-01' = {
    name: addPrefixAndSuffix('asp')
    location: rLocation
    kind: 'functionapp'
    sku: {
      name: 'P1v3'
      tier: 'FlexConsumption'
    }
    properties: {
      reserved: true
    }
}

// Function App (Python 3.11)
resource funcDocLoader 'Microsoft.Web/sites@2024-04-01' = {
    name: funcDocLoaderAppName
    location: rLocation
    kind: 'functionapp,linux'
    identity: {
        type: 'UserAssigned'
        userAssignedIdentities: {
            '${funcUAI.id}':{}
        }
    }
    properties: {
        serverFarmId: asp.id
        siteConfig: {
            minTlsVersion: '1.2'
        }
        functionAppConfig: {
            deployment: {
                storage: {
                    type: 'blobContainer'
                    value: '${sa.properties.primaryEndpoints.blob}${funcDocLoaderSaContainerName}'
                    authentication: {
                        type: 'UserAssignedIdentity'
                        userAssignedIdentityResourceId: funcUAI.id
                    }
                }
            }
            scaleAndConcurrency: {
                maximumInstanceCount: 100
                instanceMemoryMB: 4096
            }
            runtime: {
                name: 'python'
                version: '3.11'
            }
        }
    }

    resource configAppSettings 'config' = {
        name: 'appsettings'
        properties: {
            AzureWebJobsStorage__accountName: sa.name
            AzureWebJobsStorage__credential : 'managedidentity'
            AzureWebJobsStorage__clientId: funcUAI.properties.clientId
            APPLICATIONINSIGHTS_INSTRUMENTATIONKEY: applicationInsights.properties.InstrumentationKey
            APPLICATIONINSIGHTS_AUTHENTICATION_STRING: 'ClientId=${funcUAI.properties.clientId};Authorization=AAD'
        }
    }

    dependsOn: [
        applicationInsights
    ]
}

// Function App (Python 3.11)
resource funcDocSplitter 'Microsoft.Web/sites@2024-04-01' = {
    name: funcDocSplitterAppName
    location: rLocation
    kind: 'functionapp,linux'
    identity: {
        type: 'UserAssigned'
        userAssignedIdentities: {
            '${funcUAI.id}':{}
        }
    }
    properties: {
        serverFarmId: asp.id
        siteConfig: {
            minTlsVersion: '1.2'
        }
        functionAppConfig: {
            deployment: {
                storage: {
                    type: 'blobContainer'
                    value: '${sa.properties.primaryEndpoints.blob}${funcDocSplitterSaContainerName}'
                    authentication: {
                        type: 'UserAssignedIdentity'
                        userAssignedIdentityResourceId: funcUAI.id
                    }
                }
            }
            scaleAndConcurrency: {
                maximumInstanceCount: 100
                instanceMemoryMB: 4096
            }
            runtime: {
                name: 'python'
                version: '3.11'
            }
        }
    }

    resource configAppSettings 'config' = {
        name: 'appsettings'
        properties: {
            AzureWebJobsStorage__accountName: sa.name
            AzureWebJobsStorage__credential : 'managedidentity'
            AzureWebJobsStorage__clientId: funcUAI.properties.clientId
            APPLICATIONINSIGHTS_INSTRUMENTATIONKEY: applicationInsights.properties.InstrumentationKey
            APPLICATIONINSIGHTS_AUTHENTICATION_STRING: 'ClientId=${funcUAI.properties.clientId};Authorization=AAD'
        }
    }

    dependsOn: [
        applicationInsights
    ]
}

// Function App (Python 3.11)
resource funcEncoder 'Microsoft.Web/sites@2024-04-01' = {
    name: funcEncoderAppName
    location: rLocation
    kind: 'functionapp,linux'
    identity: {
        type: 'UserAssigned'
        userAssignedIdentities: {
            '${funcUAI.id}':{}
        }
    }
    properties: {
        serverFarmId: asp.id
        siteConfig: {
            minTlsVersion: '1.2'
        }
        functionAppConfig: {
            deployment: {
                storage: {
                    type: 'blobContainer'
                    value: '${sa.properties.primaryEndpoints.blob}${funcEncoderSaContainerName}'
                    authentication: {
                        type: 'UserAssignedIdentity'
                        userAssignedIdentityResourceId: funcUAI.id
                    }
                }
            }
            scaleAndConcurrency: {
                maximumInstanceCount: 100
                instanceMemoryMB: 4096
            }
            runtime: {
                name: 'python'
                version: '3.11'
            }
        }
    }

    resource configAppSettings 'config' = {
        name: 'appsettings'
        properties: {
            AzureWebJobsStorage__accountName: sa.name
            AzureWebJobsStorage__credential : 'managedidentity'
            AzureWebJobsStorage__clientId: funcUAI.properties.clientId
            APPLICATIONINSIGHTS_INSTRUMENTATIONKEY: applicationInsights.properties.InstrumentationKey
            APPLICATIONINSIGHTS_AUTHENTICATION_STRING: 'ClientId=${funcUAI.properties.clientId};Authorization=AAD'
        }
    }

    dependsOn: [
        applicationInsights
    ]
}

// Logic App
// resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
//     name: addPrefixAndSuffix('logicapp')
//     location: rLocation
//     tags: {
//         displayName: addPrefixAndSuffix('logicapp')
//     }
//     properties: {
//         definition: {
//         '$schema': logicAppSchema
//         contentVersion: '1.0.0.0'
//         parameters: {
//         }
//         triggers: {
//         }
//         actions: {
//         }
//         }
//     }
// }

// API Management
resource apiMgmt 'Microsoft.ApiManagement/service@2024-05-01' = {
    name: addPrefixAndSuffix('apim')
    location: rLocation
    sku: {
        name: 'Developer'
        capacity: 1
    }
    properties: {
        publisherName: publisherName
        publisherEmail: publisherEmail
    }
}

resource apimLogger 'Microsoft.ApiManagement/service/loggers@2022-08-01' = {
    name: addPrefixAndSuffix('apim-logger')
    parent: apiMgmt
    properties: {
        loggerType: 'applicationInsights'
        description: 'Application Insights logger with system-assigned managed identity'
        credentials: {
        connectionString: 'InstrumentationKey=${applicationInsights.properties.InstrumentationKey}'
        }
    }
}

// API Management User
resource apimSubscription 'Microsoft.ApiManagement/service/subscriptions@2024-06-01-preview' = {
    parent: apiMgmt
    name: addPrefixAndSuffix('apim-subscription')
    properties: {
        allowTracing: true
        displayName: rNamePrefix
        scope: '/apis'
    }
}

// API for Chunking
resource apimapiDocProcessing 'Microsoft.ApiManagement/service/apis@2024-05-01' = {
    parent: apiMgmt
    name: addPrefixAndSuffix('api-docprocess')
    properties: {
        type: 'http'
        displayName: 'DocProcess'
        description: 'API for DocProcess'
        path: 'data'
        subscriptionRequired: true
        format: 'openapi+json'
        value: openapi
        serviceUrl: 'https://${funcDocLoader.properties.defaultHostName}/api/search'
    }
}
