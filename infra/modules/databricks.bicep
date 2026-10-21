param location string
param tags object
param name string
param managedResourceGroupName string

// Premium is required for Unity Catalog features such as row filters and column masks.
resource dbw 'Microsoft.Databricks/workspaces@2024-05-01' = {
  name: name
  location: location
  tags: tags
  sku: { name: 'premium' }
  properties: {
    managedResourceGroupId: subscriptionResourceId('Microsoft.Resources/resourceGroups', managedResourceGroupName)
  }
}

output name string = dbw.name
output url string = 'https://${dbw.properties.workspaceUrl}'
