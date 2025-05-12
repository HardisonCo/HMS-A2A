/**
 * Geographic Calculation Utilities
 * Provides functions for geospatial calculations commonly needed in agency applications.
 */

// Earth radius in kilometers
const EARTH_RADIUS_KM = 6371;
// Earth radius in miles
const EARTH_RADIUS_MI = 3959;

/**
 * Convert degrees to radians
 * @param {number} degrees - Angle in degrees
 * @returns {number} - Angle in radians
 */
function degreesToRadians(degrees) {
  return degrees * Math.PI / 180;
}

/**
 * Convert radians to degrees
 * @param {number} radians - Angle in radians
 * @returns {number} - Angle in degrees
 */
function radiansToDegrees(radians) {
  return radians * 180 / Math.PI;
}

/**
 * Calculate distance between two coordinates using Haversine formula
 * @param {number} lat1 - Latitude of first point in degrees
 * @param {number} lon1 - Longitude of first point in degrees
 * @param {number} lat2 - Latitude of second point in degrees
 * @param {number} lon2 - Longitude of second point in degrees
 * @param {string} unit - Unit of distance ('km' or 'mi')
 * @returns {number} - Distance in specified unit
 */
function calculateDistance(lat1, lon1, lat2, lon2, unit = 'km') {
  const radius = unit.toLowerCase() === 'mi' ? EARTH_RADIUS_MI : EARTH_RADIUS_KM;
  
  const dLat = degreesToRadians(lat2 - lat1);
  const dLon = degreesToRadians(lon2 - lon1);
  
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(degreesToRadians(lat1)) * Math.cos(degreesToRadians(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
    
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = radius * c;
  
  return distance;
}

/**
 * Check if a point is within a radius of another point
 * @param {number} lat - Latitude of point to check
 * @param {number} lon - Longitude of point to check
 * @param {number} centerLat - Latitude of center point
 * @param {number} centerLon - Longitude of center point
 * @param {number} radiusKm - Radius in kilometers
 * @returns {boolean} - True if point is within radius
 */
function isPointWithinRadius(lat, lon, centerLat, centerLon, radiusKm) {
  const distance = calculateDistance(lat, lon, centerLat, centerLon, 'km');
  return distance <= radiusKm;
}

/**
 * Calculate bounding box coordinates given a center point and distance
 * @param {number} lat - Latitude of center point in degrees
 * @param {number} lon - Longitude of center point in degrees
 * @param {number} distanceKm - Distance from center in kilometers
 * @returns {Object} - Bounding box coordinates
 */
function getBoundingBox(lat, lon, distanceKm) {
  // Earth's radius in km
  const radius = EARTH_RADIUS_KM;
  
  // Angular distance in radians on a great circle
  const radDist = distanceKm / radius;
  
  const radLat = degreesToRadians(lat);
  const radLon = degreesToRadians(lon);
  
  let minLat = radLat - radDist;
  let maxLat = radLat + radDist;
  
  let minLon, maxLon;
  
  // Special case for poles
  if (minLat > -Math.PI/2 && maxLat < Math.PI/2) {
    const deltaLon = Math.asin(Math.sin(radDist) / Math.cos(radLat));
    minLon = radLon - deltaLon;
    maxLon = radLon + deltaLon;
    
    if (minLon < -Math.PI) minLon += 2 * Math.PI;
    if (maxLon > Math.PI) maxLon -= 2 * Math.PI;
  } else {
    // Near the poles
    minLat = Math.max(minLat, -Math.PI/2);
    maxLat = Math.min(maxLat, Math.PI/2);
    minLon = -Math.PI;
    maxLon = Math.PI;
  }
  
  return {
    minLat: radiansToDegrees(minLat),
    maxLat: radiansToDegrees(maxLat),
    minLon: radiansToDegrees(minLon),
    maxLon: radiansToDegrees(maxLon)
  };
}

/**
 * Check if a point is inside a polygon
 * @param {Array} point - [longitude, latitude] of the point to check
 * @param {Array} polygon - Array of [longitude, latitude] points forming the polygon
 * @returns {boolean} - True if the point is inside the polygon
 */
function isPointInPolygon(point, polygon) {
  const x = point[0];
  const y = point[1];
  
  let inside = false;
  
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i][0];
    const yi = polygon[i][1];
    const xj = polygon[j][0];
    const yj = polygon[j][1];
    
    const intersect = ((yi > y) !== (yj > y)) &&
        (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        
    if (intersect) inside = !inside;
  }
  
  return inside;
}

/**
 * Get US state from coordinates 
 * (simplified version - would need a full geospatial database for real implementation)
 * @param {number} lat - Latitude in degrees
 * @param {number} lon - Longitude in degrees
 * @returns {string|null} - State code or null if not found
 */
function getStateFromCoordinates(lat, lon) {
  // This is a placeholder implementation
  // A real implementation would use a GIS database or API
  
  // Simple rectangular boundaries for a few states as an example
  const stateBoundaries = {
    CA: { minLat: 32.5, maxLat: 42.0, minLon: -124.6, maxLon: -114.1 },
    NY: { minLat: 40.5, maxLat: 45.0, minLon: -79.8, maxLon: -71.8 },
    TX: { minLat: 25.8, maxLat: 36.5, minLon: -106.6, maxLon: -93.5 }
  };
  
  for (const [state, bounds] of Object.entries(stateBoundaries)) {
    if (lat >= bounds.minLat && lat <= bounds.maxLat && 
        lon >= bounds.minLon && lon <= bounds.maxLon) {
      return state;
    }
  }
  
  return null;
}

/**
 * Get FIPS code for a state
 * @param {string} stateAbbr - State abbreviation (e.g., 'CA')
 * @returns {string|null} - FIPS code or null if not found
 */
function getStateFipsCode(stateAbbr) {
  const fipsCodes = {
    'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06',
    'CO': '08', 'CT': '09', 'DE': '10', 'FL': '12', 'GA': '13',
    'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19',
    'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24',
    'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29',
    'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 'NJ': '34',
    'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39',
    'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45',
    'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50',
    'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55', 'WY': '56',
    'DC': '11'
  };
  
  return fipsCodes[stateAbbr.toUpperCase()] || null;
}

module.exports = {
  calculateDistance,
  isPointWithinRadius,
  getBoundingBox,
  isPointInPolygon,
  getStateFromCoordinates,
  getStateFipsCode,
  degreesToRadians,
  radiansToDegrees
};