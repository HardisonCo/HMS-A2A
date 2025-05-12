/**
 * Integration Tests for APHIS Bird Flu HMS-MFE Components
 * 
 * These tests validate that the components correctly integrate with:
 * 1. The APHIS Bird Flu API
 * 2. The Federation Hub for cross-agency data sharing
 * 3. The HMS-MFE framework
 */

const { test, expect } = require('@playwright/test');

// Configuration
const HMS_MFE_URL = process.env.HMS_MFE_URL || 'http://localhost:3000';
const API_URL = process.env.API_URL || 'http://localhost:8000';
const FEDERATION_URL = process.env.FEDERATION_URL || 'http://localhost:9000';

// Test timeouts
const TIMEOUT = 30000;

// Helper function to check if an endpoint is available
async function checkEndpointAvailability(url, name) {
  try {
    const response = await fetch(`${url}/health`);
    if (!response.ok) {
      console.warn(`Warning: ${name} health check failed with status ${response.status}`);
    }
  } catch (error) {
    console.warn(`Warning: ${name} is not available at ${url}: ${error.message}`);
    console.warn(`Tests requiring ${name} may fail`);
  }
}

// Setup for all tests
test.beforeAll(async () => {
  // Check if API and Federation Hub are available
  await checkEndpointAvailability(API_URL, 'API');
  await checkEndpointAvailability(FEDERATION_URL, 'Federation Hub');
});

// Setup for each test
test.beforeEach(async ({ page, context }) => {
  // Mock geolocation for consistent map rendering
  await context.grantPermissions(['geolocation']);
  await page.setGeolocation({ latitude: 39.7392, longitude: -104.9903 });
  
  // Enable network interception for request monitoring
  await page.route('**/*', route => route.continue());
});

// Dashboard Tests
test.describe('Dashboard View', () => {
  test('should load the dashboard page', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/surveillance`);
    
    // Wait for dashboard to load
    await page.waitForSelector('.dashboard-view', { timeout: TIMEOUT });
    
    // Check for key elements
    const title = await page.textContent('h2.title');
    expect(title).toContain('Bird Flu Surveillance');
    
    // Check for map
    const mapExists = await page.isVisible('.map-container');
    expect(mapExists).toBeTruthy();
    
    // Check for summary cards
    const cardCount = await page.locator('.summary-card').count();
    expect(cardCount).toBeGreaterThanOrEqual(4);
  });
  
  test('should fetch and display API data correctly', async ({ page }) => {
    // Monitor network requests to the API
    let apiRequestReceived = false;
    await page.route(`${API_URL}/api/dashboard*`, route => {
      apiRequestReceived = true;
      route.continue();
    });
    
    await page.goto(`${HMS_MFE_URL}/aphis/surveillance`);
    await page.waitForSelector('.dashboard-view', { timeout: TIMEOUT });
    
    // Verify API request was made
    expect(apiRequestReceived).toBeTruthy();
    
    // Check for data rendering
    await page.waitForSelector('.recent-outbreaks', { timeout: TIMEOUT });
    const outbreakCount = await page.locator('.recent-outbreaks tr').count();
    expect(outbreakCount).toBeGreaterThan(1);
  });
  
  test('should enable federation data sharing', async ({ page }) => {
    // Monitor federation requests
    let federationRequestReceived = false;
    await page.route(`${FEDERATION_URL}/api/federation*`, route => {
      federationRequestReceived = true;
      route.continue();
    });
    
    await page.goto(`${HMS_MFE_URL}/aphis/surveillance`);
    
    // Wait for dashboard and click federation button
    await page.waitForSelector('button:has-text("Federation")', { timeout: TIMEOUT });
    await page.click('button:has-text("Federation")');
    
    // Select CDC data source
    await page.waitForSelector('text=CDC (Human Health)', { timeout: TIMEOUT });
    await page.check('text=CDC (Human Health)');
    
    // Apply federation settings
    await page.click('button:has-text("Apply Settings")');
    
    // Verify federation request
    expect(federationRequestReceived).toBeTruthy();
    
    // Check for federation indicator
    await page.waitForSelector('text=Federated data from', { timeout: TIMEOUT });
    const federationText = await page.textContent('text=Federated data from');
    expect(federationText).toContain('aphis');
    expect(federationText).toContain('cdc');
  });
  
  test('should filter dashboard data correctly', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/surveillance`);
    
    // Wait for dashboard and click filter button
    await page.waitForSelector('button:has-text("Filter")', { timeout: TIMEOUT });
    await page.click('button:has-text("Filter")');
    
    // Select H5N1 subtype
    await page.waitForSelector('text=Virus Subtype', { timeout: TIMEOUT });
    await page.selectOption('select[aria-label="Virus Subtype"]', 'H5N1');
    
    // Apply filters
    await page.click('button:has-text("Apply Filters")');
    
    // Wait for filter to apply
    await page.waitForResponse(resp => 
      resp.url().includes('/api/dashboard') && resp.status() === 200, 
      { timeout: TIMEOUT }
    );
    
    // Check for filtered results
    await page.waitForSelector('.recent-outbreaks', { timeout: TIMEOUT });
    
    // Get all subtype cells
    const subtypeCells = await page.$$eval('.recent-outbreaks td:nth-child(3)', 
      cells => cells.map(cell => cell.textContent)
    );
    
    // Verify all visible outbreaks are H5N1
    for (const cell of subtypeCells) {
      expect(cell).toContain('H5N1');
    }
  });
});

