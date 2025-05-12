import { EventEmitter } from 'events';
import { 
  EconomicIndicator, 
  StagflationAnalysisModel,
  StagflationAnalysisService
} from './stagflation_analysis';
import { ThresholdConfig } from './types';

/**
 * Economic health status level enum
 */
export enum HealthStatus {
  EXCELLENT = 'excellent',
  GOOD = 'good',
  MODERATE = 'moderate',
  CONCERNING = 'concerning',
  CRITICAL = 'critical'
}

/**
 * Economic indicator category
 */
export enum IndicatorCategory {
  INFLATION = 'inflation',
  EMPLOYMENT = 'employment',
  GROWTH = 'growth',
  FINANCIAL = 'financial',
  CONSUMER = 'consumer',
  GOVERNMENT = 'government',
  TRADE = 'trade'
}

/**
 * Economic indicator frequency
 */
export enum IndicatorFrequency {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  ANNUALLY = 'annually'
}

/**
 * Interface for economic indicator trend
 */
export interface IndicatorTrend {
  direction: 'increasing' | 'decreasing' | 'stable';
  magnitude: number; // 0-1 scale of change magnitude
  percentChange: number; // Percent change over the period
  volatility: number; // 0-1 scale of volatility
  periodCount: number; // Number of periods used in analysis
}

/**
 * Economic health indicator with metadata
 */
export interface HealthIndicator {
  id: string;
  name: string;
  category: IndicatorCategory;
  frequency: IndicatorFrequency;
  currentValue: number;
  unit: string; 
  trend: IndicatorTrend;
  historicalData: Array<{ date: string; value: number }>; // Most recent periods
  status: HealthStatus;
  healthScore: number; // 0-100 score
  lastUpdated: string; // ISO date
  source?: string;
  description?: string;
  targetValue?: number;
  targetRange?: { min: number; max: number };
  alertThresholds?: ThresholdConfig;
}

/**
 * Represents the overall economic health
 */
export interface EconomicHealth {
  timestamp: string; // ISO date
  overallStatus: HealthStatus;
  compositeScore: number; // 0-100 score
  indicators: Record<string, HealthIndicator>;
  categories: Record<IndicatorCategory, {
    status: HealthStatus;
    score: number;
    indicators: string[]; // IDs of indicators in this category
  }>;
  alerts: Array<{
    severity: 'info' | 'warning' | 'critical';
    indicator: string;
    message: string;
    thresholdBreached?: { value: number; threshold: number };
    timestamp: string;
  }>;
  stagflationRisk: {
    score: number; // 0-1 probability
    status: HealthStatus;
    components: {
      inflation: number;
      unemployment: number;
      growth: number;
    }
  };
  summary: string;
  recommendations: Array<{
    area: string;
    action: string;
    urgency: 'low' | 'medium' | 'high';
    rationale: string;
  }>;
}

/**
 * Alert notification from the economic health monitor
 */
export interface HealthAlert {
  id: string;
  timestamp: string;
  severity: 'info' | 'warning' | 'critical';
  indicator: HealthIndicator;
  message: string;
  thresholdBreached?: { value: number; threshold: number };
  recommendedActions?: string[];
}

/**
 * Options for the economic health monitor
 */
export interface EconomicHealthMonitorOptions {
  pollingInterval?: number; // Milliseconds, default 24 hours
  alertThresholds?: Record<string, ThresholdConfig>;
  categoryWeights?: Record<IndicatorCategory, number>;
  stagflationAnalysisEnabled?: boolean;
  persistenceEnabled?: boolean;
  historyLength?: number; // Number of health snapshots to keep
}

/**
 * Monitor the overall health of the economic system by tracking a diverse set of 
 * economic indicators, analyzing trends, and providing alerts when indicators
 * breach defined thresholds.
 */
