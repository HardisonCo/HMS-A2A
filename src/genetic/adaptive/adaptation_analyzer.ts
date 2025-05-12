import { 
  ParameterAdaptationEvent,
  ParameterSnapshot,
  EvolutionMetrics
} from '../types';

/**
 * Utility for analyzing parameter adaptation data.
 * Extracts insights from adaptation history and parameter snapshots.
 */
export class AdaptationAnalyzer {
  private adaptationHistory: ParameterAdaptationEvent[];
  private parameterHistory: ParameterSnapshot[];
  private evolutionMetrics: EvolutionMetrics[];
  
  /**
   * Creates a new adaptation analyzer
   * @param adaptationHistory History of parameter adaptation events
   * @param parameterHistory History of parameter snapshots
   * @param evolutionMetrics History of evolution metrics
   */
  constructor(
    adaptationHistory: ParameterAdaptationEvent[] = [],
    parameterHistory: ParameterSnapshot[] = [],
    evolutionMetrics: EvolutionMetrics[] = []
  ) {
    this.adaptationHistory = adaptationHistory;
    this.parameterHistory = parameterHistory;
    this.evolutionMetrics = evolutionMetrics;
  }

  /**
   * Set adaptation history
   * @param history New adaptation history
   */
  public setAdaptationHistory(history: ParameterAdaptationEvent[]): void {
    this.adaptationHistory = history;
  }

  /**
   * Set parameter history
   * @param history New parameter history
   */
  public setParameterHistory(history: ParameterSnapshot[]): void {
    this.parameterHistory = history;
  }

  /**
   * Set evolution metrics
   * @param metrics New evolution metrics
   */
  public setEvolutionMetrics(metrics: EvolutionMetrics[]): void {
    this.evolutionMetrics = metrics;
  }

  /**
   * Get parameter trends over time
   * @returns Mapping of parameter names to their values over time
   */
  public getParameterTrends(): Record<string, {
    values: number[];
    generations: number[];
    trend: 'increasing' | 'decreasing' | 'stable' | 'fluctuating';
    volatility: number;
  }> {
    const result: Record<string, any> = {};
    
    // Skip if no history
    if (this.parameterHistory.length === 0) {
      return result;
    }
    
    // Get all parameter names from first snapshot
    const parameterNames = Object.keys(this.parameterHistory[0].parameters);
    
    // Process each parameter
    for (const name of parameterNames) {
      const values: number[] = [];
      const generations: number[] = [];
      
      // Extract values and generations
      for (const snapshot of this.parameterHistory) {
        if (snapshot.parameters[name] !== undefined) {
          values.push(snapshot.parameters[name]);
          generations.push(snapshot.generation);
        }
      }
      
      // Calculate trend direction
      const trend = this.calculateTrend(values);
      
      // Calculate volatility (standard deviation normalized by mean)
      const volatility = this.calculateVolatility(values);
      
      result[name] = {
        values,
        generations,
        trend,
        volatility
      };
    }
    
    return result;
  }

  /**
   * Calculate the trend of a series of values
   * @param values Series of values
   * @returns Trend direction
   */
  private calculateTrend(values: number[]): 'increasing' | 'decreasing' | 'stable' | 'fluctuating' {
    if (values.length < 2) {
      return 'stable';
    }
    
    // Use linear regression to determine trend
    const n = values.length;
    let sumX = 0;
    let sumY = 0;
    let sumXY = 0;
    let sumXX = 0;
    
    for (let i = 0; i < n; i++) {
      sumX += i;
      sumY += values[i];
      sumXY += i * values[i];
      sumXX += i * i;
    }
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    
    // Calculate variance to determine if stable or fluctuating
    const mean = sumY / n;
    let variance = 0;
    
    for (const value of values) {
      variance += (value - mean) * (value - mean);
    }
    
    variance /= n;
    
    // Normalized variance (coefficient of variation)
    const cv = Math.sqrt(variance) / mean;
    
    // Classify trend
    if (Math.abs(slope) < 0.001) {
      return cv < 0.05 ? 'stable' : 'fluctuating';
    } else if (slope > 0) {
      return 'increasing';
    } else {
      return 'decreasing';
    }
  }

  /**
   * Calculate the volatility of a series of values
   * @param values Series of values
   * @returns Volatility measure
   */
  private calculateVolatility(values: number[]): number {
    if (values.length < 2) {
      return 0;
    }
    
    const n = values.length;
    const mean = values.reduce((sum, val) => sum + val, 0) / n;
    
    // Calculate standard deviation
    let variance = 0;
    
    for (const value of values) {
      variance += (value - mean) * (value - mean);
    }
    
    variance /= n;
    const stdDev = Math.sqrt(variance);
    
    // Normalize by mean (coefficient of variation)
    return mean !== 0 ? stdDev / mean : 0;
  }

