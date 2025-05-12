import { 
  ParameterAdaptationEvent,
  ParameterSnapshot,
  EvolutionMetrics
} from '../genetic/types';
import { AdaptationAnalyzer } from '../genetic/adaptive/adaptation_analyzer';

/**
 * Visualizes adaptive parameter data.
 * Adapts parameter adaptation data for visualization with D3.js.
 */
export class AdaptiveVisualizationAdapter {
  private parameterHistory: ParameterSnapshot[] = [];
  private adaptationEvents: ParameterAdaptationEvent[] = [];
  private evolutionMetrics: EvolutionMetrics[] = [];
  private analyzer: AdaptationAnalyzer;
  
  /**
   * Creates a new adaptive visualization adapter
   */
  constructor() {
    this.analyzer = new AdaptationAnalyzer();
  }

  /**
   * Add parameter snapshot to history
   * @param snapshot Parameter snapshot
   */
  public addParameterSnapshot(snapshot: ParameterSnapshot): void {
    this.parameterHistory.push(snapshot);
    
    // Update analyzer
    this.analyzer.setParameterHistory(this.parameterHistory);
  }

  /**
   * Add adaptation event to history
   * @param event Parameter adaptation event
   */
  public addAdaptationEvent(event: ParameterAdaptationEvent): void {
    this.adaptationEvents.push(event);
    
    // Update analyzer
    this.analyzer.setAdaptationHistory(this.adaptationEvents);
  }

  /**
   * Add evolution metrics to history
   * @param metrics Evolution metrics
   */
  public addEvolutionMetrics(metrics: EvolutionMetrics): void {
    this.evolutionMetrics.push(metrics);
    
    // Update analyzer
    this.analyzer.setEvolutionMetrics(this.evolutionMetrics);
  }

  /**
   * Get parameter trends data for visualization
   * @returns Data formatted for parameter trend chart
   */
  public getParameterTrendData(): ParameterTrendData[] {
    const trends = this.analyzer.getParameterTrends();
    const result: ParameterTrendData[] = [];
    
    for (const [name, trend] of Object.entries(trends)) {
      result.push({
        name,
        values: trend.values.map((value, index) => ({
          generation: trend.generations[index],
          value: value
        })),
        trend: trend.trend,
        volatility: trend.volatility
      });
    }
    
    return result;
  }

  /**
   * Get correlation data for visualization
   * @returns Data formatted for correlation matrix visualization
   */
  public getCorrelationData(): CorrelationMatrixData {
    const correlations = this.analyzer.getParameterMetricCorrelations();
    const parameters: string[] = Object.keys(correlations);
    const metrics: string[] = [];
    const correlationMatrix: number[][] = [];
    
    // Get all metrics
    for (const paramCorrelations of Object.values(correlations)) {
      for (const metric of Object.keys(paramCorrelations)) {
        if (!metrics.includes(metric)) {
          metrics.push(metric);
        }
      }
    }
    
    // Build correlation matrix
    for (const parameter of parameters) {
      const paramCorrelations = correlations[parameter] || {};
      const row: number[] = [];
      
      for (const metric of metrics) {
        row.push(paramCorrelations[metric] || 0);
      }
      
      correlationMatrix.push(row);
    }
    
    return {
      parameters,
      metrics,
      correlationMatrix
    };
  }

  /**
   * Get adaptation events data for visualization
   * @returns Data formatted for adaptation events visualization
   */
  public getAdaptationEventsData(): AdaptationEventData[] {
    return this.adaptationEvents.map(event => ({
      parameter: event.parameter,
      oldValue: event.oldValue,
      newValue: event.newValue,
      generation: event.generation,
      changePercent: 
        ((event.newValue - event.oldValue) / Math.abs(event.oldValue)) * 100,
      metrics: event.metrics
    }));
  }

  /**
   * Get significant adaptation events
   * @returns Array of significant adaptation events
   */
  public getSignificantAdaptationsData(): AdaptationEventData[] {
    const significantEvents = this.analyzer.getSignificantAdaptations();
    
    return significantEvents.map(event => ({
      parameter: event.parameter,
      oldValue: event.oldValue,
      newValue: event.newValue,
      generation: event.generation,
      changePercent: 
        ((event.newValue - event.oldValue) / Math.abs(event.oldValue)) * 100,
      metrics: event.metrics
    }));
  }

