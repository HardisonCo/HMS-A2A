import { EventEmitter } from 'events';
import { EconomicIndicator } from './stagflation_analysis';

/**
 * Pattern analysis method
 */
export enum PatternAnalysisMethod {
  TIME_SERIES_CORRELATION = 'time_series_correlation',
  TURNING_POINT_DETECTION = 'turning_point_detection',
  SEQUENCE_MATCHING = 'sequence_matching',
  TEMPLATE_MATCHING = 'template_matching',
  DYNAMIC_TIME_WARPING = 'dynamic_time_warping',
  FOURIER_ANALYSIS = 'fourier_analysis',
  WAVELET_ANALYSIS = 'wavelet_analysis',
  REGIME_CHANGE_DETECTION = 'regime_change_detection'
}

/**
 * Pattern match result confidence level
 */
export enum ConfidenceLevel {
  VERY_LOW = 'very_low',
  LOW = 'low',
  MODERATE = 'moderate',
  HIGH = 'high',
  VERY_HIGH = 'very_high'
}

/**
 * Pattern matching time constraints
 */
export interface TimeConstraint {
  minDuration?: number; // Minimum duration for matching (e.g., months)
  maxDuration?: number; // Maximum duration for matching
  allowTimeWarping?: boolean; // Allow stretching/compressing of time
  warpingFactor?: number; // Maximum time warping factor (0-1)
}

/**
 * Historical economic pattern definition
 */
export interface HistoricalPattern {
  id: string;
  name: string;
  description: string;
  period: {
    start: string; // ISO date
    end: string; // ISO date
  };
  indicators: string[]; // Indicator IDs included in pattern
  sequence: Array<{
    indicator: string;
    condition: 'increasing' | 'decreasing' | 'flat' | 'volatile' | 'above' | 'below';
    threshold?: number;
    duration?: number; // Time periods
    magnitude?: number; // Size of change
  }>;
  timeConstraints?: TimeConstraint;
  context?: string; // Historical context
  outcome?: string; // What happened after this pattern
  policyResponses?: string[]; // Historical policy responses
  source?: string; // Source of pattern data
  tags?: string[]; // Classification tags (e.g. "stagflation", "recession")
}

/**
 * Result of a pattern match
 */
export interface PatternMatchResult {
  patternId: string;
  patternName: string;
  matchScore: number; // 0-1 score
  confidenceLevel: ConfidenceLevel;
  matchingPeriod: {
    start: string; // ISO date
    end: string; // ISO date
  };
  indicatorMatches: Array<{
    indicator: string;
    matchScore: number;
    details: string;
  }>;
  analysisMethod: PatternAnalysisMethod;
  timeWarpFactor?: number; // How much time warping was applied (if used)
  projectedOutcome?: string;
  suggestedResponses?: string[];
  warnings?: string[];
}

/**
 * Comprehensive pattern analysis result
 */
export interface PatternAnalysisResult {
  timestamp: string;
  currentPeriod: {
    start: string;
    end: string;
  };
  patterns: PatternMatchResult[];
  bestMatch?: PatternMatchResult;
  compositeScore: number; // Overall pattern match score
  suggestedResponses: string[];
  earlySignals: Array<{
    indicator: string;
    signal: string;
    confidence: number;
    timeToEvent?: string;
  }>;
  analysisMetadata: {
    methodsUsed: PatternAnalysisMethod[];
    dataQuality: number; // 0-1 score
    patternCoverage: number; // Percentage of time covered by patterns
    significantEvents: string[];
  };
}

/**
 * Options for historical pattern analysis
 */
export interface PatternAnalysisOptions {
  minMatchScore?: number; // Minimum score to consider a match (0-1)
  enabledMethods?: PatternAnalysisMethod[]; // Methods to use for analysis
  timeWindow?: number; // Number of periods to analyze
  minConfidenceLevel?: ConfidenceLevel; // Minimum confidence to include
  includeDerivedIndicators?: boolean; // Include calculated indicators
  useTimeWarping?: boolean; // Allow time warping for matching
  detectPartialMatches?: boolean; // Detect early stage patterns
  historicalDataSource?: string; // Source for historical data
}

/**
 * Historical economic pattern analyzer that identifies matching patterns
 * from historical economic data and provides analysis of their relevance
 * to current economic conditions.
 */
export class HistoricalPatternAnalyzer extends EventEmitter {
  private patterns: Map<string, HistoricalPattern> = new Map();
  private currentIndicators: Map<string, EconomicIndicator> = new Map();
  private historicalIndicators: Map<string, EconomicIndicator> = new Map();
  private analysisHistory: PatternAnalysisResult[] = [];
  private isInitialized: boolean = false;
  private options: PatternAnalysisOptions = {
    minMatchScore: 0.6,
    enabledMethods: [
      PatternAnalysisMethod.TIME_SERIES_CORRELATION,
      PatternAnalysisMethod.TURNING_POINT_DETECTION,
      PatternAnalysisMethod.SEQUENCE_MATCHING
    ],
    timeWindow: 24, // 24 months by default
    minConfidenceLevel: ConfidenceLevel.MODERATE,
    includeDerivedIndicators: true,
    useTimeWarping: true,
    detectPartialMatches: true
  };
  
  /**
   * Create a new historical pattern analyzer
   */
  constructor(options?: PatternAnalysisOptions) {
    super();
    if (options) {
      this.options = { ...this.options, ...options };
    }
  }
  
  /**
   * Initialize the pattern analyzer
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) return;
    
    // Load default historical patterns
    this.loadDefaultPatterns();
    
    // Load historical indicator data
    await this.loadHistoricalData();
    
    this.isInitialized = true;
    
    this.emit('initialized');
  }
  
  /**
   * Register a historical economic pattern
   */
  public registerPattern(pattern: HistoricalPattern): void {
    this.patterns.set(pattern.id, pattern);
  }
  
  /**
   * Get all registered patterns
   */
  public getPatterns(): HistoricalPattern[] {
    return Array.from(this.patterns.values());
  }
  
  /**
   * Get a specific pattern by ID
   */
  public getPattern(id: string): HistoricalPattern | undefined {
    return this.patterns.get(id);
  }
  
  /**
   * Add a current economic indicator
   */
  public addIndicator(indicator: EconomicIndicator): void {
    this.currentIndicators.set(indicator.id, indicator);
  }
  
  /**
   * Get all current indicators
   */
  public getCurrentIndicators(): EconomicIndicator[] {
    return Array.from(this.currentIndicators.values());
  }
  
  /**
   * Add a historical economic indicator
   */
  public addHistoricalIndicator(indicator: EconomicIndicator): void {
    this.historicalIndicators.set(indicator.id, indicator);
  }
  
