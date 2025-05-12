/**
 * Specialized analysis for stagflation indicators
 * 
 * Stagflation is a persistent situation where high inflation is combined with 
 * high unemployment and stagnant demand in a country's economy.
 */

import { EventEmitter } from 'events';

/**
 * Economic indicator with time series data
 */
export interface EconomicIndicator {
  id: string;
  name: string;
  description: string;
  unit: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'annually';
  source: string;
  timeSeries: {
    timestamp: number;     // Unix timestamp
    value: number;         // Indicator value
    uncertainty?: number;  // Uncertainty measure (if available)
  }[];
  metadata: Record<string, any>;
}

/**
 * Types of stagflation indicators
 */
export enum StagflationIndicatorType {
  INFLATION = 'inflation',
  UNEMPLOYMENT = 'unemployment',
  ECONOMIC_GROWTH = 'economic_growth',
  PRODUCTIVITY = 'productivity',
  ENERGY_PRICES = 'energy_prices',
  WAGE_GROWTH = 'wage_growth',
  CAPACITY_UTILIZATION = 'capacity_utilization',
  SUPPLY_CHAIN = 'supply_chain',
  CONSUMER_SENTIMENT = 'consumer_sentiment',
  BUSINESS_CONFIDENCE = 'business_confidence'
}

/**
 * Classification of an economic indicator's contribution to stagflation
 */
export enum StagflationContribution {
  STRONG_NEGATIVE = -2,    // Strongly contradicts stagflation
  NEGATIVE = -1,           // Contradicts stagflation
  NEUTRAL = 0,             // Neutral indicator
  POSITIVE = 1,            // Indicates possible stagflation
  STRONG_POSITIVE = 2      // Strongly indicates stagflation
}

/**
 * Analysis of a stagflation indicator
 */
export interface StagflationIndicatorAnalysis {
  indicator: EconomicIndicator;
  type: StagflationIndicatorType;
  currentValue: number;
  historicalAverage: number;
  percentChange: number;          // Percent change from historical average
  standardDeviation: number;      // Standard deviation of historical values
  zScore: number;                 // Z-score of current value
  trend: 'increasing' | 'decreasing' | 'stable';
  contribution: StagflationContribution;
  confidenceScore: number;        // 0-1, higher means more confident
  analysis: string;               // Textual analysis
}

/**
 * Time period for analysis
 */
export interface AnalysisPeriod {
  start: number;     // Unix timestamp
  end: number;       // Unix timestamp
  label?: string;    // Optional label (e.g., "Q1 2022")
}

/**
 * Composite index for stagflation
 */
export interface StagflationIndex {
  timestamp: number;
  value: number;      // 0-1, higher means stronger stagflation indicators
  breakdown: {
    inflationContribution: number;
    unemploymentContribution: number;
    growthContribution: number;
    otherContributions: Record<string, number>;
  };
  confidence: number;  // 0-1, higher means more confident
}

/**
 * Risk level for stagflation
 */
export enum StagflationRiskLevel {
  VERY_LOW = 'very_low',
  LOW = 'low',
  MODERATE = 'moderate',
  HIGH = 'high',
  VERY_HIGH = 'very_high'
}

/**
 * Comprehensive stagflation analysis
 */
export interface StagflationAnalysis {
  timestamp: number;
  period: AnalysisPeriod;
  indicators: StagflationIndicatorAnalysis[];
  compositeStagflationIndex: StagflationIndex;
  historicalComparison: {
    similarPeriods: AnalysisPeriod[];
    differenceFromPreviousAnalysis?: number;
    longestStagflationaryPeriod?: AnalysisPeriod;
  };
  riskLevel: StagflationRiskLevel;
  policyImplications: {
    monetaryPolicy: string[];
    fiscalPolicy: string[];
    supplyPolicy: string[];
  };
  confidenceScore: number;  // 0-1, higher means more confident
  summary: string;          // Textual summary
  recommendations: string[];
}

/**
 * Model for stagflation analysis
 */
export class StagflationAnalysisModel {
  private historicalData: Map<string, EconomicIndicator> = new Map();
  private weightsByType: Map<StagflationIndicatorType, number> = new Map();
  private thresholds: Map<string, { low: number; high: number }> = new Map();
  private indicators: Map<string, StagflationIndicatorType> = new Map();
  private isInitialized: boolean = false;
  
  /**
   * Initializes the model with default parameters
   */
  initialize(): void {
    if (this.isInitialized) {
      return;
    }
    
    // Set default weights for indicator types
    this.weightsByType.set(StagflationIndicatorType.INFLATION, 0.25);
    this.weightsByType.set(StagflationIndicatorType.UNEMPLOYMENT, 0.25);
    this.weightsByType.set(StagflationIndicatorType.ECONOMIC_GROWTH, 0.2);
    this.weightsByType.set(StagflationIndicatorType.PRODUCTIVITY, 0.1);
    this.weightsByType.set(StagflationIndicatorType.ENERGY_PRICES, 0.05);
    this.weightsByType.set(StagflationIndicatorType.WAGE_GROWTH, 0.05);
    this.weightsByType.set(StagflationIndicatorType.CAPACITY_UTILIZATION, 0.05);
    this.weightsByType.set(StagflationIndicatorType.SUPPLY_CHAIN, 0.02);
    this.weightsByType.set(StagflationIndicatorType.CONSUMER_SENTIMENT, 0.02);
    this.weightsByType.set(StagflationIndicatorType.BUSINESS_CONFIDENCE, 0.01);
    
    // Set default thresholds for common indicators
    this.thresholds.set('inflation_cpi', { low: 2.0, high: 5.0 }); // CPI inflation
    this.thresholds.set('inflation_pce', { low: 1.5, high: 4.0 }); // PCE inflation
    this.thresholds.set('unemployment_rate', { low: 4.0, high: 7.0 }); // Unemployment rate
    this.thresholds.set('real_gdp_growth', { low: 1.0, high: 3.0 }); // Real GDP growth
    this.thresholds.set('labor_productivity', { low: 0.5, high: 2.0 }); // Labor productivity growth
    this.thresholds.set('energy_price_index', { low: 10.0, high: 20.0 }); // Energy price index % change
    this.thresholds.set('average_hourly_earnings', { low: 2.0, high: 5.0 }); // Wage growth
    this.thresholds.set('capacity_utilization_rate', { low: 70.0, high: 85.0 }); // Capacity utilization
    this.thresholds.set('supplier_delivery_index', { low: 45.0, high: 55.0 }); // Supplier delivery times
    this.thresholds.set('consumer_confidence_index', { low: 70.0, high: 110.0 }); // Consumer confidence
    this.thresholds.set('business_confidence_index', { low: 90.0, high: 110.0 }); // Business confidence
    
    // Map indicators to types
    this.indicators.set('inflation_cpi', StagflationIndicatorType.INFLATION);
    this.indicators.set('inflation_pce', StagflationIndicatorType.INFLATION);
    this.indicators.set('inflation_ppi', StagflationIndicatorType.INFLATION);
    this.indicators.set('inflation_core_cpi', StagflationIndicatorType.INFLATION);
    this.indicators.set('inflation_core_pce', StagflationIndicatorType.INFLATION);
    this.indicators.set('unemployment_rate', StagflationIndicatorType.UNEMPLOYMENT);
    this.indicators.set('unemployment_u6', StagflationIndicatorType.UNEMPLOYMENT);
    this.indicators.set('labor_force_participation', StagflationIndicatorType.UNEMPLOYMENT);
    this.indicators.set('real_gdp_growth', StagflationIndicatorType.ECONOMIC_GROWTH);
    this.indicators.set('industrial_production', StagflationIndicatorType.ECONOMIC_GROWTH);
    this.indicators.set('labor_productivity', StagflationIndicatorType.PRODUCTIVITY);
    this.indicators.set('total_factor_productivity', StagflationIndicatorType.PRODUCTIVITY);
    this.indicators.set('multifactor_productivity', StagflationIndicatorType.PRODUCTIVITY);
    this.indicators.set('energy_price_index', StagflationIndicatorType.ENERGY_PRICES);
    this.indicators.set('oil_price', StagflationIndicatorType.ENERGY_PRICES);
    this.indicators.set('natural_gas_price', StagflationIndicatorType.ENERGY_PRICES);
    this.indicators.set('average_hourly_earnings', StagflationIndicatorType.WAGE_GROWTH);
    this.indicators.set('emp_cost_index', StagflationIndicatorType.WAGE_GROWTH);
    this.indicators.set('capacity_utilization_rate', StagflationIndicatorType.CAPACITY_UTILIZATION);
    this.indicators.set('supplier_delivery_index', StagflationIndicatorType.SUPPLY_CHAIN);
    this.indicators.set('global_supply_chain_pressure', StagflationIndicatorType.SUPPLY_CHAIN);
    this.indicators.set('consumer_confidence_index', StagflationIndicatorType.CONSUMER_SENTIMENT);
    this.indicators.set('business_confidence_index', StagflationIndicatorType.BUSINESS_CONFIDENCE);
    
    this.isInitialized = true;
  }
  