  /**
   * Get parameter-metric correlation chart data
   * @returns Data for correlation charts
   */
  public getParameterMetricCorrelationChartData(): ParameterMetricCorrelationData[] {
    const result: ParameterMetricCorrelationData[] = [];
    
    // Skip if not enough data
    if (this.parameterHistory.length < 3 || this.evolutionMetrics.length < 3) {
      return result;
    }
    
    // Get all parameter names from first snapshot
    const parameterNames = Object.keys(this.parameterHistory[0].parameters);
    
    // Define metrics to analyze
    const metricNames = [
      'bestFitness',
      'averageFitness',
      'diversityScore',
      'convergenceRate'
    ];
    
    // Process each parameter-metric pair
    for (const paramName of parameterNames) {
      // Extract parameter values and generations
      const paramData: { generation: number; value: number }[] = [];
      
      for (const snapshot of this.parameterHistory) {
        if (snapshot.parameters[paramName] !== undefined) {
          paramData.push({
            generation: snapshot.generation,
            value: snapshot.parameters[paramName]
          });
        }
      }
      
      // Skip if not enough parameter values
      if (paramData.length < 3) {
        continue;
      }
      
      // Process each metric
      for (const metricName of metricNames) {
        // Extract metric values
        const metricData: { generation: number; value: number }[] = [];
        
        for (const metric of this.evolutionMetrics) {
          if ((metric as any)[metricName] !== undefined) {
            metricData.push({
              generation: metric.generation,
              value: (metric as any)[metricName]
            });
          }
        }
        
        // Skip if not enough metric values
        if (metricData.length < 3) {
          continue;
        }
        
        // Create correlation chart data
        result.push({
          parameter: paramName,
          metric: metricName,
          parameterData: paramData,
          metricData: metricData
        });
      }
    }
    
    return result;
  }

  /**
   * Get adaptation summary data
   * @returns Adaptation summary
   */
  public getAdaptationSummaryData(): any {
    return this.analyzer.generateAdaptationSummary();
  }

  /**
   * Get efficiency metrics of the adaptation process
   * @returns Efficiency metrics
   */
  public getAdaptationEfficiencyMetrics(): AdaptationEfficiencyMetrics {
    // Skip if not enough data
    if (this.evolutionMetrics.length < 3 || this.adaptationEvents.length < 3) {
      return {
        adaptationRate: 0,
        adaptationImpact: 0,
        parameterStability: 0,
        metricImprovement: 0
      };
    }
    
    // Calculate adaptation rate (adaptations per generation)
    const totalGenerations = this.evolutionMetrics.length;
    const adaptationRate = this.adaptationEvents.length / totalGenerations;
    
    // Calculate parameter stability (inverse of average volatility)
    const trends = this.analyzer.getParameterTrends();
    let totalVolatility = 0;
    let parameterCount = 0;
    
    for (const trend of Object.values(trends)) {
      totalVolatility += trend.volatility;
      parameterCount++;
    }
    
    const avgVolatility = parameterCount > 0 ? totalVolatility / parameterCount : 0;
    const parameterStability = 1 - Math.min(1, avgVolatility * 2);
    
    // Calculate metric improvement
    const firstMetrics = this.evolutionMetrics[0];
    const lastMetrics = this.evolutionMetrics[this.evolutionMetrics.length - 1];
    
    const fitnessImprovement = 
      (lastMetrics.bestFitness - firstMetrics.bestFitness) / firstMetrics.bestFitness;
    
    const diversityChange = 
      (lastMetrics.diversityScore - firstMetrics.diversityScore) / firstMetrics.diversityScore;
    
    const metricImprovement = Math.max(0, fitnessImprovement - Math.max(0, -diversityChange));
    
    // Calculate adaptation impact (correlation between adaptations and improvements)
    // Simplified heuristic: average correlation of significantly adapted parameters
    const correlations = this.analyzer.getParameterMetricCorrelations();
    let totalCorrelation = 0;
    let correlationCount = 0;
    
    for (const [paramName, paramCorrelations] of Object.entries(correlations)) {
      if (paramCorrelations.bestFitness !== undefined) {
        totalCorrelation += Math.abs(paramCorrelations.bestFitness);
        correlationCount++;
      }
    }
    
    const adaptationImpact = correlationCount > 0 ? totalCorrelation / correlationCount : 0;
    
    return {
      adaptationRate,
      adaptationImpact,
      parameterStability,
      metricImprovement
    };
  }

  /**
   * Reset the adapter
   */
  public reset(): void {
    this.parameterHistory = [];
    this.adaptationEvents = [];
    this.evolutionMetrics = [];
    this.analyzer = new AdaptationAnalyzer();
  }
}

/**
 * Data for parameter trend visualization
 */
export interface ParameterTrendData {
  name: string;
  values: { generation: number; value: number }[];
  trend: 'increasing' | 'decreasing' | 'stable' | 'fluctuating';
  volatility: number;
}

/**
 * Data for correlation matrix visualization
 */
export interface CorrelationMatrixData {
  parameters: string[];
  metrics: string[];
  correlationMatrix: number[][];
}

/**
 * Data for adaptation event visualization
 */
export interface AdaptationEventData {
  parameter: string;
  oldValue: number;
  newValue: number;
  generation: number;
  changePercent: number;
  metrics: Partial<EvolutionMetrics>;
}

/**
 * Data for parameter-metric correlation visualization
 */
export interface ParameterMetricCorrelationData {
  parameter: string;
  metric: string;
  parameterData: { generation: number; value: number }[];
  metricData: { generation: number; value: number }[];
}

/**
 * Efficiency metrics for the adaptation process
 */
export interface AdaptationEfficiencyMetrics {
  adaptationRate: number;
  adaptationImpact: number;
  parameterStability: number;
  metricImprovement: number;
}