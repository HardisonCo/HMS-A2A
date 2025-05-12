/**
 * AI Agency CLI Authentication Web Interface
 * 
 * This script handles the web authentication flow for the AI Agency CLI
 */

// Configuration
const CONFIG = {
  API_URL: 'http://localhost:3000',
  AUTH_ENDPOINTS: {
    verifyCode: '/api/auth/device/verify',
    login: '/api/auth/login',
    authorizeDevice: '/api/auth/device/authorize-device',
    denyDevice: '/api/auth/device/deny-device',
    getDomains: '/api/domains'
  }
};

// DOM Elements
const sections = {
  codeEntry: document.getElementById('code-entry-section'),
  login: document.getElementById('login-section'),
  domainSelection: document.getElementById('domain-selection-section'),
  success: document.getElementById('success-section')
};

const elements = {
  // Code Entry Section
  deviceCode: document.getElementById('device-code'),
  verifyCodeBtn: document.getElementById('verify-code-btn'),
  
  // Login Section
  email: document.getElementById('email'),
  password: document.getElementById('password'),
  rememberDevice: document.getElementById('remember-device'),
  loginBtn: document.getElementById('login-btn'),
  
  // Domain Selection Section
  domainList: document.querySelector('.domain-list'),
  authorizeAllCheckbox: document.getElementById('authorize-all'),
  authorizeBtn: document.getElementById('authorize-btn'),
  backToLoginBtn: document.getElementById('back-to-login-btn'),
  
  // Success Section
  authorizedDomainsList: document.getElementById('authorized-domains-list'),
  deviceId: document.getElementById('device-id')
};

// State
let state = {
  deviceCode: null,
  userCode: null,
  clientId: null,
  userId: null,
  email: null,
  name: null,
  domains: null,
  selectedDomains: {},
  domainAccess: {}
};

/**
 * Initialize the app
 */
function initApp() {
  // Check for query parameters
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  
  if (code) {
    elements.deviceCode.value = code;
  }
  
  // Set up event listeners
  setupEventListeners();
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
  // Code Entry Section
  elements.verifyCodeBtn.addEventListener('click', verifyDeviceCode);
  
  // Login Section
  elements.loginBtn.addEventListener('click', handleLogin);
  
  // Domain Selection Section
  elements.authorizeAllCheckbox.addEventListener('change', toggleAllDomains);
  elements.authorizeBtn.addEventListener('click', authorizeDevice);
  elements.backToLoginBtn.addEventListener('click', backToLogin);
}

/**
 * Show loading state for a button
 * @param {HTMLButtonElement} button - The button element
 * @param {string} text - The loading text
 */
function showButtonLoading(button, text = 'Loading...') {
  button.innerHTML = `<span class="loading-spinner me-2"></span> ${text}`;
  button.disabled = true;
}

/**
 * Reset button state
 * @param {HTMLButtonElement} button - The button element
 * @param {string} text - The button text
 */
function resetButton(button, text) {
  button.innerHTML = text;
  button.disabled = false;
}

/**
 * Show an error message
 * @param {string} message - The error message
 */
function showError(message) {
  alert(message);
}

/**
 * Switch between sections
 * @param {string} sectionId - The section ID to show
 */
function showSection(sectionId) {
  Object.entries(sections).forEach(([id, element]) => {
    element.style.display = id === sectionId ? 'block' : 'none';
  });
}

/**
 * Verify the device code
 */
async function verifyDeviceCode() {
  const userCode = elements.deviceCode.value.trim();
  
  if (!userCode) {
    return showError('Please enter the verification code');
  }
  
  // Show loading state
  showButtonLoading(elements.verifyCodeBtn, 'Verifying...');
  
  try {
    // Call API to verify device code
    const response = await fetch(`${CONFIG.API_URL}${CONFIG.AUTH_ENDPOINTS.verifyCode}?code=${userCode}`);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error_description || 'Failed to verify code');
    }
    
    if (!data.valid) {
      throw new Error('Invalid verification code');
    }
    
    // Store device info
    state.deviceCode = data.device_code;
    state.userCode = userCode;
    state.clientId = data.client_id;
    
    // Show login section
    showSection('login');
  } catch (error) {
    showError(error.message);
    resetButton(elements.verifyCodeBtn, 'Verify Code');
  }
}

/**
 * Handle user login
 */
