/**
 * AI Agency CLI Authentication API
 * 
 * This module provides a mock API for authentication to allow testing
 * the authentication flow without a real backend.
 */
const http = require('http');
const url = require('url');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  PORT: process.env.AUTH_API_PORT || 3000,
  DATA_DIR: path.join(__dirname, 'api_data'),
  DEVICE_CODE_EXPIRY: 600, // 10 minutes
  CORS_ALLOWED_ORIGINS: [
    'http://localhost:8000', 
    'http://localhost:3000',
    'http://127.0.0.1:8000',
    'http://127.0.0.1:3000'
  ]
};

// Ensure data directory exists
if (!fs.existsSync(CONFIG.DATA_DIR)) {
  fs.mkdirSync(CONFIG.DATA_DIR, { recursive: true });
}

// Storage for active device codes and tokens
const STORAGE = {
  device_codes: path.join(CONFIG.DATA_DIR, 'device_codes.json'),
  tokens: path.join(CONFIG.DATA_DIR, 'tokens.json'),
  users: path.join(CONFIG.DATA_DIR, 'users.json'),
  domains: path.join(CONFIG.DATA_DIR, 'domains.json')
};

// Initialize storage files if they don't exist
for (const storageFile of Object.values(STORAGE)) {
  if (!fs.existsSync(storageFile)) {
    fs.writeFileSync(storageFile, JSON.stringify({}));
  }
}

// Sample domain data
const initialDomains = {
  "cber.ai": {
    "name": "Center for Biologics Evaluation and Research",
    "category": "healthcare",
    "description": "AI-driven biologics evaluation and research",
    "icon": "🧬",
    "available_scopes": ["read", "write", "admin"]
  },
  "cder.ai": {
    "name": "Center for Drug Evaluation and Research",
    "category": "healthcare",
    "description": "AI-powered drug evaluation and research",
    "icon": "💊",
    "available_scopes": ["read", "write", "admin"]
  },
  "nhtsa.ai": {
    "name": "National Highway Traffic Safety Administration",
    "category": "safety",
    "description": "AI-enhanced vehicle safety analysis",
    "icon": "🚗",
    "available_scopes": ["read", "write", "admin"]
  },
  "hsin.ai": {
    "name": "Homeland Security Information Network",
    "category": "security",
    "description": "AI-powered homeland security information analysis",
    "icon": "🔒",
    "available_scopes": ["read", "write", "admin"]
  },
  "doed.ai": {
    "name": "Department of Education",
    "category": "education",
    "description": "AI-supported educational policy planning",
    "icon": "🎓",
    "available_scopes": ["read", "write", "admin"]
  },
  "csfc.ai": {
    "name": "Cybersecurity & Financial Crimes",
    "category": "security",
    "description": "AI-assisted cybersecurity and financial crime prevention",
    "icon": "🛡️",
    "available_scopes": ["read", "write", "admin"]
  }
};

// Initialize domains data if empty
try {
  const domainsData = JSON.parse(fs.readFileSync(STORAGE.domains, 'utf8'));
  if (Object.keys(domainsData).length === 0) {
    fs.writeFileSync(STORAGE.domains, JSON.stringify(initialDomains, null, 2));
  }
} catch (error) {
  console.error('Error initializing domains data:', error);
  fs.writeFileSync(STORAGE.domains, JSON.stringify(initialDomains, null, 2));
}

// Sample user data
const initialUsers = {
  "admin@example.com": {
    "id": "usr_12345",
    "email": "admin@example.com",
    "password": "adminpass",  // In a real system, this would be hashed
    "name": "Admin User",
    "roles": ["admin"],
    "devices": [],
    "domain_access": {
      "cber.ai": ["read", "write", "admin"],
      "cder.ai": ["read", "write", "admin"],
      "nhtsa.ai": ["read", "write", "admin"],
      "hsin.ai": ["read", "write", "admin"],
      "doed.ai": ["read", "write", "admin"],
      "csfc.ai": ["read", "write", "admin"]
    }
  },
  "user@example.com": {
    "id": "usr_67890",
    "email": "user@example.com",
    "password": "userpass",  // In a real system, this would be hashed
    "name": "Regular User",
    "roles": ["user"],
    "devices": [],
    "domain_access": {
      "cber.ai": ["read"],
      "cder.ai": ["read"],
      "nhtsa.ai": ["read"],
      "hsin.ai": ["read"],
      "doed.ai": ["read"]
    }
  }
};

