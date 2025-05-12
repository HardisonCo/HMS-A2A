/**
 * AI Agency CLI Authentication Module
 * 
 * This module handles CLI-based web authentication similar to GitHub's approach,
 * allowing users to authenticate with HMS-API and access domain-specific resources.
 */
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const os = require('os');
const axios = require('axios');
const open = require('open');

// Configuration
const CONFIG = {
  AUTH_API_URL: process.env.AUTH_API_URL || 'https://api.hms.ai',
  CLIENT_ID: process.env.CLIENT_ID || 'agency-cli',
  AUTH_CONFIG_DIR: path.join(os.homedir(), '.codex', 'auth'),
  AUTH_CONFIG_FILE: path.join(os.homedir(), '.codex', 'auth', 'tokens.json'),
  DEVICE_ID_FILE: path.join(os.homedir(), '.codex', 'auth', 'device_id'),
  POLLING_INTERVAL: 5000, // 5 seconds
  MAX_POLLING_TIME: 300000, // 5 minutes
};

// Ensure auth directory exists
if (!fs.existsSync(CONFIG.AUTH_CONFIG_DIR)) {
  fs.mkdirSync(CONFIG.AUTH_CONFIG_DIR, { recursive: true });
}

// Encryption utilities
const encryption = {
  /**
   * Generate a device ID or retrieve the existing one
   * @returns {string} The device ID
   */
  getDeviceId: () => {
    if (fs.existsSync(CONFIG.DEVICE_ID_FILE)) {
      return fs.readFileSync(CONFIG.DEVICE_ID_FILE, 'utf8');
    }
    
    // Generate new device ID
    const deviceId = crypto.randomBytes(16).toString('hex');
    fs.writeFileSync(CONFIG.DEVICE_ID_FILE, deviceId);
    return deviceId;
  },
  
  /**
   * Encrypt data with device-specific key
   * @param {string} data - Data to encrypt
   * @returns {string} Encrypted data
   */
  encrypt: (data) => {
    const deviceId = encryption.getDeviceId();
    const key = crypto.createHash('sha256').update(deviceId).digest('base64').substr(0, 32);
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
    
    let encrypted = cipher.update(data, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    return iv.toString('hex') + ':' + encrypted;
  },
  
  /**
   * Decrypt data with device-specific key
   * @param {string} encryptedData - Data to decrypt
   * @returns {string} Decrypted data
   */
  decrypt: (encryptedData) => {
    try {
      const deviceId = encryption.getDeviceId();
      const key = crypto.createHash('sha256').update(deviceId).digest('base64').substr(0, 32);
      
      const parts = encryptedData.split(':');
      const iv = Buffer.from(parts[0], 'hex');
      const encryptedText = parts[1];
      
      const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
      let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      return decrypted;
    } catch (error) {
      console.error('Decryption error:', error.message);
      return null;
    }
  }
};

// Token management
const tokenManager = {
  /**
   * Save authentication data to config file
   * @param {Object} authData - Authentication data to save
   */
  saveAuthData: (authData) => {
    if (!authData) return;
    
    // Encrypt sensitive data
    const encryptedData = {
      ...authData,
      tokens: {
        ...authData.tokens,
        access_token: encryption.encrypt(authData.tokens.access_token),
        refresh_token: encryption.encrypt(authData.tokens.refresh_token)
      }
    };
    
    fs.writeFileSync(
      CONFIG.AUTH_CONFIG_FILE, 
      JSON.stringify(encryptedData, null, 2)
    );
  },
  
  /**
   * Load authentication data from config file
   * @returns {Object|null} Authentication data or null if not found/invalid
   */
  loadAuthData: () => {
    try {
      if (!fs.existsSync(CONFIG.AUTH_CONFIG_FILE)) {
        return null;
      }
      
      const rawData = fs.readFileSync(CONFIG.AUTH_CONFIG_FILE, 'utf8');
      const encryptedData = JSON.parse(rawData);
      
      // Decrypt sensitive data
      return {
        ...encryptedData,
        tokens: {
          ...encryptedData.tokens,
          access_token: encryption.decrypt(encryptedData.tokens.access_token),
          refresh_token: encryption.decrypt(encryptedData.tokens.refresh_token)
        }
      };
    } catch (error) {
      console.error('Error loading auth data:', error.message);
      return null;
    }
  },
  
  /**
   * Check if there's a valid access token
   * @returns {boolean} True if valid token exists
   */
  hasValidToken: () => {
    const authData = tokenManager.loadAuthData();
    if (!authData || !authData.tokens || !authData.tokens.expires_at) {
      return false;
    }
    
    const expiresAt = new Date(authData.tokens.expires_at);
    return expiresAt > new Date();
  },
  
  /**
   * Get a valid access token, refreshing if necessary
   * @returns {Promise<string|null>} Valid access token or null
   */
  getValidToken: async () => {
    const authData = tokenManager.loadAuthData();
    if (!authData || !authData.tokens) {
      return null;
    }
    
    const expiresAt = new Date(authData.tokens.expires_at);
    
    // If token expired, try to refresh
    if (expiresAt <= new Date()) {
      return await tokenManager.refreshToken(authData.tokens.refresh_token);
    }
    
    return authData.tokens.access_token;
  },
  
  /**
   * Refresh the access token
   * @param {string} refreshToken - The refresh token
   * @returns {Promise<string|null>} New access token or null
   */
  refreshToken: async (refreshToken) => {
    try {
      const response = await axios.post(`${CONFIG.AUTH_API_URL}/api/auth/device/refresh`, {
        refresh_token: refreshToken,
        client_id: CONFIG.CLIENT_ID
      });
      
      if (response.data && response.data.access_token) {
        const authData = tokenManager.loadAuthData();
        const newAuthData = {
          ...authData,
          tokens: {
            access_token: response.data.access_token,
            refresh_token: response.data.refresh_token || refreshToken,
            expires_at: new Date(Date.now() + (response.data.expires_in * 1000)).toISOString(),
            token_type: response.data.token_type
          },
          last_used: new Date().toISOString()
        };
        
        tokenManager.saveAuthData(newAuthData);
        return response.data.access_token;
      }
      
      return null;
    } catch (error) {
      console.error('Token refresh error:', error.message);
      return null;
    }
  },
  
  /**
   * Check if user is authorized for a specific domain
   * @param {string} domain - The domain to check authorization for
   * @returns {boolean} True if authorized
   */
  isDomainAuthorized: (domain) => {
    const authData = tokenManager.loadAuthData();
    if (!authData || !authData.authorized_domains) {
      return false;
    }
    
    const domainAuth = authData.authorized_domains.find(d => d.domain === domain);
    if (!domainAuth) {
      return false;
    }
    
    const expiresAt = new Date(domainAuth.expires_at);
    return expiresAt > new Date();
  },
  
  /**
   * Get list of authorized domains
   * @returns {Array} List of authorized domains
   */
  getAuthorizedDomains: () => {
    const authData = tokenManager.loadAuthData();
    if (!authData || !authData.authorized_domains) {
      return [];
    }
    
    return authData.authorized_domains.filter(d => {
      const expiresAt = new Date(d.expires_at);
      return expiresAt > new Date();
    });
  },
  
  /**
   * Revoke authentication tokens
   * @returns {Promise<boolean>} True if revocation successful
   */
  revokeTokens: async () => {
    try {
      const authData = tokenManager.loadAuthData();
      if (!authData || !authData.tokens) {
        return true; // Nothing to revoke
      }
      
      // Attempt to revoke on server
      await axios.post(`${CONFIG.AUTH_API_URL}/api/auth/device/revoke`, {
        token: authData.tokens.access_token,
        client_id: CONFIG.CLIENT_ID
      });
      
      // Delete local auth data
      if (fs.existsSync(CONFIG.AUTH_CONFIG_FILE)) {
        fs.unlinkSync(CONFIG.AUTH_CONFIG_FILE);
      }
      
      return true;
    } catch (error) {
      console.error('Token revocation error:', error.message);
      
      // Delete local auth data even if server request fails
      if (fs.existsSync(CONFIG.AUTH_CONFIG_FILE)) {
        fs.unlinkSync(CONFIG.AUTH_CONFIG_FILE);
      }
      
      return false;
    }
  }
};

// Authentication API client
const authClient = {
  /**
   * Request a device code for authentication
   * @param {string} scope - The requested scope
   * @returns {Promise<Object>} Device code response
   */
  requestDeviceCode: async (scope = 'read') => {
    try {
      const response = await axios.post(`${CONFIG.AUTH_API_URL}/api/auth/device/authorize`, {
        client_id: CONFIG.CLIENT_ID,
        scope: scope
      });
      
      return response.data;
    } catch (error) {
      console.error('Device code request error:', error.message);
      throw new Error('Failed to request device code');
    }
  },
  
  /**
   * Poll for token until authorized or timeout
   * @param {string} deviceCode - The device code
   * @param {number} interval - Polling interval in seconds
   * @param {number} expiresIn - Expiration time in seconds
   * @returns {Promise<Object>} Token response
   */
  pollForToken: async (deviceCode, interval, expiresIn) => {
    const startTime = Date.now();
    const maxTime = Math.min(expiresIn * 1000, CONFIG.MAX_POLLING_TIME);
    const pollInterval = interval * 1000 || CONFIG.POLLING_INTERVAL;
    
    while (Date.now() - startTime < maxTime) {
      try {
        const response = await axios.post(`${CONFIG.AUTH_API_URL}/api/auth/device/token`, {
          device_code: deviceCode,
          client_id: CONFIG.CLIENT_ID
        });
        
        if (response.data && response.data.access_token) {
          return response.data;
        }
      } catch (error) {
        // If error is not "authorization pending", throw it
        if (!error.response || error.response.data.error !== 'authorization_pending') {
          throw error;
        }
      }
      
      // Wait for next polling interval
      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }
    
    throw new Error('Authentication timed out');
  },
  
  /**
   * Request authorization for a specific domain
   * @param {string} domain - The domain to authorize
   * @param {string} accessToken - The access token
   * @returns {Promise<Object>} Domain authorization response
   */
  requestDomainAuthorization: async (domain, accessToken) => {
    try {
      const response = await axios.post(
        `${CONFIG.AUTH_API_URL}/api/auth/device/authorize-domain`,
        { domain, scope: 'read write' },
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      
      return response.data;
    } catch (error) {
      console.error('Domain authorization error:', error.message);
      throw new Error(`Failed to authorize domain: ${domain}`);
    }
  }
};

// Authentication flow
const authFlow = {
  /**
   * Start the device authorization flow
   * @param {string} domain - Optional domain to request authorization for
   * @returns {Promise<Object>} Authentication result
   */
  startDeviceFlow: async (domain = null) => {
    try {
      // Request device code
      const deviceCodeResponse = await authClient.requestDeviceCode(domain ? `domain:${domain}` : 'read');
      
      console.log('\n🔐 Please authorize AI Agency CLI:');
      console.log(`\n💻 Visit: ${deviceCodeResponse.verification_uri}`);
      console.log(`📋 And enter code: ${deviceCodeResponse.user_code}\n`);
      
      // Try to open browser automatically
      try {
        await open(deviceCodeResponse.verification_uri);
        console.log('🌐 Browser opened automatically. Please enter the code shown above.');
      } catch (error) {
        console.log('⚠️  Please open the URL in your browser manually.');
      }
      
      console.log('\n⏳ Waiting for authorization...');
      
      // Poll for token
      const tokenResponse = await authClient.pollForToken(
        deviceCodeResponse.device_code,
        deviceCodeResponse.interval,
        deviceCodeResponse.expires_in
      );
      
      // Save authentication data
      const expiresAt = new Date(Date.now() + (tokenResponse.expires_in * 1000)).toISOString();
      let authorizedDomains = [];
      
      // If domain was requested, add it to authorized domains
      if (domain) {
        authorizedDomains.push({
          domain,
          scopes: ['read', 'write'],
          expires_at: expiresAt
        });
      }
      
      const authData = {
        device_id: encryption.getDeviceId(),
        tokens: {
          access_token: tokenResponse.access_token,
          refresh_token: tokenResponse.refresh_token,
          expires_at: expiresAt,
          token_type: tokenResponse.token_type
        },
        authorized_domains: authorizedDomains,
        last_used: new Date().toISOString()
      };
      
      tokenManager.saveAuthData(authData);
      
      return {
        success: true,
        message: domain 
          ? `Successfully authenticated and authorized for ${domain}` 
          : 'Successfully authenticated'
      };
    } catch (error) {
      return {
        success: false,
        message: `Authentication failed: ${error.message}`
      };
    }
  },
  
  /**
   * Request authorization for a specific domain
   * @param {string} domain - The domain to authorize
   * @returns {Promise<Object>} Domain authorization result
   */
  requestDomainAuthorization: async (domain) => {
    try {
      // Check if already authorized
      if (tokenManager.isDomainAuthorized(domain)) {
        return {
          success: true,
          message: `Already authorized for ${domain}`
        };
      }
      
      // Get valid access token
      const accessToken = await tokenManager.getValidToken();
      if (!accessToken) {
        return {
          success: false,
          message: 'Not authenticated. Please login first.'
        };
      }
      
      // Request domain authorization
      const domainAuthResponse = await authClient.requestDomainAuthorization(domain, accessToken);
      
      // Update auth data with new domain
      const authData = tokenManager.loadAuthData();
      const expiresAt = new Date(Date.now() + (7 * 24 * 60 * 60 * 1000)).toISOString(); // 7 days
      
      if (!authData.authorized_domains) {
        authData.authorized_domains = [];
      }
      
      // Remove existing domain authorization if present
      authData.authorized_domains = authData.authorized_domains.filter(d => d.domain !== domain);
      
      // Add new domain authorization
      authData.authorized_domains.push({
        domain,
        scopes: domainAuthResponse.scopes || ['read', 'write'],
        expires_at: expiresAt
      });
      
      tokenManager.saveAuthData(authData);
      
      return {
        success: true,
        message: `Successfully authorized for ${domain}`
      };
    } catch (error) {
      return {
        success: false,
        message: `Domain authorization failed: ${error.message}`
      };
    }
  },
  
  /**
   * Check authentication and domain authorization status
   * @param {string} domain - Optional domain to check authorization for
   * @returns {Object} Status information
   */
  checkStatus: (domain = null) => {
    // Check if authenticated
    if (!tokenManager.hasValidToken()) {
      return {
        authenticated: false,
        message: 'Not authenticated'
      };
    }
    
    // Get auth data
    const authData = tokenManager.loadAuthData();
    const authorizedDomains = tokenManager.getAuthorizedDomains();
    
    // If domain specified, check domain authorization
    if (domain) {
      const isDomainAuthorized = tokenManager.isDomainAuthorized(domain);
      return {
        authenticated: true,
        domain_authorized: isDomainAuthorized,
        message: isDomainAuthorized 
          ? `Authenticated and authorized for ${domain}` 
          : `Authenticated but not authorized for ${domain}`
      };
    }
    
    // General status
    return {
      authenticated: true,
      authorized_domains: authorizedDomains,
      expires_at: authData.tokens.expires_at,
      last_used: authData.last_used,
      message: 'Authenticated'
    };
  },
  
  /**
   * Logout and revoke tokens
   * @returns {Promise<Object>} Logout result
   */
  logout: async () => {
    try {
      await tokenManager.revokeTokens();
      return {
        success: true,
        message: 'Successfully logged out'
      };
    } catch (error) {
      return {
        success: false,
        message: `Logout failed: ${error.message}`
      };
    }
  }
};

// Export authentication module
module.exports = {
  startDeviceFlow: authFlow.startDeviceFlow,
  requestDomainAuthorization: authFlow.requestDomainAuthorization,
  checkStatus: authFlow.checkStatus,
  logout: authFlow.logout,
  getAuthorizedDomains: tokenManager.getAuthorizedDomains,
  isDomainAuthorized: tokenManager.isDomainAuthorized,
  hasValidToken: tokenManager.hasValidToken,
  getValidToken: tokenManager.getValidToken
};