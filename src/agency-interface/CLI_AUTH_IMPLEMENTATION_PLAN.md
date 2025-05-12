# CLI Authentication Implementation Plan

This document outlines the plan to implement a web-based authentication mechanism for the AI Agency CLI interface, allowing users to authenticate with domain-specific admin portals directly from the command line, similar to GitHub's approach.

## 1. Overview

The authentication system will:

1. Generate a unique device code and verification URL
2. Display the URL and code to the user
3. Open the browser (if possible) to the authentication page
4. Poll the server to check authentication status
5. Retrieve and store authentication token upon successful login
6. Provide domain-specific API access based on authenticated user's permissions

## 2. Technical Components

### 2.1 API Endpoints

Based on the existing HMS-API routes, we need to implement:

1. **Device Authorization Endpoint** - Generate a device code and verification URL
2. **Token Endpoint** - Exchange a device code for an access token
3. **Authentication Status Endpoint** - Check the status of a device authorization
4. **Domain-Specific Authorization Endpoint** - Authorize access to specific AI domains

### 2.2 CLI Authentication Module

The CLI tool will need a new authentication module that:

1. Initiates the device authorization flow
2. Displays instructions to the user
3. Opens the browser if possible
4. Polls for authentication status
5. Securely stores and manages authentication tokens
6. Refreshes tokens when necessary

### 2.3 Web Authentication Interface

A web interface that:

1. Accepts the device code
2. Prompts for user credentials
3. Verifies credentials against the HMS-API authentication system
4. Authorizes the device for specific AI domains
5. Confirms successful authentication to the user

## 3. Implementation Plan

### Phase 1: Core Authentication Framework

1. **Create Authentication API Endpoints**
   - Add device authorization endpoints to HMS-API routes
   - Implement device code generation and validation
   - Create token exchange and verification endpoints

2. **Develop CLI Authentication Module**
   - Add `auth` command to CLI
   - Implement device flow initiation
   - Create polling mechanism
   - Develop token storage and management

3. **Build Basic Web Authentication Interface**
   - Create device code validation page
   - Implement user login form
   - Develop success/failure pages

### Phase 2: Domain-Specific Authorization

1. **Implement Domain Authorization Logic**
   - Add domain permissions to authentication tokens
   - Create domain-specific authorization checks
   - Implement role-based access control

2. **Enhance CLI with Domain Authorization**
   - Update CLI to request specific domain access
   - Add domain-specific authentication status
   - Implement domain-restricted command access

3. **Extend Web Interface for Domain Selection**
   - Add domain selection interface
   - Implement role verification for domains
   - Create domain-specific success messages

### Phase 3: Advanced Features and Security

1. **Implement Token Refresh**
   - Add token expiration and refresh logic
   - Create automatic token refresh mechanism
   - Implement token revocation

2. **Enhance Security Measures**
   - Add rate limiting for authentication attempts
   - Implement suspicious activity detection
   - Create audit logging for authentication events

3. **User Management Features**
   - Add authorized devices list in user dashboard
   - Implement device revocation
   - Create login notification system

## 4. Technical Specifications

### 4.1 Authentication Flow

```
┌─────────────┐           ┌────────────┐           ┌───────────────┐
│ CLI Client  │           │ HMS-API    │           │ Web Browser   │
└──────┬──────┘           └──────┬─────┘           └───────┬───────┘
       │                         │                         │
       │  1. Request Device Code │                         │
       │────────────────────────>│                         │
       │                         │                         │
       │  2. Code + Verification URL                       │
       │<────────────────────────│                         │
       │                         │                         │
       │                         │                         │
       │  3. Open Browser with URL                         │
       │────────────────────────────────────────────────────>
       │                         │                         │
       │                         │  4. User Login          │
       │                         │<────────────────────────│
       │                         │                         │
       │  5. Poll for Token      │                         │
       │────────────────────────>│                         │
       │                         │                         │
       │  6. Authentication Token│                         │
       │<────────────────────────│                         │
       │                         │                         │
┌──────┴──────┐           ┌──────┴─────┐           ┌───────┴───────┐
│ CLI Client  │           │ HMS-API    │           │ Web Browser   │
└─────────────┘           └────────────┘           └───────────────┘
```

### 4.2 API Endpoints

1. **Device Authorization**
   - `POST /api/auth/device/authorize`
   - Request: `{ client_id, scope }`
   - Response: `{ device_code, user_code, verification_uri, expires_in, interval }`

2. **Token Exchange**
   - `POST /api/auth/device/token`
   - Request: `{ device_code, client_id }`
   - Response: `{ access_token, token_type, expires_in, refresh_token, scope }`

3. **Authentication Status**
   - `GET /api/auth/device/status/{device_code}`
   - Response: `{ status, authorized_domains }`

4. **Domain Authorization**
   - `POST /api/auth/device/authorize-domain`
   - Request: `{ device_code, domain, scope }`
   - Response: `{ status, message }`