// Initialize users data if empty
try {
  const usersData = JSON.parse(fs.readFileSync(STORAGE.users, 'utf8'));
  if (Object.keys(usersData).length === 0) {
    fs.writeFileSync(STORAGE.users, JSON.stringify(initialUsers, null, 2));
  }
} catch (error) {
  console.error('Error initializing users data:', error);
  fs.writeFileSync(STORAGE.users, JSON.stringify(initialUsers, null, 2));
}

// Utility functions
const utils = {
  /**
   * Generate a random code
   * @param {number} length - Length of the code
   * @returns {string} - Random code
   */
  generateRandomCode: (length = 8) => {
    return crypto.randomBytes(length)
      .toString('base64')
      .replace(/\+/g, '')
      .replace(/\//g, '')
      .replace(/=/g, '')
      .slice(0, length);
  },
  
  /**
   * Generate a JWT token
   * @param {Object} payload - Token payload
   * @param {string} secret - Secret key
   * @param {number} expiresIn - Expiration time in seconds
   * @returns {string} - JWT token
   */
  generateJWT: (payload, secret = 'mock-jwt-secret', expiresIn = 3600) => {
    const header = {
      alg: 'HS256',
      typ: 'JWT'
    };
    
    const now = Math.floor(Date.now() / 1000);
    const tokenPayload = {
      ...payload,
      iat: now,
      exp: now + expiresIn
    };
    
    const headerBase64 = Buffer.from(JSON.stringify(header)).toString('base64');
    const payloadBase64 = Buffer.from(JSON.stringify(tokenPayload)).toString('base64');
    
    const signature = crypto
      .createHmac('sha256', secret)
      .update(`${headerBase64}.${payloadBase64}`)
      .digest('base64');
    
    return `${headerBase64}.${payloadBase64}.${signature}`;
  },
  
  /**
   * Send JSON response
   * @param {http.ServerResponse} res - Response object
   * @param {number} statusCode - HTTP status code
   * @param {Object} data - Response data
   */
  sendJSONResponse: (res, statusCode, data) => {
    res.writeHead(statusCode, { 
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': CONFIG.CORS_ALLOWED_ORIGINS.includes(res.req.headers.origin) 
        ? res.req.headers.origin 
        : CONFIG.CORS_ALLOWED_ORIGINS[0],
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400'
    });
    res.end(JSON.stringify(data));
  },
  
  /**
   * Parse request body as JSON
   * @param {http.IncomingMessage} req - Request object
   * @returns {Promise<Object>} - Parsed body
   */
  parseJSONBody: (req) => {
    return new Promise((resolve, reject) => {
      let body = '';
      
      req.on('data', chunk => {
        body += chunk.toString();
      });
      
      req.on('end', () => {
        try {
          const data = body ? JSON.parse(body) : {};
          resolve(data);
        } catch (error) {
          reject(error);
        }
      });
      
      req.on('error', err => {
        reject(err);
      });
    });
  },
  
  /**
   * Verify JWT token
   * @param {string} token - JWT token
   * @param {string} secret - Secret key
   * @returns {Object|null} - Token payload or null if invalid
   */
  verifyJWT: (token, secret = 'mock-jwt-secret') => {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;
      
      const [headerBase64, payloadBase64, signature] = parts;
      
      // Verify signature
      const expectedSignature = crypto
        .createHmac('sha256', secret)
        .update(`${headerBase64}.${payloadBase64}`)
        .digest('base64');
      
      if (signature !== expectedSignature) return null;
      
      // Decode payload
      const payload = JSON.parse(Buffer.from(payloadBase64, 'base64').toString());
      
      // Check expiration
      if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) return null;
      
      return payload;
    } catch (error) {
      console.error('JWT verification error:', error);
      return null;
    }
  },
  
  /**
   * Extract authorization token from request
   * @param {http.IncomingMessage} req - Request object
   * @returns {string|null} - Token or null if not found
   */
  extractToken: (req) => {
    const authHeader = req.headers.authorization;
    if (!authHeader) return null;
    
    const parts = authHeader.split(' ');
    if (parts.length !== 2 || parts[0] !== 'Bearer') return null;
    
    return parts[1];
  }
};

