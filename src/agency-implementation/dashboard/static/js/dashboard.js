/**
 * Bird Flu Interagency Dashboard
 * JavaScript for data fetching, processing, and visualization
 */

// Configuration
const config = {
    refreshInterval: 5 * 60 * 1000, // 5 minutes
    timeRange: 30, // Default to 30 days
    apiEndpoints: {
        summary: '/api/summary',
        cdcCases: '/api/cdc/cases',
        epaAirQuality: '/api/epa/air_quality',
        femaResources: '/api/fema/resources',
        correlation: '/api/correlation',
        caseMap: '/api/case_map',
        subtypeDistribution: '/api/subtype_distribution',
        airQualityTrends: '/api/air_quality_trends',
        resourceAllocation: '/api/resource_allocation',
        correlationChart: '/api/correlation_chart'
    }
};

// State
let dashboardState = {
    lastRefresh: null,
    timeRange: config.timeRange,
    apiStatus: {
        cdc: { status: 'unknown', lastUpdated: null },
        epa: { status: 'unknown', lastUpdated: null },
        fema: { status: 'unknown', lastUpdated: null }
    }
};

// Main initialization function
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing dashboard...');
    initializeTimeRangeSelector();
    loadDashboardData();
    
    // Set up auto-refresh
    setInterval(loadDashboardData, config.refreshInterval);
});

// Initialize time range selector
function initializeTimeRangeSelector() {
    const timeRangeLinks = document.querySelectorAll('.time-range');
    
    timeRangeLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update active status
            timeRangeLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Update dropdown button text
            const days = parseInt(this.dataset.days);
            document.getElementById('timeRangeDropdown').textContent = `Last ${days} Days`;
            
            // Update state and reload data
            dashboardState.timeRange = days;
            loadDashboardData();
        });
    });
}

// Main function to load all dashboard data
function loadDashboardData() {
    console.log('Loading dashboard data...');
    dashboardState.lastRefresh = new Date();
    
    // Update refresh timestamp
    document.getElementById('dashboard-refreshed').textContent = formatDateTime(dashboardState.lastRefresh);
    
    // Load data from APIs
    loadSummaryData();
    loadCaseMap();
    loadSubtypeDistribution();
    loadAirQualityTrends();
    loadResourceAllocation();
    loadCorrelationChart();
}

// Load summary statistics
function loadSummaryData() {
    fetch(config.apiEndpoints.summary)
        .then(response => response.json())
        .then(data => {
            updateSummaryCards(data);
            updateApiStatus(data.timestamp);
        })
        .catch(error => {
            console.error('Error loading summary data:', error);
            showErrorMessage('summary', error);
        });
}

// Update summary cards with data
function updateSummaryCards(data) {
    // CDC Health Data
    const cdcSummary = data.health;
    if (cdcSummary.error) {
        document.getElementById('cdc-summary').innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i> ${cdcSummary.error}
            </div>
        `;
    } else {
        let subtypeHtml = '';
        if (cdcSummary.by_subtype) {
            subtypeHtml = '<div class="mt-3"><h6>Cases by Subtype:</h6><ul class="list-group">';
            for (const [subtype, count] of Object.entries(cdcSummary.by_subtype)) {
                subtypeHtml += `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        ${subtype}
                        <span class="badge bg-primary rounded-pill">${count}</span>
                    </li>
                `;
            }
            subtypeHtml += '</ul></div>';
        }
        
        document.getElementById('cdc-summary').innerHTML = `
            <div class="metrics-container">
                <div class="metric-box bg-light">
                    <div class="metric-value text-primary">${cdcSummary.total_cases || 0}</div>
                    <div class="metric-label">Total Cases</div>
                </div>
                <div class="metric-box bg-light">
                    <div class="metric-value text-danger">${cdcSummary.human_cases || 0}</div>
                    <div class="metric-label">Human Cases</div>
                </div>
                <div class="metric-box bg-light">
                    <div class="metric-value text-success">${cdcSummary.bird_cases || 0}</div>
                    <div class="metric-label">Bird Cases</div>
                </div>
            </div>
            ${subtypeHtml}
        `;
    }
    
    // EPA Environmental Data
    const epaSummary = data.environmental;
    if (epaSummary.error) {
        document.getElementById('epa-summary').innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i> ${epaSummary.error}
            </div>
        `;
    } else {
        let airQualityHtml = '';
        if (epaSummary.air_quality_ratings) {
            airQualityHtml = '<div class="mt-3"><h6>Air Quality Ratings:</h6><ul class="list-group">';
            for (const [rating, count] of Object.entries(epaSummary.air_quality_ratings)) {
                // Determine color based on rating
                let badgeClass = 'bg-secondary';
                if (rating === 'good') badgeClass = 'bg-success';
                else if (rating === 'moderate') badgeClass = 'bg-warning';
                else if (rating === 'unhealthy') badgeClass = 'bg-danger';
                
                airQualityHtml += `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        ${rating.charAt(0).toUpperCase() + rating.slice(1)}
                        <span class="badge ${badgeClass} rounded-pill">${count}</span>
                    </li>
                `;
            }
            airQualityHtml += '</ul></div>';
        }
        
        document.getElementById('epa-summary').innerHTML = `
            <div class="metrics-container">
                <div class="metric-box bg-light">
                    <div class="metric-value text-success">${epaSummary.monitoring_sites || 0}</div>
                    <div class="metric-label">Monitoring Sites</div>
                </div>
            </div>
            ${airQualityHtml}
        `;
    }
    
    // FEMA Response Data
    const femaSummary = data.emergency;
    if (femaSummary.error) {
        document.getElementById('fema-summary').innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i> ${femaSummary.error}
            </div>
        `;
    } else {
        document.getElementById('fema-summary').innerHTML = `
            <div class="metrics-container">
                <div class="metric-box bg-light">
                    <div class="metric-value text-danger">${femaSummary.active_deployments || 0}</div>
                    <div class="metric-label">Active Deployments</div>
                </div>
                <div class="metric-box bg-light">
                    <div class="metric-value text-warning">${femaSummary.resources_deployed || 0}</div>
                    <div class="metric-label">Resources Deployed</div>
                </div>
                <div class="metric-box bg-light">
                    <div class="metric-value text-info">${femaSummary.regions_covered || 0}</div>
                    <div class="metric-label">Regions Covered</div>
                </div>
            </div>
            <div class="alert alert-info mt-3">
                <i class="bi bi-info-circle"></i> Emergency response resources have been deployed to all affected regions.
            </div>
        `;
    }
}

// Load case map visualization
function loadCaseMap() {
    fetch(`${config.apiEndpoints.caseMap}?days=${dashboardState.timeRange}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('case-map-container').innerHTML = `
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i> ${data.error}
                    </div>
                `;
            } else {
                document.getElementById('case-map-container').innerHTML = `
                    <img src="data:image/png;base64,${data.image}" class="img-fluid chart-img" alt="Bird Flu Case Distribution Map">
                `;
            }
        })
        .catch(error => {
            console.error('Error loading case map:', error);
            showErrorMessage('case-map-container', error);
        });
}

