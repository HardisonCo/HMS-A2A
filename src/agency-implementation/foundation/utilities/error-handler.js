/**
 * Error Handling Utility
 * Provides standardized error handling, custom error types, and error tracking.
 */

class AppError extends Error {
  constructor(message, code = 'INTERNAL_ERROR', statusCode = 500, details = {}) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
    this.timestamp = new Date().toISOString();
    
    // Capture stack trace
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }

  /**
   * Serialize error to JSON
   * @returns {Object} - Serialized error
   */
  toJSON() {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      statusCode: this.statusCode,
      details: this.details,
      timestamp: this.timestamp,
      stack: this.stack
    };
  }
}

// Common agency-specific error types
class ValidationError extends AppError {
  constructor(message, details = {}) {
    super(message, 'VALIDATION_ERROR', 400, details);
  }
}

class NotFoundError extends AppError {
  constructor(message, details = {}) {
    super(message, 'NOT_FOUND', 404, details);
  }
}

class AuthenticationError extends AppError {
  constructor(message, details = {}) {
    super(message, 'AUTHENTICATION_ERROR', 401, details);
  }
}

class AuthorizationError extends AppError {
  constructor(message, details = {}) {
    super(message, 'AUTHORIZATION_ERROR', 403, details);
  }
}

class DatabaseError extends AppError {
  constructor(message, details = {}) {
    super(message, 'DATABASE_ERROR', 500, details);
  }
}

/**
 * Global error handler for Express applications
 * @param {Error} err - Error object
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
function expressErrorHandler(err, req, res, next) {
  // Determine if error is one of our custom errors
  const isAppError = err instanceof AppError;
  
  // Default values for non-AppError instances
  const statusCode = isAppError ? err.statusCode : 500;
  const errorCode = isAppError ? err.code : 'INTERNAL_SERVER_ERROR';
  const message = isAppError ? err.message : 'An unexpected error occurred';
  const details = isAppError ? err.details : {};
  
  // Log the error (assuming a logger is available on the request object)
  if (req.logger) {
    req.logger.error(message, {
      code: errorCode,
      path: req.path,
      method: req.method,
      stack: err.stack,
      details
    });
  } else {
    console.error('[ERROR]', err);
  }
  
  // Send error response
  res.status(statusCode).json({
    error: {
      code: errorCode,
      message,
      ...(Object.keys(details).length > 0 ? { details } : {})
    }
  });
}

module.exports = {
  AppError,
  ValidationError,
  NotFoundError,
  AuthenticationError,
  AuthorizationError,
  DatabaseError,
  expressErrorHandler
};