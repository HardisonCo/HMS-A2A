import { EventEmitter } from 'events';
import { 
  StagflationAnalysisModel, 
  StagflationAnalysisService,
  StagflationAnalysis,
  PolicyRecommendation,
  EconomicIndicator
} from './stagflation_analysis';
import {
  EconomicHealthMonitor,
  HealthStatus,
  IndicatorCategory,
  HealthIndicator
} from './economic_health_monitor';

/**
 * Warning level for stagflation risks
 */
export enum WarningLevel {
  NONE = 'none',
  LOW = 'low',
  MODERATE = 'moderate',
  HIGH = 'high',
  CRITICAL = 'critical'
}

/**
 * Type of stagflation warning
 */
export enum WarningType {
  LEADING_INDICATOR = 'leading_indicator', // Early signs
  PATTERN_RECOGNITION = 'pattern_recognition', // Historical pattern matching
  THRESHOLD_BREACH = 'threshold_breach', // Indicator threshold breached
  TREND_ACCELERATION = 'trend_acceleration', // Rapid change in indicators
  COMPOSITE_INDEX = 'composite_index', // Multiple indicators combined
  EXTERNAL_FACTOR = 'external_factor', // External market conditions
  SENTIMENT_ANALYSIS = 'sentiment_analysis', // Market sentiment indicators
  EXPERT_JUDGMENT = 'expert_judgment' // Domain expert assessment
}

/**
 * Represents a stagflation warning
 */
export interface StagflationWarning {
  id: string;
  timestamp: string;
  level: WarningLevel;
  type: WarningType;
  title: string;
  description: string;
  indicators: string[]; // IDs of related indicators
  probability: number; // 0-1 probability estimation
  timeHorizon: string; // e.g., "3-6 months", "1-2 quarters"
  triggerThresholds?: Record<string, { min: number; max: number }>; // Thresholds that triggered the warning
  recommendations: string[]; // Recommended actions
  source: string; // Source of the warning (analysis method name)
  metadata?: Record<string, any>; // Additional data
}

/**
 * Options for configuring the early warning system
 */
export interface EarlyWarningOptions {
  pollingInterval?: number; // Milliseconds, default 24 hours
  sensitivityLevel?: number; // 0-1, default 0.5
  autoSendWarnings?: boolean; // Whether to automatically dispatch warnings
  historyLength?: number; // Number of warnings to keep in history
  riskThresholds?: { // Warning level thresholds
    low: number; // Default 0.3
    moderate: number; // Default 0.5
    high: number; // Default 0.7
    critical: number; // Default 0.85
  };
  leadingIndicatorWeights?: Record<string, number>; // Weights for leading indicators
  enabledAnalysisMethods?: string[]; // Enabled analysis methods
}

/**
 * Result of stagflation risk analysis
 */
export interface RiskAnalysisResult {
  timestamp: string;
  overallRisk: number; // 0-1 risk score
  warningLevel: WarningLevel;
  analysisId?: string; // Reference to full analysis if available
  components: {
    inflationRisk: number; 
    unemploymentRisk: number;
    growthRisk: number;
    leadingIndicatorsRisk: number;
    patternMatchingRisk: number;
  };
  warnings: StagflationWarning[];
  recommendations: string[];
  indicators: string[]; // IDs of indicators used in analysis
}

/**
 * Recipients for warnings
 */
export interface WarningRecipient {
  id: string;
  name: string;
  types: WarningType[]; // Types of warnings to receive
  minLevel: WarningLevel; // Minimum level to receive
  channel: 'email' | 'dashboard' | 'api' | 'message';
  contact?: string; // Contact info (email, API endpoint, etc.)
}

/**
 * Leading indicator definition for early warning detection
 */
export interface LeadingIndicator {
  id: string;
  name: string;
  category: 'inflation' | 'employment' | 'growth' | 'financial' | 'other';
  lookbackPeriods: number; // How many periods to analyze
  thresholds: {
    low: number;
    moderate: number;
    high: number;
    critical: number;
  };
  weight: number; // Importance weight 0-1
  lagPeriods?: number; // How many periods this typically leads stagflation
  transformations?: Array<'first_diff' | 'pct_change' | 'ma' | 'ema' | 'zscore'>;
}

/**
 * Historical pattern definition for pattern recognition
 */
export interface StagflationPattern {
  id: string;
  name: string;
  description: string;
  indicators: string[]; // Indicator IDs included in pattern
  sequence: Array<{
    indicator: string;
    condition: 'increases' | 'decreases' | 'above' | 'below';
    threshold?: number;
    duration?: number; // Time periods
  }>;
  timeframe: string; // e.g., "3 months", "2 quarters"
  confidence: number; // Historical confidence 0-1
  source: string; // Historical episode or research
}

/**
 * Early Warning System for detecting stagflation risks before they materialize
 * 
 * This system combines multiple analysis methods to provide early detection of
 * stagflation conditions, including:
 * 
 * 1. Leading indicator analysis
 * 2. Historical pattern recognition
 * 3. Threshold monitoring
 * 4. Trend acceleration detection
 * 5. Composite index calculation
 * 6. Integration with expert judgment
 */
export class StagflationEarlyWarningSystem extends EventEmitter {
  private stagflationService: StagflationAnalysisService;
  private healthMonitor?: EconomicHealthMonitor;
  private isInitialized: boolean = false;
  private pollingInterval: number = 86400000; // Default to daily
  private pollingTimer?: NodeJS.Timeout;
  private sensitivityLevel: number = 0.5; // 0-1, higher means more sensitive
  private autoSendWarnings: boolean = false;
  private warningHistory: StagflationWarning[] = [];
  private analysisHistory: RiskAnalysisResult[] = [];
  private historyLength: number = 100;
  private recipients: WarningRecipient[] = [];
  private riskThresholds = {
    low: 0.3,
    moderate: 0.5,
    high: 0.7,
    critical: 0.85
  };
  private leadingIndicators: Map<string, LeadingIndicator> = new Map();
  private stagflationPatterns: StagflationPattern[] = [];
  private enabledAnalysisMethods: Set<string> = new Set([
    'leadingIndicators',
    'patternRecognition',
    'thresholdMonitoring',
    'trendAcceleration',
    'compositeIndex'
  ]);
  
  /**
   * Create a new Stagflation Early Warning System
   */
  constructor(options?: EarlyWarningOptions) {
    super();
    this.stagflationService = new StagflationAnalysisService();
    
    if (options) {
      if (options.pollingInterval) this.pollingInterval = options.pollingInterval;
      if (options.sensitivityLevel !== undefined) this.sensitivityLevel = options.sensitivityLevel;
      if (options.autoSendWarnings !== undefined) this.autoSendWarnings = options.autoSendWarnings;
      if (options.historyLength !== undefined) this.historyLength = options.historyLength;
      if (options.riskThresholds) this.riskThresholds = {...this.riskThresholds, ...options.riskThresholds};
      if (options.enabledAnalysisMethods) {
        this.enabledAnalysisMethods = new Set(options.enabledAnalysisMethods);
      }
    }
    
    // Initialize default leading indicators
    this.initializeDefaultLeadingIndicators();
    
    // Initialize default stagflation patterns
    this.initializeDefaultStagflationPatterns();
  }
  