  /**
   * Loads indicator data into the model
   * @param indicators Economic indicators to load
   */
  loadIndicators(indicators: EconomicIndicator[]): void {
    for (const indicator of indicators) {
      this.historicalData.set(indicator.id, indicator);
    }
  }
  
  /**
   * Sets custom weights for indicator types
   * @param weights Map of indicator types to weights
   */
  setWeights(weights: Map<StagflationIndicatorType, number>): void {
    // Validate weights sum to 1
    const sum = Array.from(weights.values()).reduce((a, b) => a + b, 0);
    if (Math.abs(sum - 1.0) > 0.001) {
      throw new Error(`Weights must sum to 1.0, got ${sum}`);
    }
    
    this.weightsByType = new Map(weights);
  }
  
  /**
   * Sets custom thresholds for indicators
   * @param thresholds Map of indicator IDs to thresholds
   */
  setThresholds(thresholds: Map<string, { low: number; high: number }>): void {
    for (const [id, threshold] of thresholds.entries()) {
      this.thresholds.set(id, { ...threshold });
    }
  }
  
  /**
   * Gets the stagflation contribution of an indicator value
   * @param indicatorId Indicator ID
   * @param value Indicator value
   * @returns Stagflation contribution
   */
  getStagflationContribution(indicatorId: string, value: number): StagflationContribution {
    const threshold = this.thresholds.get(indicatorId);
    if (!threshold) {
      return StagflationContribution.NEUTRAL;
    }
    
    const indicatorType = this.indicators.get(indicatorId);
    
    // Different logic based on indicator type
    if (indicatorType === StagflationIndicatorType.INFLATION) {
      // For inflation, higher values indicate stagflation
      if (value < threshold.low) return StagflationContribution.STRONG_NEGATIVE;
      if (value < (threshold.low + threshold.high) / 2) return StagflationContribution.NEGATIVE;
      if (value < threshold.high) return StagflationContribution.POSITIVE;
      return StagflationContribution.STRONG_POSITIVE;
    } 
    else if (indicatorType === StagflationIndicatorType.UNEMPLOYMENT) {
      // For unemployment, higher values indicate stagflation
      if (value < threshold.low) return StagflationContribution.STRONG_NEGATIVE;
      if (value < (threshold.low + threshold.high) / 2) return StagflationContribution.NEGATIVE;
      if (value < threshold.high) return StagflationContribution.POSITIVE;
      return StagflationContribution.STRONG_POSITIVE;
    }
    else if (indicatorType === StagflationIndicatorType.ECONOMIC_GROWTH) {
      // For economic growth, lower values indicate stagflation
      if (value < 0) return StagflationContribution.STRONG_POSITIVE;
      if (value < threshold.low) return StagflationContribution.POSITIVE;
      if (value < threshold.high) return StagflationContribution.NEGATIVE;
      return StagflationContribution.STRONG_NEGATIVE;
    }
    else if (indicatorType === StagflationIndicatorType.PRODUCTIVITY) {
      // For productivity, lower values indicate stagflation
      if (value < 0) return StagflationContribution.STRONG_POSITIVE;
      if (value < threshold.low) return StagflationContribution.POSITIVE;
      if (value < threshold.high) return StagflationContribution.NEGATIVE;
      return StagflationContribution.STRONG_NEGATIVE;
    }
    else if (indicatorType === StagflationIndicatorType.ENERGY_PRICES) {
      // For energy prices, higher values indicate stagflation
      if (value < threshold.low) return StagflationContribution.STRONG_NEGATIVE;
      if (value < (threshold.low + threshold.high) / 2) return StagflationContribution.NEGATIVE;
      if (value < threshold.high) return StagflationContribution.POSITIVE;
      return StagflationContribution.STRONG_POSITIVE;
    }
    else if (indicatorType === StagflationIndicatorType.WAGE_GROWTH) {
      // For wage growth, higher values generally contradict stagflation (if not caused by inflation)
      // This is context-dependent though
      if (value < threshold.low) return StagflationContribution.POSITIVE;
      if (value < threshold.high) return StagflationContribution.NEUTRAL;
      return StagflationContribution.NEGATIVE;
    }
    else if (indicatorType === StagflationIndicatorType.CAPACITY_UTILIZATION) {
      // For capacity utilization, lower values indicate stagflation
      if (value < threshold.low) return StagflationContribution.STRONG_POSITIVE;
      if (value < (threshold.low + threshold.high) / 2) return StagflationContribution.POSITIVE;
      if (value < threshold.high) return StagflationContribution.NEGATIVE;
      return StagflationContribution.STRONG_NEGATIVE;
    }
    else if (indicatorType === StagflationIndicatorType.SUPPLY_CHAIN) {
      // For supply chain disruptions, higher values indicate stagflation
      // Assuming higher values = more disruption
      if (value < threshold.low) return StagflationContribution.STRONG_NEGATIVE;
      if (value < (threshold.low + threshold.high) / 2) return StagflationContribution.NEGATIVE;
      if (value < threshold.high) return StagflationContribution.POSITIVE;
      return StagflationContribution.STRONG_POSITIVE;
    }
    else if (
      indicatorType === StagflationIndicatorType.CONSUMER_SENTIMENT ||
      indicatorType === StagflationIndicatorType.BUSINESS_CONFIDENCE
    ) {
      // For sentiment/confidence, lower values indicate stagflation
      if (value < threshold.low) return StagflationContribution.STRONG_POSITIVE;
      if (value < (threshold.low + threshold.high) / 2) return StagflationContribution.POSITIVE;
      if (value < threshold.high) return StagflationContribution.NEGATIVE;
      return StagflationContribution.STRONG_NEGATIVE;
    }
    
    return StagflationContribution.NEUTRAL;
  }
  
