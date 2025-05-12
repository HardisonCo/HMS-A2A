import { createComponentLogger } from './logger';
const logger = createComponentLogger('error-handler');

/**
 * Base error class for all application errors
 * Provides standardized error handling with additional context
 */
export class AppError extends Error {
  public readonly code: string;
  public readonly httpStatus?: number;
  public readonly context: Record<string, any>;
  public readonly cause?: Error;
  public readonly timestamp: Date;

  constructor(
    message: string,
    options: {
      code?: string;
      httpStatus?: number;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message);
    this.name = this.constructor.name;
    this.code = options.code || 'UNKNOWN_ERROR';
    this.httpStatus = options.httpStatus;
    this.context = options.context || {};
    this.cause = options.cause;
    this.timestamp = new Date();

    // Maintains proper stack trace for where our error was thrown (only in V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }

  /**
   * Convert error to a JSON-serializable object
   */
  public toJSON(): Record<string, any> {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      httpStatus: this.httpStatus,
      context: this.context,
      cause: this.cause ? (this.cause instanceof AppError ? this.cause.toJSON() : this.cause.message) : undefined,
      stack: this.stack,
      timestamp: this.timestamp.toISOString()
    };
  }

  /**
   * Log this error with appropriate level based on code
   */
  public log(): void {
    // Choose log level based on error code pattern
    if (this.code.startsWith('FATAL_')) {
      logger.error('Fatal error:', this.toJSON());
    } else if (this.code.startsWith('CRITICAL_')) {
      logger.error('Critical error:', this.toJSON());
    } else if (this.code.startsWith('WARNING_')) {
      logger.warn('Warning:', this.toJSON());
    } else {
      logger.error('Error:', this.toJSON());
    }
  }
}

/**
 * Validation error for invalid input data
 */
export class ValidationError extends AppError {
  constructor(
    message: string,
    options: {
      code?: string;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: options.code || 'VALIDATION_ERROR',
      httpStatus: 400,
      context: options.context,
      cause: options.cause
    });
  }
}

/**
 * Network error for communication failures
 */
export class NetworkError extends AppError {
  constructor(
    message: string,
    options: {
      code?: string;
      httpStatus?: number;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: options.code || 'NETWORK_ERROR',
      httpStatus: options.httpStatus || 503,
      context: options.context,
      cause: options.cause
    });
  }
}

/**
 * Timeout error for operations that took too long
 */
export class TimeoutError extends AppError {
  constructor(
    message: string,
    options: {
      code?: string;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: options.code || 'TIMEOUT_ERROR',
      httpStatus: 408,
      context: options.context,
      cause: options.cause
    });
  }
}

/**
 * Not found error for missing resources
 */
export class NotFoundError extends AppError {
  constructor(
    message: string,
    options: {
      code?: string;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: options.code || 'NOT_FOUND_ERROR',
      httpStatus: 404,
      context: options.context,
      cause: options.cause
    });
  }
}

/**
 * Genetic algorithm error for failures in genetic operations
 */
export class GeneticError extends AppError {
  constructor(
    message: string,
    options: {
      code?: string;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: options.code || 'GENETIC_ERROR',
      context: options.context,
      cause: options.cause
    });
  }
}

/**
 * Distributed computing error for cluster/node failures
 */
export class DistributedError extends AppError {
  constructor(
    message: string,
    options: {
      code?: string;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: options.code || 'DISTRIBUTED_ERROR',
      context: options.context,
      cause: options.cause
    });
  }
}

/**
 * Recursive thinking error for failures in recursive thought process
 */
export class RecursiveThinkingError extends AppError {
  constructor(
    message: string,
    options: {
      code?: string;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: options.code || 'RECURSIVE_THINKING_ERROR',
      context: options.context,
      cause: options.cause
    });
  }
}

/**
 * Global error handler for uncaught exceptions
 */
export function setupGlobalErrorHandlers(): void {
  // Handle uncaught exceptions
  process.on('uncaughtException', (error: Error) => {
    const appError = new AppError('Uncaught exception', {
      code: 'FATAL_UNCAUGHT_EXCEPTION',
      cause: error,
      context: { processId: process.pid }
    });
    appError.log();
    
    // Give logger time to write before exiting
    setTimeout(() => {
      process.exit(1);
    }, 1000);
  });

  // Handle unhandled promise rejections
  process.on('unhandledRejection', (reason: any, promise: Promise<any>) => {
    const appError = new AppError('Unhandled promise rejection', {
      code: 'FATAL_UNHANDLED_REJECTION',
      cause: reason instanceof Error ? reason : new Error(String(reason)),
      context: { processId: process.pid }
    });
    appError.log();
  });
  
  // Handle SIGTERM signal
  process.on('SIGTERM', () => {
    logger.info('Received SIGTERM signal, shutting down gracefully');
    // Perform cleanup here
    process.exit(0);
  });

  logger.info('Global error handlers have been set up');
}

