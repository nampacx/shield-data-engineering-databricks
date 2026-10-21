param location string
param tags object
param name string
param principalId string = ''

resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: tenant().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
  }
}

// Key Vault Secrets Officer for the deploying user.
resource userRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(principalId)) {
  scope: kv
  name: guid(kv.id, principalId, 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7')
  }
}

output name string = kv.name