  /**
   * Analyzes an economic indicator for stagflation
   * @param indicator Economic indicator to analyze
   * @param currentPeriod Analysis period
   * @param baselinePeriod Optional baseline period for comparison
   * @returns Stagflation indicator analysis
   */
  analyzeIndicator(
    indicator: EconomicIndicator,
    currentPeriod: AnalysisPeriod,
    baselinePeriod?: AnalysisPeriod
  ): StagflationIndicatorAnalysis {
    // Use default baseline if not provided
    if (!baselinePeriod) {
      // Default to 10-year baseline
      const tenYearsMs = 10 * 365 * 24 * 60 * 60 * 1000;
      baselinePeriod = {
        start: currentPeriod.start - tenYearsMs,
        end: currentPeriod.start
      };
    }
    
    // Get current value (most recent value in current period)
    const currentValues = indicator.timeSeries
      .filter(point => point.timestamp >= currentPeriod.start && point.timestamp <= currentPeriod.end)
      .sort((a, b) => b.timestamp - a.timestamp); // Most recent first
    
    const currentValue = currentValues.length > 0 ? currentValues[0].value : 0;
    
    // Get historical values
    const historicalValues = indicator.timeSeries
      .filter(point => point.timestamp >= baselinePeriod.start && point.timestamp <= baselinePeriod.end)
      .map(point => point.value);
    
    // Calculate statistics
    const historicalAverage = this.calculateAverage(historicalValues);
    const standardDeviation = this.calculateStandardDeviation(historicalValues);
    const zScore = standardDeviation !== 0 ? 
      (currentValue - historicalAverage) / standardDeviation : 0;
    
    // Calculate percent change
    const percentChange = historicalAverage !== 0 ? 
      ((currentValue - historicalAverage) / historicalAverage) * 100 : 0;
    
    // Determine trend
    const trend = this.determineTrend(currentValues);
    
    // Determine type
    const type = this.indicators.get(indicator.id) || StagflationIndicatorType.INFLATION;
    
    // Determine contribution
    const contribution = this.getStagflationContribution(indicator.id, currentValue);
    
    // Calculate confidence
    const confidenceScore = this.calculateConfidence(
      indicator, 
      currentValues.length, 
      historicalValues.length, 
      standardDeviation
    );
    
    // Generate textual analysis
    const analysis = this.generateIndicatorAnalysis(
      indicator,
      currentValue,
      historicalAverage,
      percentChange,
      zScore,
      trend,
      contribution
    );
    
    return {
      indicator,
      type,
      currentValue,
      historicalAverage,
      percentChange,
      standardDeviation,
      zScore,
      trend,
      contribution,
      confidenceScore,
      analysis
    };
  }
  
  /**
   * Analyzes economic data for stagflation indicators
   * @param indicators Economic indicators to analyze
   * @param currentPeriod Analysis period
   * @param baselinePeriod Optional baseline period for comparison
   * @returns Comprehensive stagflation analysis
   */
  analyzeStagflation(
    indicators: EconomicIndicator[],
    currentPeriod: AnalysisPeriod,
    baselinePeriod?: AnalysisPeriod
  ): StagflationAnalysis {
    // Ensure model is initialized
    if (!this.isInitialized) {
      this.initialize();
    }
    
    // Load indicators
    this.loadIndicators(indicators);
    
    // Analyze each indicator
    const indicatorAnalyses: StagflationIndicatorAnalysis[] = [];
    
    for (const indicator of indicators) {
      const analysis = this.analyzeIndicator(indicator, currentPeriod, baselinePeriod);
      indicatorAnalyses.push(analysis);
    }
    
    // Calculate composite stagflation index
    const compositeStagflationIndex = this.calculateStagflationIndex(indicatorAnalyses);
    
    // Identify similar historical periods
    const similarPeriods = this.findSimilarHistoricalPeriods(indicatorAnalyses, currentPeriod);
    
    // Determine risk level
    const riskLevel = this.determineStagflationRiskLevel(compositeStagflationIndex.value);
    
    // Generate policy implications
    const policyImplications = this.generatePolicyImplications(
      indicatorAnalyses,
      compositeStagflationIndex,
      riskLevel
    );
    
    // Calculate overall confidence
    const confidenceScore = this.calculateOverallConfidence(indicatorAnalyses);
    
    // Generate summary
    const summary = this.generateStagflationSummary(
      indicatorAnalyses,
      compositeStagflationIndex,
      riskLevel,
      currentPeriod
    );
    
    // Generate recommendations
    const recommendations = this.generateRecommendations(
      indicatorAnalyses,
      compositeStagflationIndex,
      riskLevel
    );
    
    return {
      timestamp: Date.now(),
      period: currentPeriod,
      indicators: indicatorAnalyses,
      compositeStagflationIndex,
      historicalComparison: {
        similarPeriods
      },
      riskLevel,
      policyImplications,
      confidenceScore,
      summary,
      recommendations
    };
  }
  