  /**
   * Get correlation between parameters and metrics
   * @returns Correlation coefficients for each parameter-metric pair
   */
  public getParameterMetricCorrelations(): Record<string, Record<string, number>> {
    const result: Record<string, Record<string, number>> = {};
    
    // Skip if not enough data
    if (this.parameterHistory.length < 3 || this.evolutionMetrics.length < 3) {
      return result;
    }
    
    // Get all parameter names from first snapshot
    const parameterNames = Object.keys(this.parameterHistory[0].parameters);
    
    // Define metrics to correlate with
    const metricNames = [
      'bestFitness',
      'averageFitness',
      'diversityScore',
      'convergenceRate'
    ];
    
    // Process each parameter
    for (const paramName of parameterNames) {
      result[paramName] = {};
      
      // Extract parameter values
      const paramValues: number[] = [];
      const paramGenerations: number[] = [];
      
      for (const snapshot of this.parameterHistory) {
        if (snapshot.parameters[paramName] !== undefined) {
          paramValues.push(snapshot.parameters[paramName]);
          paramGenerations.push(snapshot.generation);
        }
      }
      
      // Skip if not enough parameter values
      if (paramValues.length < 3) {
        continue;
      }
      
      // Correlate with each metric
      for (const metricName of metricNames) {
        // Extract metric values aligned with parameter generations
        const metricValues: number[] = [];
        
        for (const generation of paramGenerations) {
          const metric = this.evolutionMetrics.find(m => m.generation === generation);
          
          if (metric && (metric as any)[metricName] !== undefined) {
            metricValues.push((metric as any)[metricName]);
          } else {
            // If no exact match, find closest generation
            const closest = this.evolutionMetrics
              .map(m => ({ metric: m, diff: Math.abs(m.generation - generation) }))
              .sort((a, b) => a.diff - b.diff)[0];
            
            if (closest && closest.diff <= 2) {
              metricValues.push((closest.metric as any)[metricName]);
            } else {
              // No suitable metric found, use placeholder
              metricValues.push(NaN);
            }
          }
        }
        
        // Remove any NaN entries
        const validIndices: number[] = [];
        for (let i = 0; i < paramValues.length; i++) {
          if (!isNaN(metricValues[i])) {
            validIndices.push(i);
          }
        }
        
        const validParamValues = validIndices.map(i => paramValues[i]);
        const validMetricValues = validIndices.map(i => metricValues[i]);
        
        // Calculate correlation coefficient if enough valid data
        if (validParamValues.length >= 3) {
          const correlation = this.calculateCorrelation(validParamValues, validMetricValues);
          result[paramName][metricName] = correlation;
        }
      }
    }
    
    return result;
  }

  /**
   * Calculate the correlation coefficient between two series
   * @param series1 First series of values
   * @param series2 Second series of values
   * @returns Correlation coefficient
   */
  private calculateCorrelation(series1: number[], series2: number[]): number {
    if (series1.length !== series2.length || series1.length < 2) {
      return 0;
    }
    
    const n = series1.length;
    
    // Calculate means
    const mean1 = series1.reduce((sum, val) => sum + val, 0) / n;
    const mean2 = series2.reduce((sum, val) => sum + val, 0) / n;
    
    // Calculate covariance and variances
    let covariance = 0;
    let variance1 = 0;
    let variance2 = 0;
    
    for (let i = 0; i < n; i++) {
      const diff1 = series1[i] - mean1;
      const diff2 = series2[i] - mean2;
      
      covariance += diff1 * diff2;
      variance1 += diff1 * diff1;
      variance2 += diff2 * diff2;
    }
    
    // Calculate correlation coefficient
    if (variance1 === 0 || variance2 === 0) {
      return 0;
    }
    
    return covariance / Math.sqrt(variance1 * variance2);
  }

  /**
   * Identify key adaptation events
   * @returns Array of significant adaptation events
   */
  public getSignificantAdaptations(): ParameterAdaptationEvent[] {
    // Skip if no history
    if (this.adaptationHistory.length === 0) {
      return [];
    }
    
    // Calculate change thresholds for each parameter
    const paramThresholds: Record<string, number> = {};
    
    // Group events by parameter
    const eventsByParameter: Record<string, ParameterAdaptationEvent[]> = {};
    
    for (const event of this.adaptationHistory) {
      if (!eventsByParameter[event.parameter]) {
        eventsByParameter[event.parameter] = [];
      }
      
      eventsByParameter[event.parameter].push(event);
    }
    
    // Calculate thresholds as 75th percentile of change magnitude
    for (const [param, events] of Object.entries(eventsByParameter)) {
      const changes = events.map(e => Math.abs(e.newValue - e.oldValue));
      changes.sort((a, b) => a - b);
      
      const percentile75Index = Math.floor(changes.length * 0.75);
      paramThresholds[param] = changes[percentile75Index];
    }
    
    // Filter for significant adaptations
    const significantEvents: ParameterAdaptationEvent[] = [];
    
    for (const event of this.adaptationHistory) {
      const threshold = paramThresholds[event.parameter] || 0;
      const changeMagnitude = Math.abs(event.newValue - event.oldValue);
      
      // Consider significant if change exceeds threshold
      if (changeMagnitude >= threshold) {
        significantEvents.push(event);
      }
    }
    
    return significantEvents;
  }

