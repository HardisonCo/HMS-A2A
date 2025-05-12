# HMS-A2A – API Specification

## 1. Title & Purpose
(Facilitates Application-to-Application (A2A) data exchange within the HMS ecosystem, allowing subsystems to request or fulfill data sharing operations.)

## 2. API Endpoints
1. POST /v1/a2a/requests
   - Description: Creates a new request for data exchange.
   - Body: JSON { sourceApp, destinationApp, requestType, ... }.
   - Response: { requestId, status }

2. GET /v1/a2a/requests/{id}
   - Description: Retrieves the current status and metadata of an A2A request.
   - Path Param: id (UUID)
   - Response: { id, sourceApp, destinationApp, requestType, status, created_at, updated_at }.

3. POST /v1/a2a/requests/{id}/fulfill
   - Description: Submits or updates the data payload for an existing request.
   - Path Param: id (UUID)
   - Body: JSON or multipart with the actual data payload.
   - Response: success or error message, updated status.

4. Optional: asynchronous callbacks or queue messages on topic "a2a-fulfillment" for watchers.

## 3. Authentication & Authorization
• Bearer JWT tokens validated.
• Roles:
  – admin: Full control over requests, system-level settings.
  – integrator: Create/fulfill requests, read statuses.
  – viewer: Read-only on existing requests.
• OPA or role-based checks ensuring only integrator or admin can fulfill requests.

## 4. Dependencies & External Integrations
• Connects to multiple HMS modules (EMR, ESR, genetic-engine, marketplace, etc.) depending on the data exchange request.
• Potential HPC usage if large data sets or transformations are needed.

## 5. Versioning & Lifecycle
• Current stable version: v1.
• Future expansions: multi-step request flows, partial fulfillments.
• Deprecation policy: existing requests are valid until completion.

## 6. Testing & Validation
• Integration tests verifying requests creation, fulfillment in various roles.
• Possibly load tests if large volumes of A2A requests are expected.
• Proposed: end-to-end tests simulating request from source to destination using a queue.