  /**
   * Calculates the average of an array of numbers
   * @param values Values to average
   * @returns Average value
   */
  private calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
  }
  
  /**
   * Calculates the standard deviation of an array of numbers
   * @param values Values to calculate standard deviation for
   * @returns Standard deviation
   */
  private calculateStandardDeviation(values: number[]): number {
    if (values.length === 0) return 0;
    
    const avg = this.calculateAverage(values);
    const squareDiffs = values.map(value => {
      const diff = value - avg;
      return diff * diff;
    });
    
    const avgSquareDiff = this.calculateAverage(squareDiffs);
    return Math.sqrt(avgSquareDiff);
  }
  
  /**
   * Determines the trend of a time series
   * @param timeSeries Time series data
   * @returns Trend direction
   */
  private determineTrend(timeSeries: { timestamp: number; value: number }[]): 'increasing' | 'decreasing' | 'stable' {
    if (timeSeries.length < 2) return 'stable';
    
    // Sort by timestamp (oldest first)
    const sorted = [...timeSeries].sort((a, b) => a.timestamp - b.timestamp);
    
    // Calculate linear regression slope
    const n = sorted.length;
    let sumX = 0;
    let sumY = 0;
    let sumXY = 0;
    let sumXX = 0;
    
    for (let i = 0; i < n; i++) {
      const x = i;  // Use index as x-value
      const y = sorted[i].value;
      
      sumX += x;
      sumY += y;
      sumXY += x * y;
      sumXX += x * x;
    }
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    
    // Determine trend direction based on slope
    const THRESHOLD = 0.01;  // Threshold for "stable"
    
    if (slope > THRESHOLD) return 'increasing';
    if (slope < -THRESHOLD) return 'decreasing';
    return 'stable';
  }
  
  /**
   * Calculates confidence score for an indicator analysis
   * @param indicator Economic indicator
   * @param currentDataPoints Number of data points in current period
   * @param historicalDataPoints Number of data points in historical period
   * @param standardDeviation Standard deviation of historical values
   * @returns Confidence score (0-1)
   */
  private calculateConfidence(
    indicator: EconomicIndicator,
    currentDataPoints: number,
    historicalDataPoints: number,
    standardDeviation: number
  ): number {
    // Start with base confidence
    let confidence = 0.7;
    
    // Adjust based on data points
    if (currentDataPoints < 3) {
      confidence -= 0.2;  // Penalize low current data points
    }
    
    if (historicalDataPoints < 10) {
      confidence -= 0.1;  // Penalize low historical data points
    }
    
    // Adjust based on standard deviation (high variance = lower confidence)
    const relativeSd = standardDeviation / Math.abs(this.calculateAverage(
      indicator.timeSeries.map(point => point.value)
    ));
    
    if (relativeSd > 0.5) {
      confidence -= 0.2;  // High relative standard deviation
    }
    
    // Adjust based on data source reliability (mock implementation)
    if (indicator.source === 'government') {
      confidence += 0.1;  // Assume government sources are reliable
    } else if (indicator.source === 'academic') {
      confidence += 0.05;  // Academic sources
    }
    
    // Adjust based on frequency (higher frequency = more confidence)
    if (indicator.frequency === 'daily' || indicator.frequency === 'weekly') {
      confidence += 0.05;
    } else if (indicator.frequency === 'annually') {
      confidence -= 0.05;
    }
    
    // Ensure confidence is between 0 and 1
    return Math.max(0, Math.min(1, confidence));
  }
  
  /**
   * Generates textual analysis for an indicator
   * @param indicator Economic indicator
   * @param currentValue Current value
   * @param historicalAverage Historical average
   * @param percentChange Percent change from historical average
   * @param zScore Z-score of current value
   * @param trend Trend direction
   * @param contribution Stagflation contribution
   * @returns Textual analysis
   */
  private generateIndicatorAnalysis(
    indicator: EconomicIndicator,
    currentValue: number,
    historicalAverage: number,
    percentChange: number,
    zScore: number,
    trend: 'increasing' | 'decreasing' | 'stable',
    contribution: StagflationContribution
  ): string {
    const indicatorType = this.indicators.get(indicator.id) || StagflationIndicatorType.INFLATION;
    
    let analysis = `${indicator.name} is currently at ${currentValue.toFixed(2)} ${indicator.unit}, `;
    
    // Add comparison to historical average
    if (Math.abs(percentChange) < 1) {
      analysis += `which is essentially in line with the historical average of ${historicalAverage.toFixed(2)} ${indicator.unit}. `;
    } else if (percentChange > 0) {
      analysis += `which is ${percentChange.toFixed(1)}% higher than the historical average of ${historicalAverage.toFixed(2)} ${indicator.unit}. `;
    } else {
      analysis += `which is ${Math.abs(percentChange).toFixed(1)}% lower than the historical average of ${historicalAverage.toFixed(2)} ${indicator.unit}. `;
    }
    
    // Add statistical significance
    if (Math.abs(zScore) < 1) {
      analysis += `This value is within normal historical variation. `;
    } else if (Math.abs(zScore) < 2) {
      analysis += `This value is somewhat ${zScore > 0 ? 'elevated' : 'depressed'} compared to historical norms. `;
    } else {
      analysis += `This value is significantly ${zScore > 0 ? 'elevated' : 'depressed'} compared to historical norms. `;
    }
    
    // Add trend
    if (trend === 'increasing') {
      analysis += `The indicator is showing an increasing trend. `;
    } else if (trend === 'decreasing') {
      analysis += `The indicator is showing a decreasing trend. `;
    } else {
      analysis += `The indicator is relatively stable over the analyzed period. `;
    }
    
    // Add interpretation based on indicator type and contribution
    switch (indicatorType) {
      case StagflationIndicatorType.INFLATION:
        if (contribution > 0) {
          analysis += `The elevated inflation rate is a classic sign of stagflationary pressure. `;
        } else {
          analysis += `The current inflation rate does not suggest stagflationary pressures. `;
        }
        break;
        
      case StagflationIndicatorType.UNEMPLOYMENT:
        if (contribution > 0) {
          analysis += `The elevated unemployment rate, combined with other indicators, suggests potential stagflationary conditions. `;
        } else {
          analysis += `The current unemployment rate does not indicate the stagnation component of stagflation. `;
        }
        break;
        
      case StagflationIndicatorType.ECONOMIC_GROWTH:
        if (contribution > 0) {
          analysis += `The weak economic growth figures suggest the stagnation component of stagflation may be present. `;
        } else {
          analysis += `The current economic growth rate contradicts the stagnation component of stagflation. `;
        }
        break;
        
      case StagflationIndicatorType.PRODUCTIVITY:
        if (contribution > 0) {
          analysis += `Declining productivity is often associated with stagflationary periods. `;
        } else {
          analysis += `Current productivity levels do not suggest stagflationary pressures. `;
        }
        break;
        
      case StagflationIndicatorType.ENERGY_PRICES:
        if (contribution > 0) {
          analysis += `Elevated energy prices can be both a cause and symptom of stagflationary conditions. `;
        } else {
          analysis += `Current energy prices do not suggest a supply shock that could trigger stagflation. `;
        }
        break;
        
      default:
        if (contribution > 0) {
          analysis += `This indicator suggests potential stagflationary pressures. `;
        } else if (contribution < 0) {
          analysis += `This indicator contradicts potential stagflationary conditions. `;
        } else {
          analysis += `This indicator is neutral with respect to stagflationary conditions. `;
        }
    }
    
    return analysis;
  }
  
  /**
   * Calculates the stagflation index based on indicator analyses
   * @param analyses Stagflation indicator analyses
   * @returns Stagflation index
   */
  private calculateStagflationIndex(analyses: StagflationIndicatorAnalysis[]): StagflationIndex {
    // Initialize contribution totals
    let inflationContribution = 0;
    let inflationWeight = 0;
    
    let unemploymentContribution = 0;
    let unemploymentWeight = 0;
    
    let growthContribution = 0;
    let growthWeight = 0;
    
    const otherContributions: Record<string, number> = {};
    const otherWeights: Record<string, number> = {};
    
    // Initialize all types in otherContributions and otherWeights
    for (const type of Object.values(StagflationIndicatorType)) {
      if (
        type !== StagflationIndicatorType.INFLATION &&
        type !== StagflationIndicatorType.UNEMPLOYMENT &&
        type !== StagflationIndicatorType.ECONOMIC_GROWTH
      ) {
        otherContributions[type] = 0;
        otherWeights[type] = 0;
      }
    }
    
    // Calculate weighted contributions
    for (const analysis of analyses) {
      const weight = this.weightsByType.get(analysis.type) || 0;
      const contribValue = analysis.contribution;
      
      switch (analysis.type) {
        case StagflationIndicatorType.INFLATION:
          inflationContribution += contribValue * weight;
          inflationWeight += weight;
          break;
          
        case StagflationIndicatorType.UNEMPLOYMENT:
          unemploymentContribution += contribValue * weight;
          unemploymentWeight += weight;
          break;
          
        case StagflationIndicatorType.ECONOMIC_GROWTH:
          growthContribution += contribValue * weight;
          growthWeight += weight;
          break;
          
        default:
          otherContributions[analysis.type] += contribValue * weight;
          otherWeights[analysis.type] += weight;
      }
    }
    
    // Normalize contributions
    if (inflationWeight > 0) {
      inflationContribution /= inflationWeight;
    }
    
    if (unemploymentWeight > 0) {
      unemploymentContribution /= unemploymentWeight;
    }
    
    if (growthWeight > 0) {
      growthContribution /= growthWeight;
    }
    
    for (const type of Object.keys(otherContributions)) {
      if (otherWeights[type] > 0) {
        otherContributions[type] /= otherWeights[type];
      }
    }
    
    // Calculate the overall index
    const normalizedInflation = (inflationContribution + 2) / 4; // -2 to 2 -> 0 to 1
    const normalizedUnemployment = (unemploymentContribution + 2) / 4;
    const normalizedGrowth = (growthContribution + 2) / 4;
    
    const normalizedOthers: Record<string, number> = {};
    for (const type of Object.keys(otherContributions)) {
      normalizedOthers[type] = (otherContributions[type] + 2) / 4;
    }
    
    // Weights for the composite index
    const inflationIndexWeight = this.weightsByType.get(StagflationIndicatorType.INFLATION) || 0.25;
    const unemploymentIndexWeight = this.weightsByType.get(StagflationIndicatorType.UNEMPLOYMENT) || 0.25;
    const growthIndexWeight = this.weightsByType.get(StagflationIndicatorType.ECONOMIC_GROWTH) || 0.2;
    const othersIndexWeight = 1 - inflationIndexWeight - unemploymentIndexWeight - growthIndexWeight;
    
    // Calculate weighted average of other contributions
    let otherContributionsSum = 0;
    let otherWeightsSum = 0;
    
    for (const type of Object.keys(normalizedOthers)) {
      const weight = this.weightsByType.get(type as StagflationIndicatorType) || 0;
      otherContributionsSum += normalizedOthers[type] * weight;
      otherWeightsSum += weight;
    }
    
    const normalizedOthersAvg = otherWeightsSum > 0 ? otherContributionsSum / otherWeightsSum : 0;
    
    // Calculate final index
    const index = 
      normalizedInflation * inflationIndexWeight +
      normalizedUnemployment * unemploymentIndexWeight +
      normalizedGrowth * growthIndexWeight +
      normalizedOthersAvg * othersIndexWeight;
    
    // Calculate confidence
    const confidence = this.calculateOverallConfidence(analyses);
    
    return {
      timestamp: Date.now(),
      value: index,
      breakdown: {
        inflationContribution: normalizedInflation,
        unemploymentContribution: normalizedUnemployment,
        growthContribution: normalizedGrowth,
        otherContributions: normalizedOthers
      },
      confidence
    };
  }
  
  /**
   * Determines the stagflation risk level based on index value
   * @param indexValue Stagflation index value
   * @returns Stagflation risk level
   */
  private determineStagflationRiskLevel(indexValue: number): StagflationRiskLevel {
    if (indexValue < 0.2) return StagflationRiskLevel.VERY_LOW;
    if (indexValue < 0.4) return StagflationRiskLevel.LOW;
    if (indexValue < 0.6) return StagflationRiskLevel.MODERATE;
    if (indexValue < 0.8) return StagflationRiskLevel.HIGH;
    return StagflationRiskLevel.VERY_HIGH;
  }
  
  /**
   * Finds similar historical periods with comparable stagflation indicators
   * @param analyses Stagflation indicator analyses
   * @param currentPeriod Analysis period
   * @returns Array of similar historical periods
   */
  private findSimilarHistoricalPeriods(
    analyses: StagflationIndicatorAnalysis[],
    currentPeriod: AnalysisPeriod
  ): AnalysisPeriod[] {
    // This is a placeholder implementation
    // In a real implementation, this would:
    // 1. Look for historical periods with similar indicator patterns
    // 2. Calculate similarity scores
    // 3. Return the most similar periods
    
    // For now, return empty array
    return [];
  }
  
  /**
   * Calculates overall confidence score for analyses
   * @param analyses Stagflation indicator analyses
   * @returns Overall confidence score
   */
  private calculateOverallConfidence(analyses: StagflationIndicatorAnalysis[]): number {
    if (analyses.length === 0) return 0;
    
    let weightedConfidence = 0;
    let totalWeight = 0;
    
    for (const analysis of analyses) {
      const weight = this.weightsByType.get(analysis.type) || 0;
      weightedConfidence += analysis.confidenceScore * weight;
      totalWeight += weight;
    }
    
    return totalWeight > 0 ? weightedConfidence / totalWeight : 0;
  }
  
  /**
   * Generates policy implications based on stagflation analysis
   * @param analyses Stagflation indicator analyses
   * @param index Stagflation index
   * @param riskLevel Stagflation risk level
   * @returns Policy implications
   */
  private generatePolicyImplications(
    analyses: StagflationIndicatorAnalysis[],
    index: StagflationIndex,
    riskLevel: StagflationRiskLevel
  ): { monetaryPolicy: string[]; fiscalPolicy: string[]; supplyPolicy: string[] } {
    // Initialize policy implications
    const monetaryPolicy: string[] = [];
    const fiscalPolicy: string[] = [];
    const supplyPolicy: string[] = [];
    
    // Get key indicators
    const inflationAnalyses = analyses.filter(a => 
      a.type === StagflationIndicatorType.INFLATION
    );
    
    const unemploymentAnalyses = analyses.filter(a => 
      a.type === StagflationIndicatorType.UNEMPLOYMENT
    );
    
    const growthAnalyses = analyses.filter(a => 
      a.type === StagflationIndicatorType.ECONOMIC_GROWTH
    );
    
    const energyAnalyses = analyses.filter(a => 
      a.type === StagflationIndicatorType.ENERGY_PRICES
    );
    
    const supplyChainAnalyses = analyses.filter(a => 
      a.type === StagflationIndicatorType.SUPPLY_CHAIN
    );
    
    // Generate monetary policy implications
    if (riskLevel === StagflationRiskLevel.VERY_LOW || riskLevel === StagflationRiskLevel.LOW) {
      monetaryPolicy.push(
        "Standard monetary policy tools can be employed as needed."
      );
    } else if (riskLevel === StagflationRiskLevel.MODERATE) {
      monetaryPolicy.push(
        "Balance inflation control with growth support when adjusting interest rates.",
        "Consider forward guidance to manage market expectations about policy trajectory."
      );
    } else {
      monetaryPolicy.push(
        "Traditional monetary policy faces challenges in stagflationary environments.",
        "Consider prioritizing inflation control while communicating longer-term commitment to economic stability.",
        "Evaluate targeted lending facilities for sectors most affected by supply constraints."
      );
    }
    
    // Generate fiscal policy implications
    if (riskLevel === StagflationRiskLevel.VERY_LOW || riskLevel === StagflationRiskLevel.LOW) {
      fiscalPolicy.push(
        "Standard fiscal policy tools can be employed as needed."
      );
    } else if (riskLevel === StagflationRiskLevel.MODERATE) {
      fiscalPolicy.push(
        "Consider targeted fiscal support for sectors experiencing productivity challenges.",
        "Evaluate temporary tax relief for key supply chain components."
      );
    } else {
      fiscalPolicy.push(
        "Target fiscal support to sectors facing genuine supply constraints rather than broad stimulus.",
        "Consider investment tax credits to encourage productivity-enhancing capital investment.",
        "Evaluate means-tested support for households most affected by high inflation."
      );
    }
    
    // Generate supply policy implications
    if (riskLevel === StagflationRiskLevel.VERY_LOW || riskLevel === StagflationRiskLevel.LOW) {
      supplyPolicy.push(
        "Maintain focus on long-term productivity growth and supply chain resilience."
      );
    } else if (riskLevel === StagflationRiskLevel.MODERATE) {
      supplyPolicy.push(
        "Identify and address key supply bottlenecks through regulatory streamlining.",
        "Develop contingency plans for critical supply chain components."
      );
    } else {
      supplyPolicy.push(
        "Implement aggressive supply-side reforms to address structural bottlenecks.",
        "Consider temporary regulatory relief for critical supply chains.",
        "Invest in workforce development and training to address structural unemployment.",
        "Develop emergency plans for critical resource allocation if supply constraints worsen."
      );
    }
    
    // Add specific recommendations based on indicators
    
    // Energy prices
    if (energyAnalyses.length > 0 && energyAnalyses.some(a => a.contribution > 0)) {
      supplyPolicy.push(
        "Implement strategic energy reserve management to mitigate price volatility.",
        "Consider expedited permitting for energy production and distribution projects."
      );
      
      fiscalPolicy.push(
        "Evaluate targeted energy subsidies for vulnerable households and critical industries."
      );
    }
    
    // Supply chain issues
    if (supplyChainAnalyses.length > 0 && supplyChainAnalyses.some(a => a.contribution > 0)) {
      supplyPolicy.push(
        "Develop supply chain resilience strategies for critical goods and components.",
        "Consider temporary measures to eliminate supply chain bottlenecks.",
        "Support investment in domestic production capacity for strategic goods."
      );
      
      fiscalPolicy.push(
        "Implement investment incentives for supply chain diversification."
      );
    }
    
    return {
      monetaryPolicy,
      fiscalPolicy,
      supplyPolicy
    };
  }
  
  /**
   * Generates recommendations based on stagflation analysis
   * @param analyses Stagflation indicator analyses
   * @param index Stagflation index
   * @param riskLevel Stagflation risk level
   * @returns Array of recommendations
   */
  private generateRecommendations(
    analyses: StagflationIndicatorAnalysis[],
    index: StagflationIndex,
    riskLevel: StagflationRiskLevel
  ): string[] {
    const recommendations: string[] = [];
    
    // General recommendations based on risk level
    if (riskLevel === StagflationRiskLevel.VERY_LOW) {
      recommendations.push(
        "Continue regular monitoring of inflation and growth indicators.",
        "Maintain existing policy frameworks."
      );
    } else if (riskLevel === StagflationRiskLevel.LOW) {
      recommendations.push(
        "Increase monitoring frequency for key stagflation indicators.",
        "Review contingency plans for potential stagflationary scenarios.",
        "Ensure policy coordination mechanisms are functioning effectively."
      );
    } else if (riskLevel === StagflationRiskLevel.MODERATE) {
      recommendations.push(
        "Establish an inter-agency stagflation monitoring task force.",
        "Develop early intervention thresholds for key indicators.",
        "Begin stress testing policy responses for more severe stagflation scenarios.",
        "Enhance communication channels with market participants about policy intentions."
      );
    } else if (riskLevel === StagflationRiskLevel.HIGH) {
      recommendations.push(
        "Activate coordination mechanisms between monetary, fiscal, and supply-side policymakers.",
        "Implement regular public communications about anti-stagflation strategy.",
        "Begin gradual implementation of supply-side reforms identified in contingency planning.",
        "Prioritize policies that simultaneously address both inflation and growth challenges."
      );
    } else if (riskLevel === StagflationRiskLevel.VERY_HIGH) {
      recommendations.push(
        "Implement comprehensive anti-stagflation strategy across monetary, fiscal, and supply policy domains.",
        "Establish emergency policy coordination mechanisms with enhanced authorities.",
        "Consider temporary extraordinary measures to address severe supply constraints.",
        "Implement heightened monitoring of financial stability risks associated with stagflationary environment."
      );
    }
    
    // Additional recommendations based on specific indicators
    const highInflation = analyses.filter(a => 
      a.type === StagflationIndicatorType.INFLATION && a.contribution > 0
    );
    
    const highUnemployment = analyses.filter(a => 
      a.type === StagflationIndicatorType.UNEMPLOYMENT && a.contribution > 0
    );
    
    const lowGrowth = analyses.filter(a => 
      a.type === StagflationIndicatorType.ECONOMIC_GROWTH && a.contribution > 0
    );
    
    if (highInflation.length > 0 && highUnemployment.length > 0 && lowGrowth.length > 0) {
      // Classic stagflation pattern
      recommendations.push(
        "Focus on supply-side solutions rather than demand management.",
        "Consider targeted interventions for sectors most affected by both high inflation and low growth.",
        "Evaluate medium-term framework adjustments to anchor inflation expectations while supporting growth recovery."
      );
    }
    
    if (highInflation.length > 0 && index.breakdown.inflationContribution > 0.7) {
      recommendations.push(
        "Prioritize inflation control measures while remaining mindful of growth impacts.",
        "Enhance monitoring of inflation expectations and wage-setting behavior.",
        "Consider measures to address specific high-inflation categories where applicable."
      );
    }
    
    if (highUnemployment.length > 0 && index.breakdown.unemploymentContribution > 0.7) {
      recommendations.push(
        "Implement targeted labor market interventions focusing on sectors with structural challenges.",
        "Consider skill development programs aligned with sectors showing growth potential.",
        "Evaluate labor market flexibility reforms to facilitate sectoral adjustments."
      );
    }
    
    return recommendations;
  }
  
  /**
   * Generates a textual summary of stagflation analysis
   * @param analyses Stagflation indicator analyses
   * @param index Stagflation index
   * @param riskLevel Stagflation risk level
   * @param currentPeriod Analysis period
   * @returns Textual summary
   */
  private generateStagflationSummary(
    analyses: StagflationIndicatorAnalysis[],
    index: StagflationIndex,
    riskLevel: StagflationRiskLevel,
    currentPeriod: AnalysisPeriod
  ): string {
    let periodLabel = '';
    if (currentPeriod.label) {
      periodLabel = currentPeriod.label;
    } else {
      const startDate = new Date(currentPeriod.start);
      const endDate = new Date(currentPeriod.end);
      periodLabel = `${startDate.toLocaleDateString()} to ${endDate.toLocaleDateString()}`;
    }
    
    let summary = `Stagflation Risk Assessment for ${periodLabel}\n\n`;
    
    // Add risk level summary
    summary += `Overall Stagflation Risk Level: ${riskLevel}\n`;
    summary += `Stagflation Index: ${(index.value * 100).toFixed(1)}%\n\n`;
    
    // Add key contributors
    summary += 'Key Contributors to Stagflation Risk:\n';
    
    // Add inflation indicators
    const inflationIndicators = analyses.filter(a => 
      a.type === StagflationIndicatorType.INFLATION
    );
    
    if (inflationIndicators.length > 0) {
      const avgContribution = inflationIndicators.reduce(
        (sum, a) => sum + a.contribution, 0
      ) / inflationIndicators.length;
      
      summary += `- Inflation: ${avgContribution > 0 ? 'Contributing' : 'Contradicting'} to stagflation risk\n`;
      
      for (const indicator of inflationIndicators) {
        summary += `  - ${indicator.indicator.name}: ${indicator.currentValue.toFixed(2)} ${indicator.indicator.unit}\n`;
      }
    }
    
    // Add unemployment indicators
    const unemploymentIndicators = analyses.filter(a => 
      a.type === StagflationIndicatorType.UNEMPLOYMENT
    );
    
    if (unemploymentIndicators.length > 0) {
      const avgContribution = unemploymentIndicators.reduce(
        (sum, a) => sum + a.contribution, 0
      ) / unemploymentIndicators.length;
      
      summary += `- Unemployment: ${avgContribution > 0 ? 'Contributing' : 'Contradicting'} to stagflation risk\n`;
      
      for (const indicator of unemploymentIndicators) {
        summary += `  - ${indicator.indicator.name}: ${indicator.currentValue.toFixed(2)} ${indicator.indicator.unit}\n`;
      }
    }
    
    // Add economic growth indicators
    const growthIndicators = analyses.filter(a => 
      a.type === StagflationIndicatorType.ECONOMIC_GROWTH
    );
    
    if (growthIndicators.length > 0) {
      const avgContribution = growthIndicators.reduce(
        (sum, a) => sum + a.contribution, 0
      ) / growthIndicators.length;
      
      summary += `- Economic Growth: ${avgContribution > 0 ? 'Contributing' : 'Contradicting'} to stagflation risk\n`;
      
      for (const indicator of growthIndicators) {
        summary += `  - ${indicator.indicator.name}: ${indicator.currentValue.toFixed(2)} ${indicator.indicator.unit}\n`;
      }
    }
    
    // Add assessment summary based on risk level
    summary += '\nAssessment Summary:\n';
    
    if (riskLevel === StagflationRiskLevel.VERY_LOW) {
      summary += 'Current economic indicators show minimal signs of stagflationary pressure. ' +
        'The economy demonstrates healthy growth with managed inflation and stable employment levels.';
    } else if (riskLevel === StagflationRiskLevel.LOW) {
      summary += 'Economic indicators show some minor imbalances but remain largely within normal parameters. ' +
        'While certain sectors may experience isolated pressures, the broader economy shows limited stagflation risk.';
    } else if (riskLevel === StagflationRiskLevel.MODERATE) {
      summary += 'Several key indicators are showing moderate stagflationary pressures. ' +
        'The combination of slowing growth, elevated inflation, and employment challenges warrants ' +
        'increased monitoring and preliminary policy considerations.';
    } else if (riskLevel === StagflationRiskLevel.HIGH) {
      summary += 'Multiple indicators are demonstrating strong stagflationary characteristics. ' +
        'The economy is experiencing a challenging combination of elevated inflation alongside ' +
        'stagnant growth and employment metrics. This environment presents significant policy challenges ' +
        'that require careful coordination across monetary, fiscal, and supply-side domains.';
    } else if (riskLevel === StagflationRiskLevel.VERY_HIGH) {
      summary += 'Economic indicators demonstrate clear and consistent stagflationary patterns ' +
        'across multiple domains. The combination of persistent high inflation with stagnant growth ' +
        'and elevated unemployment presents severe policy challenges requiring comprehensive intervention ' +
        'strategies and close coordination among all economic policymakers.';
    }
    
    return summary;
  }
}