// Genetic Analysis Tests
test.describe('Genetic Analysis View', () => {
  test('should load the genetic analysis page', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/genetic`);
    
    // Wait for page to load
    await page.waitForSelector('.sequence-analysis', { timeout: TIMEOUT });
    
    // Check for key elements
    const title = await page.textContent('h2.title');
    expect(title).toContain('Genetic Sequence Analysis');
    
    // Check for input form
    const formExists = await page.isVisible('textarea');
    expect(formExists).toBeTruthy();
  });
  
  test('should analyze sequence data correctly', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/genetic`);
    
    // Wait for page to load and click demo button
    await page.waitForSelector('button:has-text("Load Demo Data")', { timeout: TIMEOUT });
    await page.click('button:has-text("Load Demo Data")');
    
    // Check that sequence data was loaded
    const sequenceContent = await page.inputValue('textarea');
    expect(sequenceContent.length).toBeGreaterThan(100);
    
    // Click analyze button
    await page.click('button:has-text("Analyze Sequence")');
    
    // Wait for analysis to complete
    await page.waitForResponse(resp => 
      resp.url().includes('/api/genetic/sequence') && resp.status() === 200, 
      { timeout: TIMEOUT }
    );
    
    // Check for results tabs
    await page.waitForSelector('.v-tabs', { timeout: TIMEOUT });
    const tabCount = await page.locator('.v-tabs li').count();
    expect(tabCount).toBeGreaterThanOrEqual(4);
    
    // Check mutations tab
    const mutationsVisible = await page.isVisible('text=Detected Mutations');
    expect(mutationsVisible).toBeTruthy();
    
    // Check mutation count
    const mutationText = await page.textContent('text=mutations identified');
    const count = parseInt(mutationText.match(/(\d+)\s+mutations/)[1]);
    expect(count).toBeGreaterThan(0);
  });
  
  test('should display all analysis tabs correctly', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/genetic`);
    
    // Load demo data and analyze
    await page.waitForSelector('button:has-text("Load Demo Data")', { timeout: TIMEOUT });
    await page.click('button:has-text("Load Demo Data")');
    await page.click('button:has-text("Analyze Sequence")');
    
    // Wait for analysis to complete
    await page.waitForSelector('.v-tabs', { timeout: TIMEOUT });
    
    // Check each tab
    const tabs = ['Mutations', 'Lineage', 'Antigenic Properties', 'Zoonotic Risk'];
    for (let i = 0; i < tabs.length; i++) {
      // Click tab
      await page.click(`text=${tabs[i]}`);
      
      // Wait for tab content
      await page.waitForSelector(`.${tabs[i].toLowerCase().replace(' ', '-')}-tab`, 
        { timeout: TIMEOUT }
      );
      
      // Verify tab content is visible
      const tabVisible = await page.isVisible(`.${tabs[i].toLowerCase().replace(' ', '-')}-tab`);
      expect(tabVisible).toBeTruthy();
    }
  });
});

// Transmission Analysis Tests
test.describe('Transmission Network View', () => {
  test('should load the transmission network page', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/transmission`);
    
    // Wait for page to load
    await page.waitForSelector('.transmission-network-view', { timeout: TIMEOUT });
    
    // Check for key elements
    const title = await page.textContent('h2.title');
    expect(title).toContain('Transmission Network');
    
    // Check for parameter controls
    const controlsExist = await page.isVisible('text=Temporal Window');
    expect(controlsExist).toBeTruthy();
  });
  
  test('should analyze transmission network correctly', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/transmission`);
    
    // Wait for page to load and click demo button
    await page.waitForSelector('button:has-text("Load Demo Data")', { timeout: TIMEOUT });
    await page.click('button:has-text("Load Demo Data")');
    
    // Click analyze button
    await page.click('button:has-text("Analyze Network")');
    
    // Wait for analysis to complete
    await page.waitForResponse(resp => 
      resp.url().includes('/api/genetic/transmission-dynamics') && resp.status() === 200, 
      { timeout: TIMEOUT }
    );
    
    // Check for network visualization
    await page.waitForSelector('.network-container', { timeout: TIMEOUT });
    const networkVisible = await page.isVisible('.network-container');
    expect(networkVisible).toBeTruthy();
    
    // Check for pattern assessment
    const patternVisible = await page.isVisible('text=Transmission Pattern');
    expect(patternVisible).toBeTruthy();
    
    // Check for recommendations
    const recommendationsVisible = await page.isVisible('text=Recommended Interventions');
    expect(recommendationsVisible).toBeTruthy();
  });
  
  test('should update parameters and recalculate network', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/transmission`);
    
    // Load demo data
    await page.waitForSelector('button:has-text("Load Demo Data")', { timeout: TIMEOUT });
    await page.click('button:has-text("Load Demo Data")');
    
    // Modify parameters
    await page.fill('input[aria-label="Temporal Window (days)"]', '15');
    await page.fill('input[aria-label="Spatial Threshold (km)"]', '75');
    
    // Click analyze button
    await page.click('button:has-text("Analyze Network")');
    
    // Wait for analysis to complete
    await page.waitForResponse(resp => 
      resp.url().includes('/api/genetic/transmission-dynamics') && resp.status() === 200, 
      { timeout: TIMEOUT }
    );
    
    // Verify updated parameters in request
    const requests = page.requests();
    const transmissionRequest = requests.find(req => 
      req.url().includes('/api/genetic/transmission-dynamics') && req.method() === 'POST'
    );
    
    const postData = JSON.parse(transmissionRequest.postData());
    expect(postData.temporal_window).toBe(15);
    expect(postData.spatial_threshold).toBe(75);
  });
});

