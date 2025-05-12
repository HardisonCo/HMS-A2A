/**
 * Configuration Management Utility
 * Provides functions to load, validate, and access configuration settings.
 */

const fs = require('fs');
const path = require('path');

class ConfigManager {
  constructor(configPath = null) {
    this.config = {};
    this.configPath = configPath;
  }

  /**
   * Load configuration from file
   * @param {string} filePath - Path to config file (optional if set in constructor)
   * @returns {Object} - Loaded configuration
   */
  loadFromFile(filePath = null) {
    const configFile = filePath || this.configPath;
    if (!configFile) {
      throw new Error('No configuration file path provided');
    }

    try {
      const configContent = fs.readFileSync(configFile, 'utf8');
      const fileExt = path.extname(configFile).toLowerCase();
      
      if (fileExt === '.json') {
        this.config = JSON.parse(configContent);
      } else if (fileExt === '.js') {
        this.config = require(configFile);
      } else {
        throw new Error(`Unsupported config file format: ${fileExt}`);
      }
      
      return this.config;
    } catch (error) {
      throw new Error(`Failed to load configuration: ${error.message}`);
    }
  }

  /**
   * Load configuration from environment variables
   * @param {Array} requiredVars - List of required environment variables
   * @returns {Object} - Loaded configuration
   */
  loadFromEnv(requiredVars = []) {
    const config = {};
    
    // Load all required variables
    for (const varName of requiredVars) {
      if (!process.env[varName]) {
        throw new Error(`Required environment variable ${varName} is missing`);
      }
      config[varName] = process.env[varName];
    }
    
    this.config = { ...this.config, ...config };
    return this.config;
  }

  /**
   * Get a configuration value by key
   * @param {string} key - Configuration key
   * @param {*} defaultValue - Default value if key not found
   * @returns {*} - Configuration value
   */
  get(key, defaultValue = null) {
    const parts = key.split('.');
    let current = this.config;
    
    for (const part of parts) {
      if (current && typeof current === 'object' && part in current) {
        current = current[part];
      } else {
        return defaultValue;
      }
    }
    
    return current;
  }

  /**
   * Validate configuration against schema
   * @param {Object} schema - Schema definition
   * @returns {boolean} - True if valid
   */
  validate(schema) {
    for (const [key, rules] of Object.entries(schema)) {
      const value = this.get(key);
      
      if (rules.required && (value === null || value === undefined)) {
        throw new Error(`Required configuration key missing: ${key}`);
      }
      
      if (value !== null && value !== undefined) {
        if (rules.type && typeof value !== rules.type) {
          throw new Error(`Configuration key ${key} should be of type ${rules.type}`);
        }
        
        if (rules.validator && typeof rules.validator === 'function') {
          if (!rules.validator(value)) {
            throw new Error(`Configuration key ${key} failed validation`);
          }
        }
      }
    }
    
    return true;
  }
}

module.exports = ConfigManager;