/**
 * Service for analyzing stagflation indicators and generating reports
 */
export class StagflationAnalysisService extends EventEmitter {
  private model: StagflationAnalysisModel;
  private indicatorStore: Map<string, EconomicIndicator> = new Map();
  private analysisHistory: Map<string, StagflationAnalysis> = new Map();
  private isInitialized: boolean = false;
  
  constructor() {
    super();
    this.model = new StagflationAnalysisModel();
  }
  
  /**
   * Initializes the stagflation analysis service
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }
    
    this.model.initialize();
    this.isInitialized = true;
    
    console.log('Stagflation analysis service initialized');
  }
  
  /**
   * Loads economic indicators into the service
   * @param indicators Economic indicators to load
   */
  loadIndicators(indicators: EconomicIndicator[]): void {
    for (const indicator of indicators) {
      this.indicatorStore.set(indicator.id, indicator);
    }
    
    // Load indicators into model
    this.model.loadIndicators(indicators);
  }
  
  /**
   * Gets an economic indicator by ID
   * @param indicatorId Indicator ID
   * @returns Economic indicator or undefined if not found
   */
  getIndicator(indicatorId: string): EconomicIndicator | undefined {
    return this.indicatorStore.get(indicatorId);
  }
  
  /**
   * Gets all loaded economic indicators
   * @returns Array of economic indicators
   */
  getAllIndicators(): EconomicIndicator[] {
    return Array.from(this.indicatorStore.values());
  }
  
