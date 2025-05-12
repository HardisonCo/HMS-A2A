/**
 * Cryptography Utilities
 * Provides functions for hashing, encryption, and other security-related operations.
 */

const crypto = require('crypto');

/**
 * Generate a secure random string
 * @param {number} length - Length of the string to generate
 * @param {string} encoding - Encoding to use ('hex', 'base64', 'binary')
 * @returns {string} - Random string
 */
function generateRandomString(length = 32, encoding = 'hex') {
  const validEncodings = ['hex', 'base64', 'binary'];
  if (!validEncodings.includes(encoding)) {
    throw new Error(`Invalid encoding: ${encoding}. Must be one of: ${validEncodings.join(', ')}`);
  }
  
  const bytesNeeded = encoding === 'hex' ? Math.ceil(length / 2) : length;
  return crypto.randomBytes(bytesNeeded).toString(encoding).slice(0, length);
}

/**
 * Create a hash of a string
 * @param {string} data - Data to hash
 * @param {string} algorithm - Hash algorithm to use (default: 'sha256')
 * @param {string} encoding - Output encoding (default: 'hex')
 * @returns {string} - Hashed string
 */
function hash(data, algorithm = 'sha256', encoding = 'hex') {
  return crypto.createHash(algorithm).update(data).digest(encoding);
}

/**
 * Create an HMAC signature
 * @param {string} data - Data to sign
 * @param {string} key - Secret key
 * @param {string} algorithm - Hash algorithm to use (default: 'sha256')
 * @param {string} encoding - Output encoding (default: 'hex')
 * @returns {string} - HMAC signature
 */
function hmac(data, key, algorithm = 'sha256', encoding = 'hex') {
  return crypto.createHmac(algorithm, key).update(data).digest(encoding);
}

/**
 * Encrypt data using AES
 * @param {string} data - Data to encrypt
 * @param {string} key - Encryption key (must be 32 bytes for AES-256)
 * @param {string} iv - Initialization vector (must be 16 bytes)
 * @param {string} algorithm - Cipher algorithm (default: 'aes-256-cbc')
 * @returns {Object} - Object with encrypted data and used IV
 */
function encrypt(data, key, iv = null, algorithm = 'aes-256-cbc') {
  // If IV is not provided, generate a random one
  if (!iv) {
    iv = crypto.randomBytes(16);
  } else if (typeof iv === 'string') {
    iv = Buffer.from(iv, 'hex');
  }
  
  // Ensure key is the right length for the algorithm
  const keyBuffer = typeof key === 'string' ? Buffer.from(key) : key;
  
  const cipher = crypto.createCipheriv(algorithm, keyBuffer, iv);
  let encrypted = cipher.update(data, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  
  return {
    iv: iv.toString('hex'),
    encrypted
  };
}

/**
 * Decrypt data using AES
 * @param {string} encryptedData - Data to decrypt (hex encoded)
 * @param {string} key - Encryption key (must match the one used for encryption)
 * @param {string} iv - Initialization vector (must match the one used for encryption)
 * @param {string} algorithm - Cipher algorithm (default: 'aes-256-cbc')
 * @returns {string} - Decrypted data
 */
function decrypt(encryptedData, key, iv, algorithm = 'aes-256-cbc') {
  const ivBuffer = typeof iv === 'string' ? Buffer.from(iv, 'hex') : iv;
  const keyBuffer = typeof key === 'string' ? Buffer.from(key) : key;
  
  const decipher = crypto.createDecipheriv(algorithm, keyBuffer, ivBuffer);
  let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  
  return decrypted;
}

/**
 * Generate a secure password hash using bcrypt-like approach
 * @param {string} password - Password to hash
 * @param {number} saltRounds - Number of salt rounds (default: 10)
 * @returns {Object} - Object with hash and salt
 */
function hashPassword(password, saltRounds = 10) {
  // Generate a salt
  const salt = crypto.randomBytes(16).toString('hex');
  
  // Use PBKDF2 for password hashing (as a bcrypt alternative)
  const hash = crypto.pbkdf2Sync(
    password,
    salt,
    saltRounds * 1000, // iterations based on salt rounds
    64,
    'sha512'
  ).toString('hex');
  
  return {
    salt,
    hash
  };
}

/**
 * Verify a password against a stored hash
 * @param {string} password - Password to verify
 * @param {string} hash - Stored hash
 * @param {string} salt - Stored salt
 * @param {number} saltRounds - Number of salt rounds used (default: 10)
 * @returns {boolean} - True if password matches
 */
function verifyPassword(password, storedHash, salt, saltRounds = 10) {
  const hash = crypto.pbkdf2Sync(
    password,
    salt,
    saltRounds * 1000, // iterations based on salt rounds
    64,
    'sha512'
  ).toString('hex');
  
  return hash === storedHash;
}

/**
 * Generate a UUID v4
 * @returns {string} - UUID v4
 */
function generateUUID() {
  return crypto.randomUUID();
}

/**
 * Generate a secure token for authentication
 * @param {number} length - Token length (default: 32)
 * @returns {string} - Secure token
 */
function generateToken(length = 32) {
  return generateRandomString(length, 'base64');
}

module.exports = {
  generateRandomString,
  hash,
  hmac,
  encrypt,
  decrypt,
  hashPassword,
  verifyPassword,
  generateUUID,
  generateToken
};