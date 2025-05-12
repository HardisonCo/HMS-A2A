# Event Synchronization System

The Event Synchronization System provides a robust mechanism for communication between different components of the HMS-API to Crohn's Adaptive Trials integration. It enables real-time notification and data exchange between components, ensuring a cohesive and responsive application experience.

## Core Components

### EventManager

The EventManager is the central component of the event system. It handles:

- Registration of event listeners
- Emission of events to local listeners
- Broadcasting events to all components
- Managing event history for debugging
- Synchronizing with persistent storage

### Event

The Event class represents a single event in the system. It contains:

- Event name
- Payload data
- Metadata and options
- Timestamp and unique ID
- Propagation control

### EventPersistence

The EventPersistence interface and its implementation handle:

- Storing events in a database
- Retrieving unprocessed events
- Marking events as processed
- Querying event history
- Clean-up of old events

### EventSynchronizer

The EventSynchronizer interface and its implementation manage:

- Communication between different components
- Registration with the event network
- Subscription to specific events
- Connection management
- Component discovery

## Usage Examples

### Basic Usage

```php
// Get the event manager
$eventManager = EventManager::getInstance();

// Register an event listener
$eventManager->on('protocol.updated', function (Event $event) {
    $protocol = $event->getPayload();
    // Handle protocol update
    echo "Protocol {$protocol['id']} was updated\n";
});

// Emit an event locally
$eventManager->emit('protocol.updated', [
    'id' => 'proto-1234',
    'version' => '1.2.0',
    'status' => 'Active'
]);
```

### Broadcasting Events

```php
// Broadcast an event to all components
$eventManager->broadcast('genetic.optimization.completed', [
    'protocolId' => 'proto-1234',
    'optimizationId' => 'opt-5678',
    'metrics' => [
        'patientOutcomes' => 0.85,
        'costEffectiveness' => 0.72
    ]
]);
```

### One-time Listeners

```php
// Register a one-time event listener
$eventManager->once('verification.complete', function (Event $event) {
    // This will only be called once
    echo "Verification completed with status: {$event->getPayload()['status']}\n";
});
```

### Event Persistence

```php
// Get the persistence interface
$persistence = app(EventPersistenceInterface::class);

// Retrieve event history for a specific event
$events = $persistence->getEventsByName('protocol.updated', 10, 0);

foreach ($events as $event) {
    echo "Protocol {$event->getPayload()['id']} was updated at " . 
         date('Y-m-d H:i:s', $event->getTimestamp()) . "\n";
}
```

### Component Communication

```php
// Get the synchronizer
$synchronizer = app(EventSynchronizerInterface::class);

// Connect to the event network
$synchronizer->connect();

// Subscribe to events from another component
$synchronizer->subscribeToEvent('genetic.optimization.completed', 'genetic-engine');

// Send an event to a specific component
$event = new Event('protocol.verification.requested', [
    'protocolId' => 'proto-1234',
    'verificationLevel' => 'comprehensive'
]);

$synchronizer->sendEventTo($event, 'verification-engine');
```

## Integration Points

### Genetic Engine Integration

The Event Synchronization System integrates with the Genetic Engine through these key events:

- `genetic.optimization.requested`: Requests optimization for a protocol
- `genetic.optimization.started`: Signals the start of optimization
- `genetic.optimization.progress`: Updates on optimization progress
- `genetic.optimization.completed`: Signals optimization completion with results
- `genetic.optimization.failed`: Indicates optimization failure with error details

### Protocol Verification Integration

Integration with the Protocol Verification system includes these events:

- `protocol.verification.requested`: Requests verification of a protocol
- `protocol.verification.started`: Signals the start of verification
- `protocol.verification.progress`: Updates on verification progress
- `protocol.verification.completed`: Signals verification completion with results
- `protocol.verification.failed`: Indicates verification failure with error details

### HMS-GOV Visualization Integration

The HMS-GOV visualization UI receives updates through these events:

- `protocol.updated`: Notifies about protocol updates
- `genetic.result.available`: Signals new genetic optimization results
- `verification.result.available`: Signals new verification results
- `patient.outcome.prediction.updated`: Updates predicted patient outcomes

## Error Handling

The Event Synchronization System includes robust error handling:

- Listeners catch and log exceptions to prevent cascading failures
- Connection issues with remote components are handled gracefully
- Persistent storage ensures events aren't lost during outages
- Retry mechanisms for failed synchronization attempts
- Detailed error logging for troubleshooting

## Configuration

The system can be configured through the `event_synchronization.php` config file:

```php
return [
    // Component identification
    'component_id' => 'agency-interface',
    
    // Event hub connection
    'hub_url' => env('EVENT_HUB_URL', 'http://localhost:8000/api/event-hub'),
    'auth_token' => env('EVENT_HUB_TOKEN'),
    
    // Connection settings
    'connection_timeout' => 5.0,
    'request_timeout' => 10.0,
    'retry_attempts' => 3,
    'retry_delay' => 1.0,
    
    // Auto-connect on startup
    'auto_connect' => true,
    
    // Callback URL for receiving events
    'callback_url' => env('EVENT_CALLBACK_URL'),
    
    // Database settings
    'database' => [
        'connection' => env('EVENT_DB_CONNECTION', env('DB_CONNECTION', 'mysql')),
        'table' => 'event_sync_events',
    ],
    
    // Event cleanup
    'cleanup' => [
        'frequency' => 'daily', // Options: hourly, daily, weekly
        'retention_days' => 30, // Number of days to keep events
    ],
];
```

## Security

The Event Synchronization System implements these security measures:

- Authentication via JWT tokens for component verification
- Authorization checks for event broadcasting and subscription
- Validation of event data to prevent injection attacks
- Encryption of sensitive event payloads
- Rate limiting to prevent DoS attacks

## Performance Considerations

For optimal performance:

- Use specific event names to reduce unnecessary processing
- Limit payload size to essential data
- Consider using one-time listeners when appropriate
- Implement filtering at the subscription level
- Use the persistence layer for non-real-time requirements