async function handleLogin() {
  const email = elements.email.value.trim();
  const password = elements.password.value;
  
  if (!email || !password) {
    return showError('Please enter your email and password');
  }
  
  // Show loading state
  showButtonLoading(elements.loginBtn, 'Signing in...');
  
  try {
    // Call API to login
    const response = await fetch(`${CONFIG.API_URL}${CONFIG.AUTH_ENDPOINTS.login}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error_description || 'Failed to login');
    }
    
    // Store user info
    state.userId = data.user.id;
    state.email = data.user.email;
    state.name = data.user.name;
    state.domainAccess = data.user.domain_access || {};
    
    // Load available domains
    await loadDomains();
    
    // Show domain selection section
    showSection('domainSelection');
  } catch (error) {
    showError(error.message);
    resetButton(elements.loginBtn, 'Sign in');
  }
}

/**
 * Load available domains
 */
async function loadDomains() {
  try {
    // Create a temporary token for API call (in a real app, this would be a session token)
    const tempToken = btoa(JSON.stringify({ sub: state.userId, email: state.email }));
    
    // Call API to get domains
    const response = await fetch(`${CONFIG.API_URL}${CONFIG.AUTH_ENDPOINTS.getDomains}`, {
      headers: {
        'Authorization': `Bearer ${tempToken}`
      }
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error_description || 'Failed to load domains');
    }
    
    // Store domains
    state.domains = data;
    
    // Generate domain list HTML
    renderDomainList();
  } catch (error) {
    showError(`Failed to load domains: ${error.message}`);
  }
}

/**
 * Render domain list
 */
function renderDomainList() {
  // Clear domain list
  elements.domainList.innerHTML = '';
  
  // Group domains by category
  const domainsByCategory = {};
  
  Object.entries(state.domains).forEach(([domainId, domain]) => {
    const category = domain.category || 'Other';
    
    if (!domainsByCategory[category]) {
      domainsByCategory[category] = [];
    }
    
    domainsByCategory[category].push({ id: domainId, ...domain });
  });
  
  // Render domains by category
  Object.entries(domainsByCategory).forEach(([category, domains]) => {
    // Add category heading
    const heading = document.createElement('h5');
    heading.className = 'mt-4';
    heading.textContent = `${category.charAt(0).toUpperCase()}${category.slice(1)} Domains`;
    elements.domainList.appendChild(heading);
    
    // Add domains
    domains.forEach(domain => {
      // Check if user has access to this domain
      const hasAccess = state.domainAccess[domain.id] && state.domainAccess[domain.id].length > 0;
      
      // Create domain card
      const card = document.createElement('div');
      card.className = `domain-card${hasAccess ? ' selected' : ''}`;
      card.dataset.domain = domain.id;
      
      // If user has access, pre-select and store
      if (hasAccess) {
        state.selectedDomains[domain.id] = state.domainAccess[domain.id];
      }
      
      card.innerHTML = `
        <div class="d-flex align-items-center">
          <span class="domain-icon">${domain.icon || '🔹'}</span>
          <div>
            <div class="domain-title">${domain.id}</div>
            <div class="domain-description">${domain.name}</div>
          </div>
        </div>
        ${hasAccess ? `
        <div class="domain-access mt-2">
          <small class="text-muted">Access: ${state.domainAccess[domain.id].join(', ')}</small>
        </div>
        ` : ''}
      `;
      
      // Add click event
      card.addEventListener('click', () => toggleDomain(domain.id));
      
      elements.domainList.appendChild(card);
    });
  });
}

/**
 * Toggle domain selection
 * @param {string} domainId - The domain ID
 */
function toggleDomain(domainId) {
  const card = document.querySelector(`.domain-card[data-domain="${domainId}"]`);
  
  if (!card) return;
  
  const isSelected = card.classList.toggle('selected');
  
  if (isSelected) {
    // If domain is in user's access, use those scopes
    if (state.domainAccess[domainId]) {
      state.selectedDomains[domainId] = state.domainAccess[domainId];
    } else {
      // Otherwise use default scopes (read)
      state.selectedDomains[domainId] = ['read'];
    }
  } else {
    delete state.selectedDomains[domainId];
  }
  
  // Update "authorize all" checkbox
  const allDomains = document.querySelectorAll('.domain-card').length;
  const selectedDomains = document.querySelectorAll('.domain-card.selected').length;
  
  elements.authorizeAllCheckbox.checked = selectedDomains === allDomains;
  elements.authorizeAllCheckbox.indeterminate = selectedDomains > 0 && selectedDomains < allDomains;
}

/**
 * Toggle all domains
 */
function toggleAllDomains() {
  const selectAll = elements.authorizeAllCheckbox.checked;
  
  document.querySelectorAll('.domain-card').forEach(card => {
    const domainId = card.dataset.domain;
    
    if (selectAll) {
      card.classList.add('selected');
      
      // If domain is in user's access, use those scopes
      if (state.domainAccess[domainId]) {
        state.selectedDomains[domainId] = state.domainAccess[domainId];
      } else {
        // Otherwise use default scopes (read)
        state.selectedDomains[domainId] = ['read'];
      }
    } else {
      card.classList.remove('selected');
      delete state.selectedDomains[domainId];
    }
  });
}

/**
 * Back to login
 */
function backToLogin() {
  showSection('login');
}

/**
 * Authorize the device
 */
async function authorizeDevice() {
  const selectedDomainIds = Object.keys(state.selectedDomains);
  
  if (selectedDomainIds.length === 0) {
    return showError('Please select at least one domain to authorize');
  }
  
  // Show loading state
  showButtonLoading(elements.authorizeBtn, 'Authorizing...');
  
  try {
    // Call API to authorize device
    const response = await fetch(`${CONFIG.API_URL}${CONFIG.AUTH_ENDPOINTS.authorizeDevice}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        device_code: state.deviceCode,
        user_id: state.userId,
        authorized_scopes: 'read write',
        domain_access: state.selectedDomains
      })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error_description || 'Failed to authorize device');
    }
    
    // Populate authorized domains list
    elements.authorizedDomainsList.innerHTML = '';
    
    selectedDomainIds.forEach(domainId => {
      const domain = state.domains[domainId];
      const scopes = state.selectedDomains[domainId].join(', ');
      
      const li = document.createElement('li');
      li.className = 'list-group-item d-flex justify-content-between align-items-center';
      li.innerHTML = `
        <div>
          <div class="fw-bold">${domainId}</div>
          <div class="small text-muted">${domain ? domain.name : ''}</div>
        </div>
        <span class="badge bg-success rounded-pill">Authorized (${scopes})</span>
      `;
      
      elements.authorizedDomainsList.appendChild(li);
    });
    
    // Set device ID (mock)
    elements.deviceId.textContent = `ai-agency-cli-${Math.floor(Math.random() * 100000)}`;
    
    // Show success section
    showSection('success');
  } catch (error) {
    showError(error.message);
    resetButton(elements.authorizeBtn, 'Authorize AI Agency CLI');
  }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);