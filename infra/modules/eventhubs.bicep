param location string
param tags object
param name string
param principalId string = ''

// Standard is the lowest tier that exposes the Kafka endpoint Spark uses in chapter 09.
resource ns 'Microsoft.EventHub/namespaces@2024-01-01' = {
  name: name
  location: location
  tags: tags
  sku: { name: 'Standard', tier: 'Standard', capacity: 1 }
  properties: {
    minimumTlsVersion: '1.2'
  }
}

resource hub 'Microsoft.EventHub/namespaces/eventhubs@2024-01-01' = {
  parent: ns
  name: 'sensor-pings'
  properties: {
    partitionCount: 2
    messageRetentionInDays: 1
  }
}

// Azure Event Hubs Data Owner for the deploying user (to publish simulated pings).
resource userRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(principalId)) {
  scope: ns
  name: guid(ns.id, principalId, 'f526a384-b230-433a-b45c-95f59c4a2dec')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'f526a384-b230-433a-b45c-95f59c4a2dec')
  }
}

output name string = ns.name
