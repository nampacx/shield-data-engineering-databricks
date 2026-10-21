targetScope = 'subscription'

@minLength(1)
@maxLength(16)
@description('azd environment name, used to derive resource names.')
param environmentName string

@allowed([ 'swedencentral', 'germanywestcentral' ])
@description('Azure region. Both support Databricks serverless compute.')
param location string = 'swedencentral'

@description('Object ID of the deploying user; gets data-plane access to Key Vault, storage and Event Hubs.')
param principalId string = ''

var tags = { 'azd-env-name': environmentName, project: 'shield-data-engineering' }
var token = toLower(uniqueString(subscription().id, environmentName, location))

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

module storage 'modules/storage.bicep' = {
  scope: rg
  name: 'storage'
  params: { location: location, tags: tags, name: 'st${take(token, 20)}', principalId: principalId }
}

module connector 'modules/access-connector.bicep' = {
  scope: rg
  name: 'access-connector'
  params: { location: location, tags: tags, name: 'dbac-${environmentName}', storageAccountName: storage.outputs.name }
}

module databricks 'modules/databricks.bicep' = {
  scope: rg
  name: 'databricks'
  params: { location: location, tags: tags, name: 'dbw-${environmentName}', managedResourceGroupName: 'rg-${environmentName}-dbw-managed' }
}

module keyvault 'modules/keyvault.bicep' = {
  scope: rg
  name: 'keyvault'
  params: { location: location, tags: tags, name: 'kv-${take(token, 20)}', principalId: principalId }
}

module eventhubs 'modules/eventhubs.bicep' = {
  scope: rg
  name: 'eventhubs'
  params: { location: location, tags: tags, name: 'evhns-${take(token, 18)}', principalId: principalId }
}

output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = rg.name
output DATABRICKS_WORKSPACE_NAME string = databricks.outputs.name
output DATABRICKS_HOST string = databricks.outputs.url
output STORAGE_ACCOUNT_NAME string = storage.outputs.name
output ACCESS_CONNECTOR_ID string = connector.outputs.id
output KEY_VAULT_NAME string = keyvault.outputs.name
output EVENT_HUB_NAMESPACE string = eventhubs.outputs.name