// Load subtype distribution visualization
function loadSubtypeDistribution() {
    fetch(`${config.apiEndpoints.subtypeDistribution}?days=${dashboardState.timeRange}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('subtype-distribution-container').innerHTML = `
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i> ${data.error}
                    </div>
                `;
            } else {
                document.getElementById('subtype-distribution-container').innerHTML = `
                    <img src="data:image/png;base64,${data.image}" class="img-fluid chart-img" alt="Virus Subtype Distribution">
                `;
            }
        })
        .catch(error => {
            console.error('Error loading subtype distribution:', error);
            showErrorMessage('subtype-distribution-container', error);
        });
}

// Load air quality trends visualization
function loadAirQualityTrends() {
    fetch(`${config.apiEndpoints.airQualityTrends}?days=${dashboardState.timeRange}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('air-quality-container').innerHTML = `
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i> ${data.error}
                    </div>
                `;
            } else {
                document.getElementById('air-quality-container').innerHTML = `
                    <img src="data:image/png;base64,${data.image}" class="img-fluid chart-img" alt="Air Quality Trends">
                `;
            }
        })
        .catch(error => {
            console.error('Error loading air quality trends:', error);
            showErrorMessage('air-quality-container', error);
        });
}

// Load resource allocation visualization
function loadResourceAllocation() {
    fetch(`${config.apiEndpoints.resourceAllocation}?days=${dashboardState.timeRange}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('resource-allocation-container').innerHTML = `
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i> ${data.error}
                    </div>
                `;
            } else {
                document.getElementById('resource-allocation-container').innerHTML = `
                    <img src="data:image/png;base64,${data.image}" class="img-fluid chart-img" alt="Emergency Resource Allocation">
                `;
            }
        })
        .catch(error => {
            console.error('Error loading resource allocation:', error);
            showErrorMessage('resource-allocation-container', error);
        });
}

// Load correlation chart visualization
function loadCorrelationChart() {
    fetch(`${config.apiEndpoints.correlationChart}?days=${dashboardState.timeRange}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('correlation-container').innerHTML = `
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i> ${data.error}
                    </div>
                `;
            } else {
                document.getElementById('correlation-container').innerHTML = `
                    <img src="data:image/png;base64,${data.image}" class="img-fluid chart-img" alt="Health-Environment Correlation">
                `;
            }
        })
        .catch(error => {
            console.error('Error loading correlation chart:', error);
            showErrorMessage('correlation-container', error);
        });
}

// Update API status indicators
function updateApiStatus(timestamp) {
    // For demo purposes, set all to success
    document.getElementById('cdc-last-updated').textContent = formatDateTime(new Date(timestamp));
    document.getElementById('epa-last-updated').textContent = formatDateTime(new Date(timestamp));
    document.getElementById('fema-last-updated').textContent = formatDateTime(new Date(timestamp));
    
    // Update state
    dashboardState.apiStatus.cdc = { status: 'success', lastUpdated: new Date(timestamp) };
    dashboardState.apiStatus.epa = { status: 'success', lastUpdated: new Date(timestamp) };
    dashboardState.apiStatus.fema = { status: 'success', lastUpdated: new Date(timestamp) };
}

// Helper function to show error message
function showErrorMessage(containerId, error) {
    document.getElementById(containerId).innerHTML = `
        <div class="alert alert-danger">
            <i class="bi bi-exclamation-circle"></i> Error loading data: ${error.message || 'Unknown error'}
        </div>
    `;
}

// Helper function to format date/time
function formatDateTime(date) {
    if (!date) return '--';
    
    // Use Moment.js if available
    if (typeof moment !== 'undefined') {
        return moment(date).format('MMM D, YYYY HH:mm:ss');
    }
    
    // Fallback to native formatting
    return new Date(date).toLocaleString();
}