  /**
   * Gets indicators of a specific type
   * @param type Stagflation indicator type
   * @returns Array of economic indicators of the specified type
   */
  getIndicatorsByType(type: StagflationIndicatorType): EconomicIndicator[] {
    const indicators: EconomicIndicator[] = [];
    
    for (const indicator of this.indicatorStore.values()) {
      const indicatorType = this.getIndicatorType(indicator.id);
      if (indicatorType === type) {
        indicators.push(indicator);
      }
    }
    
    return indicators;
  }
  
  /**
   * Gets the type of an economic indicator
   * @param indicatorId Indicator ID
   * @returns Stagflation indicator type or undefined if not found
   */
  private getIndicatorType(indicatorId: string): StagflationIndicatorType | undefined {
    const prefixMap: Record<string, StagflationIndicatorType> = {
      'inflation': StagflationIndicatorType.INFLATION,
      'unemployment': StagflationIndicatorType.UNEMPLOYMENT,
      'gdp': StagflationIndicatorType.ECONOMIC_GROWTH,
      'productivity': StagflationIndicatorType.PRODUCTIVITY,
      'energy': StagflationIndicatorType.ENERGY_PRICES,
      'wage': StagflationIndicatorType.WAGE_GROWTH,
      'capacity': StagflationIndicatorType.CAPACITY_UTILIZATION,
      'supply': StagflationIndicatorType.SUPPLY_CHAIN,
      'consumer': StagflationIndicatorType.CONSUMER_SENTIMENT,
      'business': StagflationIndicatorType.BUSINESS_CONFIDENCE
    };
    
    for (const [prefix, type] of Object.entries(prefixMap)) {
      if (indicatorId.startsWith(prefix)) {
        return type;
      }
    }
    
    return undefined;
  }
  