// Federation Integration Tests
test.describe('Federation Integration', () => {
  test('should fetch available agencies from federation hub', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/surveillance`);
    
    // Monitor federation requests
    const federationRequests = [];
    await page.route(`${FEDERATION_URL}/api/federation/agencies`, route => {
      federationRequests.push(route.request());
      route.continue();
    });
    
    // Click federation button
    await page.waitForSelector('button:has-text("Federation")', { timeout: TIMEOUT });
    await page.click('button:has-text("Federation")');
    
    // Wait for agencies to load
    await page.waitForSelector('text=CDC (Human Health)', { timeout: TIMEOUT });
    
    // Verify federation request was made
    expect(federationRequests.length).toBeGreaterThan(0);
    
    // Check that all expected agencies are displayed
    const agencies = ['APHIS', 'CDC', 'EPA', 'FEMA'];
    for (const agency of agencies) {
      const agencyVisible = await page.isVisible(`text=${agency}`);
      expect(agencyVisible).toBeTruthy();
    }
  });
  
  test('should combine data from multiple agencies', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/surveillance`);
    
    // Monitor federation requests
    let federationDataRequest = null;
    await page.route(`${FEDERATION_URL}/api/federation/dashboard*`, route => {
      federationDataRequest = route.request();
      route.continue();
    });
    
    // Click federation button
    await page.waitForSelector('button:has-text("Federation")', { timeout: TIMEOUT });
    await page.click('button:has-text("Federation")');
    
    // Select multiple agencies
    await page.check('text=CDC (Human Health)');
    await page.check('text=EPA (Environmental)');
    
    // Apply federation settings
    await page.click('button:has-text("Apply Settings")');
    
    // Wait for federation data to load
    await page.waitForResponse(resp => 
      resp.url().includes('/api/federation/dashboard') && resp.status() === 200, 
      { timeout: TIMEOUT }
    );
    
    // Verify federation request parameters
    expect(federationDataRequest).toBeTruthy();
    const url = new URL(federationDataRequest.url());
    const agencies = url.searchParams.get('agencies').split(',');
    expect(agencies).toContain('aphis');
    expect(agencies).toContain('cdc');
    expect(agencies).toContain('epa');
    
    // Check for federation indicator
    const federationText = await page.textContent('text=Federated data from');
    expect(federationText).toContain('aphis');
    expect(federationText).toContain('cdc');
    expect(federationText).toContain('epa');
  });
});