  /**
   * Run a comprehensive pattern analysis on current economic indicators
   */
  public async analyzePatterns(): Promise<PatternAnalysisResult> {
    if (!this.isInitialized) {
      throw new Error('HistoricalPatternAnalyzer must be initialized before analyzing patterns');
    }
    
    const now = new Date().toISOString();
    
    // Prepare current data window
    const currentData = this.prepareCurrentDataWindow();
    
    // Calculate derived indicators if enabled
    if (this.options.includeDerivedIndicators) {
      this.calculateDerivedIndicators(currentData);
    }
    
    // Analyze each pattern using multiple methods
    const patternMatches: PatternMatchResult[] = [];
    
    for (const pattern of this.patterns.values()) {
      // Skip if the pattern uses indicators we don't have
      const missingIndicators = pattern.indicators.filter(
        id => !currentData.some(d => d.id === id || d.name.toLowerCase().includes(id.toLowerCase()))
      );
      
      if (missingIndicators.length > 0) {
        continue;
      }
      
      // Apply each enabled analysis method
      for (const method of this.options.enabledMethods || []) {
        const result = await this.applyAnalysisMethod(method, pattern, currentData);
        
        // Only include matches that meet minimum score and confidence
        if (result && 
            result.matchScore >= (this.options.minMatchScore || 0) &&
            this.getConfidenceValue(result.confidenceLevel) >= 
            this.getConfidenceValue(this.options.minConfidenceLevel || ConfidenceLevel.MODERATE)) {
          patternMatches.push(result);
        }
      }
    }
    
    // Find best match
    let bestMatch: PatternMatchResult | undefined;
    if (patternMatches.length > 0) {
      bestMatch = patternMatches.reduce((best, current) => 
        current.matchScore > best.matchScore ? current : best
      );
    }
    
    // Calculate composite score
    const compositeScore = patternMatches.length > 0
      ? patternMatches.reduce((sum, match) => sum + match.matchScore, 0) / patternMatches.length
      : 0;
    
    // Generate suggested responses
    const suggestedResponses = this.generateSuggestedResponses(patternMatches);
    
    // Detect early signals
    const earlySignals = this.detectEarlySignals(currentData, patternMatches);
    
    // Prepare analysis metadata
    const analysisMetadata = {
      methodsUsed: this.options.enabledMethods || [],
      dataQuality: this.calculateDataQuality(currentData),
      patternCoverage: this.calculatePatternCoverage(patternMatches),
      significantEvents: this.detectSignificantEvents(currentData)
    };
    
    // Create timeframe for analysis
    const oldestDate = this.findOldestDate(currentData);
    const currentPeriod = {
      start: oldestDate,
      end: now
    };
    
    // Create the full analysis result
    const result: PatternAnalysisResult = {
      timestamp: now,
      currentPeriod,
      patterns: patternMatches,
      bestMatch,
      compositeScore,
      suggestedResponses,
      earlySignals,
      analysisMetadata
    };
    
    // Add to history
    this.analysisHistory.unshift(result);
    
    // Emit event
    this.emit('analysis-completed', result);
    
    return result;
  }
  
  /**
   * Get the latest analysis result
   */
  public getLatestAnalysis(): PatternAnalysisResult | undefined {
    return this.analysisHistory.length > 0 ? this.analysisHistory[0] : undefined;
  }
  
  /**
   * Get all analysis results
   */
  public getAnalysisHistory(): PatternAnalysisResult[] {
    return [...this.analysisHistory];
  }
  
  /**
   * Set analysis options
   */
  public setOptions(options: PatternAnalysisOptions): void {
    this.options = { ...this.options, ...options };
  }
  
  /**
   * Get current options
   */
  public getOptions(): PatternAnalysisOptions {
    return { ...this.options };
  }
  
  /**
   * Search for patterns that match specific criteria
   */
  public searchPatterns(query: {
    tags?: string[];
    indicators?: string[];
    period?: { start?: string; end?: string };
    minConfidence?: ConfidenceLevel;
  }): HistoricalPattern[] {
    let matches = Array.from(this.patterns.values());
    
    // Filter by tags
    if (query.tags && query.tags.length > 0) {
      matches = matches.filter(pattern => 
        pattern.tags && query.tags?.some(tag => pattern.tags?.includes(tag))
      );
    }
    
    // Filter by indicators
    if (query.indicators && query.indicators.length > 0) {
      matches = matches.filter(pattern => 
        query.indicators?.some(ind => pattern.indicators.includes(ind))
      );
    }
    
    // Filter by time period
    if (query.period) {
      if (query.period.start) {
        matches = matches.filter(pattern => 
          new Date(pattern.period.end) >= new Date(query.period?.start || '')
        );
      }
      
      if (query.period.end) {
        matches = matches.filter(pattern => 
          new Date(pattern.period.start) <= new Date(query.period?.end || '')
        );
      }
    }
    
    return matches;
  }
  
