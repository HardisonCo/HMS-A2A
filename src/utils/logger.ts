import winston from 'winston';

// Create a custom logger with desired levels and format
export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: { service: 'hms-dev' },
  transports: [
    // Console transport for development
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(({ level, message, timestamp, component, ...meta }) => {
          const componentStr = component ? `[${component}] ` : '';
          const metaStr = Object.keys(meta).length > 0 && meta.service === 'hms-dev'
            ? ''
            : JSON.stringify(meta);
          return `${timestamp} ${level}: ${componentStr}${message} ${metaStr}`;
        })
      ),
      level: process.env.NODE_ENV === 'production' ? 'info' : 'debug'
    }),
    
    // File transports for production
    ...(process.env.NODE_ENV === 'production' ? [
      new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
      new winston.transports.File({ filename: 'logs/combined.log' })
    ] : [])
  ]
});

// Create and export specific component loggers
export function createComponentLogger(component: string): winston.Logger {
  return logger.child({ component });
}