// API endpoints
const endpoints = {
  /**
   * Device authorization endpoint
   * @param {http.IncomingMessage} req - Request object
   * @param {http.ServerResponse} res - Response object
   */
  deviceAuthorize: async (req, res) => {
    try {
      const body = await utils.parseJSONBody(req);
      
      if (!body.client_id) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_request',
          error_description: 'Missing client_id parameter'
        });
      }
      
      // Generate device and user codes
      const deviceCode = utils.generateRandomCode(40);
      const userCode = utils.generateRandomCode(8).toUpperCase().match(/.{1,4}/g).join('-');
      
      // Store device code data
      const deviceCodesData = JSON.parse(fs.readFileSync(STORAGE.device_codes, 'utf8'));
      
      deviceCodesData[deviceCode] = {
        device_code: deviceCode,
        user_code: userCode,
        client_id: body.client_id,
        scope: body.scope || 'read',
        status: 'pending',
        created_at: Date.now(),
        expires_at: Date.now() + (CONFIG.DEVICE_CODE_EXPIRY * 1000)
      };
      
      fs.writeFileSync(STORAGE.device_codes, JSON.stringify(deviceCodesData, null, 2));
      
      // Send response
      utils.sendJSONResponse(res, 200, {
        device_code: deviceCode,
        user_code: userCode,
        verification_uri: 'http://localhost:8000',
        verification_uri_complete: `http://localhost:8000?code=${userCode}`,
        expires_in: CONFIG.DEVICE_CODE_EXPIRY,
        interval: 5
      });
    } catch (error) {
      console.error('Device authorize error:', error);
      utils.sendJSONResponse(res, 500, { 
        error: 'server_error',
        error_description: 'Internal server error'
      });
    }
  },
  
  /**
   * Device token endpoint
   * @param {http.IncomingMessage} req - Request object
   * @param {http.ServerResponse} res - Response object
   */
  deviceToken: async (req, res) => {
    try {
      const body = await utils.parseJSONBody(req);
      
      if (!body.device_code || !body.client_id) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_request',
          error_description: 'Missing required parameters'
        });
      }
      
      // Check device code
      const deviceCodesData = JSON.parse(fs.readFileSync(STORAGE.device_codes, 'utf8'));
      const deviceCodeData = deviceCodesData[body.device_code];
      
      if (!deviceCodeData) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_grant',
          error_description: 'Invalid device code'
        });
      }
      
      if (deviceCodeData.client_id !== body.client_id) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_grant',
          error_description: 'Client ID does not match'
        });
      }
      
      if (deviceCodeData.expires_at < Date.now()) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'expired_token',
          error_description: 'Device code has expired'
        });
      }
      
      if (deviceCodeData.status === 'pending') {
        return utils.sendJSONResponse(res, 400, { 
          error: 'authorization_pending',
          error_description: 'Authorization is pending'
        });
      }
      
      if (deviceCodeData.status === 'denied') {
        return utils.sendJSONResponse(res, 400, { 
          error: 'access_denied',
          error_description: 'User denied the authorization request'
        });
      }
      
      // Generate tokens
      const accessToken = utils.generateJWT({
        sub: deviceCodeData.user_id,
        client_id: body.client_id,
        scope: deviceCodeData.authorized_scopes || deviceCodeData.scope,
        domain_access: deviceCodeData.domain_access || {}
      }, 'mock-jwt-secret', 3600); // 1 hour
      
      const refreshToken = utils.generateRandomCode(40);
      
      // Store token data
      const tokensData = JSON.parse(fs.readFileSync(STORAGE.tokens, 'utf8'));
      
      tokensData[accessToken] = {
        access_token: accessToken,
        refresh_token: refreshToken,
        user_id: deviceCodeData.user_id,
        client_id: body.client_id,
        scope: deviceCodeData.authorized_scopes || deviceCodeData.scope,
        domain_access: deviceCodeData.domain_access || {},
        created_at: Date.now(),
        expires_at: Date.now() + (3600 * 1000) // 1 hour
      };
      
      fs.writeFileSync(STORAGE.tokens, JSON.stringify(tokensData, null, 2));
      
      // Update user's devices
      if (deviceCodeData.user_id) {
        const usersData = JSON.parse(fs.readFileSync(STORAGE.users, 'utf8'));
        const user = Object.values(usersData).find(u => u.id === deviceCodeData.user_id);
        
        if (user) {
          if (!user.devices) user.devices = [];
          
          user.devices.push({
            client_id: body.client_id,
            device_code: body.device_code,
            name: 'AI Agency CLI',
            last_used: Date.now()
          });
          
          fs.writeFileSync(STORAGE.users, JSON.stringify(usersData, null, 2));
        }
      }
      
      // Remove device code
      delete deviceCodesData[body.device_code];
      fs.writeFileSync(STORAGE.device_codes, JSON.stringify(deviceCodesData, null, 2));
      
      // Send response
      utils.sendJSONResponse(res, 200, {
        access_token: accessToken,
        token_type: 'Bearer',
        expires_in: 3600,
        refresh_token: refreshToken,
        scope: deviceCodeData.authorized_scopes || deviceCodeData.scope
      });
    } catch (error) {
      console.error('Device token error:', error);
      utils.sendJSONResponse(res, 500, { 
        error: 'server_error',
        error_description: 'Internal server error'
      });
    }
  },
  
  /**
   * Device token refresh endpoint
   * @param {http.IncomingMessage} req - Request object
   * @param {http.ServerResponse} res - Response object
   */
  refreshToken: async (req, res) => {
    try {
      const body = await utils.parseJSONBody(req);
      
      if (!body.refresh_token || !body.client_id) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_request',
          error_description: 'Missing required parameters'
        });
      }
      
      // Check refresh token
      const tokensData = JSON.parse(fs.readFileSync(STORAGE.tokens, 'utf8'));
      const tokenEntry = Object.values(tokensData).find(t => t.refresh_token === body.refresh_token);
      
      if (!tokenEntry) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_grant',
          error_description: 'Invalid refresh token'
        });
      }
      
      if (tokenEntry.client_id !== body.client_id) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_grant',
          error_description: 'Client ID does not match'
        });
      }
      
      // Generate new tokens
      const accessToken = utils.generateJWT({
        sub: tokenEntry.user_id,
        client_id: body.client_id,
        scope: tokenEntry.scope,
        domain_access: tokenEntry.domain_access
      }, 'mock-jwt-secret', 3600); // 1 hour
      
      const refreshToken = utils.generateRandomCode(40);
      
      // Store new token data
      delete tokensData[tokenEntry.access_token];
      
      tokensData[accessToken] = {
        access_token: accessToken,
        refresh_token: refreshToken,
        user_id: tokenEntry.user_id,
        client_id: body.client_id,
        scope: tokenEntry.scope,
        domain_access: tokenEntry.domain_access,
        created_at: Date.now(),
        expires_at: Date.now() + (3600 * 1000) // 1 hour
      };
      
      fs.writeFileSync(STORAGE.tokens, JSON.stringify(tokensData, null, 2));
      
      // Send response
      utils.sendJSONResponse(res, 200, {
        access_token: accessToken,
        token_type: 'Bearer',
        expires_in: 3600,
        refresh_token: refreshToken,
        scope: tokenEntry.scope
      });
    } catch (error) {
      console.error('Refresh token error:', error);
      utils.sendJSONResponse(res, 500, { 
        error: 'server_error',
        error_description: 'Internal server error'
      });
    }
  },
  
  /**
   * Verify device code endpoint
   * @param {http.IncomingMessage} req - Request object
   * @param {http.ServerResponse} res - Response object
   */
  verifyDeviceCode: async (req, res) => {
    try {
      const reqUrl = url.parse(req.url, true);
      const userCode = reqUrl.query.code;
      
      if (!userCode) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_request',
          error_description: 'Missing code parameter'
        });
      }
      
      // Check device code
      const deviceCodesData = JSON.parse(fs.readFileSync(STORAGE.device_codes, 'utf8'));
      const deviceCodeEntry = Object.values(deviceCodesData).find(d => d.user_code === userCode);
      
      if (!deviceCodeEntry) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_code',
          error_description: 'Invalid device code'
        });
      }
      
      if (deviceCodeEntry.expires_at < Date.now()) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'expired_code',
          error_description: 'Device code has expired'
        });
      }
      
      // Send response
      utils.sendJSONResponse(res, 200, {
        valid: true,
        client_id: deviceCodeEntry.client_id,
        device_code: deviceCodeEntry.device_code,
        scope: deviceCodeEntry.scope
      });
    } catch (error) {
      console.error('Verify device code error:', error);
      utils.sendJSONResponse(res, 500, { 
        error: 'server_error',
        error_description: 'Internal server error'
      });
    }
  },
  
  /**
   * Authorize device endpoint
   * @param {http.IncomingMessage} req - Request object
   * @param {http.ServerResponse} res - Response object
   */
  authorizeDevice: async (req, res) => {
    try {
      const body = await utils.parseJSONBody(req);
      
      if (!body.device_code || !body.user_id || !body.authorized_scopes) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_request',
          error_description: 'Missing required parameters'
        });
      }
      
      // Check device code
      const deviceCodesData = JSON.parse(fs.readFileSync(STORAGE.device_codes, 'utf8'));
      
      if (!deviceCodesData[body.device_code]) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_code',
          error_description: 'Invalid device code'
        });
      }
      
      // Update device code status
      deviceCodesData[body.device_code].status = 'authorized';
      deviceCodesData[body.device_code].user_id = body.user_id;
      deviceCodesData[body.device_code].authorized_scopes = body.authorized_scopes;
      deviceCodesData[body.device_code].domain_access = body.domain_access || {};
      
      fs.writeFileSync(STORAGE.device_codes, JSON.stringify(deviceCodesData, null, 2));
      
      // Send response
      utils.sendJSONResponse(res, 200, {
        success: true,
        device_code: body.device_code
      });
    } catch (error) {
      console.error('Authorize device error:', error);
      utils.sendJSONResponse(res, 500, { 
        error: 'server_error',
        error_description: 'Internal server error'
      });
    }
  },
  
  /**
   * Deny device endpoint
   * @param {http.IncomingMessage} req - Request object
   * @param {http.ServerResponse} res - Response object
   */
  denyDevice: async (req, res) => {
    try {
      const body = await utils.parseJSONBody(req);
      
      if (!body.device_code) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_request',
          error_description: 'Missing device_code parameter'
        });
      }
      
      // Check device code
      const deviceCodesData = JSON.parse(fs.readFileSync(STORAGE.device_codes, 'utf8'));
      
      if (!deviceCodesData[body.device_code]) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_code',
          error_description: 'Invalid device code'
        });
      }
      
      // Update device code status
      deviceCodesData[body.device_code].status = 'denied';
      
      fs.writeFileSync(STORAGE.device_codes, JSON.stringify(deviceCodesData, null, 2));
      
      // Send response
      utils.sendJSONResponse(res, 200, {
        success: true,
        device_code: body.device_code
      });
    } catch (error) {
      console.error('Deny device error:', error);
      utils.sendJSONResponse(res, 500, { 
        error: 'server_error',
        error_description: 'Internal server error'
      });
    }
  },
  
  /**
   * Revoke token endpoint
   * @param {http.IncomingMessage} req - Request object
   * @param {http.ServerResponse} res - Response object
   */
  revokeToken: async (req, res) => {
    try {
      const body = await utils.parseJSONBody(req);
      
      if (!body.token || !body.client_id) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_request',
          error_description: 'Missing required parameters'
        });
      }
      
      // Check token
      const tokensData = JSON.parse(fs.readFileSync(STORAGE.tokens, 'utf8'));
      
      // Remove token if it exists
      if (tokensData[body.token]) {
        delete tokensData[body.token];
        fs.writeFileSync(STORAGE.tokens, JSON.stringify(tokensData, null, 2));
      }
      
      // Send response
      utils.sendJSONResponse(res, 200, {
        success: true
      });
    } catch (error) {
      console.error('Revoke token error:', error);
      utils.sendJSONResponse(res, 500, { 
        error: 'server_error',
        error_description: 'Internal server error'
      });
    }
  },
  
  /**
   * User login endpoint
   * @param {http.IncomingMessage} req - Request object
   * @param {http.ServerResponse} res - Response object
   */
  login: async (req, res) => {
    try {
      const body = await utils.parseJSONBody(req);
      
      if (!body.email || !body.password) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_request',
          error_description: 'Missing email or password'
        });
      }
      
      // Check user credentials
      const usersData = JSON.parse(fs.readFileSync(STORAGE.users, 'utf8'));
      const user = usersData[body.email];
      
      if (!user || user.password !== body.password) {
        return utils.sendJSONResponse(res, 401, { 
          error: 'invalid_credentials',
          error_description: 'Invalid email or password'
        });
      }
      
      // Send response
      utils.sendJSONResponse(res, 200, {
        success: true,
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          roles: user.roles,
          domain_access: user.domain_access
        }
      });
    } catch (error) {
      console.error('Login error:', error);
      utils.sendJSONResponse(res, 500, { 
        error: 'server_error',
        error_description: 'Internal server error'
      });
    }
  },
  
  /**
   * Get domains endpoint
   * @param {http.IncomingMessage} req - Request object
   * @param {http.ServerResponse} res - Response object
   */
  getDomains: async (req, res) => {
    try {
      // Check authorization
      const token = utils.extractToken(req);
      
      if (!token) {
        return utils.sendJSONResponse(res, 401, { 
          error: 'unauthorized',
          error_description: 'Authentication required'
        });
      }
      
      const payload = utils.verifyJWT(token);
      
      if (!payload) {
        return utils.sendJSONResponse(res, 401, { 
          error: 'invalid_token',
          error_description: 'Invalid or expired token'
        });
      }
      
      // Get domains
      const domainsData = JSON.parse(fs.readFileSync(STORAGE.domains, 'utf8'));
      
      // Get user's domain access
      const usersData = JSON.parse(fs.readFileSync(STORAGE.users, 'utf8'));
      const user = Object.values(usersData).find(u => u.id === payload.sub);
      
      // Add user's access level to each domain
      const domainsWithAccess = {};
      
      Object.entries(domainsData).forEach(([domain, data]) => {
        domainsWithAccess[domain] = {
          ...data,
          access: user && user.domain_access && user.domain_access[domain] 
            ? user.domain_access[domain] 
            : []
        };
      });
      
      // Send response
      utils.sendJSONResponse(res, 200, domainsWithAccess);
    } catch (error) {
      console.error('Get domains error:', error);
      utils.sendJSONResponse(res, 500, { 
        error: 'server_error',
        error_description: 'Internal server error'
      });
    }
  },
  
  /**
   * Authorize domain endpoint
   * @param {http.IncomingMessage} req - Request object
   * @param {http.ServerResponse} res - Response object
   */
  authorizeDomain: async (req, res) => {
    try {
      const body = await utils.parseJSONBody(req);
      
      if (!body.domain || !body.scope) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_request',
          error_description: 'Missing domain or scope parameter'
        });
      }
      
      // Check authorization
      const token = utils.extractToken(req);
      
      if (!token) {
        return utils.sendJSONResponse(res, 401, { 
          error: 'unauthorized',
          error_description: 'Authentication required'
        });
      }
      
      const payload = utils.verifyJWT(token);
      
      if (!payload) {
        return utils.sendJSONResponse(res, 401, { 
          error: 'invalid_token',
          error_description: 'Invalid or expired token'
        });
      }
      
      // Check if domain exists
      const domainsData = JSON.parse(fs.readFileSync(STORAGE.domains, 'utf8'));
      
      if (!domainsData[body.domain]) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_domain',
          error_description: 'Domain not found'
        });
      }
      
      // Check if user has access to the domain
      const usersData = JSON.parse(fs.readFileSync(STORAGE.users, 'utf8'));
      const user = Object.values(usersData).find(u => u.id === payload.sub);
      
      if (!user) {
        return utils.sendJSONResponse(res, 401, { 
          error: 'invalid_user',
          error_description: 'User not found'
        });
      }
      
      if (!user.domain_access[body.domain]) {
        return utils.sendJSONResponse(res, 403, { 
          error: 'access_denied',
          error_description: 'User does not have access to the domain'
        });
      }
      
      // Check if user has the requested scope
      const requestedScopes = Array.isArray(body.scope) ? body.scope : body.scope.split(' ');
      const userScopes = user.domain_access[body.domain];
      
      for (const scope of requestedScopes) {
        if (!userScopes.includes(scope)) {
          return utils.sendJSONResponse(res, 403, { 
            error: 'invalid_scope',
            error_description: `User does not have '${scope}' scope for the domain`
          });
        }
      }
      
      // Update token with domain access
      const tokensData = JSON.parse(fs.readFileSync(STORAGE.tokens, 'utf8'));
      
      if (tokensData[token]) {
        if (!tokensData[token].domain_access) {
          tokensData[token].domain_access = {};
        }
        
        tokensData[token].domain_access[body.domain] = requestedScopes;
        
        fs.writeFileSync(STORAGE.tokens, JSON.stringify(tokensData, null, 2));
      }
      
      // Send response
      utils.sendJSONResponse(res, 200, {
        success: true,
        domain: body.domain,
        scopes: requestedScopes
      });
    } catch (error) {
      console.error('Authorize domain error:', error);
      utils.sendJSONResponse(res, 500, { 
        error: 'server_error',
        error_description: 'Internal server error'
      });
    }
  },
  
  /**
   * Domain status endpoint
   * @param {http.IncomingMessage} req - Request object
   * @param {http.ServerResponse} res - Response object
   */
  domainStatus: async (req, res) => {
    try {
      const reqUrl = url.parse(req.url, true);
      const domain = reqUrl.query.domain;
      
      if (!domain) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_request',
          error_description: 'Missing domain parameter'
        });
      }
      
      // Check authorization
      const token = utils.extractToken(req);
      
      if (!token) {
        return utils.sendJSONResponse(res, 401, { 
          error: 'unauthorized',
          error_description: 'Authentication required'
        });
      }
      
      const payload = utils.verifyJWT(token);
      
      if (!payload) {
        return utils.sendJSONResponse(res, 401, { 
          error: 'invalid_token',
          error_description: 'Invalid or expired token'
        });
      }
      
      // Check if domain exists
      const domainsData = JSON.parse(fs.readFileSync(STORAGE.domains, 'utf8'));
      
      if (!domainsData[domain]) {
        return utils.sendJSONResponse(res, 400, { 
          error: 'invalid_domain',
          error_description: 'Domain not found'
        });
      }
      
      // Check if token has access to the domain
      const authorized = payload.domain_access && payload.domain_access[domain];
      
      // Send response
      utils.sendJSONResponse(res, 200, {
        domain,
        authorized: !!authorized,
        scopes: authorized || []
      });
    } catch (error) {
      console.error('Domain status error:', error);
      utils.sendJSONResponse(res, 500, { 
        error: 'server_error',
        error_description: 'Internal server error'
      });
    }
  }
};