  /**
   * Find similar historical periods to current conditions
   */
  public findSimilarPeriods(options?: {
    indicators?: string[];
    timeWindow?: number;
    minSimilarity?: number;
    maxResults?: number;
  }): Array<{
    period: { start: string; end: string };
    similarity: number;
    matchingIndicators: string[];
    description?: string;
    outcome?: string;
  }> {
    const indicators = options?.indicators || 
      Array.from(this.currentIndicators.keys());
    
    const timeWindow = options?.timeWindow || this.options.timeWindow || 24;
    const minSimilarity = options?.minSimilarity || 0.7;
    const maxResults = options?.maxResults || 5;
    
    // Get current data
    const currentData = this.prepareCurrentDataWindow(timeWindow);
    
    // Extract historical periods from patterns
    const historicalPeriods = this.patterns.values();
    
    const results: Array<{
      period: { start: string; end: string };
      similarity: number;
      matchingIndicators: string[];
      description?: string;
      outcome?: string;
    }> = [];
    
    // Analyze each historical period
    for (const pattern of historicalPeriods) {
      // Skip if missing critical indicators
      const availableIndicators = indicators.filter(id => 
        pattern.indicators.includes(id) && 
        this.historicalIndicators.has(id)
      );
      
      if (availableIndicators.length === 0) continue;
      
      // Calculate similarity score
      let totalSimilarity = 0;
      const matchingIndicators: string[] = [];
      
      for (const indId of availableIndicators) {
        const currentInd = currentData.find(d => d.id === indId);
        const historicalInd = this.historicalIndicators.get(indId);
        
        if (currentInd && historicalInd) {
          const similarity = this.calculateIndicatorSimilarity(
            currentInd, 
            historicalInd,
            {
              start: pattern.period.start,
              end: pattern.period.end
            }
          );
          
          if (similarity > 0.6) {
            matchingIndicators.push(indId);
            totalSimilarity += similarity;
          }
        }
      }
      
      const averageSimilarity = matchingIndicators.length > 0 ?
        totalSimilarity / matchingIndicators.length : 0;
      
      if (averageSimilarity >= minSimilarity) {
        results.push({
          period: pattern.period,
          similarity: averageSimilarity,
          matchingIndicators,
          description: pattern.description,
          outcome: pattern.outcome
        });
      }
    }
    
    // Sort by similarity and limit results
    return results
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, maxResults);
  }
  
  /**
   * Calculate similarity between current indicator data and historical data
   */
  private calculateIndicatorSimilarity(
    currentIndicator: EconomicIndicator,
    historicalIndicator: EconomicIndicator,
    period: { start: string; end: string }
  ): number {
    // Extract relevant historical data for the period
    const historicalData = historicalIndicator.data
      .filter(d => 
        new Date(d.date) >= new Date(period.start) && 
        new Date(d.date) <= new Date(period.end)
      )
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    
    if (historicalData.length === 0) return 0;
    
    // Extract current data points
    const currentData = [...currentIndicator.data]
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    
    if (currentData.length === 0) return 0;
    
    // Get sequences of values
    const historicalValues = historicalData.map(d => d.value);
    const currentValues = currentData.map(d => d.value);
    
    // Normalize sequences to same length if needed
    const normalizedHistorical = this.normalizeSequence(historicalValues, currentValues.length);
    const normalizedCurrent = this.normalizeSequence(currentValues, normalizedHistorical.length);
    
    // Calculate measures of similarity
    
    // 1. Correlation coefficient
    const correlation = this.calculateCorrelation(normalizedHistorical, normalizedCurrent);
    
    // 2. Trend direction similarity
    const trendSimilarity = this.calculateTrendSimilarity(normalizedHistorical, normalizedCurrent);
    
    // 3. Value range similarity
    const rangeSimilarity = this.calculateRangeSimilarity(normalizedHistorical, normalizedCurrent);
    
    // 4. Turning point similarity
    const turningPointSimilarity = this.calculateTurningPointSimilarity(
      normalizedHistorical, 
      normalizedCurrent
    );
    
    // Weighted combination of similarity measures
    return (
      correlation * 0.4 +
      trendSimilarity * 0.3 +
      rangeSimilarity * 0.1 +
      turningPointSimilarity * 0.2
    );
  }
  
  /**
   * Normalize a sequence to a target length
   */
  private normalizeSequence(sequence: number[], targetLength: number): number[] {
    if (sequence.length === targetLength) {
      return sequence;
    }
    
    const result: number[] = [];
    const ratio = (sequence.length - 1) / (targetLength - 1);
    
    for (let i = 0; i < targetLength; i++) {
      const exactIndex = i * ratio;
      const lowerIndex = Math.floor(exactIndex);
      const upperIndex = Math.min(Math.ceil(exactIndex), sequence.length - 1);
      
      if (lowerIndex === upperIndex) {
        result.push(sequence[lowerIndex]);
      } else {
        const weight = exactIndex - lowerIndex;
        result.push(
          sequence[lowerIndex] * (1 - weight) + sequence[upperIndex] * weight
        );
      }
    }
    
    return result;
  }
  
  /**
   * Calculate correlation coefficient between two sequences
   */
  private calculateCorrelation(sequence1: number[], sequence2: number[]): number {
    if (sequence1.length !== sequence2.length || sequence1.length < 2) {
      return 0;
    }
    
    const n = sequence1.length;
    const mean1 = sequence1.reduce((sum, val) => sum + val, 0) / n;
    const mean2 = sequence2.reduce((sum, val) => sum + val, 0) / n;
    
    let numerator = 0;
    let denom1 = 0;
    let denom2 = 0;
    
    for (let i = 0; i < n; i++) {
      const diff1 = sequence1[i] - mean1;
      const diff2 = sequence2[i] - mean2;
      numerator += diff1 * diff2;
      denom1 += diff1 * diff1;
      denom2 += diff2 * diff2;
    }
    
    const denominator = Math.sqrt(denom1 * denom2);
    
    if (denominator === 0) return 0;
    
    // Convert to 0-1 range from -1 to 1
    return (numerator / denominator + 1) / 2;
  }
  
  /**
   * Calculate similarity of trend directions
   */
  private calculateTrendSimilarity(sequence1: number[], sequence2: number[]): number {
    if (sequence1.length !== sequence2.length || sequence1.length < 2) {
      return 0;
    }
    
    let matchCount = 0;
    
    for (let i = 1; i < sequence1.length; i++) {
      const trend1 = Math.sign(sequence1[i] - sequence1[i - 1]);
      const trend2 = Math.sign(sequence2[i] - sequence2[i - 1]);
      
      if (trend1 === trend2) {
        matchCount++;
      }
    }
    
    return matchCount / (sequence1.length - 1);
  }
  
  /**
   * Calculate similarity of value ranges
   */
  private calculateRangeSimilarity(sequence1: number[], sequence2: number[]): number {
    if (sequence1.length === 0 || sequence2.length === 0) {
      return 0;
    }
    
    const min1 = Math.min(...sequence1);
    const max1 = Math.max(...sequence1);
    const min2 = Math.min(...sequence2);
    const max2 = Math.max(...sequence2);
    
    const range1 = max1 - min1;
    const range2 = max2 - min2;
    
    if (range1 === 0 && range2 === 0) return 1;
    if (range1 === 0 || range2 === 0) return 0;
    
    // Calculate ratio of smaller range to larger range
    return Math.min(range1, range2) / Math.max(range1, range2);
  }
  
  /**
   * Calculate similarity of turning points
   */
  private calculateTurningPointSimilarity(sequence1: number[], sequence2: number[]): number {
    if (sequence1.length !== sequence2.length || sequence1.length < 3) {
      return 0;
    }
    
    // Identify turning points in both sequences
    const turningPoints1: number[] = [];
    const turningPoints2: number[] = [];
    
    for (let i = 1; i < sequence1.length - 1; i++) {
      if ((sequence1[i] > sequence1[i - 1] && sequence1[i] > sequence1[i + 1]) ||
          (sequence1[i] < sequence1[i - 1] && sequence1[i] < sequence1[i + 1])) {
        turningPoints1.push(i);
      }
      
      if ((sequence2[i] > sequence2[i - 1] && sequence2[i] > sequence2[i + 1]) ||
          (sequence2[i] < sequence2[i - 1] && sequence2[i] < sequence2[i + 1])) {
        turningPoints2.push(i);
      }
    }
    
    // If either sequence has no turning points, return 0
    if (turningPoints1.length === 0 || turningPoints2.length === 0) {
      return 0;
    }
    
    // Find the number of approximately matching turning points
    let matchCount = 0;
    const tolerance = Math.floor(sequence1.length * 0.1); // 10% tolerance
    
    for (const tp1 of turningPoints1) {
      for (const tp2 of turningPoints2) {
        if (Math.abs(tp1 - tp2) <= tolerance) {
          matchCount++;
          break;
        }
      }
    }
    
    // Calculate similarity score
    return matchCount / Math.max(turningPoints1.length, turningPoints2.length);
  }
  
  /**
   * Apply a specific analysis method to match a pattern
   */
  private async applyAnalysisMethod(
    method: PatternAnalysisMethod,
    pattern: HistoricalPattern,
    currentData: EconomicIndicator[]
  ): Promise<PatternMatchResult | null> {
    switch (method) {
      case PatternAnalysisMethod.TIME_SERIES_CORRELATION:
        return this.applyTimeSeriesCorrelation(pattern, currentData);
      
      case PatternAnalysisMethod.TURNING_POINT_DETECTION:
        return this.applyTurningPointDetection(pattern, currentData);
      
      case PatternAnalysisMethod.SEQUENCE_MATCHING:
        return this.applySequenceMatching(pattern, currentData);
      
      case PatternAnalysisMethod.TEMPLATE_MATCHING:
        return this.applyTemplateMatching(pattern, currentData);
      
      case PatternAnalysisMethod.DYNAMIC_TIME_WARPING:
        return this.applyDynamicTimeWarping(pattern, currentData);
      
      case PatternAnalysisMethod.FOURIER_ANALYSIS:
        return this.applyFourierAnalysis(pattern, currentData);
      
      case PatternAnalysisMethod.WAVELET_ANALYSIS:
        return this.applyWaveletAnalysis(pattern, currentData);
      
      case PatternAnalysisMethod.REGIME_CHANGE_DETECTION:
        return this.applyRegimeChangeDetection(pattern, currentData);
      
      default:
        console.warn(`Analysis method ${method} not implemented`);
        return null;
    }
  }
  
  /**
   * Apply time series correlation analysis
   */
  private applyTimeSeriesCorrelation(
    pattern: HistoricalPattern,
    currentData: EconomicIndicator[]
  ): PatternMatchResult {
    const indicatorMatches: Array<{
      indicator: string;
      matchScore: number;
      details: string;
    }> = [];
    
    // Process each indicator in the pattern
    for (const patternIndicatorId of pattern.indicators) {
      // Find matching current indicator
      const currentIndicator = currentData.find(ind => 
        ind.id === patternIndicatorId || 
        ind.name.toLowerCase().includes(patternIndicatorId.toLowerCase())
      );
      
      // Find matching historical indicator
      const historicalIndicator = this.historicalIndicators.get(patternIndicatorId);
      
      if (currentIndicator && historicalIndicator) {
        // Calculate similarity for this indicator
        const similarity = this.calculateIndicatorSimilarity(
          currentIndicator,
          historicalIndicator,
          pattern.period
        );
        
        // Add to matches
        indicatorMatches.push({
          indicator: patternIndicatorId,
          matchScore: similarity,
          details: `Time series correlation: ${(similarity * 100).toFixed(1)}%`
        });
      }
    }
    
    // Calculate overall match score
    const matchScore = indicatorMatches.length > 0
      ? indicatorMatches.reduce((sum, match) => sum + match.matchScore, 0) / indicatorMatches.length
      : 0;
    
    // Determine confidence level
    const confidenceLevel = this.scoreToConfidenceLevel(matchScore);
    
    // Define period of analysis
    const oldestDate = this.findOldestDate(currentData);
    const now = new Date().toISOString();
    
    // Create match result
    return {
      patternId: pattern.id,
      patternName: pattern.name,
      matchScore,
      confidenceLevel,
      matchingPeriod: {
        start: oldestDate,
        end: now
      },
      indicatorMatches,
      analysisMethod: PatternAnalysisMethod.TIME_SERIES_CORRELATION,
      projectedOutcome: pattern.outcome,
      suggestedResponses: pattern.policyResponses,
      warnings: matchScore < 0.7 ? ['Moderate to low correlation strength'] : undefined
    };
  }
  
  /**
   * Apply turning point detection analysis
   */
  private applyTurningPointDetection(
    pattern: HistoricalPattern,
    currentData: EconomicIndicator[]
  ): PatternMatchResult {
    const indicatorMatches: Array<{
      indicator: string;
      matchScore: number;
      details: string;
    }> = [];
    
    // Process each indicator in the pattern
    for (const patternIndicatorId of pattern.indicators) {
      // Find matching current indicator
      const currentIndicator = currentData.find(ind => 
        ind.id === patternIndicatorId || 
        ind.name.toLowerCase().includes(patternIndicatorId.toLowerCase())
      );
      
      // Find matching historical indicator
      const historicalIndicator = this.historicalIndicators.get(patternIndicatorId);
      
      if (currentIndicator && historicalIndicator) {
        // Extract data points and sort by date
        const currentPoints = [...currentIndicator.data]
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
          .map(d => d.value);
        
        const historicalPoints = historicalIndicator.data
          .filter(d => 
            new Date(d.date) >= new Date(pattern.period.start) && 
            new Date(d.date) <= new Date(pattern.period.end)
          )
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
          .map(d => d.value);
        
        // Detect turning points in both sequences
        const currentTurningPoints = this.detectTurningPoints(currentPoints);
        const historicalTurningPoints = this.detectTurningPoints(historicalPoints);
        
        // Calculate turning point similarity
        let similarity = 0;
        if (currentTurningPoints.length > 0 && historicalTurningPoints.length > 0) {
          // Normalize positions to 0-1 range
          const normalizedCurrent = currentTurningPoints.map(
            tp => tp / (currentPoints.length - 1)
          );
          const normalizedHistorical = historicalTurningPoints.map(
            tp => tp / (historicalPoints.length - 1)
          );
          
          // Match turning points
          let matchCount = 0;
          const tolerance = 0.1; // 10% position tolerance
          
          for (const tp1 of normalizedCurrent) {
            for (const tp2 of normalizedHistorical) {
              if (Math.abs(tp1 - tp2) <= tolerance) {
                matchCount++;
                break;
              }
            }
          }
          
          // Calculate similarity score
          similarity = matchCount / Math.max(normalizedCurrent.length, normalizedHistorical.length);
        }
        
        // Add to matches
        indicatorMatches.push({
          indicator: patternIndicatorId,
          matchScore: similarity,
          details: `Turning point match: ${(similarity * 100).toFixed(1)}%, ` +
                   `Current: ${currentTurningPoints.length} turning points, ` +
                   `Historical: ${historicalTurningPoints.length} turning points`
        });
      }
    }
    
    // Calculate overall match score
    const matchScore = indicatorMatches.length > 0
      ? indicatorMatches.reduce((sum, match) => sum + match.matchScore, 0) / indicatorMatches.length
      : 0;
    
    // Determine confidence level
    const confidenceLevel = this.scoreToConfidenceLevel(matchScore);
    
    // Define period of analysis
    const oldestDate = this.findOldestDate(currentData);
    const now = new Date().toISOString();
    
    // Create match result
    return {
      patternId: pattern.id,
      patternName: pattern.name,
      matchScore,
      confidenceLevel,
      matchingPeriod: {
        start: oldestDate,
        end: now
      },
      indicatorMatches,
      analysisMethod: PatternAnalysisMethod.TURNING_POINT_DETECTION,
      projectedOutcome: pattern.outcome,
      suggestedResponses: pattern.policyResponses,
      warnings: indicatorMatches.some(m => m.matchScore === 0)
        ? ['Some indicators lack sufficient turning points for analysis']
        : undefined
    };
  }
  
  /**
   * Apply sequence matching analysis
   */
  private applySequenceMatching(
    pattern: HistoricalPattern,
    currentData: EconomicIndicator[]
  ): PatternMatchResult {
    const indicatorMatches: Array<{
      indicator: string;
      matchScore: number;
      details: string;
    }> = [];
    
    // Check each sequence step in the pattern
    for (const sequenceStep of pattern.sequence) {
      // Find matching current indicator
      const currentIndicator = currentData.find(ind => 
        ind.id === sequenceStep.indicator || 
        ind.name.toLowerCase().includes(sequenceStep.indicator.toLowerCase())
      );
      
      if (!currentIndicator || !currentIndicator.data || currentIndicator.data.length < 2) {
        continue;
      }
      
      // Sort data by date (newest first)
      const data = [...currentIndicator.data]
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
      
      // Analyze the condition
      let matchScore = 0;
      let details = '';
      
      if (sequenceStep.condition === 'increasing') {
        // Check if the indicator has been increasing
        let increasing = true;
        let magnitude = 0;
        for (let i = 0; i < Math.min(data.length - 1, sequenceStep.duration || 3); i++) {
          if (data[i].value <= data[i + 1].value) {
            increasing = false;
            break;
          }
          magnitude += (data[i].value - data[i + 1].value) / Math.abs(data[i + 1].value);
        }
        
        if (increasing) {
          const avgChange = magnitude / Math.min(data.length - 1, sequenceStep.duration || 3);
          matchScore = Math.min(avgChange * 5, 1); // Scale change rate to 0-1
          details = `Increasing trend confirmed with ${(avgChange * 100).toFixed(1)}% avg change`;
        } else {
          matchScore = 0;
          details = 'Increasing trend not found';
        }
      } else if (sequenceStep.condition === 'decreasing') {
        // Check if the indicator has been decreasing
        let decreasing = true;
        let magnitude = 0;
        for (let i = 0; i < Math.min(data.length - 1, sequenceStep.duration || 3); i++) {
          if (data[i].value >= data[i + 1].value) {
            decreasing = false;
            break;
          }
          magnitude += (data[i + 1].value - data[i].value) / Math.abs(data[i].value);
        }
        
        if (decreasing) {
          const avgChange = magnitude / Math.min(data.length - 1, sequenceStep.duration || 3);
          matchScore = Math.min(avgChange * 5, 1); // Scale change rate to 0-1
          details = `Decreasing trend confirmed with ${(avgChange * 100).toFixed(1)}% avg change`;
        } else {
          matchScore = 0;
          details = 'Decreasing trend not found';
        }
      } else if (sequenceStep.condition === 'flat') {
        // Check if the indicator has been flat
        let isFlat = true;
        let totalDiff = 0;
        for (let i = 0; i < Math.min(data.length - 1, sequenceStep.duration || 3); i++) {
          const pctChange = Math.abs((data[i].value - data[i + 1].value) / data[i + 1].value);
          totalDiff += pctChange;
          if (pctChange > 0.03) { // More than 3% change
            isFlat = false;
          }
        }
        
        const avgChange = totalDiff / Math.min(data.length - 1, sequenceStep.duration || 3);
        if (isFlat) {
          matchScore = 1 - avgChange * 10; // Higher score for smaller changes
          details = `Flat trend confirmed with ${(avgChange * 100).toFixed(1)}% avg change`;
        } else {
          matchScore = 0;
          details = `Flat trend not found, ${(avgChange * 100).toFixed(1)}% avg change`;
        }
      } else if (sequenceStep.condition === 'volatile') {
        // Check if the indicator has been volatile
        let totalChange = 0;
        let directionChanges = 0;
        let prevDirection = 0;
        
        for (let i = 0; i < Math.min(data.length - 1, sequenceStep.duration || 3); i++) {
          const pctChange = (data[i].value - data[i + 1].value) / Math.abs(data[i + 1].value);
          totalChange += Math.abs(pctChange);
          
          const direction = Math.sign(pctChange);
          if (prevDirection !== 0 && direction !== 0 && direction !== prevDirection) {
            directionChanges++;
          }
          prevDirection = direction;
        }
        
        const volatility = totalChange / Math.min(data.length - 1, sequenceStep.duration || 3);
        const changeRate = directionChanges / Math.max(1, Math.min(data.length - 2, sequenceStep.duration || 3));
        
        // Higher score for more volatility and direction changes
        matchScore = Math.min((volatility * 5 + changeRate) / 2, 1);
        details = `Volatility score: ${(matchScore * 100).toFixed(1)}%, ` +
                 `Avg change: ${(volatility * 100).toFixed(1)}%, ` +
                 `Direction changes: ${directionChanges}`;
      } else if (sequenceStep.condition === 'above' && sequenceStep.threshold !== undefined) {
        // Check if the indicator is above the threshold
        let aboveCount = 0;
        for (let i = 0; i < Math.min(data.length, sequenceStep.duration || 3); i++) {
          if (data[i].value > sequenceStep.threshold) {
            aboveCount++;
          }
        }
        
        const aboveRatio = aboveCount / Math.min(data.length, sequenceStep.duration || 3);
        matchScore = aboveRatio;
        details = `Above threshold ${sequenceStep.threshold} for ${(aboveRatio * 100).toFixed(1)}% of periods`;
      } else if (sequenceStep.condition === 'below' && sequenceStep.threshold !== undefined) {
        // Check if the indicator is below the threshold
        let belowCount = 0;
        for (let i = 0; i < Math.min(data.length, sequenceStep.duration || 3); i++) {
          if (data[i].value < sequenceStep.threshold) {
            belowCount++;
          }
        }
        
        const belowRatio = belowCount / Math.min(data.length, sequenceStep.duration || 3);
        matchScore = belowRatio;
        details = `Below threshold ${sequenceStep.threshold} for ${(belowRatio * 100).toFixed(1)}% of periods`;
      }
      
      // Add to matches
      indicatorMatches.push({
        indicator: sequenceStep.indicator,
        matchScore,
        details
      });
    }
    
    // Calculate overall match score
    const matchScore = indicatorMatches.length > 0
      ? indicatorMatches.reduce((sum, match) => sum + match.matchScore, 0) / indicatorMatches.length
      : 0;
    
    // Determine confidence level
    const confidenceLevel = this.scoreToConfidenceLevel(matchScore);
    
    // Define period of analysis
    const oldestDate = this.findOldestDate(currentData);
    const now = new Date().toISOString();
    
    // Create match result
    return {
      patternId: pattern.id,
      patternName: pattern.name,
      matchScore,
      confidenceLevel,
      matchingPeriod: {
        start: oldestDate,
        end: now
      },
      indicatorMatches,
      analysisMethod: PatternAnalysisMethod.SEQUENCE_MATCHING,
      projectedOutcome: pattern.outcome,
      suggestedResponses: pattern.policyResponses,
      warnings: indicatorMatches.some(m => m.matchScore === 0)
        ? ['Some sequence conditions not met']
        : undefined
    };
  }
  
  /**
   * Apply template matching analysis (placeholder - not fully implemented)
   */
  private applyTemplateMatching(
    pattern: HistoricalPattern,
    currentData: EconomicIndicator[]
  ): PatternMatchResult | null {
    // NOTE: This is a placeholder for template matching implementation
    // In a real implementation, this would use more sophisticated pattern matching
    
    // Define period of analysis
    const oldestDate = this.findOldestDate(currentData);
    const now = new Date().toISOString();
    
    return {
      patternId: pattern.id,
      patternName: pattern.name,
      matchScore: 0.5, // Placeholder score
      confidenceLevel: ConfidenceLevel.MODERATE,
      matchingPeriod: {
        start: oldestDate,
        end: now
      },
      indicatorMatches: [],
      analysisMethod: PatternAnalysisMethod.TEMPLATE_MATCHING,
      warnings: ['Template matching not fully implemented']
    };
  }
  
  /**
   * Apply dynamic time warping analysis (placeholder - not fully implemented)
   */
  private applyDynamicTimeWarping(
    pattern: HistoricalPattern,
    currentData: EconomicIndicator[]
  ): PatternMatchResult | null {
    // NOTE: This is a placeholder for DTW implementation
    // In a real implementation, this would use the Dynamic Time Warping algorithm
    
    // Define period of analysis
    const oldestDate = this.findOldestDate(currentData);
    const now = new Date().toISOString();
    
    return {
      patternId: pattern.id,
      patternName: pattern.name,
      matchScore: 0.5, // Placeholder score
      confidenceLevel: ConfidenceLevel.MODERATE,
      matchingPeriod: {
        start: oldestDate,
        end: now
      },
      indicatorMatches: [],
      analysisMethod: PatternAnalysisMethod.DYNAMIC_TIME_WARPING,
      timeWarpFactor: 0.2, // Placeholder value
      warnings: ['Dynamic Time Warping not fully implemented']
    };
  }
  
  /**
   * Apply Fourier analysis (placeholder - not fully implemented)
   */
  private applyFourierAnalysis(
    pattern: HistoricalPattern,
    currentData: EconomicIndicator[]
  ): PatternMatchResult | null {
    // NOTE: This is a placeholder for Fourier analysis implementation
    // In a real implementation, this would analyze frequency components
    
    return null; // Not implemented
  }
  
  /**
   * Apply wavelet analysis (placeholder - not fully implemented)
   */
  private applyWaveletAnalysis(
    pattern: HistoricalPattern,
    currentData: EconomicIndicator[]
  ): PatternMatchResult | null {
    // NOTE: This is a placeholder for wavelet analysis implementation
    // In a real implementation, this would analyze time-frequency components
    
    return null; // Not implemented
  }
  
  /**
   * Apply regime change detection (placeholder - not fully implemented)
   */
  private applyRegimeChangeDetection(
    pattern: HistoricalPattern,
    currentData: EconomicIndicator[]
  ): PatternMatchResult | null {
    // NOTE: This is a placeholder for regime change detection implementation
    // In a real implementation, this would detect structural breaks and regime shifts
    
    return null; // Not implemented
  }
  
  /**
   * Prepare current data window for analysis
   */
  private prepareCurrentDataWindow(timeWindow?: number): EconomicIndicator[] {
    const window = timeWindow || this.options.timeWindow || 24;
    const result: EconomicIndicator[] = [];
    
    // Calculate cutoff date
    const now = new Date();
    const cutoffDate = new Date(now);
    cutoffDate.setMonth(cutoffDate.getMonth() - window);
    
    // Process each indicator
    for (const indicator of this.currentIndicators.values()) {
      // Filter data by cutoff date
      const filteredData = indicator.data.filter(d => 
        new Date(d.date) >= cutoffDate
      );
      
      if (filteredData.length > 0) {
        result.push({
          ...indicator,
          data: filteredData
        });
      }
    }
    
    return result;
  }
  
  /**
   * Calculate derived indicators
   */
  private calculateDerivedIndicators(indicators: EconomicIndicator[]): void {
    // TODO: Implement derived indicator calculation
    // For example, calculating:
    // - Growth rates
    // - Moving averages
    // - Relative values (e.g., relative to GDP)
    // - Composite indicators
  }
  
  /**
   * Detect turning points in a sequence
   */
  private detectTurningPoints(values: number[]): number[] {
    const turningPoints: number[] = [];
    
    for (let i = 1; i < values.length - 1; i++) {
      // Local maximum
      if (values[i] > values[i - 1] && values[i] > values[i + 1]) {
        turningPoints.push(i);
      }
      // Local minimum
      else if (values[i] < values[i - 1] && values[i] < values[i + 1]) {
        turningPoints.push(i);
      }
    }
    
    return turningPoints;
  }
  
  /**
   * Convert match score to confidence level
   */
  private scoreToConfidenceLevel(score: number): ConfidenceLevel {
    if (score >= 0.9) return ConfidenceLevel.VERY_HIGH;
    if (score >= 0.75) return ConfidenceLevel.HIGH;
    if (score >= 0.6) return ConfidenceLevel.MODERATE;
    if (score >= 0.4) return ConfidenceLevel.LOW;
    return ConfidenceLevel.VERY_LOW;
  }
  
  /**
   * Get numerical value for confidence level
   */
  private getConfidenceValue(level: ConfidenceLevel): number {
    switch (level) {
      case ConfidenceLevel.VERY_HIGH: return 4;
      case ConfidenceLevel.HIGH: return 3;
      case ConfidenceLevel.MODERATE: return 2;
      case ConfidenceLevel.LOW: return 1;
      case ConfidenceLevel.VERY_LOW: return 0;
      default: return 0;
    }
  }
  
  /**
   * Generate suggested responses based on pattern matches
   */
  private generateSuggestedResponses(matches: PatternMatchResult[]): string[] {
    if (matches.length === 0) {
      return [
        'No significant historical patterns detected',
        'Continue regular economic monitoring',
        'Consider more data collection to improve pattern recognition'
      ];
    }
    
    // Collect and deduplicate responses
    const responses = new Set<string>();
    
    // Start with the best match responses
    const bestMatch = matches.reduce((best, current) => 
      current.matchScore > best.matchScore ? current : best
    );
    
    const pattern = this.patterns.get(bestMatch.patternId);
    if (pattern && pattern.policyResponses) {
      pattern.policyResponses.forEach(response => responses.add(response));
    }
    
    // Add responses from other high-confidence matches
    for (const match of matches) {
      if (match.patternId !== bestMatch.patternId && 
          match.confidenceLevel >= ConfidenceLevel.HIGH) {
        const pattern = this.patterns.get(match.patternId);
        if (pattern && pattern.policyResponses) {
          pattern.policyResponses.forEach(response => responses.add(response));
        }
      }
    }
    
    // If no policy responses were found, provide general guidance
    if (responses.size === 0) {
      responses.add(`Review historical policy responses to ${bestMatch.patternName} conditions`);
      responses.add('Develop contingency plan based on potential outcomes');
      responses.add('Monitor indicators closely for further pattern development');
    }
    
    return Array.from(responses);
  }
  
  /**
   * Detect early signals that may precede full pattern development
   */
  private detectEarlySignals(
    currentData: EconomicIndicator[],
    matches: PatternMatchResult[]
  ): Array<{
    indicator: string;
    signal: string;
    confidence: number;
    timeToEvent?: string;
  }> {
    const signals: Array<{
      indicator: string;
      signal: string;
      confidence: number;
      timeToEvent?: string;
    }> = [];
    
    // Return empty array if no partial pattern detection
    if (!this.options.detectPartialMatches) {
      return signals;
    }
    
    // Check for early signals in top matches
    const topMatches = matches
      .filter(m => m.confidenceLevel >= ConfidenceLevel.MODERATE)
      .sort((a, b) => b.matchScore - a.matchScore)
      .slice(0, 3); // Top 3 matches
    
    for (const match of topMatches) {
      const pattern = this.patterns.get(match.patternId);
      if (!pattern) continue;
      
      // Check indicator matches for signals
      for (const indMatch of match.indicatorMatches) {
        if (indMatch.matchScore >= 0.7) {
          // Get historical sequence for this indicator
          const sequenceStep = pattern.sequence.find(s => s.indicator === indMatch.indicator);
          
          if (sequenceStep) {
            // Find the current indicator
            const currentIndicator = currentData.find(ind => 
              ind.id === indMatch.indicator || 
              ind.name.toLowerCase().includes(indMatch.indicator.toLowerCase())
            );
            
            if (currentIndicator && currentIndicator.data.length > 0) {
              // Get the latest value
              const latestData = [...currentIndicator.data]
                .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())[0];
              
              // Create signal based on sequence step
              const signal = this.createSignalForSequenceStep(
                sequenceStep, 
                latestData.value,
                pattern.name
              );
              
              if (signal) {
                signals.push({
                  indicator: indMatch.indicator,
                  signal,
                  confidence: indMatch.matchScore,
                  timeToEvent: this.estimateTimeToEvent(pattern, sequenceStep)
                });
              }
            }
          }
        }
      }
    }
    
    return signals;
  }
  
  /**
   * Create a signal description for a sequence step
   */
  private createSignalForSequenceStep(
    step: HistoricalPattern['sequence'][0],
    currentValue: number,
    patternName: string
  ): string | null {
    switch (step.condition) {
      case 'increasing':
        return `Increasing ${step.indicator} (${currentValue.toFixed(2)}) is a potential early signal of ${patternName} development`;
      
      case 'decreasing':
        return `Decreasing ${step.indicator} (${currentValue.toFixed(2)}) is a potential early signal of ${patternName} development`;
      
      case 'above':
        if (step.threshold !== undefined && currentValue > step.threshold) {
          return `${step.indicator} above threshold ${step.threshold} (currently ${currentValue.toFixed(2)}) matches early stage of ${patternName}`;
        }
        break;
      
      case 'below':
        if (step.threshold !== undefined && currentValue < step.threshold) {
          return `${step.indicator} below threshold ${step.threshold} (currently ${currentValue.toFixed(2)}) matches early stage of ${patternName}`;
        }
        break;
      
      case 'volatile':
        return `Volatility in ${step.indicator} may signal early stages of ${patternName}`;
    }
    
    return null;
  }
  
  /**
   * Estimate time to event based on pattern and sequence step
   */
  private estimateTimeToEvent(
    pattern: HistoricalPattern,
    step: HistoricalPattern['sequence'][0]
  ): string {
    // Default estimate
    return '3-6 months';
  }
  
  /**
   * Calculate data quality score (0-1)
   */
  private calculateDataQuality(data: EconomicIndicator[]): number {
    if (data.length === 0) return 0;
    
    let totalScore = 0;
    
    for (const indicator of data) {
      // Check data points count
      const pointsScore = Math.min(indicator.data.length / 12, 1); // Ideal: 12+ data points
      
      // Check data freshness
      const latestDate = new Date(Math.max(...indicator.data.map(d => new Date(d.date).getTime())));
      const now = new Date();
      const monthsOld = (now.getTime() - latestDate.getTime()) / (30 * 24 * 60 * 60 * 1000);
      const freshnessScore = Math.max(0, 1 - monthsOld / 6); // Penalize data older than 6 months
      
      // Check data completeness
      const datesSet = new Set(indicator.data.map(d => d.date));
      const uniqueDatesCount = datesSet.size;
      const completeScore = uniqueDatesCount === indicator.data.length ? 1 : 0.8;
      
      // Average score for this indicator
      const indicatorScore = (pointsScore + freshnessScore + completeScore) / 3;
      totalScore += indicatorScore;
    }
    
    return totalScore / data.length;
  }
  
  /**
   * Calculate pattern coverage (percentage of time covered by patterns)
   */
  private calculatePatternCoverage(matches: PatternMatchResult[]): number {
    if (matches.length === 0) return 0;
    
    // Just return a simple coverage based on match count and scores
    return Math.min(matches.length * 0.2, 1) * (
      matches.reduce((sum, match) => sum + match.matchScore, 0) / matches.length
    );
  }
  
  /**
   * Detect significant events in the data
   */
  private detectSignificantEvents(data: EconomicIndicator[]): string[] {
    const events: string[] = [];
    
    // Placeholder implementation - would use more sophisticated event detection
    for (const indicator of data) {
      if (indicator.data.length < 2) continue;
      
      // Sort data by date (oldest first)
      const sortedData = [...indicator.data]
        .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      
      // Check for large changes
      for (let i = 1; i < sortedData.length; i++) {
        const prev = sortedData[i - 1].value;
        const curr = sortedData[i].value;
        
        if (prev !== 0) {
          const pctChange = (curr - prev) / Math.abs(prev);
          
          if (Math.abs(pctChange) > 0.15) { // 15% change
            events.push(
              `${indicator.name} changed by ${(pctChange * 100).toFixed(1)}% ` +
              `on ${new Date(sortedData[i].date).toLocaleDateString()}`
            );
          }
        }
      }
    }
    
    return events;
  }
  
  /**
   * Find oldest date in the current data
   */
  private findOldestDate(data: EconomicIndicator[]): string {
    let oldestTimestamp = Date.now();
    
    for (const indicator of data) {
      for (const point of indicator.data) {
        const timestamp = new Date(point.date).getTime();
        if (timestamp < oldestTimestamp) {
          oldestTimestamp = timestamp;
        }
      }
    }
    
    return new Date(oldestTimestamp).toISOString();
  }
  
  /**
   * Load default historical patterns
   */
  private loadDefaultPatterns(): void {
    // Add some well-known economic patterns
    const patterns: HistoricalPattern[] = [
      {
        id: '1970s-stagflation',
        name: '1970s Stagflation',
        description: 'Period of high inflation combined with high unemployment and low economic growth in the 1970s, triggered by oil price shocks and expansionary monetary policy',
        period: {
          start: '1973-01-01',
          end: '1975-12-31'
        },
        indicators: ['inflation', 'unemployment', 'gdp-growth', 'oil-price'],
        sequence: [
          { indicator: 'oil-price', condition: 'increasing', duration: 6, magnitude: 0.5 },
          { indicator: 'inflation', condition: 'increasing', duration: 12, magnitude: 0.3 },
          { indicator: 'gdp-growth', condition: 'decreasing', duration: 6, magnitude: 0.2 },
          { indicator: 'unemployment', condition: 'increasing', duration: 12, magnitude: 0.3 }
        ],
        context: 'OPEC oil embargo and collapse of Bretton Woods system',
        outcome: 'Prolonged period of stagflation lasting until early 1980s, requiring significant monetary policy tightening to resolve',
        policyResponses: [
          'Tight monetary policy to control inflation',
          'Supply-side reforms to increase productivity',
          'Energy policy changes to reduce oil dependence'
        ],
        source: 'Federal Reserve Economic Data',
        tags: ['stagflation', 'inflation', 'oil-shock', 'unemployment']
      },
      {
        id: '2008-financial-crisis',
        name: '2008 Financial Crisis',
        description: 'Global financial crisis triggered by the collapse of the housing market and subsequent banking crisis',
        period: {
          start: '2007-08-01',
          end: '2009-06-30'
        },
        indicators: ['housing-index', 'unemployment', 'gdp-growth', 'credit-spread', 'stock-market'],
        sequence: [
          { indicator: 'housing-index', condition: 'decreasing', duration: 6, magnitude: 0.2 },
          { indicator: 'credit-spread', condition: 'increasing', duration: 3, magnitude: 0.5 },
          { indicator: 'stock-market', condition: 'decreasing', duration: 6, magnitude: 0.3 },
          { indicator: 'gdp-growth', condition: 'decreasing', duration: 3, magnitude: 0.3 },
          { indicator: 'unemployment', condition: 'increasing', duration: 12, magnitude: 0.5 }
        ],
        context: 'Housing bubble, excessive risk-taking in financial sector, and regulatory failures',
        outcome: 'Severe recession with slow recovery, requiring extraordinary monetary and fiscal policy responses',
        policyResponses: [
          'Expansionary monetary policy (quantitative easing)',
          'Financial sector bailouts and recapitalization',
          'Fiscal stimulus packages',
          'Strengthened financial regulations'
        ],
        source: 'Federal Reserve Economic Data, BLS',
        tags: ['financial-crisis', 'recession', 'banking-crisis', 'housing-bubble']
      },
      {
        id: 'dot-com-bubble',
        name: 'Dot-Com Bubble and Crash',
        description: 'Speculative bubble in internet-related companies followed by market crash',
        period: {
          start: '1995-01-01',
          end: '2002-12-31'
        },
        indicators: ['nasdaq', 'tech-pe-ratio', 'venture-capital', 'gdp-growth', 'unemployment'],
        sequence: [
          { indicator: 'nasdaq', condition: 'increasing', duration: 24, magnitude: 1.0 },
          { indicator: 'tech-pe-ratio', condition: 'increasing', duration: 24, magnitude: 2.0 },
          { indicator: 'venture-capital', condition: 'increasing', duration: 12, magnitude: 1.0 },
          { indicator: 'nasdaq', condition: 'decreasing', duration: 24, magnitude: 0.7 },
          { indicator: 'gdp-growth', condition: 'decreasing', duration: 6, magnitude: 0.2 },
          { indicator: 'unemployment', condition: 'increasing', duration: 12, magnitude: 0.3 }
        ],
        context: 'Rapid adoption of internet technologies, speculation in tech stocks, and excessive valuations',
        outcome: 'Significant market correction, tech sector recession, and modest broader economic recession',
        policyResponses: [
          'Interest rate cuts to stimulate economy',
          'Fiscal stimulus',
          'Improved accounting standards and transparency'
        ],
        source: 'NASDAQ, BEA, BLS',
        tags: ['bubble', 'crash', 'tech', 'recession']
      },
      {
        id: 'covid-recession',
        name: 'COVID-19 Pandemic Recession',
        description: 'Sharp economic contraction due to global COVID-19 pandemic lockdowns, followed by rapid but uneven recovery',
        period: {
          start: '2020-02-01',
          end: '2021-06-30'
        },
        indicators: ['unemployment', 'gdp-growth', 'inflation', 'retail-sales', 'services-pmi'],
        sequence: [
          { indicator: 'services-pmi', condition: 'decreasing', duration: 2, magnitude: 0.5 },
          { indicator: 'unemployment', condition: 'increasing', duration: 2, magnitude: 1.0 },
          { indicator: 'gdp-growth', condition: 'decreasing', duration: 1, magnitude: 0.3 },
          { indicator: 'retail-sales', condition: 'decreasing', duration: 2, magnitude: 0.2 },
          { indicator: 'gdp-growth', condition: 'increasing', duration: 4, magnitude: 0.3 },
          { indicator: 'unemployment', condition: 'decreasing', duration: 12, magnitude: 0.5 },
          { indicator: 'inflation', condition: 'increasing', duration: 12, magnitude: 0.4 }
        ],
        context: 'Global pandemic, lockdowns, supply chain disruptions, and massive fiscal and monetary stimulus',
        outcome: 'K-shaped recovery with high inflation, supply chain challenges, and labor market disruptions',
        policyResponses: [
          'Unprecedented fiscal stimulus',
          'Near-zero interest rates and quantitative easing',
          'Emergency lending facilities',
          'Direct payments to households',
          'Enhanced unemployment benefits'
        ],
        source: 'BEA, BLS, Federal Reserve',
        tags: ['pandemic', 'recession', 'stimulus', 'inflation']
      },
      {
        id: 'early-80s-double-dip',
        name: 'Early 1980s Double-Dip Recession',
        description: 'Back-to-back recessions triggered by aggressive monetary tightening to combat inflation',
        period: {
          start: '1980-01-01',
          end: '1982-12-31'
        },
        indicators: ['inflation', 'fed-funds-rate', 'unemployment', 'gdp-growth'],
        sequence: [
          { indicator: 'inflation', condition: 'above', threshold: 10.0, duration: 12 },
          { indicator: 'fed-funds-rate', condition: 'increasing', duration: 6, magnitude: 0.5 },
          { indicator: 'gdp-growth', condition: 'decreasing', duration: 3, magnitude: 0.2 },
          { indicator: 'unemployment', condition: 'increasing', duration: 6, magnitude: 0.3 },
          { indicator: 'gdp-growth', condition: 'increasing', duration: 3, magnitude: 0.1 },
          { indicator: 'gdp-growth', condition: 'decreasing', duration: 6, magnitude: 0.2 },
          { indicator: 'unemployment', condition: 'above', threshold: 10.0, duration: 6 },
          { indicator: 'inflation', condition: 'decreasing', duration: 24, magnitude: 0.5 }
        ],
        context: 'Volcker Fed's aggressive interest rate hikes to combat persistent inflation from the 1970s',
        outcome: 'Successfully reduced inflation but at the cost of deep recession and high unemployment',
        policyResponses: [
          'Tight monetary policy to reduce inflation',
          'Tax cuts to stimulate recovery',
          'Deregulation initiatives'
        ],
        source: 'Federal Reserve, BEA, BLS',
        tags: ['recession', 'inflation', 'monetary-policy', 'double-dip']
      }
    ];
    
    // Register patterns
    for (const pattern of patterns) {
      this.registerPattern(pattern);
    }
  }
  
  /**
   * Load historical indicator data
   */
  private async loadHistoricalData(): Promise<void> {
    // In a real implementation, this would load data from a database or API
    // For demonstration, we'll just create some mock historical data
    
    // Mock inflation data (1970-2023)
    const inflationData: EconomicIndicator = {
      id: 'inflation',
      name: 'Inflation Rate (CPI)',
      data: [
        // 1970s stagflation period
        { date: '1972-01-01', value: 3.3 },
        { date: '1973-01-01', value: 6.2 },
        { date: '1974-01-01', value: 11.0 },
        { date: '1975-01-01', value: 9.1 },
        { date: '1976-01-01', value: 5.8 },
        { date: '1977-01-01', value: 6.5 },
        { date: '1978-01-01', value: 7.6 },
        { date: '1979-01-01', value: 11.3 },
        // Volcker era
        { date: '1980-01-01', value: 13.5 },
        { date: '1981-01-01', value: 10.3 },
        { date: '1982-01-01', value: 6.2 },
        { date: '1983-01-01', value: 3.2 },
        // Great moderation
        { date: '1990-01-01', value: 5.4 },
        { date: '1995-01-01', value: 2.8 },
        { date: '2000-01-01', value: 3.4 },
        { date: '2005-01-01', value: 3.4 },
        // Financial crisis
        { date: '2008-01-01', value: 3.8 },
        { date: '2009-01-01', value: -0.4 }, // Deflation during crisis
        // Post-crisis
        { date: '2010-01-01', value: 1.6 },
        { date: '2015-01-01', value: 0.1 },
        // Pandemic
        { date: '2020-01-01', value: 1.4 },
        { date: '2021-01-01', value: 4.7 },
        { date: '2022-01-01', value: 8.0 },
        { date: '2023-01-01', value: 6.4 }
      ],
      frequency: 'annual',
      unit: 'percent',
      source: 'Bureau of Labor Statistics'
    };
    
    // Mock unemployment data
    const unemploymentData: EconomicIndicator = {
      id: 'unemployment',
      name: 'Unemployment Rate',
      data: [
        // 1970s stagflation period
        { date: '1972-01-01', value: 5.6 },
        { date: '1973-01-01', value: 4.9 },
        { date: '1974-01-01', value: 5.6 },
        { date: '1975-01-01', value: 8.5 },
        { date: '1976-01-01', value: 7.7 },
        { date: '1977-01-01', value: 7.1 },
        { date: '1978-01-01', value: 6.1 },
        { date: '1979-01-01', value: 5.8 },
        // Volcker era
        { date: '1980-01-01', value: 7.1 },
        { date: '1981-01-01', value: 7.6 },
        { date: '1982-01-01', value: 9.7 },
        { date: '1983-01-01', value: 9.6 },
        // Great moderation
        { date: '1990-01-01', value: 5.6 },
        { date: '1995-01-01', value: 5.6 },
        { date: '2000-01-01', value: 4.0 },
        { date: '2005-01-01', value: 5.1 },
        // Financial crisis
        { date: '2008-01-01', value: 5.8 },
        { date: '2009-01-01', value: 9.3 },
        { date: '2010-01-01', value: 9.6 },
        // Post-crisis
        { date: '2015-01-01', value: 5.3 },
        { date: '2019-01-01', value: 3.7 },
        // Pandemic
        { date: '2020-01-01', value: 8.1 },
        { date: '2021-01-01', value: 5.4 },
        { date: '2022-01-01', value: 3.6 },
        { date: '2023-01-01', value: 3.4 }
      ],
      frequency: 'annual',
      unit: 'percent',
      source: 'Bureau of Labor Statistics'
    };
    
    // Mock GDP growth data
    const gdpGrowthData: EconomicIndicator = {
      id: 'gdp-growth',
      name: 'GDP Growth Rate',
      data: [
        // 1970s stagflation period
        { date: '1972-01-01', value: 5.3 },
        { date: '1973-01-01', value: 5.6 },
        { date: '1974-01-01', value: -0.5 },
        { date: '1975-01-01', value: -0.2 },
        { date: '1976-01-01', value: 5.4 },
        { date: '1977-01-01', value: 4.6 },
        { date: '1978-01-01', value: 5.6 },
        { date: '1979-01-01', value: 3.2 },
        // Volcker era
        { date: '1980-01-01', value: -0.3 },
        { date: '1981-01-01', value: 2.5 },
        { date: '1982-01-01', value: -1.8 },
        { date: '1983-01-01', value: 4.6 },
        // Great moderation
        { date: '1990-01-01', value: 1.9 },
        { date: '1995-01-01', value: 2.7 },
        { date: '2000-01-01', value: 4.1 },
        { date: '2005-01-01', value: 3.5 },
        // Financial crisis
        { date: '2008-01-01', value: -0.1 },
        { date: '2009-01-01', value: -2.5 },
        // Post-crisis
        { date: '2010-01-01', value: 2.6 },
        { date: '2015-01-01', value: 2.9 },
        { date: '2019-01-01', value: 2.3 },
        // Pandemic
        { date: '2020-01-01', value: -3.4 },
        { date: '2021-01-01', value: 5.7 },
        { date: '2022-01-01', value: 2.1 },
        { date: '2023-01-01', value: 2.5 }
      ],
      frequency: 'annual',
      unit: 'percent',
      source: 'Bureau of Economic Analysis'
    };
    
    // Add historical data to the system
    this.addHistoricalIndicator(inflationData);
    this.addHistoricalIndicator(unemploymentData);
    this.addHistoricalIndicator(gdpGrowthData);
    
    // Add more indicators as needed (oil prices, interest rates, etc.)
  }
}