export class EconomicHealthMonitor extends EventEmitter {
  private indicators: Map<string, HealthIndicator> = new Map();
  private healthHistory: EconomicHealth[] = [];
  private alertHistory: HealthAlert[] = [];
  private isInitialized: boolean = false;
  private pollingInterval: number = 86400000; // Default to daily
  private pollingTimer?: NodeJS.Timeout;
  private alertThresholds: Record<string, ThresholdConfig> = {};
  private categoryWeights: Record<IndicatorCategory, number> = {
    [IndicatorCategory.INFLATION]: 0.2,
    [IndicatorCategory.EMPLOYMENT]: 0.2,
    [IndicatorCategory.GROWTH]: 0.2,
    [IndicatorCategory.FINANCIAL]: 0.1,
    [IndicatorCategory.CONSUMER]: 0.1,
    [IndicatorCategory.GOVERNMENT]: 0.1,
    [IndicatorCategory.TRADE]: 0.1
  };
  private stagflationAnalysisEnabled: boolean = true;
  private stagflationAnalysisService?: StagflationAnalysisService;
  private persistenceEnabled: boolean = false;
  private historyLength: number = 100;
  
  /**
   * Create a new economic health monitor
   */
  constructor(options?: EconomicHealthMonitorOptions) {
    super();
    if (options) {
      if (options.pollingInterval) this.pollingInterval = options.pollingInterval;
      if (options.alertThresholds) this.alertThresholds = options.alertThresholds;
      if (options.categoryWeights) this.categoryWeights = options.categoryWeights;
      if (options.stagflationAnalysisEnabled !== undefined) {
        this.stagflationAnalysisEnabled = options.stagflationAnalysisEnabled;
      }
      if (options.persistenceEnabled !== undefined) {
        this.persistenceEnabled = options.persistenceEnabled;
      }
      if (options.historyLength) this.historyLength = options.historyLength;
    }
  }
  
  /**
   * Initialize the economic health monitor
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) return;
    
    // Initialize stagflation analysis if enabled
    if (this.stagflationAnalysisEnabled) {
      this.stagflationAnalysisService = new StagflationAnalysisService();
      await this.stagflationAnalysisService.initialize();
    }
    
    // Load saved indicators and health history if persistence is enabled
    if (this.persistenceEnabled) {
      await this.loadPersistedData();
    }
    
    this.isInitialized = true;
    
    // Start polling
    this.startPolling();
    
    this.emit('initialized');
  }
  
  /**
   * Add or update an economic health indicator
   */
  public addIndicator(indicator: Partial<HealthIndicator> & { id: string; currentValue: number }): void {
    if (!this.isInitialized) {
      throw new Error('EconomicHealthMonitor must be initialized before adding indicators');
    }
    
    const existingIndicator = this.indicators.get(indicator.id);
    
    // Create a new indicator or update the existing one
    const newIndicator: HealthIndicator = {
      id: indicator.id,
      name: indicator.name || existingIndicator?.name || indicator.id,
      category: indicator.category || existingIndicator?.category || IndicatorCategory.GROWTH,
      frequency: indicator.frequency || existingIndicator?.frequency || IndicatorFrequency.MONTHLY,
      currentValue: indicator.currentValue,
      unit: indicator.unit || existingIndicator?.unit || '',
      trend: indicator.trend || existingIndicator?.trend || {
        direction: 'stable',
        magnitude: 0,
        percentChange: 0,
        volatility: 0,
        periodCount: 1
      },
      historicalData: indicator.historicalData || existingIndicator?.historicalData || [],
      status: indicator.status || existingIndicator?.status || HealthStatus.MODERATE,
      healthScore: indicator.healthScore || existingIndicator?.healthScore || 50,
      lastUpdated: new Date().toISOString(),
      source: indicator.source || existingIndicator?.source,
      description: indicator.description || existingIndicator?.description,
      targetValue: indicator.targetValue || existingIndicator?.targetValue,
      targetRange: indicator.targetRange || existingIndicator?.targetRange,
      alertThresholds: indicator.alertThresholds || existingIndicator?.alertThresholds || this.alertThresholds[indicator.id]
    };
    
    // Add current value to historical data if not already present
    const currentDate = new Date().toISOString().split('T')[0];
    if (!newIndicator.historicalData.some(d => d.date.startsWith(currentDate))) {
      newIndicator.historicalData.unshift({
        date: currentDate,
        value: newIndicator.currentValue
      });
      
      // Limit the size of historical data
      if (newIndicator.historicalData.length > 100) {
        newIndicator.historicalData = newIndicator.historicalData.slice(0, 100);
      }
    }
    
    // Calculate trend if there's enough historical data
    if (newIndicator.historicalData.length > 1) {
      newIndicator.trend = this.calculateTrend(newIndicator.historicalData);
    }
    
    // Calculate health status and score
    const healthAssessment = this.assessIndicatorHealth(newIndicator);
    newIndicator.status = healthAssessment.status;
    newIndicator.healthScore = healthAssessment.score;
    
    // Check for threshold breaches and emit alerts
    this.checkThresholds(newIndicator, existingIndicator);
    
    // Update the indicator map
    this.indicators.set(indicator.id, newIndicator);
    
    // Update economic health with new indicator
    this.updateEconomicHealth();
    
    this.emit('indicator-updated', newIndicator);
  }
  