  /**
   * Generate a summary of parameter adaptation
   * @returns Parameter adaptation summary
   */
  public generateAdaptationSummary(): AdaptationSummary {
    // Get parameter trends
    const trends = this.getParameterTrends();
    
    // Get significant adaptations
    const significantEvents = this.getSignificantAdaptations();
    
    // Get correlations
    const correlations = this.getParameterMetricCorrelations();
    
    // Build parameter summaries
    const parameters: Record<string, ParameterAdaptationSummary> = {};
    
    for (const [name, trend] of Object.entries(trends)) {
      // Get all events for this parameter
      const events = this.adaptationHistory.filter(e => e.parameter === name);
      
      // Calculate average and range
      const values = trend.values;
      const avgValue = values.reduce((sum, val) => sum + val, 0) / values.length;
      const minValue = Math.min(...values);
      const maxValue = Math.max(...values);
      
      // Get correlation insights
      const paramCorrelations = correlations[name] || {};
      const correlationInsights: string[] = [];
      
      for (const [metric, value] of Object.entries(paramCorrelations)) {
        if (Math.abs(value) >= 0.5) {
          const direction = value > 0 ? 'positive' : 'negative';
          const strength = Math.abs(value) >= 0.7 ? 'strong' : 'moderate';
          
          correlationInsights.push(
            `${strength} ${direction} correlation with ${metric} (${value.toFixed(2)})`
          );
        }
      }
      
      // Calculate adaptation frequency
      const adaptationFrequency = events.length / this.adaptationHistory.length;
      
      parameters[name] = {
        trend: trend.trend,
        volatility: trend.volatility,
        avgValue,
        minValue,
        maxValue,
        adaptationCount: events.length,
        adaptationFrequency,
        correlations: paramCorrelations,
        correlationInsights
      };
    }
    
    // Build overall summary
    const summary: AdaptationSummary = {
      totalAdaptations: this.adaptationHistory.length,
      significantAdaptations: significantEvents.length,
      parameters,
      mostAdaptedParameter: '',
      mostCorrelatedParameter: '',
      recommendations: []
    };
    
    // Find most adapted parameter
    let maxAdaptations = 0;
    for (const [name, param] of Object.entries(parameters)) {
      if (param.adaptationCount > maxAdaptations) {
        maxAdaptations = param.adaptationCount;
        summary.mostAdaptedParameter = name;
      }
    }
    
    // Find most correlated parameter
    let maxCorrelation = 0;
    for (const [name, param] of Object.entries(parameters)) {
      for (const value of Object.values(param.correlations)) {
        if (Math.abs(value) > maxCorrelation) {
          maxCorrelation = Math.abs(value);
          summary.mostCorrelatedParameter = name;
        }
      }
    }
    
    // Generate recommendations
    for (const [name, param] of Object.entries(parameters)) {
      // High volatility parameters
      if (param.volatility > 0.2) {
        summary.recommendations.push(
          `Consider reducing adaptation rate for ${name} due to high volatility`
        );
      }
      
      // Consistently increasing or decreasing parameters
      if (param.trend === 'increasing' && param.maxValue >= param.avgValue * 1.5) {
        summary.recommendations.push(
          `Consider increasing max value for ${name} as it consistently increases`
        );
      } else if (param.trend === 'decreasing' && param.minValue <= param.avgValue * 0.5) {
        summary.recommendations.push(
          `Consider decreasing min value for ${name} as it consistently decreases`
        );
      }
      
      // Uncorrelated parameters
      let hasStrongCorrelation = false;
      for (const value of Object.values(param.correlations)) {
        if (Math.abs(value) >= 0.5) {
          hasStrongCorrelation = true;
          break;
        }
      }
      
      if (!hasStrongCorrelation && param.adaptationCount > 5) {
        summary.recommendations.push(
          `Reconsider adaptation strategy for ${name} as it shows no strong correlation with metrics`
        );
      }
    }
    
    return summary;
  }
}

/**
 * Summary of parameter adaptation
 */
export interface AdaptationSummary {
  totalAdaptations: number;
  significantAdaptations: number;
  parameters: Record<string, ParameterAdaptationSummary>;
  mostAdaptedParameter: string;
  mostCorrelatedParameter: string;
  recommendations: string[];
}

/**
 * Summary of adaptation for a single parameter
 */
export interface ParameterAdaptationSummary {
  trend: 'increasing' | 'decreasing' | 'stable' | 'fluctuating';
  volatility: number;
  avgValue: number;
  minValue: number;
  maxValue: number;
  adaptationCount: number;
  adaptationFrequency: number;
  correlations: Record<string, number>;
  correlationInsights: string[];
}