/**
 * Logging Utility
 * Provides standardized logging functionality with different log levels,
 * timestamps, and output formats.
 */

class Logger {
  constructor(options = {}) {
    this.options = {
      level: 'info',
      appName: 'agency-app',
      timestamp: true,
      console: true,
      file: null,
      ...options
    };
    
    this.levels = {
      error: 0,
      warn: 1,
      info: 2,
      debug: 3,
      trace: 4
    };
  }

  /**
   * Format a log message
   * @private
   * @param {string} level - Log level
   * @param {string} message - Log message
   * @param {Object} meta - Additional metadata
   * @returns {string} - Formatted log message
   */
  _formatMessage(level, message, meta = {}) {
    const timestamp = this.options.timestamp ? new Date().toISOString() : '';
    const metaStr = Object.keys(meta).length > 0 ? JSON.stringify(meta) : '';
    
    return `${timestamp} [${this.options.appName}] [${level.toUpperCase()}] ${message} ${metaStr}`.trim();
  }

  /**
   * Log a message if level is enabled
   * @private
   * @param {string} level - Log level
   * @param {string} message - Log message
   * @param {Object} meta - Additional metadata
   */
  _log(level, message, meta = {}) {
    if (this.levels[level] <= this.levels[this.options.level]) {
      const formattedMessage = this._formatMessage(level, message, meta);
      
      if (this.options.console) {
        const consoleMethod = level === 'error' ? 'error' : 
                              level === 'warn' ? 'warn' : 'log';
        console[consoleMethod](formattedMessage);
      }
      
      if (this.options.file) {
        // Implementation for file logging would go here
        // This is a placeholder for actual file writing logic
      }
    }
  }

  /**
   * Log an error message
   * @param {string} message - Log message
   * @param {Object} meta - Additional metadata
   */
  error(message, meta = {}) {
    this._log('error', message, meta);
  }

  /**
   * Log a warning message
   * @param {string} message - Log message
   * @param {Object} meta - Additional metadata
   */
  warn(message, meta = {}) {
    this._log('warn', message, meta);
  }

  /**
   * Log an info message
   * @param {string} message - Log message
   * @param {Object} meta - Additional metadata
   */
  info(message, meta = {}) {
    this._log('info', message, meta);
  }

  /**
   * Log a debug message
   * @param {string} message - Log message
   * @param {Object} meta - Additional metadata
   */
  debug(message, meta = {}) {
    this._log('debug', message, meta);
  }

  /**
   * Log a trace message
   * @param {string} message - Log message
   * @param {Object} meta - Additional metadata
   */
  trace(message, meta = {}) {
    this._log('trace', message, meta);
  }
}

module.exports = Logger;