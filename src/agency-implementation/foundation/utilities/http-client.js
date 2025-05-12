/**
 * HTTP Client Utility
 * Provides a standardized way to make HTTP requests with consistent error handling and logging.
 */

const axios = require('axios');

class HttpClient {
  /**
   * Create a new HTTP client
   * @param {Object} options - Configuration options
   * @param {string} options.baseURL - Base URL for all requests
   * @param {Object} options.headers - Default headers
   * @param {number} options.timeout - Request timeout in milliseconds
   * @param {Function} options.logger - Logger function
   */
  constructor(options = {}) {
    this.options = {
      baseURL: '',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      timeout: 30000, // 30 seconds
      ...options
    };
    
    this.axios = axios.create({
      baseURL: this.options.baseURL,
      headers: this.options.headers,
      timeout: this.options.timeout
    });
    
    // Add request interceptor for logging
    this.axios.interceptors.request.use(
      (config) => {
        if (this.options.logger) {
          this.options.logger.debug(`HTTP ${config.method.toUpperCase()} ${config.url}`, {
            headers: this._sanitizeHeaders(config.headers),
            params: config.params
          });
        }
        return config;
      },
      (error) => {
        if (this.options.logger) {
          this.options.logger.error('HTTP Request Error', { error: error.message });
        }
        return Promise.reject(error);
      }
    );
    
    // Add response interceptor for logging
    this.axios.interceptors.response.use(
      (response) => {
        if (this.options.logger) {
          this.options.logger.debug(`HTTP Response: ${response.status}`, {
            headers: this._sanitizeHeaders(response.headers),
            size: response.data ? JSON.stringify(response.data).length : 0
          });
        }
        return response;
      },
      (error) => {
        if (this.options.logger) {
          const status = error.response ? error.response.status : 'NETWORK_ERROR';
          this.options.logger.error(`HTTP Error: ${status}`, {
            message: error.message,
            response: error.response ? {
              status: error.response.status,
              data: error.response.data
            } : null
          });
        }
        return Promise.reject(this._normalizeError(error));
      }
    );
  }

  /**
   * Sanitize headers for logging (remove sensitive info)
   * @private
   * @param {Object} headers - Headers to sanitize
   * @returns {Object} - Sanitized headers
   */
  _sanitizeHeaders(headers) {
    const sanitized = { ...headers };
    const sensitiveHeaders = ['authorization', 'x-api-key', 'api-key'];
    
    for (const header of sensitiveHeaders) {
      if (sanitized[header]) {
        sanitized[header] = '[REDACTED]';
      }
    }
    
    return sanitized;
  }

  /**
   * Normalize error format
   * @private
   * @param {Error} error - Error to normalize
   * @returns {Error} - Normalized error
   */
  _normalizeError(error) {
    // Format the error to have consistent structure
    const normalizedError = new Error(
      error.response ? 
        `HTTP Error ${error.response.status}: ${error.response.statusText}` : 
        error.message || 'Network Error'
    );
    
    normalizedError.status = error.response ? error.response.status : 0;
    normalizedError.data = error.response ? error.response.data : null;
    normalizedError.originalError = error;
    
    return normalizedError;
  }

  /**
   * Make a GET request
   * @param {string} url - URL to request
   * @param {Object} options - Request options
   * @returns {Promise} - Response promise
   */
  async get(url, options = {}) {
    try {
      const response = await this.axios.get(url, options);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Make a POST request
   * @param {string} url - URL to request
   * @param {Object} data - Request payload
   * @param {Object} options - Request options
   * @returns {Promise} - Response promise
   */
  async post(url, data = {}, options = {}) {
    try {
      const response = await this.axios.post(url, data, options);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Make a PUT request
   * @param {string} url - URL to request
   * @param {Object} data - Request payload
   * @param {Object} options - Request options
   * @returns {Promise} - Response promise
   */
  async put(url, data = {}, options = {}) {
    try {
      const response = await this.axios.put(url, data, options);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Make a PATCH request
   * @param {string} url - URL to request
   * @param {Object} data - Request payload
   * @param {Object} options - Request options
   * @returns {Promise} - Response promise
   */
  async patch(url, data = {}, options = {}) {
    try {
      const response = await this.axios.patch(url, data, options);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Make a DELETE request
   * @param {string} url - URL to request
   * @param {Object} options - Request options
   * @returns {Promise} - Response promise
   */
  async delete(url, options = {}) {
    try {
      const response = await this.axios.delete(url, options);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Set a default header for all requests
   * @param {string} name - Header name
   * @param {string} value - Header value
   */
  setHeader(name, value) {
    this.axios.defaults.headers.common[name] = value;
  }

  /**
   * Set authorization header
   * @param {string} token - Bearer token
   */
  setAuthToken(token) {
    this.setHeader('Authorization', `Bearer ${token}`);
  }

  /**
   * Clear authorization header
   */
  clearAuthToken() {
    delete this.axios.defaults.headers.common['Authorization'];
  }
}

module.exports = HttpClient;