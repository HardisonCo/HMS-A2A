/**
 * Data Validation Utilities
 * Provides functions for validating common data types and formats.
 */

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} - True if valid
 */
function isValidEmail(email) {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
}

/**
 * Validate phone number format (US)
 * @param {string} phone - Phone number to validate
 * @returns {boolean} - True if valid
 */
function isValidUSPhone(phone) {
  // Remove all non-digits
  const digitsOnly = phone.replace(/\D/g, '');
  
  // Check if it's a valid US phone (10 digits, or 11 digits starting with 1)
  if (digitsOnly.length === 10) {
    return true;
  } else if (digitsOnly.length === 11 && digitsOnly.charAt(0) === '1') {
    return true;
  }
  
  return false;
}

/**
 * Validate ZIP code format (US)
 * @param {string} zip - ZIP code to validate
 * @param {boolean} allowPlusFour - Allow ZIP+4 format
 * @returns {boolean} - True if valid
 */
function isValidUSZip(zip, allowPlusFour = true) {
  if (allowPlusFour) {
    return /^\d{5}(-\d{4})?$/.test(zip);
  }
  
  return /^\d{5}$/.test(zip);
}

/**
 * Validate Social Security Number format (US)
 * @param {string} ssn - SSN to validate
 * @returns {boolean} - True if valid
 */
function isValidSSN(ssn) {
  // Remove hyphens and spaces
  const digitsOnly = ssn.replace(/[\s-]/g, '');
  
  // Check if it's 9 digits and not all same digits or sequential
  if (/^\d{9}$/.test(digitsOnly)) {
    // Check for all same digits (e.g., 111-11-1111)
    if (/^(\d)\1{8}$/.test(digitsOnly)) {
      return false;
    }
    
    // Check for invalid prefixes
    const prefix = digitsOnly.substring(0, 3);
    if (prefix === '000' || prefix === '666' || parseInt(prefix, 10) >= 900) {
      return false;
    }
    
    // Check for invalid group or serial numbers
    const group = digitsOnly.substring(3, 5);
    const serial = digitsOnly.substring(5, 9);
    if (group === '00' || serial === '0000') {
      return false;
    }
    
    return true;
  }
  
  return false;
}

/**
 * Validate date format
 * @param {string} dateStr - Date string to validate
 * @param {string} format - Expected format (e.g., 'YYYY-MM-DD')
 * @returns {boolean} - True if valid
 */
function isValidDate(dateStr, format = 'YYYY-MM-DD') {
  // Convert the format to a regex pattern
  let pattern = format
    .replace('YYYY', '(\\d{4})')
    .replace('MM', '(0[1-9]|1[0-2])')
    .replace('DD', '(0[1-9]|[12]\\d|3[01])');
  
  const regex = new RegExp(`^${pattern}$`);
  
  if (!regex.test(dateStr)) {
    return false;
  }
  
  // Extract components based on format
  let year, month, day;
  
  if (format === 'YYYY-MM-DD') {
    [year, month, day] = dateStr.split('-').map(Number);
  } else if (format === 'MM/DD/YYYY') {
    const parts = dateStr.split('/').map(Number);
    month = parts[0];
    day = parts[1];
    year = parts[2];
  } else {
    // For other formats, we'd need more parsing logic
    // For now, just return true if it matches the regex
    return true;
  }
  
  // Check if the date actually exists
  const date = new Date(year, month - 1, day);
  return date.getFullYear() === year && 
         date.getMonth() === month - 1 && 
         date.getDate() === day;
}

/**
 * Validate Federal Employer Identification Number (EIN)
 * @param {string} ein - EIN to validate
 * @returns {boolean} - True if valid
 */
function isValidEIN(ein) {
  // Remove hyphens and spaces
  const digitsOnly = ein.replace(/[\s-]/g, '');
  
  // EIN is 9 digits and first two digits have specific ranges
  if (/^\d{9}$/.test(digitsOnly)) {
    const prefix = parseInt(digitsOnly.substring(0, 2), 10);
    
    // Valid EIN prefixes
    const validPrefixes = [
      10, 12, 60, 67, 50, 53, 
      // Ranges
      [1, 7], [10, 19], [20, 29], [30, 39], 
      [40, 49], [50, 59], [60, 69], [70, 79], [80, 89]
    ];
    
    return validPrefixes.some(val => {
      if (Array.isArray(val)) {
        return prefix >= val[0] && prefix <= val[1];
      }
      return prefix === val;
    });
  }
  
  return false;
}

/**
 * Validate a federal agency code
 * @param {string} code - Agency code to validate
 * @returns {boolean} - True if valid
 */
function isValidAgencyCode(code) {
  // Agency codes are typically 3 characters
  return /^[A-Z0-9]{2,4}$/.test(code.toUpperCase());
}

/**
 * Validate a DUNS number (Data Universal Numbering System)
 * @param {string} duns - DUNS number to validate
 * @returns {boolean} - True if valid
 */
function isValidDUNS(duns) {
  // DUNS is 9 digits
  const digitsOnly = duns.replace(/[\s-]/g, '');
  return /^\d{9}$/.test(digitsOnly);
}

/**
 * Validate a CAGE code (Commercial and Government Entity)
 * @param {string} cage - CAGE code to validate
 * @returns {boolean} - True if valid
 */
function isValidCAGE(cage) {
  // CAGE is 5 characters: A-Z and 0-9
  return /^[A-Z0-9]{5}$/i.test(cage);
}

/**
 * Validate a UEI (Unique Entity Identifier) that replaced DUNS
 * @param {string} uei - UEI to validate
 * @returns {boolean} - True if valid
 */
function isValidUEI(uei) {
  // UEI is 12 characters
  return /^[A-Z0-9]{12}$/i.test(uei);
}

/**
 * Validate a URL
 * @param {string} url - URL to validate
 * @param {boolean} requireHttps - Require HTTPS protocol
 * @returns {boolean} - True if valid
 */
function isValidURL(url, requireHttps = false) {
  try {
    const urlObj = new URL(url);
    if (requireHttps && urlObj.protocol !== 'https:') {
      return false;
    }
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Validate a US state code
 * @param {string} state - State code to validate
 * @returns {boolean} - True if valid
 */
function isValidUSState(state) {
  const states = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    'DC', 'AS', 'GU', 'MP', 'PR', 'VI'
  ];
  
  return states.includes(state.toUpperCase());
}

module.exports = {
  isValidEmail,
  isValidUSPhone,
  isValidUSZip,
  isValidSSN,
  isValidDate,
  isValidEIN,
  isValidAgencyCode,
  isValidDUNS,
  isValidCAGE,
  isValidUEI,
  isValidURL,
  isValidUSState
};