  /**
   * Add multiple indicators at once
   */
  public addIndicators(indicators: Array<Partial<HealthIndicator> & { id: string; currentValue: number }>): void {
    indicators.forEach(indicator => this.addIndicator(indicator));
  }
  
  /**
   * Remove an indicator by ID
   */
  public removeIndicator(id: string): boolean {
    const result = this.indicators.delete(id);
    if (result) {
      this.updateEconomicHealth();
      this.emit('indicator-removed', id);
    }
    return result;
  }
  
  /**
   * Get an indicator by ID
   */
  public getIndicator(id: string): HealthIndicator | undefined {
    return this.indicators.get(id);
  }
  
  /**
   * Get all indicators
   */
  public getAllIndicators(): HealthIndicator[] {
    return Array.from(this.indicators.values());
  }
  
  /**
   * Get indicators by category
   */
  public getIndicatorsByCategory(category: IndicatorCategory): HealthIndicator[] {
    return Array.from(this.indicators.values())
      .filter(indicator => indicator.category === category);
  }
  
  /**
   * Get the current economic health
   */
  public getCurrentHealth(): EconomicHealth | undefined {
    return this.healthHistory.length > 0 ? this.healthHistory[0] : undefined;
  }
  
  /**
   * Get economic health history
   */
  public getHealthHistory(): EconomicHealth[] {
    return [...this.healthHistory];
  }
  
  /**
   * Get alert history
   */
  public getAlertHistory(): HealthAlert[] {
    return [...this.alertHistory];
  }
  
  /**
   * Force immediate health check
   */
  public async performHealthCheck(): Promise<EconomicHealth | undefined> {
    return this.updateEconomicHealth();
  }
  
