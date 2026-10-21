param location string
param tags object
param name string
param storageAccountName string

resource sa 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

// Managed identity that Unity Catalog uses to reach the storage account.
resource connector 'Microsoft.Databricks/accessConnectors@2024-05-01' = {
  name: name
  location: location
  tags: tags
  identity: { type: 'SystemAssigned' }
}

resource role 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: sa
  name: guid(sa.id, connector.id, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  properties: {
    principalId: connector.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  }
}

output id string = connector.id
