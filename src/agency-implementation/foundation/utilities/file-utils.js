/**
 * File Utility Functions
 * Provides common file operations needed across agency implementations.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { promisify } = require('util');

// Promisify filesystem functions
const readFileAsync = promisify(fs.readFile);
const writeFileAsync = promisify(fs.writeFile);
const appendFileAsync = promisify(fs.appendFile);
const mkdirAsync = promisify(fs.mkdir);
const statAsync = promisify(fs.stat);
const readdirAsync = promisify(fs.readdir);
const unlinkAsync = promisify(fs.unlink);
const renameAsync = promisify(fs.rename);
const accessAsync = promisify(fs.access);

/**
 * Check if a file exists
 * @param {string} filePath - Path to file
 * @returns {Promise<boolean>} - True if file exists
 */
async function fileExists(filePath) {
  try {
    await accessAsync(filePath, fs.constants.F_OK);
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Read a file asynchronously
 * @param {string} filePath - Path to file
 * @param {string} encoding - File encoding (default: 'utf8')
 * @returns {Promise<string|Buffer>} - File contents
 */
async function readFile(filePath, encoding = 'utf8') {
  try {
    return await readFileAsync(filePath, encoding);
  } catch (error) {
    throw new Error(`Failed to read file ${filePath}: ${error.message}`);
  }
}

/**
 * Write to a file asynchronously
 * @param {string} filePath - Path to file
 * @param {string|Buffer} data - Data to write
 * @param {Object} options - Write options
 * @returns {Promise<void>}
 */
async function writeFile(filePath, data, options = {}) {
  try {
    const dirname = path.dirname(filePath);
    await ensureDirectoryExists(dirname);
    await writeFileAsync(filePath, data, options);
  } catch (error) {
    throw new Error(`Failed to write to file ${filePath}: ${error.message}`);
  }
}

/**
 * Append to a file asynchronously
 * @param {string} filePath - Path to file
 * @param {string|Buffer} data - Data to append
 * @param {Object} options - Append options
 * @returns {Promise<void>}
 */
async function appendFile(filePath, data, options = {}) {
  try {
    const dirname = path.dirname(filePath);
    await ensureDirectoryExists(dirname);
    await appendFileAsync(filePath, data, options);
  } catch (error) {
    throw new Error(`Failed to append to file ${filePath}: ${error.message}`);
  }
}

/**
 * Ensure a directory exists, creating it if necessary
 * @param {string} dirPath - Path to directory
 * @param {Object} options - mkdir options
 * @returns {Promise<void>}
 */
async function ensureDirectoryExists(dirPath, options = { recursive: true }) {
  try {
    await mkdirAsync(dirPath, options);
  } catch (error) {
    // Directory already exists, ignore error
    if (error.code !== 'EEXIST') {
      throw new Error(`Failed to create directory ${dirPath}: ${error.message}`);
    }
  }
}

/**
 * Get file stats
 * @param {string} filePath - Path to file
 * @returns {Promise<Object>} - File stats
 */
async function getFileStats(filePath) {
  try {
    return await statAsync(filePath);
  } catch (error) {
    throw new Error(`Failed to get file stats for ${filePath}: ${error.message}`);
  }
}

/**
 * List files in a directory
 * @param {string} dirPath - Path to directory
 * @param {Object} options - Options object
 * @param {boolean} options.includeHidden - Include hidden files
 * @param {string} options.extension - Filter by extension
 * @param {boolean} options.recursive - Recursively list files
 * @param {boolean} options.fullPath - Return full paths
 * @returns {Promise<Array>} - List of files
 */
async function listFiles(dirPath, options = {}) {
  const {
    includeHidden = false,
    extension = null,
    recursive = false,
    fullPath = false
  } = options;
  
  try {
    let files = await readdirAsync(dirPath);
    
    // Filter hidden files if not included
    if (!includeHidden) {
      files = files.filter(file => !file.startsWith('.'));
    }
    
    // Filter by extension if specified
    if (extension) {
      const ext = extension.startsWith('.') ? extension : `.${extension}`;
      files = files.filter(file => path.extname(file) === ext);
    }
    
    // Build full paths if requested
    if (fullPath) {
      files = files.map(file => path.join(dirPath, file));
    }
    
    // Handle recursive listing
    if (recursive) {
      const result = [...files];
      
      for (const file of files) {
        const filePath = fullPath ? file : path.join(dirPath, file);
        const stats = await statAsync(filePath);
        
        if (stats.isDirectory()) {
          const subFiles = await listFiles(filePath, {
            includeHidden,
            extension,
            recursive,
            fullPath: true
          });
          
          if (!fullPath) {
            // Convert back to relative paths
            const relativePaths = subFiles.map(subFile => path.relative(dirPath, subFile));
            result.push(...relativePaths);
          } else {
            result.push(...subFiles);
          }
        }
      }
      
      return result;
    }
    
    return files;
  } catch (error) {
    throw new Error(`Failed to list files in ${dirPath}: ${error.message}`);
  }
}

/**
 * Delete a file
 * @param {string} filePath - Path to file
 * @returns {Promise<void>}
 */
async function deleteFile(filePath) {
  try {
    await unlinkAsync(filePath);
  } catch (error) {
    throw new Error(`Failed to delete file ${filePath}: ${error.message}`);
  }
}

/**
 * Rename a file
 * @param {string} oldPath - Current file path
 * @param {string} newPath - New file path
 * @returns {Promise<void>}
 */
async function renameFile(oldPath, newPath) {
  try {
    await renameAsync(oldPath, newPath);
  } catch (error) {
    throw new Error(`Failed to rename file ${oldPath} to ${newPath}: ${error.message}`);
  }
}

/**
 * Calculate file hash
 * @param {string} filePath - Path to file
 * @param {string} algorithm - Hash algorithm (default: 'sha256')
 * @returns {Promise<string>} - File hash
 */
async function getFileHash(filePath, algorithm = 'sha256') {
  try {
    const fileBuffer = await readFileAsync(filePath);
    const hashSum = crypto.createHash(algorithm);
    hashSum.update(fileBuffer);
    return hashSum.digest('hex');
  } catch (error) {
    throw new Error(`Failed to calculate hash for ${filePath}: ${error.message}`);
  }
}

/**
 * Extract file extension
 * @param {string} filePath - Path to file
 * @returns {string} - File extension
 */
function getFileExtension(filePath) {
  return path.extname(filePath).toLowerCase();
}

/**
 * Get a unique filename by appending a timestamp or counter
 * @param {string} filePath - Original file path
 * @param {string} method - Method to use ('timestamp' or 'counter')
 * @returns {Promise<string>} - Unique file path
 */
async function getUniqueFilename(filePath, method = 'timestamp') {
  const ext = path.extname(filePath);
  const baseFilename = path.basename(filePath, ext);
  const dir = path.dirname(filePath);
  
  if (method === 'timestamp') {
    const timestamp = Date.now();
    return path.join(dir, `${baseFilename}_${timestamp}${ext}`);
  } else if (method === 'counter') {
    let counter = 0;
    let uniquePath = filePath;
    
    while (await fileExists(uniquePath)) {
      counter++;
      uniquePath = path.join(dir, `${baseFilename}_${counter}${ext}`);
    }
    
    return uniquePath;
  } else {
    throw new Error(`Unsupported method: ${method}`);
  }
}

/**
 * Parse a CSV file
 * @param {string} filePath - Path to CSV file
 * @param {Object} options - Parse options
 * @param {string} options.delimiter - Field delimiter
 * @param {boolean} options.hasHeader - Whether file has header row
 * @returns {Promise<Array>} - Parsed data
 */
async function parseCSV(filePath, options = { delimiter: ',', hasHeader: true }) {
  try {
    const content = await readFileAsync(filePath, 'utf8');
    const lines = content.split(/\r?\n/).filter(line => line.trim());
    
    if (lines.length === 0) {
      return [];
    }
    
    const { delimiter, hasHeader } = options;
    const result = [];
    let headers = [];
    
    // Parse header if present
    if (hasHeader) {
      headers = lines[0].split(delimiter).map(h => h.trim());
    }
    
    // Parse data rows
    const startRow = hasHeader ? 1 : 0;
    
    for (let i = startRow; i < lines.length; i++) {
      const values = lines[i].split(delimiter).map(v => v.trim());
      
      if (hasHeader) {
        // Create object with header keys
        const row = {};
        for (let j = 0; j < headers.length; j++) {
          row[headers[j]] = values[j] || '';
        }
        result.push(row);
      } else {
        // Simply add array of values
        result.push(values);
      }
    }
    
    return result;
  } catch (error) {
    throw new Error(`Failed to parse CSV file ${filePath}: ${error.message}`);
  }
}

module.exports = {
  fileExists,
  readFile,
  writeFile,
  appendFile,
  ensureDirectoryExists,
  getFileStats,
  listFiles,
  deleteFile,
  renameFile,
  getFileHash,
  getFileExtension,
  getUniqueFilename,
  parseCSV
};