  /**
   * Analyzes current economic data for stagflation indicators
   * @param currentPeriod Analysis period
   * @param baselinePeriod Optional baseline period for comparison
   * @returns Comprehensive stagflation analysis
   */
  analyzeStagflation(
    currentPeriod: AnalysisPeriod,
    baselinePeriod?: AnalysisPeriod
  ): StagflationAnalysis {
    if (!this.isInitialized) {
      this.initialize();
    }
    
    const indicators = this.getAllIndicators();
    const analysis = this.model.analyzeStagflation(indicators, currentPeriod, baselinePeriod);
    
    // Store analysis in history
    const analysisId = `analysis_${Date.now()}`;
    this.analysisHistory.set(analysisId, analysis);
    
    // Emit event
    this.emit('analysisCompleted', analysis);
    
    return analysis;
  }
  
  /**
   * Gets historical stagflation analyses
   * @returns Array of stagflation analyses
   */
  getAnalysisHistory(): StagflationAnalysis[] {
    return Array.from(this.analysisHistory.values());
  }
  
  /**
   * Compares two stagflation analyses
   * @param firstAnalysisId First analysis ID
   * @param secondAnalysisId Second analysis ID
   * @returns Comparison of the two analyses
   */
  compareAnalyses(firstAnalysisId: string, secondAnalysisId: string): Record<string, any> {
    const first = this.analysisHistory.get(firstAnalysisId);
    const second = this.analysisHistory.get(secondAnalysisId);
    
    if (!first || !second) {
      throw new Error('One or both analyses not found');
    }
    
    // Calculate index difference
    const indexDiff = second.compositeStagflationIndex.value - first.compositeStagflationIndex.value;
    
    // Compare key indicators
    const indicatorComparisons: Record<string, any> = {};
    
    for (const secondIndicator of second.indicators) {
      const firstIndicator = first.indicators.find(i => 
        i.indicator.id === secondIndicator.indicator.id
      );
      
      if (firstIndicator) {
        indicatorComparisons[secondIndicator.indicator.id] = {
          name: secondIndicator.indicator.name,
          valueDiff: secondIndicator.currentValue - firstIndicator.currentValue,
          contributionDiff: secondIndicator.contribution - firstIndicator.contribution,
          trendChanged: secondIndicator.trend !== firstIndicator.trend
        };
      }
    }
    
    // Generate summary
    let summary = '';
    if (indexDiff > 0.1) {
      summary = 'Stagflation risk has increased significantly since the previous analysis.';
    } else if (indexDiff > 0.05) {
      summary = 'Stagflation risk has increased moderately since the previous analysis.';
    } else if (indexDiff > 0.01) {
      summary = 'Stagflation risk has increased slightly since the previous analysis.';
    } else if (indexDiff < -0.1) {
      summary = 'Stagflation risk has decreased significantly since the previous analysis.';
    } else if (indexDiff < -0.05) {
      summary = 'Stagflation risk has decreased moderately since the previous analysis.';
    } else if (indexDiff < -0.01) {
      summary = 'Stagflation risk has decreased slightly since the previous analysis.';
    } else {
      summary = 'Stagflation risk has remained relatively stable since the previous analysis.';
    }
    
    return {
      firstAnalysis: {
        timestamp: first.timestamp,
        period: first.period,
        riskLevel: first.riskLevel,
        index: first.compositeStagflationIndex.value
      },
      secondAnalysis: {
        timestamp: second.timestamp,
        period: second.period,
        riskLevel: second.riskLevel,
        index: second.compositeStagflationIndex.value
      },
      comparison: {
        indexDiff,
        riskLevelChange: second.riskLevel !== first.riskLevel,
        indicators: indicatorComparisons
      },
      summary
    };
  }
  