  /**
   * Stop health monitoring
   */
  public stop(): void {
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
      this.pollingTimer = undefined;
    }
    this.emit('monitoring-stopped');
  }
  
  /**
   * Start or resume health monitoring
   */
  public startPolling(): void {
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
    }
    
    this.pollingTimer = setInterval(() => {
      this.updateEconomicHealth();
    }, this.pollingInterval);
    
    this.emit('monitoring-started');
  }
  
  /**
   * Set polling interval
   */
  public setPollingInterval(interval: number): void {
    this.pollingInterval = interval;
    
    // Restart polling with new interval if already running
    if (this.pollingTimer) {
      this.startPolling();
    }
  }
  
  /**
   * Load indicators and health history from persistence
   */
  private async loadPersistedData(): Promise<void> {
    // This would be implemented to load from a database or file system
    // For now, this is a placeholder
    console.log('Loading persisted economic health data...');
  }
  
  /**
   * Save current indicators and health history to persistence
   */
  private async saveData(): Promise<void> {
    if (!this.persistenceEnabled) return;
    
    // This would be implemented to save to a database or file system
    // For now, this is a placeholder
    console.log('Saving economic health data...');
  }
  
  /**
   * Calculate trend from historical data
   */
  private calculateTrend(historicalData: Array<{ date: string; value: number }>): IndicatorTrend {
    if (historicalData.length < 2) {
      return {
        direction: 'stable',
        magnitude: 0,
        percentChange: 0,
        volatility: 0,
        periodCount: historicalData.length
      };
    }
    
    // Sort data by date (newest first)
    const sortedData = [...historicalData].sort((a, b) => 
      new Date(b.date).getTime() - new Date(a.date).getTime()
    );
    
    const currentValue = sortedData[0].value;
    const previousValue = sortedData[1].value;
    
    // Calculate percent change
    const percentChange = previousValue !== 0 
      ? ((currentValue - previousValue) / Math.abs(previousValue)) * 100
      : 0;
    
    // Calculate volatility (standard deviation of percent changes)
    let volatility = 0;
    if (sortedData.length > 2) {
      const changes: number[] = [];
      for (let i = 0; i < sortedData.length - 1; i++) {
        const current = sortedData[i].value;
        const previous = sortedData[i + 1].value;
        if (previous !== 0) {
          changes.push(((current - previous) / Math.abs(previous)) * 100);
        }
      }
      
      const mean = changes.reduce((sum, val) => sum + val, 0) / changes.length;
      const squaredDiffs = changes.map(val => Math.pow(val - mean, 2));
      const variance = squaredDiffs.reduce((sum, val) => sum + val, 0) / changes.length;
      volatility = Math.sqrt(variance) / 100; // Scale to 0-1 range approximately
    }
    
    // Determine direction and magnitude
    let direction: 'increasing' | 'decreasing' | 'stable';
    if (Math.abs(percentChange) < 1) {
      direction = 'stable';
    } else {
      direction = percentChange > 0 ? 'increasing' : 'decreasing';
    }
    
    // Calculate magnitude (0-1 scale)
    const magnitude = Math.min(Math.abs(percentChange) / 20, 1); // Scale where 20% change = 1.0
    
    return {
      direction,
      magnitude,
      percentChange,
      volatility: Math.min(volatility, 1), // Cap at 1.0
      periodCount: sortedData.length
    };
  }
  
  /**
   * Assess health status and score for an indicator
   */
  private assessIndicatorHealth(indicator: HealthIndicator): { status: HealthStatus; score: number } {
    let score = 50; // Default moderate score
    
    // If we have target values, calculate score based on proximity to target
    if (indicator.targetValue !== undefined) {
      const percentDiff = Math.abs((indicator.currentValue - indicator.targetValue) / indicator.targetValue);
      score = Math.max(0, 100 - (percentDiff * 100));
    } 
    // If we have target range, score based on whether in range and how close to center
    else if (indicator.targetRange) {
      const { min, max } = indicator.targetRange;
      const value = indicator.currentValue;
      
      if (value >= min && value <= max) {
        // Within range - score based on proximity to center
        const center = (min + max) / 2;
        const rangeSize = max - min;
        const distFromCenter = Math.abs(value - center);
        const percentFromCenter = distFromCenter / (rangeSize / 2);
        score = 100 - (percentFromCenter * 50); // 100 at center, 50 at edges
      } else {
        // Outside range - score based on distance outside
        const closest = value < min ? min : max;
        const percentOutside = Math.abs(value - closest) / closest;
        score = Math.max(0, 50 - (percentOutside * 50)); // 50 at edge, lower as moves away
      }
    }
    // If we have thresholds but no target, calculate based on thresholds
    else if (indicator.alertThresholds) {
      const { warning, critical } = indicator.alertThresholds;
      
      if (warning && critical) {
        if (indicator.currentValue >= critical.min && indicator.currentValue <= critical.max) {
          score = 10; // Critical range
        } else if (indicator.currentValue >= warning.min && indicator.currentValue <= warning.max) {
          score = 30; // Warning range
        } else {
          score = 70; // Outside alert ranges
        }
      }
    }
    // Otherwise, use trend information
    else if (indicator.trend) {
      const baseTrendScore = indicator.trend.direction === 'stable' ? 50 :
        indicator.category === IndicatorCategory.INFLATION || 
        indicator.category === IndicatorCategory.EMPLOYMENT ? 
          (indicator.trend.direction === 'increasing' ? 30 : 70) : 
          (indicator.trend.direction === 'increasing' ? 70 : 30);
          
      // Adjust for volatility and magnitude
      score = baseTrendScore - (indicator.trend.volatility * 20) +
              (indicator.trend.direction === 'stable' ? 0 : 
                (indicator.trend.magnitude * 20 * (baseTrendScore > 50 ? 1 : -1)));
    }
    
    // Ensure score is within 0-100 range
    score = Math.max(0, Math.min(100, score));
    
    // Determine status based on score
    let status: HealthStatus;
    if (score >= 80) status = HealthStatus.EXCELLENT;
    else if (score >= 60) status = HealthStatus.GOOD;
    else if (score >= 40) status = HealthStatus.MODERATE;
    else if (score >= 20) status = HealthStatus.CONCERNING;
    else status = HealthStatus.CRITICAL;
    
    return { status, score };
  }
  
  /**
   * Check if indicator breaches any thresholds and emit alerts
   */
  private checkThresholds(newIndicator: HealthIndicator, oldIndicator?: HealthIndicator): void {
    const thresholds = newIndicator.alertThresholds;
    
    if (!thresholds) return;
    
    // Check for crossing into critical range
    if (thresholds.critical) {
      const { min, max } = thresholds.critical;
      const value = newIndicator.currentValue;
      
      const inCriticalRange = value >= min && value <= max;
      const wasInCriticalRange = oldIndicator ? 
        (oldIndicator.currentValue >= min && oldIndicator.currentValue <= max) : false;
      
      if (inCriticalRange && !wasInCriticalRange) {
        const threshold = value < (min + max) / 2 ? min : max;
        this.emitAlert({
          id: `${newIndicator.id}-critical-${Date.now()}`,
          timestamp: new Date().toISOString(),
          severity: 'critical',
          indicator: newIndicator,
          message: `${newIndicator.name} has entered critical range (${min}-${max})`,
          thresholdBreached: { value, threshold },
          recommendedActions: [
            'Review immediate policy responses',
            'Schedule emergency analysis meeting',
            'Prepare stakeholder communication'
          ]
        });
      }
    }
    
    // Check for crossing into warning range
    if (thresholds.warning) {
      const { min, max } = thresholds.warning;
      const value = newIndicator.currentValue;
      
      const inWarningRange = value >= min && value <= max;
      const wasInWarningRange = oldIndicator ? 
        (oldIndicator.currentValue >= min && oldIndicator.currentValue <= max) : false;
      
      // Only emit warning if not already in critical (avoids duplicate alerts)
      if (inWarningRange && !wasInWarningRange && 
          !(thresholds.critical && 
            value >= thresholds.critical.min && 
            value <= thresholds.critical.max)) {
        
        const threshold = value < (min + max) / 2 ? min : max;
        this.emitAlert({
          id: `${newIndicator.id}-warning-${Date.now()}`,
          timestamp: new Date().toISOString(),
          severity: 'warning',
          indicator: newIndicator,
          message: `${newIndicator.name} has entered warning range (${min}-${max})`,
          thresholdBreached: { value, threshold },
          recommendedActions: [
            'Monitor closely for further deterioration',
            'Review contingency plans',
            'Analyze potential impacts'
          ]
        });
      }
    }
    
    // Check for significant trend changes
    if (newIndicator.trend && oldIndicator?.trend) {
      const oldTrend = oldIndicator.trend;
      const newTrend = newIndicator.trend;
      
      // Direction change 
      if (oldTrend.direction !== newTrend.direction && 
          oldTrend.direction !== 'stable' && 
          newTrend.direction !== 'stable') {
        
        this.emitAlert({
          id: `${newIndicator.id}-trend-${Date.now()}`,
          timestamp: new Date().toISOString(),
          severity: 'info',
          indicator: newIndicator,
          message: `${newIndicator.name} trend has reversed from ${oldTrend.direction} to ${newTrend.direction}`,
          recommendedActions: [
            'Analyze potential reasons for the trend change',
            'Update forecasts and projections',
            'Consider implications for related indicators'
          ]
        });
      }
      
      // Volatility increase
      if (newTrend.volatility > oldTrend.volatility * 1.5 && newTrend.volatility > 0.3) {
        this.emitAlert({
          id: `${newIndicator.id}-volatility-${Date.now()}`,
          timestamp: new Date().toISOString(),
          severity: 'info',
          indicator: newIndicator,
          message: `${newIndicator.name} volatility has increased significantly`,
          recommendedActions: [
            'Monitor for market instability',
            'Review risk management strategies',
            'Analyze causes of increased volatility'
          ]
        });
      }
    }
  }
  
  /**
   * Emit and record an alert
   */
  private emitAlert(alert: HealthAlert): void {
    // Add to alert history
    this.alertHistory.unshift(alert);
    
    // Limit alert history size
    if (this.alertHistory.length > 100) {
      this.alertHistory = this.alertHistory.slice(0, 100);
    }
    
    // Emit event
    this.emit('alert', alert);
  }
  
  /**
   * Calculate overall economic health based on all indicators
   */
  private async updateEconomicHealth(): Promise<EconomicHealth | undefined> {
    if (this.indicators.size === 0) return undefined;
    
    const now = new Date().toISOString();
    
    // Group indicators by category
    const categorizedIndicators: Record<IndicatorCategory, HealthIndicator[]> = {
      [IndicatorCategory.INFLATION]: [],
      [IndicatorCategory.EMPLOYMENT]: [],
      [IndicatorCategory.GROWTH]: [],
      [IndicatorCategory.FINANCIAL]: [],
      [IndicatorCategory.CONSUMER]: [],
      [IndicatorCategory.GOVERNMENT]: [],
      [IndicatorCategory.TRADE]: []
    };
    
    // Collect all indicators and organize by category
    for (const indicator of this.indicators.values()) {
      categorizedIndicators[indicator.category].push(indicator);
    }
    
    // Calculate category scores and status
    const categories: Record<IndicatorCategory, {
      status: HealthStatus;
      score: number;
      indicators: string[];
    }> = {} as any;
    
    for (const category of Object.values(IndicatorCategory)) {
      const indicators = categorizedIndicators[category];
      
      if (indicators.length === 0) {
        categories[category] = {
          status: HealthStatus.MODERATE,
          score: 50,
          indicators: []
        };
        continue;
      }
      
      // Calculate average score for the category
      const totalScore = indicators.reduce((sum, ind) => sum + ind.healthScore, 0);
      const avgScore = totalScore / indicators.length;
      
      // Determine status based on score
      let status: HealthStatus;
      if (avgScore >= 80) status = HealthStatus.EXCELLENT;
      else if (avgScore >= 60) status = HealthStatus.GOOD;
      else if (avgScore >= 40) status = HealthStatus.MODERATE;
      else if (avgScore >= 20) status = HealthStatus.CONCERNING;
      else status = HealthStatus.CRITICAL;
      
      categories[category] = {
        status,
        score: avgScore,
        indicators: indicators.map(i => i.id)
      };
    }
    
    // Calculate composite score with category weights
    let weightedScore = 0;
    let totalWeight = 0;
    
    for (const category of Object.values(IndicatorCategory)) {
      const weight = this.categoryWeights[category] || 0;
      totalWeight += weight;
      weightedScore += categories[category].score * weight;
    }
    
    const compositeScore = totalWeight > 0 ? weightedScore / totalWeight : 50;
    
    // Determine overall status
    let overallStatus: HealthStatus;
    if (compositeScore >= 80) overallStatus = HealthStatus.EXCELLENT;
    else if (compositeScore >= 60) overallStatus = HealthStatus.GOOD;
    else if (compositeScore >= 40) overallStatus = HealthStatus.MODERATE;
    else if (compositeScore >= 20) overallStatus = HealthStatus.CONCERNING;
    else overallStatus = HealthStatus.CRITICAL;
    
    // Create the indicators map
    const indicatorsMap: Record<string, HealthIndicator> = {};
    for (const [id, indicator] of this.indicators.entries()) {
      indicatorsMap[id] = { ...indicator };
    }
    
    // Get recent alerts (last 24 hours)
    const recentTime = new Date();
    recentTime.setHours(recentTime.getHours() - 24);
    const recentAlerts = this.alertHistory.filter(
      alert => new Date(alert.timestamp) > recentTime
    );
    
    // Format alerts for health report
    const alerts = recentAlerts.map(alert => ({
      severity: alert.severity,
      indicator: alert.indicator.id,
      message: alert.message,
      thresholdBreached: alert.thresholdBreached,
      timestamp: alert.timestamp
    }));
    
    // Calculate stagflation risk if enabled
    let stagflationRisk = { 
      score: 0, 
      status: HealthStatus.GOOD,
      components: { inflation: 0, unemployment: 0, growth: 0 }
    };
    
    if (this.stagflationAnalysisEnabled && this.stagflationAnalysisService) {
      try {
        // Convert relevant indicators to format expected by stagflation analysis
        const relevantIndicators: EconomicIndicator[] = [];
        
        // Get inflation indicators
        const inflationIndicators = categorizedIndicators[IndicatorCategory.INFLATION];
        if (inflationIndicators.length > 0) {
          relevantIndicators.push({
            id: 'inflation',
            name: 'Inflation Rate',
            data: inflationIndicators[0].historicalData,
            frequency: inflationIndicators[0].frequency.toLowerCase(),
            unit: inflationIndicators[0].unit,
            source: inflationIndicators[0].source || 'Economic Health Monitor'
          });
        }
        
        // Get unemployment indicators
        const employmentIndicators = categorizedIndicators[IndicatorCategory.EMPLOYMENT];
        const unemploymentIndicator = employmentIndicators.find(i => 
          i.name.toLowerCase().includes('unemployment') || i.id.toLowerCase().includes('unemployment')
        );
        
        if (unemploymentIndicator) {
          relevantIndicators.push({
            id: 'unemployment',
            name: 'Unemployment Rate',
            data: unemploymentIndicator.historicalData,
            frequency: unemploymentIndicator.frequency.toLowerCase(),
            unit: unemploymentIndicator.unit,
            source: unemploymentIndicator.source || 'Economic Health Monitor'
          });
        }
        
        // Get GDP growth indicators
        const growthIndicators = categorizedIndicators[IndicatorCategory.GROWTH];
        const gdpIndicator = growthIndicators.find(i => 
          i.name.toLowerCase().includes('gdp') || i.id.toLowerCase().includes('gdp')
        );
        
        if (gdpIndicator) {
          relevantIndicators.push({
            id: 'gdp',
            name: 'GDP Growth Rate',
            data: gdpIndicator.historicalData,
            frequency: gdpIndicator.frequency.toLowerCase(),
            unit: gdpIndicator.unit,
            source: gdpIndicator.source || 'Economic Health Monitor'
          });
        }
        
        // If we have at least two of the three key indicators, run stagflation analysis
        if (relevantIndicators.length >= 2) {
          // Add indicators to stagflation service
          relevantIndicators.forEach(indicator => {
            this.stagflationAnalysisService!.addIndicator(indicator);
          });
          
          // Run analysis
          const analysisId = await this.stagflationAnalysisService.runAnalysis('health-monitor-analysis');
          const analysis = await this.stagflationAnalysisService.getAnalysis(analysisId);
          
          if (analysis) {
            // Map stagflation probability to health status
            let status: HealthStatus;
            if (analysis.stagflationProbability < 0.2) status = HealthStatus.EXCELLENT;
            else if (analysis.stagflationProbability < 0.4) status = HealthStatus.GOOD;
            else if (analysis.stagflationProbability < 0.6) status = HealthStatus.MODERATE;
            else if (analysis.stagflationProbability < 0.8) status = HealthStatus.CONCERNING;
            else status = HealthStatus.CRITICAL;
            
            stagflationRisk = {
              score: analysis.stagflationProbability,
              status,
              components: {
                inflation: analysis.components.inflation.score,
                unemployment: analysis.components.unemployment.score,
                growth: analysis.components.stagnation.score
              }
            };
          }
        }
      } catch (error) {
        console.error('Error running stagflation analysis:', error);
      }
    }
    
    // Generate summary based on health status
    let summary = `Economic health is currently ${overallStatus}. `;
    
    // Add category insights
    const criticalCategories = Object.entries(categories)
      .filter(([_, data]) => data.status === HealthStatus.CRITICAL)
      .map(([category, _]) => category);
      
    const concerningCategories = Object.entries(categories)
      .filter(([_, data]) => data.status === HealthStatus.CONCERNING)
      .map(([category, _]) => category);
      
    const excellentCategories = Object.entries(categories)
      .filter(([_, data]) => data.status === HealthStatus.EXCELLENT)
      .map(([category, _]) => category);
    
    if (criticalCategories.length > 0) {
      summary += `Critical concerns in ${criticalCategories.join(', ')}. `;
    }
    
    if (concerningCategories.length > 0) {
      summary += `Concerning trends in ${concerningCategories.join(', ')}. `;
    }
    
    if (excellentCategories.length > 0) {
      summary += `Excellent performance in ${excellentCategories.join(', ')}. `;
    }
    
    // Add stagflation insight if relevant
    if (stagflationRisk.score > 0.5) {
      summary += `Stagflation risk is ${stagflationRisk.status} with score of ${(stagflationRisk.score * 100).toFixed(1)}%. `;
    }
    
    // Generate basic recommendations
    const recommendations: Array<{
      area: string;
      action: string;
      urgency: 'low' | 'medium' | 'high';
      rationale: string;
    }> = [];
    
    // Add recommendations based on category status
    if (criticalCategories.length > 0) {
      criticalCategories.forEach(category => {
        recommendations.push({
          area: category,
          action: `Implement emergency stabilization measures for ${category}`,
          urgency: 'high',
          rationale: `${category} indicators have reached critical levels requiring immediate intervention`
        });
      });
    }
    
    if (concerningCategories.length > 0) {
      concerningCategories.forEach(category => {
        recommendations.push({
          area: category,
          action: `Develop risk mitigation strategy for ${category}`,
          urgency: 'medium',
          rationale: `${category} indicators show concerning trends that require attention`
        });
      });
    }
    
    // Add stagflation-specific recommendation if risk is high
    if (stagflationRisk.score > 0.6) {
      recommendations.push({
        area: 'Stagflation',
        action: 'Develop comprehensive anti-stagflation policy package',
        urgency: 'high',
        rationale: `High stagflation risk (${(stagflationRisk.score * 100).toFixed(1)}%) requires coordinated policy response`
      });
    }
    
    // Create economic health object
    const economicHealth: EconomicHealth = {
      timestamp: now,
      overallStatus,
      compositeScore,
      indicators: indicatorsMap,
      categories,
      alerts,
      stagflationRisk,
      summary,
      recommendations
    };
    
    // Add to history
    this.healthHistory.unshift(economicHealth);
    
    // Limit history size
    if (this.healthHistory.length > this.historyLength) {
      this.healthHistory = this.healthHistory.slice(0, this.historyLength);
    }
    
    // Save data if persistence is enabled
    if (this.persistenceEnabled) {
      this.saveData();
    }
    
    // Emit event
    this.emit('health-updated', economicHealth);
    
    return economicHealth;
  }
}