# agency-interface – API Specification

## 1. Title & Purpose
The Agency Interface API provides a set of endpoints for launching and interacting with Codex CLI in agency-specific contexts. It enables access to federal agency data, implementation plans, and issue tracking capabilities across various domains including healthcare, agriculture, defense, and more.

## 2. API Endpoints

### CLI Interface Endpoints

1. GET `/api/v1/agencies`
   - Description: Retrieves a list of all available agencies.
   - Query Params: `tier` (optional, filter by tier 1-8)
   - Response: JSON array of agency objects with IDs, names, tiers, and status.

2. GET `/api/v1/agencies/{agency_id}`
   - Description: Retrieves detailed information about a specific agency.
   - Path Param: `agency_id` (string)
   - Response: Detailed agency object with metadata, domains, and implementation status.

3. GET `/api/v1/agencies/{agency_id}/ascii-art`
   - Description: Retrieves ASCII art for a specific agency.
   - Path Param: `agency_id` (string)
   - Response: ASCII art string ready for terminal display.

4. GET `/api/v1/agencies/{agency_id}/topics`
   - Description: Retrieves available topics for a specific agency.
   - Path Param: `agency_id` (string)
   - Response: Array of topic objects with IDs, names, and descriptions.

5. POST `/api/v1/agencies/{agency_id}/launch`
   - Description: Launches a Codex CLI instance with agency-specific context.
   - Path Param: `agency_id` (string)
   - Body: JSON with `topic_id` and optional `prompt`
   - Response: Launch status and context information.

### Issue Finder Endpoints

1. GET `/api/v1/agencies/{agency_id}/issues`
   - Description: Retrieves current issues for a specific agency.
   - Path Param: `agency_id` (string)
   - Query Params: `topic_id` (optional), `severity` (optional)
   - Response: Array of issue objects with details and contexts.

2. GET `/api/v1/agencies/{agency_id}/research`
   - Description: Retrieves research materials for a specific agency.
   - Path Param: `agency_id` (string)
   - Query Params: `topic_id` (optional)
   - Response: Array of research document objects.

### FFI Integration Endpoints

1. GET `/api/v1/agencies/{agency_id}/context`
   - Description: Retrieves context information for FFI integration.
   - Path Param: `agency_id` (string)
   - Response: Agency context data suitable for cross-language communication.

2. POST `/api/v1/agencies/{agency_id}/ffi/validate`
   - Description: Validates agency-specific data through FFI.
   - Path Param: `agency_id` (string)
   - Body: Data structure to validate
   - Response: Validation results and errors if any.

### Implementation Management Endpoints

1. GET `/api/v1/agencies/implementation-status`
   - Description: Retrieves implementation status for all agencies.
   - Query Params: `tier` (optional)
   - Response: Implementation status summary with percentages and counts.

2. POST `/api/v1/agencies/generate`
   - Description: Generates agency components using the agency generator.
   - Body: Agency data and domain templates
   - Response: Generation status and results.

3. GET `/api/v1/agencies/{agency_id}/implementation-status`
   - Description: Retrieves detailed implementation status for a specific agency.
   - Path Param: `agency_id` (string)
   - Response: Detailed implementation status for the agency.

## 3. Authentication & Authorization

- JWT-based authentication for secure API access
- Role-based permissions:
  - `admin`: Full access to all endpoints and agency data
  - `developer`: Access to implementation endpoints and agency data
  - `researcher`: Read-only access to agency data and research materials
  - `agency-user`: Access limited to specific agencies based on user profile
- Domain separation with agency-specific tokens
- Rate limiting based on role and endpoint

## 4. Dependencies & External Integrations

- HMS-API: Provides backend services and data storage
- Codex CLI: Launches CLI instances with agency contexts
- Codex-RS: Provides Rust-based agency command processing
- FFI Integration: Enables cross-language communication with Go, Python, Rust, and TypeScript
- Prover System: Provides theorem proving for agency-specific issues
- Self-Healing System: Monitors and repairs agency component issues

## 5. Versioning & Lifecycle

- Current API version: v1
- Versioning strategy: URL-based versioning (e.g., `/api/v1/agencies`)
- Future versions will add enhanced topic support and agent communication
- Deprecation policy: 6 months notice before retiring API versions
- Version evolution to track new agency implementation tiers

## 6. Testing & Validation

- Unit tests for all API endpoints
- Integration tests with Codex CLI
- Test scripts available:
  - `test_agency_interface.sh`: Comprehensive API tests
  - `agency_status_fixed.sh`: Implementation status validation
- Performance testing for agency context switching
- Cross-language FFI testing
- Validation against federal agency metadata
- Test coverage metrics tracked with implementation status