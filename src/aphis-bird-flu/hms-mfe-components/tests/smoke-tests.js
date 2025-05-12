/**
 * Smoke Tests for APHIS Bird Flu HMS-MFE Components
 * 
 * These are lightweight tests that are run after deployment to verify 
 * that the application is functioning properly in the deployed environment.
 */

const { test, expect } = require('@playwright/test');

// Configuration
const HMS_MFE_URL = process.env.HMS_MFE_URL || 'http://localhost:3000';
const API_URL = process.env.API_URL || 'http://localhost:8000';
const FEDERATION_URL = process.env.FEDERATION_URL || 'http://localhost:9000';

// Test timeouts - shorter for smoke tests
const TIMEOUT = 15000;

// Basic availability checks
test.describe('Smoke Tests', () => {
  test('application loads and returns 200', async ({ page }) => {
    const response = await page.goto(HMS_MFE_URL);
    expect(response.status()).toBe(200);
    
    // Check for basic structure
    await page.waitForSelector('header', { timeout: TIMEOUT });
    await page.waitForSelector('footer', { timeout: TIMEOUT });
    
    // Title should contain APHIS
    const title = await page.title();
    expect(title).toContain('APHIS');
  });
  
  test('dashboard component loads', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/surveillance`);
    
    // Check for dashboard content
    await page.waitForSelector('.dashboard-view', { timeout: TIMEOUT });
    
    // Check for map component
    await page.waitForSelector('.map-container', { timeout: TIMEOUT });
  });
  
  test('genetic analysis component loads', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/genetic`);
    
    // Check for sequence analysis form
    await page.waitForSelector('.sequence-analysis', { timeout: TIMEOUT });
    await page.waitForSelector('textarea', { timeout: TIMEOUT });
    
    // Check for analysis button
    const buttonText = await page.textContent('button');
    expect(buttonText).toContain('Analyze');
  });
  
  test('transmission network component loads', async ({ page }) => {
    await page.goto(`${HMS_MFE_URL}/aphis/transmission`);
    
    // Check for network view
    await page.waitForSelector('.transmission-network-view', { timeout: TIMEOUT });
    
    // Check for parameter controls
    await page.waitForSelector('input[aria-label="Temporal Window (days)"]', { timeout: TIMEOUT });
  });
  
  test('basic API connectivity', async ({ page }) => {
    // Monitor API requests
    let apiRequestReceived = false;
    let apiResponseStatus = 0;
    
    await page.route(`${API_URL}/api/dashboard*`, route => {
      apiRequestReceived = true;
      apiResponseStatus = route.request().response()?.status() || 0;
      route.continue();
    });
    
    await page.goto(`${HMS_MFE_URL}/aphis/surveillance`);
    await page.waitForSelector('.dashboard-view', { timeout: TIMEOUT });
    
    // Wait for API request to complete
    await page.waitForTimeout(2000);
    
    expect(apiRequestReceived).toBeTruthy();
    expect(apiResponseStatus).toBe(200);
  });
  
  test('federation hub connectivity', async ({ page }) => {
    // Monitor federation requests
    let federationRequestReceived = false;
    
    await page.route(`${FEDERATION_URL}/api/federation*`, route => {
      federationRequestReceived = true;
      route.continue();
    });
    
    await page.goto(`${HMS_MFE_URL}/aphis/surveillance`);
    
    // Click federation button
    await page.waitForSelector('button:has-text("Federation")', { timeout: TIMEOUT });
    await page.click('button:has-text("Federation")');
    
    // Wait for agency list to load
    await page.waitForSelector('text=CDC (Human Health)', { timeout: TIMEOUT });
    
    expect(federationRequestReceived).toBeTruthy();
  });
  
  test('health endpoint returns 200', async ({ request }) => {
    const healthResponse = await request.get(`${HMS_MFE_URL}/health`);
    expect(healthResponse.ok()).toBeTruthy();
    
    const data = await healthResponse.json();
    expect(data.status).toBe('ok');
  });
});

// Navigation check
test.describe('Navigation', () => {
  test('navigation works between components', async ({ page }) => {
    // Start at dashboard
    await page.goto(`${HMS_MFE_URL}/aphis/surveillance`);
    await page.waitForSelector('.dashboard-view', { timeout: TIMEOUT });
    
    // Navigate to genetic analysis
    await page.click('a[href="/aphis/genetic"]');
    await page.waitForSelector('.sequence-analysis', { timeout: TIMEOUT });
    
    // Navigate to transmission network
    await page.click('a[href="/aphis/transmission"]');
    await page.waitForSelector('.transmission-network-view', { timeout: TIMEOUT });
    
    // Navigate back to dashboard
    await page.click('a[href="/aphis/surveillance"]');
    await page.waitForSelector('.dashboard-view', { timeout: TIMEOUT });
  });
});