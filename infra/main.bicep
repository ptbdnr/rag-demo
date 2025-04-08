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
var storageQueueDataContributorId = '974c5e8b-45b9-4653-ba55-5f855dd0fb88' // for Azure Durable Functions
// var storageTableDataContributorId = '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3'
var monitoringMetricsPublisherId = '3913510d-42f4-4e42-8a64-420c390055eb'

var funcDocProcessorAppName = addPrefixAndSuffix('func-docprocessor')

var funcDocProcessorSaContainerName = 'func-docprocessor-package-${rNameSuffix}'

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
    resource deploymentDocProcessorContainer 'containers' = {
      name: funcDocProcessorSaContainerName
      properties: {
        publicAccess: 'None'
      }
    }

    resource objectStoreContainer 'containers' = {
        name: 'objectstore'
        properties: {
          publicAccess: 'None'
        }
      }
  }
}

// Cosmos DB - NoSQL
resource nosqlAccount 'Microsoft.DocumentDB/databaseAccounts@2022-05-15' = {
    name: addPrefixAndSuffix('nosql')
    location: rLocation
    kind: 'GlobalDocumentDB'
    properties: {
      consistencyPolicy: {
        defaultConsistencyLevel: 'Eventual'
      }
      locations: [{
        locationName: rLocation
        failoverPriority: 0
        isZoneRedundant: false
      }]
      databaseAccountOfferType: 'Standard'
      enableAutomaticFailover: true
      apiProperties: {
        serverVersion: '4.2'
      }
      capabilities: [
        {
          name: 'DisableRateLimitingResponses'
        }
      ]
    }
  }
  
  resource nosqlKnowledgeDatabase 'Microsoft.DocumentDB/databaseAccounts/mongodbDatabases@2022-05-15' = {
    parent: nosqlAccount
    name: rgName
    properties: {
      resource: {
        id: '_id'
      }
      options: {
        throughput: 400
      }
    }
  }
  
  var nosqlKnowledgeCollectionName = 'collection1'
  resource nosqlCustomerCollectionCustomers 'Microsoft.DocumentDb/databaseAccounts/mongodbDatabases/collections@2022-05-15' = {
    parent: nosqlKnowledgeDatabase
    name: nosqlKnowledgeCollectionName
    properties: {
      resource: {
        id: nosqlKnowledgeCollectionName
        shardKey: {
          _shard_key: 'Hash'
        }
        indexes: [
          {
            key: {
              keys: [
                '_id'
                '_shard_key'
              ]
            }
          }
          {
            key: {
              keys: [
                '$**'
              ]
            }
          }
        ]
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
        'hidden-link:${resourceId('Microsoft.Web/sites', funcDocProcessorAppName)}': 'Resource'
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
    name: guid(subscription().id, sa.id, funcUAI.id, 'BlobDataOwner')
    scope: sa
    properties: {
        roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataOwnerRoleId)
        principalId: funcUAI.properties.principalId
        principalType: 'ServicePrincipal'
    }
}

// required for Azure Durable Functions
resource roleAssignmentQueueDataContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
    name: guid(subscription().id, sa.id, funcUAI.id, 'QueueDataContributor')
    scope: sa
    properties: {
        roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageQueueDataContributorId)
        principalId: funcUAI.properties.principalId
        principalType: 'ServicePrincipal'
    }
}

// optional
// resource roleAssignmentTableDataContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
//     name: guid(subscription().id, sa.id, funcUAI.id, 'TableDataContributor')
//     scope: sa
//     properties: {
//         roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageTableDataContributorId)
//         principalId: funcUAI.properties.principalId
//         principalType: 'ServicePrincipal'
//     }
// }

resource roleAssignmentBlobDataContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
    name: guid(subscription().id, sa.id, funcUAI.id, 'BlobDataContributor')
    scope: sa
    properties: {
        roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
        principalId: funcUAI.properties.principalId
        principalType: 'ServicePrincipal'
    }
}

// Assign the User Assigned Identity to the Application Insights
resource roleAssignmentMetricsPublisher 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
    name: guid(subscription().id, applicationInsights.id, funcUAI.id, 'MetricsPublisher')
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
resource aspDocProcessor 'Microsoft.Web/serverfarms@2024-04-01' = {
    name: addPrefixAndSuffix('asp-docprocessor')
    location: rLocation
    kind: 'functionapp'
    sku: {
        name: 'FC1'
        tier: 'FlexConsumption'
    }
    properties: {
      reserved: true
    }
}

// Function App (Python 3.11)
resource funcDocProcessor 'Microsoft.Web/sites@2024-04-01' = {
    name: funcDocProcessorAppName
    location: rLocation
    kind: 'functionapp,linux'
    identity: {
        type: 'UserAssigned'
        userAssignedIdentities: {
            '${funcUAI.id}':{}
        }
    }
    properties: {
        serverFarmId: aspDocProcessor.id
        siteConfig: {
            minTlsVersion: '1.2'
            cors: {
                allowedOrigins: [
                  'https://portal.azure.com'
                ]
                supportCredentials: true
            }
        }
        functionAppConfig: {
            deployment: {
                storage: {
                    type: 'blobContainer'
                    value: '${sa.properties.primaryEndpoints.blob}${funcDocProcessorSaContainerName}'
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
            AzureWebJobsStorage__credential: 'managedidentity'
            AzureWebJobsStorage__clientId: funcUAI.properties.clientId
            APPLICATIONINSIGHTS_INSTRUMENTATIONKEY: applicationInsights.properties.InstrumentationKey
            APPLICATIONINSIGHTS_AUTHENTICATION_STRING: 'ClientId=${funcUAI.properties.clientId};Authorization=AAD'
            AzureWebJobsFeatureFlags: 'EnableWorkerIndexing'
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
        serviceUrl: 'https://${funcDocProcessor.properties.defaultHostName}/api'
    }
}