// Create HTTP server
const server = http.createServer((req, res) => {
  // Handle preflight CORS requests
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': CONFIG.CORS_ALLOWED_ORIGINS.includes(req.headers.origin) 
        ? req.headers.origin 
        : CONFIG.CORS_ALLOWED_ORIGINS[0],
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400'
    });
    return res.end();
  }
  
  // Parse URL
  const reqUrl = url.parse(req.url, true);
  const path = reqUrl.pathname;
  
  // Route requests to endpoints
  try {
    if (path === '/api/auth/device/authorize' && req.method === 'POST') {
      return endpoints.deviceAuthorize(req, res);
    } else if (path === '/api/auth/device/token' && req.method === 'POST') {
      return endpoints.deviceToken(req, res);
    } else if (path === '/api/auth/device/refresh' && req.method === 'POST') {
      return endpoints.refreshToken(req, res);
    } else if (path === '/api/auth/device/verify' && req.method === 'GET') {
      return endpoints.verifyDeviceCode(req, res);
    } else if (path === '/api/auth/device/authorize-device' && req.method === 'POST') {
      return endpoints.authorizeDevice(req, res);
    } else if (path === '/api/auth/device/deny-device' && req.method === 'POST') {
      return endpoints.denyDevice(req, res);
    } else if (path === '/api/auth/device/revoke' && req.method === 'POST') {
      return endpoints.revokeToken(req, res);
    } else if (path === '/api/auth/login' && req.method === 'POST') {
      return endpoints.login(req, res);
    } else if (path === '/api/domains' && req.method === 'GET') {
      return endpoints.getDomains(req, res);
    } else if (path === '/api/auth/device/authorize-domain' && req.method === 'POST') {
      return endpoints.authorizeDomain(req, res);
    } else if (path === '/api/auth/device/domain-status' && req.method === 'GET') {
      return endpoints.domainStatus(req, res);
    } else {
      // Endpoint not found
      utils.sendJSONResponse(res, 404, { 
        error: 'not_found',
        error_description: 'Endpoint not found'
      });
    }
  } catch (error) {
    console.error('Server error:', error);
    utils.sendJSONResponse(res, 500, { 
      error: 'server_error',
      error_description: 'Internal server error'
    });
  }
});

// Start server
server.listen(CONFIG.PORT, () => {
  console.log(`Mock API server running at http://localhost:${CONFIG.PORT}/`);
  console.log(`Available users:`);
  console.log(`  - admin@example.com / adminpass (full access)`);
  console.log(`  - user@example.com / userpass (read-only access)`);
});

module.exports = server;