// HMS-MFE Integration Tests
test.describe('HMS-MFE Integration', () => {
  test('should navigate between HMS-MFE routes correctly', async ({ page }) => {
    // Start at dashboard
    await page.goto(`${HMS_MFE_URL}/aphis/surveillance`);
    await page.waitForSelector('.dashboard-view', { timeout: TIMEOUT });
    
    // Navigate to genetic analysis
    await page.click('a[href="/aphis/genetic"]');
    await page.waitForSelector('.sequence-analysis', { timeout: TIMEOUT });
    
    // Verify correct component loaded
    const geneticTitle = await page.textContent('h2.title');
    expect(geneticTitle).toContain('Genetic Sequence Analysis');
    
    // Navigate to transmission analysis
    await page.click('a[href="/aphis/transmission"]');
    await page.waitForSelector('.transmission-network-view', { timeout: TIMEOUT });
    
    // Verify correct component loaded
    const transmissionTitle = await page.textContent('h2.title');
    expect(transmissionTitle).toContain('Transmission Network');
    
    // Navigate back to dashboard
    await page.click('a[href="/aphis/surveillance"]');
    await page.waitForSelector('.dashboard-view', { timeout: TIMEOUT });
    
    // Verify correct component loaded
    const dashboardTitle = await page.textContent('h2.title');
    expect(dashboardTitle).toContain('Bird Flu Surveillance');
  });
  
  test('should integrate with HMS-MFE styles correctly', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/surveillance`);
    
    // Check for HMS-MFE style classes
    const hasMfeClasses = await page.evaluate(() => {
      const elements = document.querySelectorAll('.vuero-card, .is-navbar, .is-sidebar');
      return elements.length > 0;
    });
    
    expect(hasMfeClasses).toBeTruthy();
    
    // Check for consistent styling
    const stylesConsistent = await page.evaluate(() => {
      // Get computed styles for HMS-MFE elements
      const getStyleProperty = (selector, property) => {
        const element = document.querySelector(selector);
        if (!element) return null;
        return window.getComputedStyle(element).getPropertyValue(property);
      };
      
      // Check primary color consistency
      const primaryColor = getStyleProperty('.is-primary', 'background-color');
      const primaryButtonColor = getStyleProperty('button.is-primary', 'background-color');
      
      // Check font consistency
      const bodyFont = getStyleProperty('body', 'font-family');
      const buttonFont = getStyleProperty('button', 'font-family');
      
      return {
        colorMatch: primaryColor === primaryButtonColor,
        fontMatch: bodyFont === buttonFont
      };
    });
    
    expect(stylesConsistent.colorMatch).toBeTruthy();
    expect(stylesConsistent.fontMatch).toBeTruthy();
  });
});