  /**
   * Initialize the early warning system
   */
  public async initialize(healthMonitor?: EconomicHealthMonitor): Promise<void> {
    if (this.isInitialized) return;
    
    // Initialize stagflation analysis service
    await this.stagflationService.initialize();
    
    // Connect to health monitor if provided
    if (healthMonitor) {
      this.healthMonitor = healthMonitor;
      
      // Subscribe to health monitor events
      this.healthMonitor.on('health-updated', async (health) => {
        await this.analyzeEconomicHealth(health);
      });
      
      this.healthMonitor.on('alert', async (alert) => {
        if (alert.indicator.category === IndicatorCategory.INFLATION ||
            alert.indicator.category === IndicatorCategory.EMPLOYMENT ||
            alert.indicator.category === IndicatorCategory.GROWTH) {
          await this.handleHealthAlert(alert);
        }
      });
    }
    
    this.isInitialized = true;
    
    // Start polling
    this.startPolling();
    
    this.emit('initialized');
  }
  
  /**
   * Start polling for automated analysis
   */
  public startPolling(): void {
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
    }
    
    // Run an initial analysis
    this.runAnalysis();
    
    this.pollingTimer = setInterval(() => {
      this.runAnalysis();
    }, this.pollingInterval);
    
    this.emit('polling-started');
  }
  
  /**
   * Stop polling
   */
  public stopPolling(): void {
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
      this.pollingTimer = undefined;
    }
    
    this.emit('polling-stopped');
  }
  
  /**
   * Run a complete stagflation risk analysis
   */
  public async runAnalysis(): Promise<RiskAnalysisResult> {
    if (!this.isInitialized) {
      throw new Error('StagflationEarlyWarningSystem must be initialized before running analysis');
    }
    
    const warnings: StagflationWarning[] = [];
    let overallRisk = 0;
    const now = new Date().toISOString();
    
    // Get current economic indicators from health monitor or stagflation service
    const indicators = this.collectIndicators();
    
    // Component risk scores
    const components = {
      inflationRisk: 0,
      unemploymentRisk: 0,
      growthRisk: 0,
      leadingIndicatorsRisk: 0,
      patternMatchingRisk: 0
    };
    
    // Run each enabled analysis method
    if (this.enabledAnalysisMethods.has('leadingIndicators')) {
      const leadingResults = await this.analyzeLeadingIndicators(indicators);
      components.leadingIndicatorsRisk = leadingResults.riskScore;
      warnings.push(...leadingResults.warnings);
    }
    
    if (this.enabledAnalysisMethods.has('patternRecognition')) {
      const patternResults = await this.detectStagflationPatterns(indicators);
      components.patternMatchingRisk = patternResults.riskScore;
      warnings.push(...patternResults.warnings);
    }
    
    if (this.enabledAnalysisMethods.has('thresholdMonitoring')) {
      const thresholdResults = await this.monitorThresholds(indicators);
      // Update component risks based on which indicators triggered
      for (const warning of thresholdResults.warnings) {
        if (warning.type === WarningType.THRESHOLD_BREACH) {
          for (const indId of warning.indicators) {
            const indicator = indicators.find(i => i.id === indId);
            if (indicator) {
              if (indicator.category === IndicatorCategory.INFLATION) {
                components.inflationRisk = Math.max(components.inflationRisk, warning.probability);
              } else if (indicator.category === IndicatorCategory.EMPLOYMENT) {
                components.unemploymentRisk = Math.max(components.unemploymentRisk, warning.probability);
              } else if (indicator.category === IndicatorCategory.GROWTH) {
                components.growthRisk = Math.max(components.growthRisk, warning.probability);
              }
            }
          }
        }
      }
      warnings.push(...thresholdResults.warnings);
    }
    
    if (this.enabledAnalysisMethods.has('trendAcceleration')) {
      const trendResults = await this.detectTrendAcceleration(indicators);
      // Update component risks based on which indicators triggered
      for (const warning of trendResults.warnings) {
        if (warning.type === WarningType.TREND_ACCELERATION) {
          for (const indId of warning.indicators) {
            const indicator = indicators.find(i => i.id === indId);
            if (indicator) {
              if (indicator.category === IndicatorCategory.INFLATION) {
                components.inflationRisk = Math.max(components.inflationRisk, warning.probability);
              } else if (indicator.category === IndicatorCategory.EMPLOYMENT) {
                components.unemploymentRisk = Math.max(components.unemploymentRisk, warning.probability);
              } else if (indicator.category === IndicatorCategory.GROWTH) {
                components.growthRisk = Math.max(components.growthRisk, warning.probability);
              }
            }
          }
        }
      }
      warnings.push(...trendResults.warnings);
    }
    
    if (this.enabledAnalysisMethods.has('compositeIndex')) {
      const compositeResults = await this.calculateCompositeIndex(indicators);
      warnings.push(...compositeResults.warnings);
      
      // Update overall risk from composite index
      overallRisk = compositeResults.riskScore;
    } else {
      // Calculate overall risk as weighted average of component risks
      const weights = {
        inflation: 0.3,
        unemployment: 0.3, 
        growth: 0.2,
        leading: 0.15,
        pattern: 0.05
      };
      
      overallRisk = 
        components.inflationRisk * weights.inflation +
        components.unemploymentRisk * weights.unemployment +
        components.growthRisk * weights.growth +
        components.leadingIndicatorsRisk * weights.leading +
        components.patternMatchingRisk * weights.pattern;
    }
    
    // Increase sensitivity based on sensitivity level
    overallRisk = Math.min(1, overallRisk * (1 + (this.sensitivityLevel - 0.5)));
    
    // Determine warning level
    let warningLevel = WarningLevel.NONE;
    if (overallRisk >= this.riskThresholds.critical) warningLevel = WarningLevel.CRITICAL;
    else if (overallRisk >= this.riskThresholds.high) warningLevel = WarningLevel.HIGH;
    else if (overallRisk >= this.riskThresholds.moderate) warningLevel = WarningLevel.MODERATE;
    else if (overallRisk >= this.riskThresholds.low) warningLevel = WarningLevel.LOW;
    
    // Gather recommendations from warnings
    const recommendations = this.consolidateRecommendations(warnings);
    
    // Create analysis result
    const result: RiskAnalysisResult = {
      timestamp: now,
      overallRisk,
      warningLevel,
      components,
      warnings,
      recommendations,
      indicators: indicators.map(i => i.id)
    };
    
    // Add to analysis history
    this.analysisHistory.unshift(result);
    
    // Trim history if needed
    if (this.analysisHistory.length > this.historyLength) {
      this.analysisHistory = this.analysisHistory.slice(0, this.historyLength);
    }
    
    // Add warnings to history
    for (const warning of warnings) {
      this.warningHistory.unshift(warning);
    }
    
    // Trim warning history if needed
    if (this.warningHistory.length > this.historyLength) {
      this.warningHistory = this.warningHistory.slice(0, this.historyLength);
    }
    
    // Emit events
    this.emit('analysis-completed', result);
    
    if (warnings.length > 0) {
      this.emit('warnings-generated', warnings);
      
      // Auto-send warnings if enabled
      if (this.autoSendWarnings) {
        await this.dispatchWarnings(warnings);
      }
    }
    
    return result;
  }
  
  /**
   * Get the most recent analysis result
   */
  public getLatestAnalysis(): RiskAnalysisResult | undefined {
    return this.analysisHistory.length > 0 ? this.analysisHistory[0] : undefined;
  }
  
  /**
   * Get all analysis results
   */
  public getAnalysisHistory(): RiskAnalysisResult[] {
    return [...this.analysisHistory];
  }
  
  /**
   * Get warning history
   */
  public getWarningHistory(): StagflationWarning[] {
    return [...this.warningHistory];
  }
  
  /**
   * Add a warning recipient
   */
  public addRecipient(recipient: WarningRecipient): void {
    this.recipients.push(recipient);
  }
  
  /**
   * Remove a warning recipient
   */
  public removeRecipient(id: string): boolean {
    const initialLength = this.recipients.length;
    this.recipients = this.recipients.filter(r => r.id !== id);
    return this.recipients.length < initialLength;
  }
  
  /**
   * Get all warning recipients
   */
  public getRecipients(): WarningRecipient[] {
    return [...this.recipients];
  }
  
  /**
   * Register a leading indicator for early warning detection
   */
  public registerLeadingIndicator(indicator: LeadingIndicator): void {
    this.leadingIndicators.set(indicator.id, indicator);
  }
  
  /**
   * Get all registered leading indicators
   */
  public getLeadingIndicators(): LeadingIndicator[] {
    return Array.from(this.leadingIndicators.values());
  }
  
  /**
   * Register a stagflation pattern for pattern recognition
   */
  public registerStagflationPattern(pattern: StagflationPattern): void {
    this.stagflationPatterns.push(pattern);
  }
  
  /**
   * Get all registered stagflation patterns
   */
  public getStagflationPatterns(): StagflationPattern[] {
    return [...this.stagflationPatterns];
  }
  
  /**
   * Set the sensitivity level (0-1)
   */
  public setSensitivityLevel(level: number): void {
    if (level < 0 || level > 1) {
      throw new Error('Sensitivity level must be between 0 and 1');
    }
    this.sensitivityLevel = level;
  }
  
  /**
   * Enable or disable an analysis method
   */
  public setAnalysisMethodEnabled(method: string, enabled: boolean): void {
    if (enabled) {
      this.enabledAnalysisMethods.add(method);
    } else {
      this.enabledAnalysisMethods.delete(method);
    }
  }
  
  /**
   * Get current settings
   */
  public getSettings(): {
    pollingInterval: number;
    sensitivityLevel: number;
    autoSendWarnings: boolean;
    riskThresholds: typeof this.riskThresholds;
    enabledAnalysisMethods: string[];
  } {
    return {
      pollingInterval: this.pollingInterval,
      sensitivityLevel: this.sensitivityLevel,
      autoSendWarnings: this.autoSendWarnings,
      riskThresholds: {...this.riskThresholds},
      enabledAnalysisMethods: Array.from(this.enabledAnalysisMethods)
    };
  }
  
  /**
   * Send one or more warnings to recipients
   */
  private async dispatchWarnings(warnings: StagflationWarning[]): Promise<void> {
    if (warnings.length === 0 || this.recipients.length === 0) return;
    
    // Group warnings by level
    const warningsByLevel: Record<WarningLevel, StagflationWarning[]> = {
      [WarningLevel.NONE]: [],
      [WarningLevel.LOW]: [],
      [WarningLevel.MODERATE]: [],
      [WarningLevel.HIGH]: [],
      [WarningLevel.CRITICAL]: []
    };
    
    for (const warning of warnings) {
      warningsByLevel[warning.level].push(warning);
    }
    
    // Send warnings to each recipient based on their settings
    for (const recipient of this.recipients) {
      const recipientWarnings: StagflationWarning[] = [];
      
      // Filter warnings by level and type
      for (const warning of warnings) {
        const levelMatch = this.getWarningLevelValue(warning.level) >= this.getWarningLevelValue(recipient.minLevel);
        const typeMatch = recipient.types.includes(warning.type);
        
        if (levelMatch && typeMatch) {
          recipientWarnings.push(warning);
        }
      }
      
      if (recipientWarnings.length > 0) {
        try {
          // In a real system, this would send the warnings through the appropriate channel
          console.log(`Sending ${recipientWarnings.length} warnings to ${recipient.name} via ${recipient.channel}`);
          
          this.emit('warnings-dispatched', {
            recipient: recipient.id,
            warnings: recipientWarnings
          });
        } catch (error) {
          console.error(`Error dispatching warnings to ${recipient.name}:`, error);
        }
      }
    }
  }
  
  /**
   * Get numeric value for warning level
   */
  private getWarningLevelValue(level: WarningLevel): number {
    switch (level) {
      case WarningLevel.NONE: return 0;
      case WarningLevel.LOW: return 1;
      case WarningLevel.MODERATE: return 2;
      case WarningLevel.HIGH: return 3;
      case WarningLevel.CRITICAL: return 4;
      default: return 0;
    }
  }
  
  /**
   * Analyze economic health status from the health monitor
   */
  private async analyzeEconomicHealth(health: any): Promise<void> {
    if (!health || !health.indicators) return;
    
    const indicators: HealthIndicator[] = Object.values(health.indicators);
    
    // Look for concerning or critical statuses in key categories
    const inflationStatus = health.categories[IndicatorCategory.INFLATION]?.status;
    const employmentStatus = health.categories[IndicatorCategory.EMPLOYMENT]?.status;
    const growthStatus = health.categories[IndicatorCategory.GROWTH]?.status;
    
    const isConcerning = (status: string) => 
      status === HealthStatus.CONCERNING || status === HealthStatus.CRITICAL;
      
    // If multiple categories are concerning, run a quick analysis
    if ((isConcerning(inflationStatus) && isConcerning(employmentStatus)) ||
        (isConcerning(inflationStatus) && isConcerning(growthStatus)) ||
        (isConcerning(employmentStatus) && isConcerning(growthStatus))) {
      
      await this.runAnalysis();
    }
  }
  
  /**
   * Handle alerts from the health monitor
   */
  private async handleHealthAlert(alert: any): Promise<void> {
    // If we get a critical alert for inflation, employment, or growth, run analysis
    if (alert.severity === 'critical') {
      await this.runAnalysis();
    }
  }
  
  /**
   * Analyze leading indicators for early warning signs
   */
  private async analyzeLeadingIndicators(indicators: any[]): Promise<{
    riskScore: number;
    warnings: StagflationWarning[];
  }> {
    const warnings: StagflationWarning[] = [];
    let totalRisk = 0;
    let totalWeight = 0;
    
    // Check each leading indicator
    for (const leadingInd of this.leadingIndicators.values()) {
      // Find the actual indicator data
      const indicator = indicators.find(i => 
        i.id === leadingInd.id || 
        i.name.toLowerCase() === leadingInd.name.toLowerCase()
      );
      
      if (!indicator || !indicator.historicalData || indicator.historicalData.length < 2) {
        continue;
      }
      
      // Apply transformations if needed
      let data = [...indicator.historicalData]
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
        .slice(0, leadingInd.lookbackPeriods);
      
      // Calculate indicator value (could be transformed)
      let indicatorValue = data[0].value;
      
      // Optional transformations
      if (leadingInd.transformations) {
        for (const transform of leadingInd.transformations) {
          if (transform === 'first_diff' && data.length >= 2) {
            indicatorValue = data[0].value - data[1].value;
          } else if (transform === 'pct_change' && data.length >= 2) {
            indicatorValue = ((data[0].value - data[1].value) / Math.abs(data[1].value)) * 100;
          } else if (transform === 'ma' && data.length >= 3) {
            // Simple moving average
            const sum = data.reduce((acc, d) => acc + d.value, 0);
            indicatorValue = sum / data.length;
          } else if (transform === 'ema' && data.length >= 3) {
            // Exponential moving average
            const alpha = 2 / (data.length + 1);
            let ema = data[0].value;
            for (let i = 1; i < data.length; i++) {
              ema = (data[i].value * alpha) + (ema * (1 - alpha));
            }
            indicatorValue = ema;
          } else if (transform === 'zscore' && data.length >= 5) {
            // Z-score (standardized value)
            const values = data.map(d => d.value);
            const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
            const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
            const variance = squaredDiffs.reduce((sum, val) => sum + val, 0) / values.length;
            const stdDev = Math.sqrt(variance);
            indicatorValue = (data[0].value - mean) / stdDev;
          }
        }
      }
      
      // Determine risk level based on thresholds
      let riskLevel = 0;
      let warningLevel = WarningLevel.NONE;
      
      if (indicatorValue >= leadingInd.thresholds.critical) {
        riskLevel = 1;
        warningLevel = WarningLevel.CRITICAL;
      } else if (indicatorValue >= leadingInd.thresholds.high) {
        riskLevel = 0.75;
        warningLevel = WarningLevel.HIGH;
      } else if (indicatorValue >= leadingInd.thresholds.moderate) {
        riskLevel = 0.5;
        warningLevel = WarningLevel.MODERATE;
      } else if (indicatorValue >= leadingInd.thresholds.low) {
        riskLevel = 0.25;
        warningLevel = WarningLevel.LOW;
      }
      
      // Add to weighted average
      totalRisk += riskLevel * leadingInd.weight;
      totalWeight += leadingInd.weight;
      
      // Generate a warning if risk is high enough
      if (warningLevel !== WarningLevel.NONE) {
        const warning: StagflationWarning = {
          id: `leading-${leadingInd.id}-${Date.now()}`,
          timestamp: new Date().toISOString(),
          level: warningLevel,
          type: WarningType.LEADING_INDICATOR,
          title: `${leadingInd.name} indicating potential stagflation risk`,
          description: `${leadingInd.name} has reached a level of ${indicatorValue} which has historically preceded stagflation conditions by approximately ${leadingInd.lagPeriods || 'several'} periods.`,
          indicators: [leadingInd.id],
          probability: riskLevel,
          timeHorizon: leadingInd.lagPeriods ? `${leadingInd.lagPeriods} periods` : '3-6 months',
          recommendations: [
            `Monitor ${leadingInd.name} closely for continued deterioration`,
            'Prepare contingency plans for potential stagflation',
            'Review policy options for addressing this indicator specifically'
          ],
          source: 'Leading Indicator Analysis',
          metadata: {
            currentValue: indicatorValue,
            threshold: leadingInd.thresholds,
            category: leadingInd.category
          }
        };
        
        warnings.push(warning);
      }
    }
    
    const riskScore = totalWeight > 0 ? totalRisk / totalWeight : 0;
    
    return {
      riskScore,
      warnings
    };
  }
  
  /**
   * Detect stagflation patterns in the data
   */
  private async detectStagflationPatterns(indicators: any[]): Promise<{
    riskScore: number;
    warnings: StagflationWarning[];
  }> {
    const warnings: StagflationWarning[] = [];
    let highestPatternRisk = 0;
    
    // Check each stagflation pattern
    for (const pattern of this.stagflationPatterns) {
      // Check if we have all required indicators
      const missingIndicators = pattern.indicators.filter(id => 
        !indicators.some(i => i.id === id || i.name.toLowerCase().includes(id.toLowerCase()))
      );
      
      if (missingIndicators.length > 0) {
        continue; // Skip this pattern if we're missing indicators
      }
      
      // Check the sequence of conditions
      let matchCount = 0;
      for (const step of pattern.sequence) {
        const indicator = indicators.find(i => 
          i.id === step.indicator || 
          i.name.toLowerCase().includes(step.indicator.toLowerCase())
        );
        
        if (!indicator || !indicator.historicalData || indicator.historicalData.length < 2) {
          continue;
        }
        
        // Sort data by date (newest first)
        const data = [...indicator.historicalData]
          .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
        
        // Check the condition
        if (step.condition === 'increases') {
          // Check if the indicator has been increasing
          let increasing = true;
          for (let i = 0; i < Math.min(data.length - 1, step.duration || 3); i++) {
            if (data[i].value <= data[i + 1].value) {
              increasing = false;
              break;
            }
          }
          if (increasing) matchCount++;
        } else if (step.condition === 'decreases') {
          // Check if the indicator has been decreasing
          let decreasing = true;
          for (let i = 0; i < Math.min(data.length - 1, step.duration || 3); i++) {
            if (data[i].value >= data[i + 1].value) {
              decreasing = false;
              break;
            }
          }
          if (decreasing) matchCount++;
        } else if (step.condition === 'above' && step.threshold !== undefined) {
          // Check if the indicator is above the threshold
          if (data[0].value > step.threshold) {
            matchCount++;
          }
        } else if (step.condition === 'below' && step.threshold !== undefined) {
          // Check if the indicator is below the threshold
          if (data[0].value < step.threshold) {
            matchCount++;
          }
        }
      }
      
      // Calculate match percentage
      const matchPercentage = pattern.sequence.length > 0 ? 
        matchCount / pattern.sequence.length : 0;
      
      // Calculate risk based on match percentage and pattern confidence
      const risk = matchPercentage * pattern.confidence;
      
      if (risk > highestPatternRisk) {
        highestPatternRisk = risk;
      }
      
      // Generate warning if match percentage is high enough
      if (matchPercentage >= 0.75) {
        let warningLevel = WarningLevel.MODERATE;
        if (risk >= 0.9) warningLevel = WarningLevel.CRITICAL;
        else if (risk >= 0.7) warningLevel = WarningLevel.HIGH;
        else if (risk >= 0.5) warningLevel = WarningLevel.MODERATE;
        else warningLevel = WarningLevel.LOW;
        
        const warning: StagflationWarning = {
          id: `pattern-${pattern.id}-${Date.now()}`,
          timestamp: new Date().toISOString(),
          level: warningLevel,
          type: WarningType.PATTERN_RECOGNITION,
          title: `Detected potential "${pattern.name}" stagflation pattern`,
          description: `Economic indicators are showing a ${Math.round(matchPercentage * 100)}% match to the "${pattern.name}" stagflation pattern: ${pattern.description}`,
          indicators: pattern.indicators,
          probability: risk,
          timeHorizon: pattern.timeframe,
          recommendations: [
            'Review historical policy responses to this pattern',
            'Prepare stagflation contingency plans',
            'Consider preemptive policy adjustments'
          ],
          source: 'Historical Pattern Recognition',
          metadata: {
            patternId: pattern.id,
            matchPercentage,
            confidence: pattern.confidence,
            historicalSource: pattern.source
          }
        };
        
        warnings.push(warning);
      }
    }
    
    return {
      riskScore: highestPatternRisk,
      warnings
    };
  }
  
  /**
   * Monitor for threshold breaches
   */
  private async monitorThresholds(indicators: any[]): Promise<{
    riskScore: number;
    warnings: StagflationWarning[];
  }> {
    const warnings: StagflationWarning[] = [];
    const criticalThresholds = {
      inflation: 6.0, // High inflation
      unemployment: 7.0, // High unemployment
      growth: 1.0 // Low growth
    };
    
    const warningThresholds = {
      inflation: 4.5,
      unemployment: 5.5,
      growth: 1.5
    };
    
    // Extract key indicators
    const inflation = indicators.find(i => 
      i.category === IndicatorCategory.INFLATION || 
      i.id === 'inflation' || 
      (i.name && i.name.toLowerCase().includes('inflation'))
    );
    
    const unemployment = indicators.find(i => 
      i.category === IndicatorCategory.EMPLOYMENT && 
      (i.id === 'unemployment' || 
      (i.name && i.name.toLowerCase().includes('unemployment')))
    );
    
    const growth = indicators.find(i => 
      i.category === IndicatorCategory.GROWTH && 
      (i.id === 'gdp' || i.id === 'gdp-growth' || 
      (i.name && i.name.toLowerCase().includes('gdp')))
    );
    
    // Check for threshold breaches
    let highestRisk = 0;
    
    if (inflation && inflation.currentValue !== undefined) {
      if (inflation.currentValue >= criticalThresholds.inflation) {
        const warning: StagflationWarning = {
          id: `threshold-inflation-${Date.now()}`,
          timestamp: new Date().toISOString(),
          level: WarningLevel.CRITICAL,
          type: WarningType.THRESHOLD_BREACH,
          title: 'Critical inflation threshold breached',
          description: `Inflation rate at ${inflation.currentValue}% has breached the critical threshold of ${criticalThresholds.inflation}%, significantly increasing stagflation risk.`,
          indicators: [inflation.id],
          probability: 0.85,
          timeHorizon: 'Immediate',
          triggerThresholds: { 'inflation': { min: criticalThresholds.inflation, max: 100 } },
          recommendations: [
            'Implement immediate anti-inflation measures',
            'Review monetary policy stance',
            'Prepare for potential stagflation scenario'
          ],
          source: 'Threshold Monitoring',
          metadata: {
            actualValue: inflation.currentValue,
            threshold: criticalThresholds.inflation
          }
        };
        warnings.push(warning);
        highestRisk = Math.max(highestRisk, 0.85);
      } else if (inflation.currentValue >= warningThresholds.inflation) {
        const warning: StagflationWarning = {
          id: `threshold-inflation-${Date.now()}`,
          timestamp: new Date().toISOString(),
          level: WarningLevel.MODERATE,
          type: WarningType.THRESHOLD_BREACH,
          title: 'Inflation warning threshold breached',
          description: `Inflation rate at ${inflation.currentValue}% has breached the warning threshold of ${warningThresholds.inflation}%, increasing stagflation risk.`,
          indicators: [inflation.id],
          probability: 0.6,
          timeHorizon: 'Near-term (1-3 months)',
          triggerThresholds: { 'inflation': { min: warningThresholds.inflation, max: criticalThresholds.inflation } },
          recommendations: [
            'Monitor inflation trends closely',
            'Prepare anti-inflation contingency plans',
            'Review price stability policy options'
          ],
          source: 'Threshold Monitoring',
          metadata: {
            actualValue: inflation.currentValue,
            threshold: warningThresholds.inflation
          }
        };
        warnings.push(warning);
        highestRisk = Math.max(highestRisk, 0.6);
      }
    }
    
    if (unemployment && unemployment.currentValue !== undefined) {
      if (unemployment.currentValue >= criticalThresholds.unemployment) {
        const warning: StagflationWarning = {
          id: `threshold-unemployment-${Date.now()}`,
          timestamp: new Date().toISOString(),
          level: WarningLevel.CRITICAL,
          type: WarningType.THRESHOLD_BREACH,
          title: 'Critical unemployment threshold breached',
          description: `Unemployment rate at ${unemployment.currentValue}% has breached the critical threshold of ${criticalThresholds.unemployment}%, significantly increasing stagflation risk.`,
          indicators: [unemployment.id],
          probability: 0.8,
          timeHorizon: 'Immediate',
          triggerThresholds: { 'unemployment': { min: criticalThresholds.unemployment, max: 100 } },
          recommendations: [
            'Implement immediate employment support measures',
            'Review labor market policies',
            'Prepare for potential stagflation scenario'
          ],
          source: 'Threshold Monitoring',
          metadata: {
            actualValue: unemployment.currentValue,
            threshold: criticalThresholds.unemployment
          }
        };
        warnings.push(warning);
        highestRisk = Math.max(highestRisk, 0.8);
      } else if (unemployment.currentValue >= warningThresholds.unemployment) {
        const warning: StagflationWarning = {
          id: `threshold-unemployment-${Date.now()}`,
          timestamp: new Date().toISOString(),
          level: WarningLevel.MODERATE,
          type: WarningType.THRESHOLD_BREACH,
          title: 'Unemployment warning threshold breached',
          description: `Unemployment rate at ${unemployment.currentValue}% has breached the warning threshold of ${warningThresholds.unemployment}%, increasing stagflation risk.`,
          indicators: [unemployment.id],
          probability: 0.55,
          timeHorizon: 'Near-term (1-3 months)',
          triggerThresholds: { 'unemployment': { min: warningThresholds.unemployment, max: criticalThresholds.unemployment } },
          recommendations: [
            'Monitor labor market trends closely',
            'Prepare employment support contingency plans',
            'Review labor market policy options'
          ],
          source: 'Threshold Monitoring',
          metadata: {
            actualValue: unemployment.currentValue,
            threshold: warningThresholds.unemployment
          }
        };
        warnings.push(warning);
        highestRisk = Math.max(highestRisk, 0.55);
      }
    }
    
    if (growth && growth.currentValue !== undefined) {
      if (growth.currentValue <= criticalThresholds.growth) {
        const warning: StagflationWarning = {
          id: `threshold-growth-${Date.now()}`,
          timestamp: new Date().toISOString(),
          level: WarningLevel.CRITICAL,
          type: WarningType.THRESHOLD_BREACH,
          title: 'Critical growth threshold breached',
          description: `GDP growth rate at ${growth.currentValue}% has fallen below the critical threshold of ${criticalThresholds.growth}%, significantly increasing stagflation risk.`,
          indicators: [growth.id],
          probability: 0.85,
          timeHorizon: 'Immediate',
          triggerThresholds: { 'growth': { min: 0, max: criticalThresholds.growth } },
          recommendations: [
            'Implement immediate growth stimulus measures',
            'Review fiscal and monetary policy stance',
            'Prepare for potential stagflation scenario'
          ],
          source: 'Threshold Monitoring',
          metadata: {
            actualValue: growth.currentValue,
            threshold: criticalThresholds.growth
          }
        };
        warnings.push(warning);
        highestRisk = Math.max(highestRisk, 0.85);
      } else if (growth.currentValue <= warningThresholds.growth) {
        const warning: StagflationWarning = {
          id: `threshold-growth-${Date.now()}`,
          timestamp: new Date().toISOString(),
          level: WarningLevel.MODERATE,
          type: WarningType.THRESHOLD_BREACH,
          title: 'Growth warning threshold breached',
          description: `GDP growth rate at ${growth.currentValue}% has fallen below the warning threshold of ${warningThresholds.growth}%, increasing stagflation risk.`,
          indicators: [growth.id],
          probability: 0.6,
          timeHorizon: 'Near-term (1-3 months)',
          triggerThresholds: { 'growth': { min: 0, max: warningThresholds.growth } },
          recommendations: [
            'Monitor economic growth trends closely',
            'Prepare growth stimulus contingency plans',
            'Review growth policy options'
          ],
          source: 'Threshold Monitoring',
          metadata: {
            actualValue: growth.currentValue,
            threshold: warningThresholds.growth
          }
        };
        warnings.push(warning);
        highestRisk = Math.max(highestRisk, 0.6);
      }
    }
    
    // Combined threshold checking (stagflation conditions)
    if (inflation && unemployment && growth && 
        inflation.currentValue !== undefined && 
        unemployment.currentValue !== undefined && 
        growth.currentValue !== undefined) {
      
      if (inflation.currentValue > warningThresholds.inflation && 
          unemployment.currentValue > warningThresholds.unemployment && 
          growth.currentValue < warningThresholds.growth) {
        
        // This is a classic stagflation scenario
        const isCritical = inflation.currentValue > criticalThresholds.inflation || 
                         unemployment.currentValue > criticalThresholds.unemployment || 
                         growth.currentValue < criticalThresholds.growth;
        
        const warning: StagflationWarning = {
          id: `threshold-stagflation-${Date.now()}`,
          timestamp: new Date().toISOString(),
          level: isCritical ? WarningLevel.CRITICAL : WarningLevel.HIGH,
          type: WarningType.THRESHOLD_BREACH,
          title: `${isCritical ? 'Critical' : 'High'} stagflation risk detected`,
          description: `All three key stagflation indicators have breached thresholds: Inflation at ${inflation.currentValue}%, Unemployment at ${unemployment.currentValue}%, and GDP Growth at ${growth.currentValue}%.`,
          indicators: [inflation.id, unemployment.id, growth.id],
          probability: isCritical ? 0.95 : 0.80,
          timeHorizon: 'Immediate',
          triggerThresholds: {
            'inflation': { min: warningThresholds.inflation, max: 100 },
            'unemployment': { min: warningThresholds.unemployment, max: 100 },
            'growth': { min: 0, max: warningThresholds.growth }
          },
          recommendations: [
            'Activate stagflation response plan immediately',
            'Coordinate monetary and fiscal policy responses',
            'Implement comprehensive stagflation mitigation strategy',
            'Prepare communication strategy for markets and public'
          ],
          source: 'Threshold Monitoring',
          metadata: {
            inflationValue: inflation.currentValue,
            unemploymentValue: unemployment.currentValue,
            growthValue: growth.currentValue
          }
        };
        warnings.push(warning);
        highestRisk = Math.max(highestRisk, isCritical ? 0.95 : 0.80);
      }
    }
    
    return {
      riskScore: highestRisk,
      warnings
    };
  }
  
  /**
   * Detect accelerating trends that could lead to stagflation
   */
  private async detectTrendAcceleration(indicators: any[]): Promise<{
    riskScore: number;
    warnings: StagflationWarning[];
  }> {
    const warnings: StagflationWarning[] = [];
    let highestRisk = 0;
    
    // Extract key indicators
    const inflationIndicators = indicators.filter(i => 
      i.category === IndicatorCategory.INFLATION ||
      (i.id && i.id.toLowerCase().includes('inflation')) ||
      (i.name && i.name.toLowerCase().includes('inflation'))
    );
    
    const unemploymentIndicators = indicators.filter(i => 
      (i.category === IndicatorCategory.EMPLOYMENT) && 
      ((i.id && i.id.toLowerCase().includes('unemploy')) || 
       (i.name && i.name.toLowerCase().includes('unemploy')))
    );
    
    const growthIndicators = indicators.filter(i => 
      (i.category === IndicatorCategory.GROWTH) && 
      ((i.id && i.id.toLowerCase().includes('gdp')) || 
       (i.name && i.name.toLowerCase().includes('gdp')) ||
       (i.name && i.name.toLowerCase().includes('growth')))
    );
    
    // Check for acceleration in inflation
    for (const indicator of inflationIndicators) {
      if (!indicator.historicalData || indicator.historicalData.length < 4) {
        continue;
      }
      
      // Sort data by date (newest first)
      const data = [...indicator.historicalData]
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
      
      // Calculate first and second derivative
      const values = data.map(d => d.value);
      const firstDiffs = [];
      const secondDiffs = [];
      
      for (let i = 0; i < values.length - 1; i++) {
        firstDiffs.push(values[i] - values[i + 1]);
      }
      
      for (let i = 0; i < firstDiffs.length - 1; i++) {
        secondDiffs.push(firstDiffs[i] - firstDiffs[i + 1]);
      }
      
      // Check for acceleration (positive first and second derivative)
      if (firstDiffs[0] > 0 && secondDiffs[0] > 0) {
        const accelFactor = (secondDiffs[0] / Math.abs(values[0])) * 100;
        
        if (accelFactor > 20) {
          // Significant acceleration
          const warning: StagflationWarning = {
            id: `trend-inflation-${Date.now()}`,
            timestamp: new Date().toISOString(),
            level: WarningLevel.HIGH,
            type: WarningType.TREND_ACCELERATION,
            title: 'Rapidly accelerating inflation detected',
            description: `${indicator.name} is accelerating at an increasing rate, with the rate of increase itself growing by ${accelFactor.toFixed(1)}%.`,
            indicators: [indicator.id],
            probability: 0.75,
            timeHorizon: 'Short-term (1-2 months)',
            recommendations: [
              'Implement preemptive anti-inflation measures',
              'Review monetary policy stance urgently',
              'Prepare communication strategy for markets'
            ],
            source: 'Trend Acceleration Detection',
            metadata: {
              currentValue: values[0],
              firstDerivative: firstDiffs[0],
              secondDerivative: secondDiffs[0],
              accelerationFactor: accelFactor
            }
          };
          warnings.push(warning);
          highestRisk = Math.max(highestRisk, 0.75);
        } else if (accelFactor > 10) {
          // Moderate acceleration
          const warning: StagflationWarning = {
            id: `trend-inflation-${Date.now()}`,
            timestamp: new Date().toISOString(),
            level: WarningLevel.MODERATE,
            type: WarningType.TREND_ACCELERATION,
            title: 'Accelerating inflation detected',
            description: `${indicator.name} is showing signs of acceleration, with the rate of increase growing by ${accelFactor.toFixed(1)}%.`,
            indicators: [indicator.id],
            probability: 0.55,
            timeHorizon: 'Medium-term (2-3 months)',
            recommendations: [
              'Monitor inflation trends closely',
              'Prepare anti-inflation contingency plans',
              'Review price stability tools'
            ],
            source: 'Trend Acceleration Detection',
            metadata: {
              currentValue: values[0],
              firstDerivative: firstDiffs[0],
              secondDerivative: secondDiffs[0],
              accelerationFactor: accelFactor
            }
          };
          warnings.push(warning);
          highestRisk = Math.max(highestRisk, 0.55);
        }
      }
    }
    
    // Check for acceleration in unemployment
    for (const indicator of unemploymentIndicators) {
      if (!indicator.historicalData || indicator.historicalData.length < 4) {
        continue;
      }
      
      // Sort data by date (newest first)
      const data = [...indicator.historicalData]
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
      
      // Calculate first and second derivative
      const values = data.map(d => d.value);
      const firstDiffs = [];
      const secondDiffs = [];
      
      for (let i = 0; i < values.length - 1; i++) {
        firstDiffs.push(values[i] - values[i + 1]);
      }
      
      for (let i = 0; i < firstDiffs.length - 1; i++) {
        secondDiffs.push(firstDiffs[i] - firstDiffs[i + 1]);
      }
      
      // Check for acceleration (positive first and second derivative)
      if (firstDiffs[0] > 0 && secondDiffs[0] > 0) {
        const accelFactor = (secondDiffs[0] / Math.abs(values[0])) * 100;
        
        if (accelFactor > 15) {
          // Significant acceleration
          const warning: StagflationWarning = {
            id: `trend-unemployment-${Date.now()}`,
            timestamp: new Date().toISOString(),
            level: WarningLevel.HIGH,
            type: WarningType.TREND_ACCELERATION,
            title: 'Rapidly accelerating unemployment detected',
            description: `${indicator.name} is accelerating at an increasing rate, with the rate of increase itself growing by ${accelFactor.toFixed(1)}%.`,
            indicators: [indicator.id],
            probability: 0.7,
            timeHorizon: 'Short-term (1-2 months)',
            recommendations: [
              'Implement preemptive employment support measures',
              'Review labor market policies urgently',
              'Prepare communication strategy for labor market'
            ],
            source: 'Trend Acceleration Detection',
            metadata: {
              currentValue: values[0],
              firstDerivative: firstDiffs[0],
              secondDerivative: secondDiffs[0],
              accelerationFactor: accelFactor
            }
          };
          warnings.push(warning);
          highestRisk = Math.max(highestRisk, 0.7);
        } else if (accelFactor > 7) {
          // Moderate acceleration
          const warning: StagflationWarning = {
            id: `trend-unemployment-${Date.now()}`,
            timestamp: new Date().toISOString(),
            level: WarningLevel.MODERATE,
            type: WarningType.TREND_ACCELERATION,
            title: 'Accelerating unemployment detected',
            description: `${indicator.name} is showing signs of acceleration, with the rate of increase growing by ${accelFactor.toFixed(1)}%.`,
            indicators: [indicator.id],
            probability: 0.5,
            timeHorizon: 'Medium-term (2-3 months)',
            recommendations: [
              'Monitor labor market trends closely',
              'Prepare employment support contingency plans',
              'Review labor market policy tools'
            ],
            source: 'Trend Acceleration Detection',
            metadata: {
              currentValue: values[0],
              firstDerivative: firstDiffs[0],
              secondDerivative: secondDiffs[0],
              accelerationFactor: accelFactor
            }
          };
          warnings.push(warning);
          highestRisk = Math.max(highestRisk, 0.5);
        }
      }
    }
    
    // Check for deceleration in growth (negative first derivative, negative second derivative)
    for (const indicator of growthIndicators) {
      if (!indicator.historicalData || indicator.historicalData.length < 4) {
        continue;
      }
      
      // Sort data by date (newest first)
      const data = [...indicator.historicalData]
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
      
      // Calculate first and second derivative
      const values = data.map(d => d.value);
      const firstDiffs = [];
      const secondDiffs = [];
      
      for (let i = 0; i < values.length - 1; i++) {
        firstDiffs.push(values[i] - values[i + 1]);
      }
      
      for (let i = 0; i < firstDiffs.length - 1; i++) {
        secondDiffs.push(firstDiffs[i] - firstDiffs[i + 1]);
      }
      
      // Check for accelerating deceleration (negative first and negative second derivative)
      if (firstDiffs[0] < 0 && secondDiffs[0] < 0) {
        const decelFactor = (Math.abs(secondDiffs[0]) / Math.abs(values[0])) * 100;
        
        if (decelFactor > 25) {
          // Significant deceleration
          const warning: StagflationWarning = {
            id: `trend-growth-${Date.now()}`,
            timestamp: new Date().toISOString(),
            level: WarningLevel.HIGH,
            type: WarningType.TREND_ACCELERATION,
            title: 'Rapidly decelerating economic growth detected',
            description: `${indicator.name} is decelerating at an increasing rate, with the rate of decrease itself growing by ${decelFactor.toFixed(1)}%.`,
            indicators: [indicator.id],
            probability: 0.75,
            timeHorizon: 'Short-term (1-2 months)',
            recommendations: [
              'Implement preemptive growth stimulus measures',
              'Review fiscal policy stance urgently',
              'Prepare communication strategy for markets'
            ],
            source: 'Trend Acceleration Detection',
            metadata: {
              currentValue: values[0],
              firstDerivative: firstDiffs[0],
              secondDerivative: secondDiffs[0],
              decelerationFactor: decelFactor
            }
          };
          warnings.push(warning);
          highestRisk = Math.max(highestRisk, 0.75);
        } else if (decelFactor > 10) {
          // Moderate deceleration
          const warning: StagflationWarning = {
            id: `trend-growth-${Date.now()}`,
            timestamp: new Date().toISOString(),
            level: WarningLevel.MODERATE,
            type: WarningType.TREND_ACCELERATION,
            title: 'Decelerating economic growth detected',
            description: `${indicator.name} is showing signs of deceleration, with the rate of decrease growing by ${decelFactor.toFixed(1)}%.`,
            indicators: [indicator.id],
            probability: 0.55,
            timeHorizon: 'Medium-term (2-3 months)',
            recommendations: [
              'Monitor economic growth trends closely',
              'Prepare growth stimulus contingency plans',
              'Review fiscal policy tools'
            ],
            source: 'Trend Acceleration Detection',
            metadata: {
              currentValue: values[0],
              firstDerivative: firstDiffs[0],
              secondDerivative: secondDiffs[0],
              decelerationFactor: decelFactor
            }
          };
          warnings.push(warning);
          highestRisk = Math.max(highestRisk, 0.55);
        }
      }
    }
    
    return {
      riskScore: highestRisk,
      warnings
    };
  }
  
  /**
   * Calculate composite index from multiple indicators
   */
  private async calculateCompositeIndex(indicators: any[]): Promise<{
    riskScore: number;
    warnings: StagflationWarning[];
  }> {
    // For now, run a full stagflation analysis
    try {
      // Convert indicators to the format expected by stagflation analysis
      const economicIndicators: EconomicIndicator[] = indicators
        .filter(ind => ind.historicalData && ind.historicalData.length > 0)
        .map(ind => ({
          id: ind.id,
          name: ind.name,
          data: ind.historicalData,
          frequency: ind.frequency?.toLowerCase() || 'monthly',
          unit: ind.unit || '%',
          source: ind.source || 'Early Warning System'
        }));
      
      // Add indicators to stagflation service
      economicIndicators.forEach(ind => {
        this.stagflationService.addIndicator(ind);
      });
      
      // Run analysis
      const analysisId = await this.stagflationService.runAnalysis('early-warning-analysis');
      const analysis = await this.stagflationService.getAnalysis(analysisId);
      
      if (!analysis) {
        return { riskScore: 0, warnings: [] };
      }
      
      // Use the stagflation probability as risk score
      const riskScore = analysis.stagflationProbability;
      
      // Determine warning level
      let warningLevel = WarningLevel.NONE;
      if (riskScore >= this.riskThresholds.critical) warningLevel = WarningLevel.CRITICAL;
      else if (riskScore >= this.riskThresholds.high) warningLevel = WarningLevel.HIGH;
      else if (riskScore >= this.riskThresholds.moderate) warningLevel = WarningLevel.MODERATE;
      else if (riskScore >= this.riskThresholds.low) warningLevel = WarningLevel.LOW;
      
      // Only generate a warning if the risk is high enough
      if (warningLevel !== WarningLevel.NONE) {
        const warning: StagflationWarning = {
          id: `composite-${Date.now()}`,
          timestamp: new Date().toISOString(),
          level: warningLevel,
          type: WarningType.COMPOSITE_INDEX,
          title: `${warningLevel.charAt(0).toUpperCase() + warningLevel.slice(1)} stagflation risk detected`,
          description: `Comprehensive analysis of economic indicators shows a ${(riskScore * 100).toFixed(1)}% probability of stagflation conditions developing.`,
          indicators: indicators.map(i => i.id),
          probability: riskScore,
          timeHorizon: '1-3 months',
          recommendations: [
            'Develop comprehensive stagflation response strategy',
            'Coordinate monetary and fiscal policy tools',
            'Prepare market communication strategy',
            'Review supply-side measures to address stagflation'
          ],
          source: 'Comprehensive Stagflation Analysis',
          metadata: {
            analysisId,
            stagflationProbability: riskScore,
            components: analysis.components
          }
        };
        
        return {
          riskScore,
          warnings: [warning]
        };
      }
      
      return {
        riskScore,
        warnings: []
      };
    } catch (error) {
      console.error('Error calculating composite index:', error);
      return {
        riskScore: 0,
        warnings: []
      };
    }
  }
  
  /**
   * Collect indicators from various sources
   */
  private collectIndicators(): any[] {
    const indicators: any[] = [];
    
    // Collect from health monitor if available
    if (this.healthMonitor) {
      const healthIndicators = this.healthMonitor.getAllIndicators();
      indicators.push(...healthIndicators);
    }
    
    // TODO: Collect from other sources as needed
    
    return indicators;
  }
  
  /**
   * Consolidate recommendations from multiple warnings
   */
  private consolidateRecommendations(warnings: StagflationWarning[]): string[] {
    if (warnings.length === 0) return [];
    
    // Collect all unique recommendations
    const recommendationSet = new Set<string>();
    
    for (const warning of warnings) {
      warning.recommendations.forEach(rec => recommendationSet.add(rec));
    }
    
    // Sort by priority (mentioned most frequently)
    const recommendationCounts = new Map<string, number>();
    for (const warning of warnings) {
      for (const rec of warning.recommendations) {
        recommendationCounts.set(rec, (recommendationCounts.get(rec) || 0) + 1);
      }
    }
    
    // Convert to array and sort by count
    return Array.from(recommendationSet)
      .sort((a, b) => (recommendationCounts.get(b) || 0) - (recommendationCounts.get(a) || 0));
  }
  
  /**
   * Initialize default leading indicators
   */
  private initializeDefaultLeadingIndicators(): void {
    const defaultIndicators: LeadingIndicator[] = [
      {
        id: 'yield-curve',
        name: 'Yield Curve Spread (10Y-2Y)',
        category: 'financial',
        lookbackPeriods: 12,
        lagPeriods: 12, // Typically leads by about 1 year
        thresholds: {
          low: 0.5,
          moderate: 0,
          high: -0.25,
          critical: -0.5
        },
        weight: 0.8,
        transformations: ['first_diff']
      },
      {
        id: 'producer-price-index',
        name: 'Producer Price Index',
        category: 'inflation',
        lookbackPeriods: 6,
        lagPeriods: 3, // Typically leads consumer inflation by 3 months
        thresholds: {
          low: 4.0,
          moderate: 5.0,
          high: 6.0,
          critical: 7.0
        },
        weight: 0.7,
        transformations: ['pct_change']
      },
      {
        id: 'business-confidence',
        name: 'Business Confidence Index',
        category: 'growth',
        lookbackPeriods: 6,
        lagPeriods: 6, // Typically leads by about 6 months
        thresholds: {
          low: 95,
          moderate: 90,
          high: 85,
          critical: 80
        },
        weight: 0.6,
        transformations: ['first_diff']
      },
      {
        id: 'initial-jobless-claims',
        name: 'Initial Jobless Claims',
        category: 'employment',
        lookbackPeriods: 8,
        lagPeriods: 2, // Typically leads unemployment by 2 months
        thresholds: {
          low: 300000,
          moderate: 350000,
          high: 400000,
          critical: 450000
        },
        weight: 0.7,
        transformations: ['pct_change', 'ma']
      },
      {
        id: 'capacity-utilization',
        name: 'Industrial Capacity Utilization',
        category: 'growth',
        lookbackPeriods: 6,
        lagPeriods: 4, // Typically leads by about 4 months
        thresholds: {
          low: 78,
          moderate: 75,
          high: 72,
          critical: 70
        },
        weight: 0.5,
        transformations: ['first_diff']
      }
    ];
    
    // Register default indicators
    for (const indicator of defaultIndicators) {
      this.leadingIndicators.set(indicator.id, indicator);
    }
  }
  
  /**
   * Initialize default stagflation patterns
   */
  private initializeDefaultStagflationPatterns(): void {
    const defaultPatterns: StagflationPattern[] = [
      {
        id: '1970s-stagflation',
        name: '1970s Stagflation Pattern',
        description: 'Pattern similar to the 1970s stagflation with rapid inflation rise followed by economic slowdown and rising unemployment',
        indicators: ['inflation', 'unemployment', 'gdp-growth', 'oil-price'],
        sequence: [
          { indicator: 'oil-price', condition: 'increases', duration: 3 },
          { indicator: 'inflation', condition: 'increases', duration: 3 },
          { indicator: 'gdp-growth', condition: 'decreases', duration: 2 },
          { indicator: 'unemployment', condition: 'increases', duration: 2 }
        ],
        timeframe: '6-12 months',
        confidence: 0.85,
        source: '1973-1975 US Stagflation'
      },
      {
        id: 'fiscal-monetary-mismatch',
        name: 'Fiscal-Monetary Policy Mismatch Pattern',
        description: 'Pattern where expansionary fiscal policy combined with tight monetary policy leads to stagflation',
        indicators: ['inflation', 'interest-rate', 'government-spending', 'gdp-growth'],
        sequence: [
          { indicator: 'government-spending', condition: 'increases', duration: 2 },
          { indicator: 'interest-rate', condition: 'increases', duration: 2 },
          { indicator: 'inflation', condition: 'increases', duration: 2 },
          { indicator: 'gdp-growth', condition: 'decreases', duration: 2 }
        ],
        timeframe: '3-6 months',
        confidence: 0.7,
        source: 'Historical Policy Mismatch Analysis'
      },
      {
        id: 'supply-shock-stagflation',
        name: 'Supply Shock Stagflation Pattern',
        description: 'Pattern where a major supply shock leads to stagflation conditions',
        indicators: ['commodity-prices', 'inflation', 'gdp-growth', 'unemployment'],
        sequence: [
          { indicator: 'commodity-prices', condition: 'increases', duration: 1 },
          { indicator: 'inflation', condition: 'increases', duration: 2 },
          { indicator: 'gdp-growth', condition: 'decreases', duration: 2 },
          { indicator: 'unemployment', condition: 'increases', duration: 2 }
        ],
        timeframe: '3-9 months',
        confidence: 0.8,
        source: 'Historical Supply Shock Analysis'
      },
      {
        id: 'wage-price-spiral',
        name: 'Wage-Price Spiral Pattern',
        description: 'Pattern where wage increases and price increases feed into each other, leading to stagflation',
        indicators: ['wage-growth', 'inflation', 'gdp-growth', 'corporate-profits'],
        sequence: [
          { indicator: 'wage-growth', condition: 'increases', duration: 3 },
          { indicator: 'inflation', condition: 'increases', duration: 3 },
          { indicator: 'corporate-profits', condition: 'decreases', duration: 2 },
          { indicator: 'gdp-growth', condition: 'decreases', duration: 2 }
        ],
        timeframe: '6-12 months',
        confidence: 0.75,
        source: 'Wage-Price Spiral Research'
      }
    ];
    
    // Register default patterns
    for (const pattern of defaultPatterns) {
      this.stagflationPatterns.push(pattern);
    }
  }
}