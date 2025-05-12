/**
 * Date and Time Utilities
 * Provides functions for common date-time operations needed in agency applications.
 */

/**
 * Format a date according to agency standard format
 * @param {Date|string|number} date - Date to format
 * @param {string} format - Format string (default: 'YYYY-MM-DD')
 * @returns {string} - Formatted date string
 */
function formatDate(date, format = 'YYYY-MM-DD') {
  const d = new Date(date);
  
  if (isNaN(d.getTime())) {
    throw new Error('Invalid date provided');
  }
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
}

/**
 * Calculate the difference between two dates
 * @param {Date|string|number} date1 - First date
 * @param {Date|string|number} date2 - Second date
 * @param {string} unit - Unit of time ('days', 'hours', 'minutes', 'seconds', 'milliseconds')
 * @returns {number} - Difference in the specified unit
 */
function dateDiff(date1, date2, unit = 'days') {
  const d1 = new Date(date1).getTime();
  const d2 = new Date(date2).getTime();
  
  if (isNaN(d1) || isNaN(d2)) {
    throw new Error('Invalid date provided');
  }
  
  const diff = Math.abs(d2 - d1);
  
  switch (unit.toLowerCase()) {
    case 'days':
      return diff / (1000 * 60 * 60 * 24);
    case 'hours':
      return diff / (1000 * 60 * 60);
    case 'minutes':
      return diff / (1000 * 60);
    case 'seconds':
      return diff / 1000;
    case 'milliseconds':
      return diff;
    default:
      throw new Error(`Unsupported unit: ${unit}`);
  }
}

/**
 * Add time to a date
 * @param {Date|string|number} date - Base date
 * @param {number} amount - Amount to add
 * @param {string} unit - Unit of time ('years', 'months', 'days', 'hours', 'minutes', 'seconds')
 * @returns {Date} - New date
 */
function addTime(date, amount, unit = 'days') {
  const d = new Date(date);
  
  if (isNaN(d.getTime())) {
    throw new Error('Invalid date provided');
  }
  
  switch (unit.toLowerCase()) {
    case 'years':
      d.setFullYear(d.getFullYear() + amount);
      break;
    case 'months':
      d.setMonth(d.getMonth() + amount);
      break;
    case 'days':
      d.setDate(d.getDate() + amount);
      break;
    case 'hours':
      d.setHours(d.getHours() + amount);
      break;
    case 'minutes':
      d.setMinutes(d.getMinutes() + amount);
      break;
    case 'seconds':
      d.setSeconds(d.getSeconds() + amount);
      break;
    default:
      throw new Error(`Unsupported unit: ${unit}`);
  }
  
  return d;
}

/**
 * Check if a date is between two other dates
 * @param {Date|string|number} date - Date to check
 * @param {Date|string|number} startDate - Start date
 * @param {Date|string|number} endDate - End date
 * @param {boolean} inclusive - Whether to include start and end dates
 * @returns {boolean} - True if date is between start and end
 */
function isBetween(date, startDate, endDate, inclusive = true) {
  const d = new Date(date).getTime();
  const start = new Date(startDate).getTime();
  const end = new Date(endDate).getTime();
  
  if (isNaN(d) || isNaN(start) || isNaN(end)) {
    throw new Error('Invalid date provided');
  }
  
  return inclusive ? d >= start && d <= end : d > start && d < end;
}

/**
 * Convert a date to a fiscal year value (using Oct 1 fiscal year start)
 * @param {Date|string|number} date - Date to convert
 * @returns {string} - Fiscal year in format 'FY2023'
 */
function getFiscalYear(date) {
  const d = new Date(date);
  
  if (isNaN(d.getTime())) {
    throw new Error('Invalid date provided');
  }
  
  // Fiscal year starts on October 1 in many federal agencies
  let fiscalYear = d.getFullYear();
  if (d.getMonth() >= 9) { // October (0-indexed month 9) or later
    fiscalYear += 1;
  }
  
  return `FY${fiscalYear}`;
}

/**
 * Get the start and end dates of a fiscal quarter
 * @param {number} year - Calendar year
 * @param {number} quarter - Quarter (1-4)
 * @returns {Object} - Object with start and end dates
 */
function getFiscalQuarterDates(year, quarter) {
  if (quarter < 1 || quarter > 4 || !Number.isInteger(quarter)) {
    throw new Error('Quarter must be an integer between 1 and 4');
  }
  
  // Fiscal quarters for many federal agencies:
  // Q1: Oct-Dec, Q2: Jan-Mar, Q3: Apr-Jun, Q4: Jul-Sep
  let startMonth, endMonth, startYear, endYear;
  
  switch (quarter) {
    case 1:
      startMonth = 9; // October (0-indexed)
      endMonth = 11; // December
      startYear = year - 1;
      endYear = year - 1;
      break;
    case 2:
      startMonth = 0; // January
      endMonth = 2; // March
      startYear = year;
      endYear = year;
      break;
    case 3:
      startMonth = 3; // April
      endMonth = 5; // June
      startYear = year;
      endYear = year;
      break;
    case 4:
      startMonth = 6; // July
      endMonth = 8; // September
      startYear = year;
      endYear = year;
      break;
  }
  
  const startDate = new Date(startYear, startMonth, 1);
  
  // Last day of the end month
  const endDate = new Date(endYear, endMonth + 1, 0);
  
  return { startDate, endDate };
}

module.exports = {
  formatDate,
  dateDiff,
  addTime,
  isBetween,
  getFiscalYear,
  getFiscalQuarterDates
};