### 4.3 Token Storage

Tokens will be securely stored in:

1. **Primary Storage**: `~/.codex/auth/tokens.json` (encrypted)
2. **Secondary (Fallback) Storage**: OS-specific secure storage
   - macOS: Keychain
   - Windows: Credential Manager
   - Linux: SecretService API or encrypted file

### 4.4 Security Considerations

1. **Token Encryption**: AES-256 with device-specific key
2. **Token Expiration**: Default 7-day expiration with refresh
3. **Scope Limitation**: Tokens limited to specific domains and operations
4. **Device Verification**: Device fingerprinting to detect suspicious logins
5. **Revocation**: Ability to revoke access from web interface

## 5. Integration with Existing HMS-API

Based on the existing HMS-API routes (api.php), we'll integrate with:

1. **Authentication Routes**:
   - Login Controller (Line 55, 137): `LoginController@login`, `LoginController@adminLogin`
   - Registration Controller (Line 136): `RegisterController@register`
   - Social Login Controller (Lines 127-131): For social authentication

2. **User Management Routes**:
   - User Data (Line 176): `UsersController@getUserData`
   - Authentication at Tenant (Line 192): `UsersController@authenticateAtTenant`

3. **Domain Authorization Routes**:
   - Tenant Interface (Line 171): `TenantInterfaceController@all`
   - Agency-Specific APIs (Lines 280-291): Agent communication

## 6. CLI Implementation Details

### 6.1 New Auth Commands

```bash
# Initialize authentication
ai-agency auth login [--domain=domain.ai]

# Check authentication status
ai-agency auth status

# Logout/revoke token
ai-agency auth logout

# List authorized domains
ai-agency auth domains

# Request access to a specific domain
ai-agency auth request-domain domain.ai
```

### 6.2 Auth Configuration File

```json
{
  "auth": {
    "device_id": "unique-device-identifier",
    "tokens": {
      "access_token": "encrypted-access-token",
      "refresh_token": "encrypted-refresh-token",
      "expires_at": "2025-05-30T12:00:00Z"
    },
    "authorized_domains": [
      {
        "domain": "cber.ai",
        "scopes": ["read", "write", "admin"],
        "expires_at": "2025-05-30T12:00:00Z"
      },
      {
        "domain": "nhtsa.ai",
        "scopes": ["read"],
        "expires_at": "2025-05-30T12:00:00Z"
      }
    ],
    "last_used": "2025-05-10T12:00:00Z"
  }
}
```

## 7. Web Interface Implementation

### 7.1 Authentication Pages

1. **Device Code Entry Page**
   - URL: `/auth/device`
   - Features:
     - Code entry field
     - Explanation of the process
     - "Next" button

2. **Login Page**
   - URL: `/auth/device/login`
   - Features:
     - Username/password fields
     - Social login options
     - Remember device option

3. **Domain Authorization Page**
   - URL: `/auth/device/domains`
   - Features:
     - List of available domains
     - Permission scopes per domain
     - Authorization confirmation

4. **Success Page**
   - URL: `/auth/device/success`
   - Features:
     - Success confirmation
     - Instructions to return to CLI
     - Additional setup options

### 7.2 User Management Pages

1. **Authorized Devices**
   - URL: `/user/devices`
   - Features:
     - List of authorized devices
     - Last used timestamp
     - Revocation option

2. **Domain Permissions**
   - URL: `/user/domains`
   - Features:
     - List of authorized domains per device
     - Permission management
     - Add/remove domain access

## 8. Implementation Timeline

### Week 1: Core Authentication Framework
- Day 1-2: Design and implement API endpoints
- Day 3-4: Create CLI authentication module
- Day 5: Build basic web authentication interface

### Week 2: Domain-Specific Authorization
- Day 1-2: Implement domain authorization logic
- Day 3-4: Enhance CLI with domain authorization
- Day 5: Extend web interface for domain selection

### Week 3: Advanced Features and Security
- Day 1-2: Implement token refresh and security
- Day 3-4: Add user management features
- Day 5: Testing and refinement

## 9. Testing Plan

1. **Unit Tests**
   - Test token generation and validation
   - Test encryption/decryption of tokens
   - Test device code validation

2. **Integration Tests**
   - Test end-to-end authentication flow
   - Test token refresh process
   - Test domain authorization logic

3. **Security Tests**
   - Test token storage security
   - Test against common attack vectors
   - Test rate limiting and suspicious activity detection

4. **User Acceptance Tests**
   - Test CLI login experience
   - Test web interface usability
   - Test error handling and recovery

## 10. Implementation Steps

1. Create authentication endpoints in HMS-API
2. Build web authentication interface
3. Implement CLI authentication module
4. Add domain-specific authorization
5. Implement token storage and management
6. Add advanced security features
7. Create user management interface
8. Test and refine the implementation
9. Document the authentication system
10. Deploy and monitor usage