  /**
   * Generates a report for a stagflation analysis
   * @param analysisId Analysis ID
   * @param format Report format ('text', 'markdown', or 'html')
   * @returns Formatted report
   */
  generateReport(analysisId: string, format: 'text' | 'markdown' | 'html' = 'text'): string {
    const analysis = this.analysisHistory.get(analysisId);
    
    if (!analysis) {
      throw new Error(`Analysis ${analysisId} not found`);
    }
    
    if (format === 'text') {
      return this.generateTextReport(analysis);
    } else if (format === 'markdown') {
      return this.generateMarkdownReport(analysis);
    } else if (format === 'html') {
      return this.generateHtmlReport(analysis);
    } else {
      throw new Error(`Unsupported format: ${format}`);
    }
  }
  
  /**
   * Generates a text report for a stagflation analysis
   * @param analysis Stagflation analysis
   * @returns Text report
   */
  private generateTextReport(analysis: StagflationAnalysis): string {
    return analysis.summary;
  }
  
  /**
   * Generates a Markdown report for a stagflation analysis
   * @param analysis Stagflation analysis
   * @returns Markdown report
   */
  private generateMarkdownReport(analysis: StagflationAnalysis): string {
    let report = `# Stagflation Analysis Report\n\n`;
    
    // Period and date
    const date = new Date(analysis.timestamp).toLocaleDateString();
    let periodLabel = '';
    if (analysis.period.label) {
      periodLabel = analysis.period.label;
    } else {
      const startDate = new Date(analysis.period.start).toLocaleDateString();
      const endDate = new Date(analysis.period.end).toLocaleDateString();
      periodLabel = `${startDate} to ${endDate}`;
    }
    
    report += `Analysis Date: ${date}\n`;
    report += `Analysis Period: ${periodLabel}\n\n`;
    
    // Risk level and index
    report += `## Summary\n\n`;
    report += `**Stagflation Risk Level: ${analysis.riskLevel}**\n\n`;
    report += `**Stagflation Index: ${(analysis.compositeStagflationIndex.value * 100).toFixed(1)}%**\n\n`;
    report += `${analysis.summary}\n\n`;
    
    // Indicator breakdown
    report += `## Key Indicators\n\n`;
    
    // Group indicators by type
    const indicatorsByType = new Map<StagflationIndicatorType, StagflationIndicatorAnalysis[]>();
    
    for (const indicatorAnalysis of analysis.indicators) {
      if (!indicatorsByType.has(indicatorAnalysis.type)) {
        indicatorsByType.set(indicatorAnalysis.type, []);
      }
      indicatorsByType.get(indicatorAnalysis.type)?.push(indicatorAnalysis);
    }
    
    // Add each type
    for (const [type, indicators] of indicatorsByType.entries()) {
      report += `### ${type}\n\n`;
      
      for (const indicator of indicators) {
        report += `#### ${indicator.indicator.name}\n\n`;
        report += `- Current Value: ${indicator.currentValue.toFixed(2)} ${indicator.indicator.unit}\n`;
        report += `- Historical Average: ${indicator.historicalAverage.toFixed(2)} ${indicator.indicator.unit}\n`;
        report += `- Change: ${indicator.percentChange > 0 ? '+' : ''}${indicator.percentChange.toFixed(1)}%\n`;
        report += `- Trend: ${indicator.trend}\n`;
        report += `- Contribution to Stagflation: ${
          indicator.contribution > 0 ? 'Positive' : 
          indicator.contribution < 0 ? 'Negative' : 'Neutral'
        }\n\n`;
        report += `${indicator.analysis}\n\n`;
      }
    }
    
    // Policy implications
    report += `## Policy Implications\n\n`;
    
    report += `### Monetary Policy\n\n`;
    for (const policy of analysis.policyImplications.monetaryPolicy) {
      report += `- ${policy}\n`;
    }
    report += `\n`;
    
    report += `### Fiscal Policy\n\n`;
    for (const policy of analysis.policyImplications.fiscalPolicy) {
      report += `- ${policy}\n`;
    }
    report += `\n`;
    
    report += `### Supply-Side Policy\n\n`;
    for (const policy of analysis.policyImplications.supplyPolicy) {
      report += `- ${policy}\n`;
    }
    report += `\n`;
    
    // Recommendations
    report += `## Recommendations\n\n`;
    for (const recommendation of analysis.recommendations) {
      report += `- ${recommendation}\n`;
    }
    report += `\n`;
    
    return report;
  }
  
  /**
   * Generates an HTML report for a stagflation analysis
   * @param analysis Stagflation analysis
   * @returns HTML report
   */
  private generateHtmlReport(analysis: StagflationAnalysis): string {
    // Convert Markdown to HTML (basic implementation)
    const markdown = this.generateMarkdownReport(analysis);
    
    // Very basic Markdown to HTML conversion
    const html = markdown
      .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
      .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
      .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
      .replace(/^#### (.*?)$/gm, '<h4>$1</h4>')
      .replace(/^- (.*?)$/gm, '<li>$1</li>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n\n/g, '<p>');
    
    const fullHtml = `
<!DOCTYPE html>
<html>
<head>
  <title>Stagflation Analysis Report</title>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
    h1 { color: #2c3e50; }
    h2 { color: #3498db; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    h3 { color: #2980b9; }
    h4 { color: #16a085; }
    li { margin-bottom: 5px; }
    strong { color: #c0392b; }
  </style>
</head>
<body>
  ${html}
</body>
</html>
`;
    
    return fullHtml;
  }
}

export default StagflationAnalysisService;