/**
 * Try to execute a function and handle errors
 * @param fn Function to execute
 * @param errorHandler Optional custom error handler
 * @returns Function result or undefined if error
 */
export async function tryCatch<T>(
  fn: () => Promise<T> | T,
  errorHandler?: (error: Error) => void
): Promise<T | undefined> {
  try {
    return await fn();
  } catch (error) {
    if (errorHandler) {
      errorHandler(error instanceof Error ? error : new Error(String(error)));
    } else {
      // Default error handling
      const appError = error instanceof AppError
        ? error
        : new AppError('Operation failed', {
            code: 'OPERATION_ERROR',
            cause: error instanceof Error ? error : new Error(String(error))
          });
      appError.log();
    }
    return undefined;
  }
}

/**
 * Retry a function multiple times with exponential backoff
 * @param fn Function to execute
 * @param options Retry options
 * @returns Function result
 * @throws Error if all retries fail
 */
export async function retry<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    initialDelay?: number;
    maxDelay?: number;
    factor?: number;
    shouldRetry?: (error: Error) => boolean;
  } = {}
): Promise<T> {
  const maxRetries = options.maxRetries ?? 3;
  const initialDelay = options.initialDelay ?? 100;
  const maxDelay = options.maxDelay ?? 5000;
  const factor = options.factor ?? 2;
  const shouldRetry = options.shouldRetry ?? (() => true);

  let lastError: Error;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      
      if (attempt === maxRetries || !shouldRetry(lastError)) {
        throw new AppError('Operation failed after retries', {
          code: 'RETRY_FAILED',
          cause: lastError,
          context: { attempts: attempt + 1, maxRetries }
        });
      }
      
      // Calculate delay with exponential backoff and jitter
      const delay = Math.min(
        initialDelay * Math.pow(factor, attempt) * (0.5 + Math.random()),
        maxDelay
      );
      
      logger.debug(`Retry attempt ${attempt + 1}/${maxRetries} after ${delay}ms delay`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  // This should never happen due to the throw in the loop
  throw lastError!;
}

/**
 * Circuit breaker implementation for preventing cascading failures
 */
export class CircuitBreaker {
  private failures: number = 0;
  private lastFailureTime: number = 0;
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';

  constructor(
    private readonly options: {
      failureThreshold?: number;
      resetTimeout?: number;
      onStateChange?: (from: string, to: string) => void;
    } = {}
  ) {}

  /**
   * Execute a function with circuit breaker protection
   */
  public async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      // Check if it's time to try again
      const now = Date.now();
      const resetTimeout = this.options.resetTimeout ?? 10000;
      
      if (now > this.lastFailureTime + resetTimeout) {
        this.setState('HALF_OPEN');
      } else {
        throw new AppError('Circuit breaker is open', {
          code: 'CIRCUIT_OPEN',
          context: {
            failureCount: this.failures,
            lastFailureTime: new Date(this.lastFailureTime).toISOString(),
            remainingTimeMs: this.lastFailureTime + resetTimeout - now
          }
        });
      }
    }

    try {
      const result = await fn();
      
      if (this.state === 'HALF_OPEN') {
        this.reset();
      }
      
      return result;
    } catch (error) {
      this.recordFailure();
      throw error instanceof Error ? error : new Error(String(error));
    }
  }

  /**
   * Record a failure and potentially open the circuit
   */
  private recordFailure(): void {
    this.failures++;
    this.lastFailureTime = Date.now();
    
    const threshold = this.options.failureThreshold ?? 5;
    if (this.failures >= threshold) {
      this.setState('OPEN');
    }
  }

  /**
   * Reset the circuit breaker
   */
  public reset(): void {
    this.setState('CLOSED');
    this.failures = 0;
  }

  /**
   * Change circuit breaker state
   */
  private setState(newState: 'CLOSED' | 'OPEN' | 'HALF_OPEN'): void {
    if (this.state !== newState) {
      logger.info(`Circuit breaker state changing from ${this.state} to ${newState}`);
      
      if (this.options.onStateChange) {
        this.options.onStateChange(this.state, newState);
      }
      
      this.state = newState;
    }
  }

  /**
   * Get current circuit breaker state
   */
  public getState(): string {
    return this.state;
  }

  /**
   * Get current failure count
   */
  public getFailureCount(): number {
    return this.failures;
  }
}