import { EventEmitter } from 'events';

/**
 * Represents a tariff policy with rate, scope, exclusions and other properties
 */
export interface TariffPolicy {
  id: string;
  name: string;
  description: string;
  countryOfOrigin?: string;
  targetCountries: string[];
  effectiveDate: Date;
  expirationDate?: Date;
  rate: number;  // Percentage rate (e.g., 25 for 25%)
  valueType: 'ad_valorem' | 'specific' | 'compound' | 'mixed';
  scope: 'global' | 'bilateral' | 'regional' | 'sectoral';
  productCategories: string[];
  harmonizedSystemCodes?: string[]; // HS codes for specific products
  exclusions?: string[];
  exceptions?: TariffException[];
  quotaLimit?: number;
  quotaUnit?: string;
  retaliatory?: boolean;
  safeguard?: boolean;
  antidumping?: boolean;
  countervailing?: boolean;
  metadata?: Record<string, any>;
  revisions?: TariffRevision[];
}

/**
 * Represents an exception to a tariff policy
 */
export interface TariffException {
  id: string;
  description: string;
  criteria: string;
  rate?: number;
  expirationDate?: Date;
}

/**
 * Represents a revision to a tariff policy
 */
export interface TariffRevision {
  id: string;
  date: Date;
  previousRate: number;
  newRate: number;
  reason: string;
  authorizedBy?: string;
}

/**
 * Economic sector or industry categorization
 */
export interface EconomicSector {
  id: string;
  name: string;
  description: string;
  naicsCode?: string; // North American Industry Classification System code
  isicCode?: string;  // International Standard Industrial Classification code
  subsectors?: string[];
  relatedSectors?: string[];
  exportVolume?: number;
  importVolume?: number;
  domesticProduction?: number;
  employmentCount?: number;
  averageWage?: number;
  gdpContribution?: number;
  tradeBalance?: number;
  priceElasticity?: number;
  crossElasticities?: Record<string, number>;
  substitutionOptions?: string[];
  supplyChainPosition?: 'upstream' | 'midstream' | 'downstream' | 'mixed';
  strategicImportance?: 'critical' | 'high' | 'medium' | 'low';
}

/**
 * Response of an economy to a tariff change
 */
export interface TariffResponse {
  economicVariables: {
    importVolume: number;
    domesticProduction: number;
    consumerPrices: number;
    producerPrices: number;
    governmentRevenue: number;
    employment: number;
    wages: number;
    productionCosts: number;
    investmentFlow: number;
    profitMargins: number;
    tradeBalance: number;
    exchangeRate?: number;
    inflationRate?: number;
    gdpGrowth?: number;
  };
  timeFrame: 'immediate' | 'short_term' | 'medium_term' | 'long_term';
  confidence: number;
  assumptions: string[];
  marketAdjustments?: string[];
  consumerBehavior?: string[];
  secondaryEffects?: TariffSecondaryEffect[];
  distributionalImpacts?: DistributionalImpact[];
}

/**
 * Secondary effects of a tariff policy
 */
export interface TariffSecondaryEffect {
  type: 'supply_chain' | 'substitution' | 'retaliation' | 'efficiency' | 'innovation' | 'other';
  description: string;
  impactedSectors: string[];
  magnitude: 'negligible' | 'minor' | 'moderate' | 'significant' | 'severe';
  timeFrame: 'immediate' | 'short_term' | 'medium_term' | 'long_term';
  probability: number; // 0-1
}

/**
 * Distributional impact of tariff policy
 */
export interface DistributionalImpact {
  stakeholder: 'consumers' | 'producers' | 'workers' | 'investors' | 'government' | string;
  impactType: 'price' | 'income' | 'employment' | 'wealth' | 'welfare' | string;
  magnitude: number; // Can be positive or negative
  description: string;
  incomeGroup?: 'low' | 'middle' | 'high' | 'all';
  geographicRegion?: string;
  demographicGroup?: string;
}

/**
 * Results of a tariff impact analysis
 */
export interface TariffAnalysisResult {
  policyId: string;
  timestamp: Date;
  targetSectors: EconomicSector[];
  relatedSectors?: EconomicSector[];
  directImpacts: TariffResponse;
  indirectImpacts?: TariffResponse;
  longTermOutcomes?: TariffResponse;
  welfareAnalysis?: {
    consumerSurplus: number;
    producerSurplus: number;
    governmentRevenue: number;
    deadweightLoss: number;
    netWelfare: number;
  };
  tradeFlowChanges?: {
    imports: Record<string, number>; // country: percent change
    exports: Record<string, number>; // country: percent change
    diversionEffects?: Record<string, number>; // country: percent change
  };
  uncertaintyFactors?: {
    key: string;
    description: string;
    impactSeverity: 'low' | 'medium' | 'high';
    probability: number; // 0-1
  }[];
  policyRecommendations?: {
    recommendation: string;
    reasoning: string;
    expectedOutcome: string;
    implementationChallenges?: string[];
    alternativeOptions?: string[];
  }[];
  confidenceScore: number; // 0-1
  analysisMethods: string[];
  modelAssumptions: string[];
  dataSources: string[];
}

/**
 * Configuration for tariff analysis
 */
export interface TariffAnalysisConfig {
  analysisTimeHorizon: 'immediate' | 'short_term' | 'medium_term' | 'long_term' | 'all';
  includeSecondaryEffects: boolean;
  includeDistributionalImpacts: boolean;
  confidenceThreshold: number; // 0-1
  sensitivityAnalysis: boolean;
  scenarioBased: boolean;
  includePolicyRecommendations: boolean;
  modelType: 'partial_equilibrium' | 'general_equilibrium' | 'input_output' | 'hybrid' | 'machine_learning';
  useHistoricalData: boolean;
  simulateRetaliations: boolean;
  supplyChainDepth: number; // How many levels of supply chain to analyze
}

/**
 * Interface for a simple country trade profile
 */
export interface CountryTradeProfile {
  countryCode: string;
  countryName: string;
  gdp: number;
  gdpPerCapita: number;
  totalExports: number;
  totalImports: number;
  tradeBalance: number;
  majorExportSectors: string[];
  majorImportSectors: string[];
  tradeAgreements: string[];
  tradingPartners: {
    countryCode: string;
    exportVolume: number;
    importVolume: number;
    tradeBalance: number;
  }[];
  tariffProfiles?: {
    averageMfnApplied: number;
    averageFinalBound: number;
    dutyCoverage: number;
    preferentialArrangements: Record<string, number>;
  };
}

/**
 * Trade flow between two countries for specific sectors
 */
export interface TradeFlow {
  exportingCountry: string;
  importingCountry: string;
  year: number;
  quarter?: number;
  month?: number;
  sector?: string;
  harmonizedSystemCode?: string;
  productDescription?: string;
  value: number;
  unit: string;
  quantity?: number;
  quantityUnit?: string;
  tariffRate?: number;
  nonTariffBarriers?: string[];
}

/**
 * Tariff impact scenario for simulation
 */
export interface TariffScenario {
  id: string;
  name: string;
  description: string;
  baselinePolicies: TariffPolicy[];
  proposedPolicies: TariffPolicy[];
  affectedSectors: string[];
  affectedCountries: string[];
  timeHorizon: 'immediate' | 'short_term' | 'medium_term' | 'long_term';
  parameters?: Record<string, any>;
  expectedOutcomes?: string[];
  policyGoals?: string[];
  stakeholderConcerns?: Record<string, string>;
  assumptionOverrides?: Record<string, any>;
}

/**
 * Result comparison between different tariff scenarios
 */
export interface ScenarioComparison {
  baselineScenario: string;
  comparisonScenarios: string[];
  metrics: {
    name: string;
    description: string;
    baselineValue: number;
    scenarioValues: Record<string, number>;
    percentChanges: Record<string, number>;
    winner?: string; // ID of the winning scenario for this metric
  }[];
  overallAssessment: {
    scenario: string;
    summary: string;
    strengths: string[];
    weaknesses: string[];
    uncertainties: string[];
  }[];
  recommendations: {
    preferredScenario: string;
    reasoning: string;
    conditionalFactors: string[];
    implementationConsiderations: string[];
  };
}

/**
 * Class for analyzing tariff impacts on economic sectors
 */
export class TariffAnalysisModel {
  private policies: Map<string, TariffPolicy> = new Map();
  private sectors: Map<string, EconomicSector> = new Map();
  private countries: Map<string, CountryTradeProfile> = new Map();
  private tradeFlows: TradeFlow[] = [];
  private scenarios: Map<string, TariffScenario> = new Map();
  private analysisResults: Map<string, TariffAnalysisResult> = new Map();
  private scenarioComparisons: Map<string, ScenarioComparison> = new Map();
  private defaultConfig: TariffAnalysisConfig = {
    analysisTimeHorizon: 'medium_term',
    includeSecondaryEffects: true,
    includeDistributionalImpacts: true,
    confidenceThreshold: 0.7,
    sensitivityAnalysis: true,
    scenarioBased: true,
    includePolicyRecommendations: true,
    modelType: 'partial_equilibrium',
    useHistoricalData: true,
    simulateRetaliations: true,
    supplyChainDepth: 2
  };
  private isInitialized: boolean = false;

  /**
   * Initialize the tariff analysis model with baseline data
   * @param initialData Optional initial data to load
   */
  public async initialize(initialData?: {
    policies?: TariffPolicy[];
    sectors?: EconomicSector[];
    countries?: CountryTradeProfile[];
    tradeFlows?: TradeFlow[];
    scenarios?: TariffScenario[];
  }): Promise<void> {
    if (initialData) {
      if (initialData.policies) {
        initialData.policies.forEach(policy => this.policies.set(policy.id, policy));
      }
      if (initialData.sectors) {
        initialData.sectors.forEach(sector => this.sectors.set(sector.id, sector));
      }
      if (initialData.countries) {
        initialData.countries.forEach(country => this.countries.set(country.countryCode, country));
      }
      if (initialData.tradeFlows) {
        this.tradeFlows = [...initialData.tradeFlows];
      }
      if (initialData.scenarios) {
        initialData.scenarios.forEach(scenario => this.scenarios.set(scenario.id, scenario));
      }
    }
    
    this.isInitialized = true;
  }

  /**
   * Add or update tariff policy
   * @param policy The tariff policy to add or update
   */
  public addPolicy(policy: TariffPolicy): void {
    this.validateInitialization();
    this.policies.set(policy.id, policy);
  }

  /**
   * Get a tariff policy by ID
   * @param policyId The ID of the policy to retrieve
   */
  public getPolicy(policyId: string): TariffPolicy | undefined {
    this.validateInitialization();
    return this.policies.get(policyId);
  }

  /**
   * Add or update an economic sector
   * @param sector The economic sector to add or update
   */
  public addSector(sector: EconomicSector): void {
    this.validateInitialization();
    this.sectors.set(sector.id, sector);
  }

  /**
   * Get an economic sector by ID
   * @param sectorId The ID of the sector to retrieve
   */
  public getSector(sectorId: string): EconomicSector | undefined {
    this.validateInitialization();
    return this.sectors.get(sectorId);
  }

  /**
   * Add or update a country trade profile
   * @param country The country trade profile to add or update
   */
  public addCountry(country: CountryTradeProfile): void {
    this.validateInitialization();
    this.countries.set(country.countryCode, country);
  }

  /**
   * Get a country trade profile by country code
   * @param countryCode The country code to retrieve
   */
  public getCountry(countryCode: string): CountryTradeProfile | undefined {
    this.validateInitialization();
    return this.countries.get(countryCode);
  }

  /**
   * Add trade flow data
   * @param flow The trade flow data to add
   */
  public addTradeFlow(flow: TradeFlow): void {
    this.validateInitialization();
    this.tradeFlows.push(flow);
  }

  /**
   * Add multiple trade flows at once
   * @param flows Array of trade flows to add
   */
  public addTradeFlows(flows: TradeFlow[]): void {
    this.validateInitialization();
    this.tradeFlows.push(...flows);
  }

  /**
   * Get trade flows filtered by criteria
   * @param criteria The criteria to filter by
   */
  public getTradeFlows(criteria: Partial<TradeFlow>): TradeFlow[] {
    this.validateInitialization();
    return this.tradeFlows.filter(flow => {
      return Object.entries(criteria).every(([key, value]) => {
        return flow[key as keyof TradeFlow] === value;
      });
    });
  }

  /**
   * Add or update a tariff scenario
   * @param scenario The tariff scenario to add or update
   */
  public addScenario(scenario: TariffScenario): void {
    this.validateInitialization();
    this.scenarios.set(scenario.id, scenario);
  }

  /**
   * Get a tariff scenario by ID
   * @param scenarioId The ID of the scenario to retrieve
   */
  public getScenario(scenarioId: string): TariffScenario | undefined {
    this.validateInitialization();
    return this.scenarios.get(scenarioId);
  }

  /**
   * Analyze the impact of a tariff policy on the specified sectors
   * @param policyId The ID of the tariff policy to analyze
   * @param sectorIds The IDs of the sectors to analyze
   * @param config Optional configuration for the analysis
   */
  public analyzeTariffImpact(
    policyId: string, 
    sectorIds: string[], 
    config?: Partial<TariffAnalysisConfig>
  ): TariffAnalysisResult {
    this.validateInitialization();

    const policy = this.policies.get(policyId);
    if (!policy) {
      throw new Error(`Tariff policy with ID ${policyId} not found`);
    }

    const sectors: EconomicSector[] = [];
    for (const sectorId of sectorIds) {
      const sector = this.sectors.get(sectorId);
      if (!sector) {
        throw new Error(`Economic sector with ID ${sectorId} not found`);
      }
      sectors.push(sector);
    }

    const analysisConfig: TariffAnalysisConfig = {
      ...this.defaultConfig,
      ...(config || {})
    };

    // Implement the actual analysis logic
    const result = this.performTariffAnalysis(policy, sectors, analysisConfig);
    this.analysisResults.set(`${policyId}_${Date.now()}`, result);
    
    return result;
  }

  /**
   * Analyze and compare multiple tariff scenarios
   * @param baselineScenarioId ID of the baseline scenario
   * @param comparisonScenarioIds IDs of scenarios to compare against the baseline
   * @param metrics Optional specific metrics to compare
   */
  public compareScenarios(
    baselineScenarioId: string,
    comparisonScenarioIds: string[],
    metrics?: string[]
  ): ScenarioComparison {
    this.validateInitialization();

    const baselineScenario = this.scenarios.get(baselineScenarioId);
    if (!baselineScenario) {
      throw new Error(`Baseline scenario with ID ${baselineScenarioId} not found`);
    }

    const comparisonScenarios: TariffScenario[] = [];
    for (const scenarioId of comparisonScenarioIds) {
      const scenario = this.scenarios.get(scenarioId);
      if (!scenario) {
        throw new Error(`Comparison scenario with ID ${scenarioId} not found`);
      }
      comparisonScenarios.push(scenario);
    }

    // Analyze each scenario
    const baselineResult = this.analyzeScenario(baselineScenario);
    const comparisonResults = new Map<string, TariffAnalysisResult>();
    
    comparisonScenarios.forEach(scenario => {
      comparisonResults.set(scenario.id, this.analyzeScenario(scenario));
    });

    // Perform the comparison
    const comparison = this.performScenarioComparison(
      baselineScenario, 
      baselineResult, 
      comparisonScenarios, 
      comparisonResults,
      metrics
    );

    const comparisonId = `comparison_${Date.now()}`;
    this.scenarioComparisons.set(comparisonId, comparison);
    
    return comparison;
  }

  /**
   * Generate what-if scenarios based on a baseline policy
   * @param baselinePolicyId ID of the baseline policy
   * @param variations Parameters to vary in the what-if scenarios
   * @param count Number of scenarios to generate
   */
  public generateWhatIfScenarios(
    baselinePolicyId: string,
    variations: { 
      parameter: string; 
      values: any[] | { min: number; max: number; steps: number } 
    }[],
    count: number = 5
  ): TariffScenario[] {
    this.validateInitialization();

    const baselinePolicy = this.policies.get(baselinePolicyId);
    if (!baselinePolicy) {
      throw new Error(`Baseline policy with ID ${baselinePolicyId} not found`);
    }

    const scenarios: TariffScenario[] = [];

    // Generate scenarios based on variations of the baseline policy
    // This is a simplified version - a real implementation would be more sophisticated
    variations.forEach(variation => {
      const values = Array.isArray(variation.values) 
        ? variation.values 
        : this.generateValueRange(variation.values);
      
      values.slice(0, count).forEach((value, index) => {
        const modifiedPolicy = { ...baselinePolicy };
        // Apply the variation to the policy
        if (this.isValidPolicyField(variation.parameter)) {
          // @ts-ignore - we validated the field exists
          modifiedPolicy[variation.parameter] = value;
        }

        const scenario: TariffScenario = {
          id: `scenario_${baselinePolicyId}_${variation.parameter}_${index}`,
          name: `What-if: ${baselinePolicy.name} with ${variation.parameter} = ${value}`,
          description: `Scenario exploring impact of changing ${variation.parameter} to ${value}`,
          baselinePolicies: [baselinePolicy],
          proposedPolicies: [modifiedPolicy],
          affectedSectors: baselinePolicy.productCategories,
          affectedCountries: baselinePolicy.targetCountries,
          timeHorizon: 'medium_term'
        };

        scenarios.push(scenario);
        this.scenarios.set(scenario.id, scenario);
      });
    });

    return scenarios;
  }

  /**
   * Get the direct trade impact of a tariff policy
   * @param policyId ID of the tariff policy
   */
  public getDirectTradeImpact(policyId: string): {
    importChanges: Record<string, number>;
    revenueGenerated: number;
    priceEffect: number;
    domesticProduction: number;
  } {
    this.validateInitialization();

    const policy = this.policies.get(policyId);
    if (!policy) {
      throw new Error(`Tariff policy with ID ${policyId} not found`);
    }

    // Filter relevant trade flows
    const relevantFlows = this.tradeFlows.filter(flow => {
      // Match if flow is for a target country and product category
      return policy.targetCountries.includes(flow.exportingCountry) &&
             (policy.productCategories.includes(flow.sector || '') ||
              (flow.harmonizedSystemCode && policy.harmonizedSystemCodes?.includes(flow.harmonizedSystemCode)));
    });

    // Calculate direct impacts
    const totalImportValue = relevantFlows.reduce((sum, flow) => sum + flow.value, 0);
    const estimatedElasticity = -1.5; // Simplified elasticity assumption
    const importChangePercent = estimatedElasticity * policy.rate / 100;
    const importChange = totalImportValue * importChangePercent;
    const newImportValue = totalImportValue + importChange;
    const revenueGenerated = newImportValue * (policy.rate / 100);
    
    // Simplified price effect calculation (assumes some pass-through to consumers)
    const priceEffect = policy.rate * 0.7; // 70% pass-through to consumer prices
    
    // Simplified domestic production effect (assumes some substitution)
    const domesticProductionChange = -importChange * 0.6; // 60% of import reduction is replaced by domestic production
    
    // Organize by country
    const importChanges: Record<string, number> = {};
    relevantFlows.forEach(flow => {
      const countryChange = flow.value * importChangePercent;
      importChanges[flow.exportingCountry] = (importChanges[flow.exportingCountry] || 0) + countryChange;
    });

    return {
      importChanges,
      revenueGenerated,
      priceEffect,
      domesticProduction: domesticProductionChange
    };
  }

  /**
   * Estimate potential retaliation measures from affected countries
   * @param policyId ID of the tariff policy
   */
  public estimateRetaliationMeasures(policyId: string): {
    likelyRetaliators: string[];
    retaliationPolicies: TariffPolicy[];
    estimatedImpact: {
      exportLoss: number;
      affectedSectors: string[];
      jobImpact: number;
    };
  } {
    this.validateInitialization();

    const policy = this.policies.get(policyId);
    if (!policy) {
      throw new Error(`Tariff policy with ID ${policyId} not found`);
    }

    // Identify countries most likely to retaliate
    const affectedTradeVolumes: Record<string, number> = {};
    policy.targetCountries.forEach(country => {
      const relevantFlows = this.tradeFlows.filter(flow => 
        flow.exportingCountry === country && 
        (policy.productCategories.includes(flow.sector || '') ||
         (flow.harmonizedSystemCode && policy.harmonizedSystemCodes?.includes(flow.harmonizedSystemCode)))
      );
      
      affectedTradeVolumes[country] = relevantFlows.reduce((sum, flow) => sum + flow.value, 0);
    });

    // Sort countries by affected trade volume
    const likelyRetaliators = Object.entries(affectedTradeVolumes)
      .sort((a, b) => b[1] - a[1])
      .filter(([_, volume]) => volume > 1000000) // Threshold for retaliation (e.g., $1M)
      .map(([country]) => country);

    // Generate potential retaliation policies
    const retaliationPolicies: TariffPolicy[] = likelyRetaliators.map(country => {
      // Find major export sectors from the retaliating country to the country imposing the tariff
      const countryProfile = this.countries.get(country);
      const targetExportSectors = countryProfile?.majorExportSectors || [];
      
      // Generate a retaliation policy
      return {
        id: `retaliation_${policyId}_${country}`,
        name: `Retaliation against ${policy.name} by ${country}`,
        description: `Retaliatory tariff policy implemented by ${country} in response to ${policy.name}`,
        countryOfOrigin: country,
        targetCountries: [policy.countryOfOrigin || 'unknown'],
        effectiveDate: new Date(policy.effectiveDate.getTime() + 90 * 24 * 60 * 60 * 1000), // 90 days after original policy
        rate: policy.rate, // Matching rate
        valueType: 'ad_valorem',
        scope: 'bilateral',
        productCategories: targetExportSectors.slice(0, 5), // Top 5 export sectors
        retaliatory: true
      };
    });

    // Estimate impact of retaliation
    let totalExportLoss = 0;
    const affectedSectors = new Set<string>();
    let jobImpact = 0;

    retaliationPolicies.forEach(retPolicy => {
      retPolicy.targetCountries.forEach(targetCountry => {
        const relevantFlows = this.tradeFlows.filter(flow => 
          flow.exportingCountry === targetCountry &&
          flow.importingCountry === retPolicy.countryOfOrigin &&
          retPolicy.productCategories.includes(flow.sector || '')
        );
        
        const exportValue = relevantFlows.reduce((sum, flow) => sum + flow.value, 0);
        const elasticity = -1.2; // Assumed elasticity
        const exportChange = exportValue * (elasticity * retPolicy.rate / 100);
        totalExportLoss += Math.abs(exportChange);
        
        // Track affected sectors
        relevantFlows.forEach(flow => {
          if (flow.sector) {
            affectedSectors.add(flow.sector);
            
            // Estimate job impact
            const sector = this.sectors.get(flow.sector);
            if (sector && sector.employmentCount) {
              // Simple job impact estimation
              const sectorExportShare = exportValue / (sector.exportVolume || exportValue);
              const jobLoss = sector.employmentCount * sectorExportShare * (exportChange / exportValue);
              jobImpact += Math.abs(jobLoss);
            }
          }
        });
      });
    });

    return {
      likelyRetaliators,
      retaliationPolicies,
      estimatedImpact: {
        exportLoss: totalExportLoss,
        affectedSectors: Array.from(affectedSectors),
        jobImpact: Math.round(jobImpact)
      }
    };
  }

  /**
   * Get optimal tariff rate based on economic analysis
   * @param countryCode Country code
   * @param sectorId Sector ID
   * @param policyGoals Policy goals to optimize for
   */
  public calculateOptimalTariffRate(
    countryCode: string,
    sectorId: string,
    policyGoals: {
      revenueGeneration: number;
      domesticProtection: number;
      negotiationLeverage: number;
      consumerWelfare: number;
    }
  ): {
    optimalRate: number;
    confidence: number;
    rationale: string;
    sensitivity: {
      elasticityEffect: number;
      retaliationRisk: number;
    }
  } {
    this.validateInitialization();

    const country = this.countries.get(countryCode);
    if (!country) {
      throw new Error(`Country with code ${countryCode} not found`);
    }

    const sector = this.sectors.get(sectorId);
    if (!sector) {
      throw new Error(`Sector with ID ${sectorId} not found`);
    }

    // Weight the importance of different objectives
    const sumOfWeights = Object.values(policyGoals).reduce((sum, weight) => sum + weight, 0);
    const normalizedWeights = {
      revenueGeneration: policyGoals.revenueGeneration / sumOfWeights,
      domesticProtection: policyGoals.domesticProtection / sumOfWeights,
      negotiationLeverage: policyGoals.negotiationLeverage / sumOfWeights,
      consumerWelfare: policyGoals.consumerWelfare / sumOfWeights
    };

    // Extract sector characteristics
    const priceElasticity = sector.priceElasticity || -1.5;
    const strategicImportance = sector.strategicImportance || 'medium';
    const importVolume = sector.importVolume || 0;
    const domesticProduction = sector.domesticProduction || 0;
    const importPenetration = importVolume / (importVolume + domesticProduction);

    // Base rate calculations for different objectives
    const revenueMaximizingRate = 1 / (1 - priceElasticity) * 100;
    const protectionRate = this.calculateProtectionRate(strategicImportance, importPenetration);
    const leverageRate = this.calculateLeverageRate(sector, country);
    const welfareRate = policyGoals.consumerWelfare > 0.7 ? 0 : 5; // High consumer welfare priority means low tariffs

    // Calculate weighted average
    const optimalRate = (
      normalizedWeights.revenueGeneration * revenueMaximizingRate +
      normalizedWeights.domesticProtection * protectionRate +
      normalizedWeights.negotiationLeverage * leverageRate +
      normalizedWeights.consumerWelfare * welfareRate
    );

    // Clamp to reasonable range (0-100%)
    const clampedRate = Math.min(Math.max(0, optimalRate), 100);
    
    // Calculate confidence based on data quality and consistency of objectives
    const dataQuality = this.assessDataQuality(sector, country);
    const objectiveConsistency = this.calculateObjectiveConsistency(policyGoals);
    const confidence = (dataQuality + objectiveConsistency) / 2;

    // Sensitivity analysis
    const elasticityEffect = Math.abs((revenueMaximizingRate - optimalRate) / optimalRate);
    const retaliationRisk = this.calculateRetaliationRisk(countryCode, sectorId, clampedRate);

    return {
      optimalRate: Math.round(clampedRate * 10) / 10, // Round to nearest 0.1%
      confidence,
      rationale: this.generateTariffRationale(
        policyGoals, 
        sector, 
        country, 
        clampedRate, 
        { revenueMaximizingRate, protectionRate, leverageRate, welfareRate }
      ),
      sensitivity: {
        elasticityEffect,
        retaliationRisk
      }
    };
  }

  // Private helper methods

  private validateInitialization() {
    if (!this.isInitialized) {
      throw new Error('TariffAnalysisModel must be initialized before use');
    }
  }

  private performTariffAnalysis(
    policy: TariffPolicy, 
    sectors: EconomicSector[], 
    config: TariffAnalysisConfig
  ): TariffAnalysisResult {
    // This is a simplified implementation - a real system would have sophisticated economic models
    
    // Direct impact calculation
    const directImpacts: TariffResponse = {
      economicVariables: {
        importVolume: 0,
        domesticProduction: 0,
        consumerPrices: 0,
        producerPrices: 0,
        governmentRevenue: 0,
        employment: 0,
        wages: 0,
        productionCosts: 0,
        investmentFlow: 0,
        profitMargins: 0,
        tradeBalance: 0
      },
      timeFrame: config.analysisTimeHorizon === 'all' ? 'short_term' : config.analysisTimeHorizon,
      confidence: 0.85,
      assumptions: [
        'Market competition is imperfect but responsive',
        'No significant supply constraints in the short term',
        'Demand elasticity is consistent across product categories'
      ]
    };

    // Calculate sector-specific impacts
    sectors.forEach(sector => {
      // Calculate direct impacts based on sector characteristics
      const importElasticity = sector.priceElasticity || -1.5;
      const importValue = sector.importVolume || 1000000;
      
      // Import volume impact (based on price elasticity)
      const importVolumeChange = importValue * importElasticity * (policy.rate / 100);
      directImpacts.economicVariables.importVolume += importVolumeChange;
      
      // Domestic production impact (some substitution effect)
      const substitutionRate = 0.6; // 60% of imports replaced by domestic
      const domesticProductionIncrease = -importVolumeChange * substitutionRate;
      directImpacts.economicVariables.domesticProduction += domesticProductionIncrease;
      
      // Price impacts
      const consumerPriceIncrease = policy.rate * 0.7; // 70% pass-through
      directImpacts.economicVariables.consumerPrices += consumerPriceIncrease;
      
      // Producer prices (slight increase due to reduced competition)
      directImpacts.economicVariables.producerPrices += policy.rate * 0.3;
      
      // Government revenue from tariffs
      const newImportValue = importValue + importVolumeChange;
      const tariffRevenue = newImportValue * (policy.rate / 100);
      directImpacts.economicVariables.governmentRevenue += tariffRevenue;
      
      // Employment impact
      if (sector.employmentCount) {
        const employmentImpact = (domesticProductionIncrease / (sector.domesticProduction || importValue)) * sector.employmentCount;
        directImpacts.economicVariables.employment += employmentImpact;
      }
      
      // Wage impact (slight increase for domestic producers)
      directImpacts.economicVariables.wages += 0.2 * (policy.rate / 100);
      
      // Production costs (potentially higher due to input tariffs)
      directImpacts.economicVariables.productionCosts += policy.rate * 0.1;
      
      // Investment flow (could increase for domestic production)
      directImpacts.economicVariables.investmentFlow += domesticProductionIncrease * 0.15;
      
      // Profit margins for domestic producers
      directImpacts.economicVariables.profitMargins += policy.rate * 0.25;
      
      // Trade balance impact
      directImpacts.economicVariables.tradeBalance -= importVolumeChange;
    });

    // For indirect impacts, we'd calculate secondary effects on upstream/downstream sectors
    // This is simplified for this implementation
    const indirectImpacts: TariffResponse | undefined = config.includeSecondaryEffects ? {
      economicVariables: {
        importVolume: directImpacts.economicVariables.importVolume * 0.3,
        domesticProduction: directImpacts.economicVariables.domesticProduction * 0.4,
        consumerPrices: directImpacts.economicVariables.consumerPrices * 0.5,
        producerPrices: directImpacts.economicVariables.producerPrices * 0.4,
        governmentRevenue: directImpacts.economicVariables.governmentRevenue * 0.1,
        employment: directImpacts.economicVariables.employment * 0.5,
        wages: directImpacts.economicVariables.wages * 0.3,
        productionCosts: directImpacts.economicVariables.productionCosts * 0.7,
        investmentFlow: directImpacts.economicVariables.investmentFlow * 0.6,
        profitMargins: directImpacts.economicVariables.profitMargins * 0.3,
        tradeBalance: directImpacts.economicVariables.tradeBalance * 0.3
      },
      timeFrame: 'medium_term',
      confidence: 0.7,
      assumptions: [
        'Upstream and downstream sectors adapt within 1-2 years',
        'Supply chains can be partially reorganized',
        'Some fixed capital investments are required for adaptation'
      ],
      secondaryEffects: [
        {
          type: 'supply_chain',
          description: 'Disruption in international supply chains leading to input cost increases',
          impactedSectors: sectors.map(s => s.id),
          magnitude: 'moderate',
          timeFrame: 'medium_term',
          probability: 0.8
        },
        {
          type: 'substitution',
          description: 'Shift to domestic or third-country suppliers',
          impactedSectors: sectors.map(s => s.id),
          magnitude: 'significant',
          timeFrame: 'medium_term',
          probability: 0.75
        }
      ]
    } : undefined;

    // Long-term outcomes if requested
    const longTermOutcomes: TariffResponse | undefined = 
      (config.analysisTimeHorizon === 'long_term' || config.analysisTimeHorizon === 'all') ? {
        economicVariables: {
          importVolume: directImpacts.economicVariables.importVolume * 0.5, // Some recovery as markets adjust
          domesticProduction: directImpacts.economicVariables.domesticProduction * 0.7, // Some lasting protection benefit
          consumerPrices: directImpacts.economicVariables.consumerPrices * 0.6, // Some price adaptation
          producerPrices: directImpacts.economicVariables.producerPrices * 0.5,
          governmentRevenue: directImpacts.economicVariables.governmentRevenue * 0.4, // Revenue declines as imports adjust
          employment: directImpacts.economicVariables.employment * 0.6,
          wages: directImpacts.economicVariables.wages * 0.8,
          productionCosts: directImpacts.economicVariables.productionCosts * 0.9,
          investmentFlow: directImpacts.economicVariables.investmentFlow * 1.2, // Potential increased investment
          profitMargins: directImpacts.economicVariables.profitMargins * 0.6, // Competition adjusts
          tradeBalance: directImpacts.economicVariables.tradeBalance * 0.4
        },
        timeFrame: 'long_term',
        confidence: 0.6,
        assumptions: [
          'Long-term elasticities are higher than short-term',
          'Industry has time to fully adapt production capabilities',
          'New trade relationships develop over time',
          'Some permanent market structure changes occur'
        ],
        secondaryEffects: [
          {
            type: 'innovation',
            description: 'Increased R&D investment to reduce dependence on imports',
            impactedSectors: sectors.map(s => s.id),
            magnitude: 'moderate',
            timeFrame: 'long_term',
            probability: 0.65
          },
          {
            type: 'efficiency',
            description: 'Productivity improvements to remain competitive despite higher input costs',
            impactedSectors: sectors.map(s => s.id),
            magnitude: 'moderate',
            timeFrame: 'long_term',
            probability: 0.7
          }
        ]
      } : undefined;

    // Calculate welfare effects
    const importValue = sectors.reduce((sum, s) => sum + (s.importVolume || 0), 0);
    const importChange = directImpacts.economicVariables.importVolume;
    const tariffRate = policy.rate / 100;
    
    const welfareAnalysis = {
      consumerSurplus: -(importValue * tariffRate + 0.5 * importChange * tariffRate),
      producerSurplus: sectors.reduce((sum, s) => {
        const domesticValue = s.domesticProduction || 0;
        const priceIncrease = tariffRate * 0.3; // Simplified producer price effect
        return sum + (domesticValue * priceIncrease);
      }, 0),
      governmentRevenue: (importValue + importChange) * tariffRate,
      deadweightLoss: -0.5 * importChange * tariffRate,
      netWelfare: 0 // Will be calculated below
    };
    
    welfareAnalysis.netWelfare = 
      welfareAnalysis.consumerSurplus + 
      welfareAnalysis.producerSurplus + 
      welfareAnalysis.governmentRevenue + 
      welfareAnalysis.deadweightLoss;

    // Trade flow changes
    const tradeFlowChanges = {
      imports: {} as Record<string, number>,
      exports: {} as Record<string, number>,
      diversionEffects: {} as Record<string, number>
    };
    
    // Basic calculation of import changes by country
    policy.targetCountries.forEach(country => {
      tradeFlowChanges.imports[country] = importElasticity * policy.rate;
    });
    
    // Simplified export effects (potential retaliation)
    if (config.simulateRetaliations) {
      policy.targetCountries.forEach(country => {
        tradeFlowChanges.exports[country] = -0.5 * policy.rate;
      });
    }
    
    // Trade diversion (shift to non-targeted countries)
    const nonTargetedCountries = Array.from(this.countries.keys())
      .filter(c => !policy.targetCountries.includes(c));
    
    nonTargetedCountries.forEach(country => {
      tradeFlowChanges.diversionEffects[country] = 0.2 * policy.rate;
    });

    // Policy recommendations if requested
    const policyRecommendations = config.includePolicyRecommendations ? [
      {
        recommendation: policy.rate > 15 
          ? "Consider a more targeted approach with lower overall rates" 
          : "The current tariff rate appears appropriate based on analysis",
        reasoning: policy.rate > 15 
          ? "High tariff rates risk significant market distortions and retaliation" 
          : "Current rate balances revenue generation with economic impact",
        expectedOutcome: policy.rate > 15 
          ? "Reduced risk of retaliation while maintaining some protection" 
          : "Modest revenue generation with manageable economic distortions",
        implementationChallenges: [
          "Administrative capacity to enforce tariffs",
          "Political pressure from affected industries",
          "International diplomatic considerations"
        ],
        alternativeOptions: [
          "Targeted subsidies for domestic producers",
          "Non-tariff technical standards",
          "Trade facilitation measures for strategic partners"
        ]
      }
    ] : undefined;

    // Assemble the final analysis result
    const result: TariffAnalysisResult = {
      policyId: policy.id,
      timestamp: new Date(),
      targetSectors: sectors,
      directImpacts,
      indirectImpacts,
      longTermOutcomes,
      welfareAnalysis,
      tradeFlowChanges,
      policyRecommendations,
      confidenceScore: 0.75,
      analysisMethods: [config.modelType, 'elasticity_analysis', 'welfare_calculation'],
      modelAssumptions: [
        'Partial market coverage',
        'Standard import demand elasticity',
        'No significant macroeconomic shocks during analysis period'
      ],
      dataSources: [
        'Internal trade flow database',
        'Economic sector profiles',
        'Country trade profiles'
      ]
    };

    return result;
  }

  private analyzeScenario(scenario: TariffScenario): TariffAnalysisResult {
    // For each scenario, analyze the proposed policies
    // This is a simplified implementation
    
    if (scenario.proposedPolicies.length === 0) {
      throw new Error('Scenario must include at least one proposed policy');
    }
    
    // Use the first proposed policy for analysis
    const policy = scenario.proposedPolicies[0];
    
    // Get sectors from affected sectors list
    const sectors: EconomicSector[] = [];
    for (const sectorId of scenario.affectedSectors) {
      const sector = this.sectors.get(sectorId);
      if (sector) {
        sectors.push(sector);
      }
    }
    
    if (sectors.length === 0) {
      throw new Error('No valid sectors found for scenario analysis');
    }
    
    // Create analysis configuration based on scenario timeHorizon
    const config: TariffAnalysisConfig = {
      ...this.defaultConfig,
      analysisTimeHorizon: scenario.timeHorizon,
      includeSecondaryEffects: true,
      includeDistributionalImpacts: true,
      scenarioBased: true
    };
    
    // Perform the analysis
    return this.performTariffAnalysis(policy, sectors, config);
  }

  private performScenarioComparison(
    baselineScenario: TariffScenario,
    baselineResult: TariffAnalysisResult,
    comparisonScenarios: TariffScenario[],
    comparisonResults: Map<string, TariffAnalysisResult>,
    metrics?: string[]
  ): ScenarioComparison {
    // Define standard metrics to compare if not specified
    const metricsToCompare = metrics || [
      'importVolume',
      'domesticProduction',
      'consumerPrices',
      'governmentRevenue',
      'employment',
      'netWelfare'
    ];
    
    // Prepare the metrics comparison
    const metricsComparison = metricsToCompare.map(metricName => {
      let baselineValue = 0;
      
      // Get value from baseline result
      if (metricName === 'netWelfare' && baselineResult.welfareAnalysis) {
        baselineValue = baselineResult.welfareAnalysis.netWelfare;
      } else if (Object.keys(baselineResult.directImpacts.economicVariables).includes(metricName)) {
        baselineValue = baselineResult.directImpacts.economicVariables[metricName as keyof typeof baselineResult.directImpacts.economicVariables];
      }
      
      // Get values from comparison scenarios
      const scenarioValues: Record<string, number> = {};
      const percentChanges: Record<string, number> = {};
      
      comparisonScenarios.forEach(scenario => {
        const result = comparisonResults.get(scenario.id);
        if (!result) return;
        
        let scenarioValue = 0;
        
        if (metricName === 'netWelfare' && result.welfareAnalysis) {
          scenarioValue = result.welfareAnalysis.netWelfare;
        } else if (Object.keys(result.directImpacts.economicVariables).includes(metricName)) {
          scenarioValue = result.directImpacts.economicVariables[metricName as keyof typeof result.directImpacts.economicVariables];
        }
        
        scenarioValues[scenario.id] = scenarioValue;
        
        // Calculate percent change
        if (baselineValue !== 0) {
          percentChanges[scenario.id] = ((scenarioValue - baselineValue) / Math.abs(baselineValue)) * 100;
        } else {
          percentChanges[scenario.id] = scenarioValue > 0 ? 100 : 0;
        }
      });
      
      // Determine winner based on the metric (different metrics have different optimization directions)
      const isHigherBetter = this.isHigherBetterForMetric(metricName);
      let winner = baselineScenario.id;
      let bestValue = baselineValue;
      
      Object.entries(scenarioValues).forEach(([scenarioId, value]) => {
        if (isHigherBetter && value > bestValue) {
          bestValue = value;
          winner = scenarioId;
        } else if (!isHigherBetter && value < bestValue) {
          bestValue = value;
          winner = scenarioId;
        }
      });
      
      // Get human-readable description
      const metricDescription = this.getMetricDescription(metricName);
      
      return {
        name: metricName,
        description: metricDescription,
        baselineValue,
        scenarioValues,
        percentChanges,
        winner
      };
    });
    
    // Count wins for overall assessment
    const winCounts: Record<string, number> = {};
    metricsComparison.forEach(metric => {
      if (metric.winner) {
        winCounts[metric.winner] = (winCounts[metric.winner] || 0) + 1;
      }
    });
    
    // Determine overall preferred scenario
    let preferredScenario = baselineScenario.id;
    let maxWins = 0;
    
    Object.entries(winCounts).forEach(([scenarioId, wins]) => {
      if (wins > maxWins) {
        maxWins = wins;
        preferredScenario = scenarioId;
      }
    });
    
    // Generate overall assessment
    const overallAssessment = [baselineScenario, ...comparisonScenarios].map(scenario => {
      const result = scenario.id === baselineScenario.id 
        ? baselineResult 
        : comparisonResults.get(scenario.id);
        
      if (!result) {
        return {
          scenario: scenario.id,
          summary: "No analysis result available",
          strengths: [],
          weaknesses: [],
          uncertainties: []
        };
      }
      
      // Find metrics where this scenario performs well
      const strengths = metricsComparison
        .filter(m => m.winner === scenario.id)
        .map(m => `Strong performance on ${m.description}`);
        
      // Find metrics where this scenario performs poorly
      const weaknesses = metricsComparison
        .filter(m => {
          if (scenario.id === baselineScenario.id) {
            // For baseline, check if it's significantly worse than any comparison
            return Object.entries(m.percentChanges).some(([_, change]) => 
              (this.isHigherBetterForMetric(m.name) && change > 15) || 
              (!this.isHigherBetterForMetric(m.name) && change < -15)
            );
          } else {
            // For comparisons, check against baseline
            const change = m.percentChanges[scenario.id];
            return (this.isHigherBetterForMetric(m.name) && change < -10) || 
                   (!this.isHigherBetterForMetric(m.name) && change > 10);
          }
        })
        .map(m => `Suboptimal performance on ${m.description}`);
        
      // General uncertainties
      const uncertainties = [
        "Long-term adaptation effects not fully captured",
        "Potential for unexpected retaliation not quantified",
        "Supply chain restructuring complexity"
      ];
      
      let summary = "";
      if (scenario.id === preferredScenario) {
        summary = "Preferred scenario based on overall metric performance";
      } else if (scenario.id === baselineScenario.id) {
        summary = "Baseline scenario provides reference point for comparison";
      } else {
        const winCount = winCounts[scenario.id] || 0;
        summary = `Alternative scenario winning on ${winCount} metrics`;
      }
      
      return {
        scenario: scenario.id,
        summary,
        strengths,
        weaknesses,
        uncertainties
      };
    });
    
    // Generate recommendations
    const recommendations = {
      preferredScenario,
      reasoning: preferredScenario === baselineScenario.id
        ? "Baseline scenario performs best across evaluated metrics"
        : `Alternative scenario ${preferredScenario} shows improvement on key metrics`,
      conditionalFactors: [
        "Prioritization of metrics may affect recommended scenario",
        "Timeframe considerations might change optimal policy",
        "Political feasibility not factored into pure economic analysis"
      ],
      implementationConsiderations: [
        "Phase-in period may reduce adjustment costs",
        "Clear communication to affected industries recommended",
        "Monitoring system for unintended consequences advised"
      ]
    };
    
    return {
      baselineScenario: baselineScenario.id,
      comparisonScenarios: comparisonScenarios.map(s => s.id),
      metrics: metricsComparison,
      overallAssessment,
      recommendations
    };
  }

  private generateValueRange(range: { min: number, max: number, steps: number }): number[] {
    const { min, max, steps } = range;
    const values = [];
    const stepSize = (max - min) / (steps - 1);
    
    for (let i = 0; i < steps; i++) {
      values.push(min + i * stepSize);
    }
    
    return values;
  }

  private isValidPolicyField(field: string): boolean {
    const validFields = [
      'rate', 'valueType', 'scope', 'productCategories',
      'harmonizedSystemCodes', 'exclusions', 'exceptions',
      'quotaLimit', 'quotaUnit'
    ];
    
    return validFields.includes(field);
  }

  private isHigherBetterForMetric(metricName: string): boolean {
    const higherBetterMetrics = [
      'domesticProduction', 'governmentRevenue', 'employment',
      'wages', 'investmentFlow', 'profitMargins', 'tradeBalance',
      'netWelfare', 'producerSurplus'
    ];
    
    const lowerBetterMetrics = [
      'importVolume', 'consumerPrices', 'productionCosts',
      'deadweightLoss'
    ];
    
    if (higherBetterMetrics.includes(metricName)) {
      return true;
    }
    
    if (lowerBetterMetrics.includes(metricName)) {
      return false;
    }
    
    // Default for unknown metrics
    return true;
  }

  private getMetricDescription(metricName: string): string {
    const descriptions: Record<string, string> = {
      importVolume: 'Change in volume of imports',
      domesticProduction: 'Domestic production output',
      consumerPrices: 'Consumer price levels',
      producerPrices: 'Producer price levels',
      governmentRevenue: 'Government tariff revenue',
      employment: 'Employment in affected sectors',
      wages: 'Wage levels in affected sectors',
      productionCosts: 'Production costs for domestic industry',
      investmentFlow: 'Investment in productive capacity',
      profitMargins: 'Profit margins for domestic producers',
      tradeBalance: 'Overall trade balance impact',
      netWelfare: 'Net economic welfare effect',
      consumerSurplus: 'Economic welfare of consumers',
      producerSurplus: 'Economic welfare of producers',
      deadweightLoss: 'Economic inefficiency created'
    };
    
    return descriptions[metricName] || `Impact on ${metricName}`;
  }

  private calculateProtectionRate(
    strategicImportance: string, 
    importPenetration: number
  ): number {
    // Higher rates for strategically important sectors with high import penetration
    const baseRate = importPenetration * 100; // Convert to percentage
    
    const importanceMultiplier = {
      'critical': 1.5,
      'high': 1.2,
      'medium': 1.0,
      'low': 0.7
    }[strategicImportance] || 1.0;
    
    return baseRate * importanceMultiplier;
  }

  private calculateLeverageRate(
    sector: EconomicSector, 
    country: CountryTradeProfile
  ): number {
    // Rate based on negotiation leverage factors
    let leverageRate = 15; // Base rate
    
    // Adjust based on country's trade position
    if (country.tradeBalance < 0) {
      // Trade deficit countries have less leverage
      leverageRate *= 0.8;
    } else {
      // Trade surplus countries have more leverage
      leverageRate *= 1.2;
    }
    
    // Adjust based on sector's strategic importance
    if (sector.strategicImportance === 'critical') {
      leverageRate *= 1.3;
    } else if (sector.strategicImportance === 'high') {
      leverageRate *= 1.1;
    }
    
    return leverageRate;
  }

  private assessDataQuality(
    sector: EconomicSector, 
    country: CountryTradeProfile
  ): number {
    // Assess data quality based on completeness of sector and country data
    let completeness = 0;
    let totalFields = 0;
    
    // Check sector data completeness
    const sectorFields = [
      'exportVolume', 'importVolume', 'domesticProduction',
      'employmentCount', 'averageWage', 'gdpContribution',
      'tradeBalance', 'priceElasticity'
    ];
    
    sectorFields.forEach(field => {
      totalFields++;
      if (sector[field as keyof EconomicSector] !== undefined) {
        completeness++;
      }
    });
    
    // Check country data completeness
    const countryFields = [
      'gdp', 'totalExports', 'totalImports',
      'tradeBalance', 'majorExportSectors', 'majorImportSectors'
    ];
    
    countryFields.forEach(field => {
      totalFields++;
      if (country[field as keyof CountryTradeProfile] !== undefined) {
        completeness++;
      }
    });
    
    return completeness / totalFields;
  }

  private calculateObjectiveConsistency(policyGoals: {
    revenueGeneration: number;
    domesticProtection: number;
    negotiationLeverage: number;
    consumerWelfare: number;
  }): number {
    // Calculate how consistent the policy goals are with each other
    // Some goals are inherently contradictory (e.g., consumer welfare vs domestic protection)
    
    const contradictions = [
      // [goal1, goal2, contradiction severity (0-1)]
      ['consumerWelfare', 'domesticProtection', 0.8],
      ['consumerWelfare', 'revenueGeneration', 0.7],
      ['revenueGeneration', 'negotiationLeverage', 0.5]
    ];
    
    let inconsistencyScore = 0;
    let maxPossibleInconsistency = 0;
    
    contradictions.forEach(([goal1, goal2, severity]) => {
      const weight1 = policyGoals[goal1 as keyof typeof policyGoals];
      const weight2 = policyGoals[goal2 as keyof typeof policyGoals];
      
      // Inconsistency occurs when both contradictory goals have high weights
      const inconsistency = (weight1 * weight2 * severity as number);
      inconsistencyScore += inconsistency;
      
      // Calculate max possible inconsistency (if all contradictory goals had weight 1)
      maxPossibleInconsistency += severity as number;
    });
    
    // Convert to consistency score (1 - normalized inconsistency)
    return 1 - (inconsistencyScore / maxPossibleInconsistency);
  }

  private calculateRetaliationRisk(
    countryCode: string,
    sectorId: string,
    tariffRate: number
  ): number {
    // Calculate risk of retaliation based on country relationships and tariff rate
    const country = this.countries.get(countryCode);
    if (!country) return 0.5; // Default if country not found
    
    // Base risk increases with tariff rate
    let risk = tariffRate / 100; // 0-1 scale
    
    // Adjust based on country trade balance
    if (country.tradeBalance < 0) {
      // Trade deficit countries less likely to retaliate (more dependent)
      risk *= 0.8;
    } else {
      // Trade surplus countries more likely to retaliate
      risk *= 1.2;
    }
    
    // Cap at 1.0
    return Math.min(risk, 1.0);
  }

  private generateTariffRationale(
    policyGoals: any, 
    sector: EconomicSector, 
    country: CountryTradeProfile,
    finalRate: number,
    rateComponents: {
      revenueMaximizingRate: number;
      protectionRate: number;
      leverageRate: number;
      welfareRate: number;
    }
  ): string {
    // Create human-readable rationale for the tariff rate recommendation
    const dominantGoal = Object.entries(policyGoals)
      .sort((a, b) => b[1] - a[1])[0][0];
    
    const dominantRateComponent = (() => {
      switch (dominantGoal) {
        case 'revenueGeneration': return 'revenueMaximizingRate';
        case 'domesticProtection': return 'protectionRate';
        case 'negotiationLeverage': return 'leverageRate';
        case 'consumerWelfare': return 'welfareRate';
        default: return 'revenueMaximizingRate';
      }
    })();
    
    const dominantRateValue = rateComponents[dominantRateComponent as keyof typeof rateComponents];
    
    let rationale = `The recommended tariff rate of ${finalRate.toFixed(1)}% is based primarily on ${this.humanizeGoal(dominantGoal)} considerations, which suggested a rate of ${dominantRateValue.toFixed(1)}%.`;
    
    rationale += ` The rate was adjusted to balance competing objectives including `;
    
    const otherGoals = Object.entries(policyGoals)
      .filter(([key]) => key !== dominantGoal)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 2)
      .map(([key]) => this.humanizeGoal(key));
    
    rationale += otherGoals.join(' and ') + '.';
    
    // Add sector-specific context
    if (sector.strategicImportance) {
      rationale += ` The ${sector.strategicImportance} strategic importance of the ${sector.name} sector was a key factor.`;
    }
    
    return rationale;
  }

  private humanizeGoal(goalKey: string): string {
    const mappings: Record<string, string> = {
      'revenueGeneration': 'government revenue generation',
      'domesticProtection': 'domestic industry protection',
      'negotiationLeverage': 'international negotiation leverage',
      'consumerWelfare': 'consumer welfare preservation'
    };
    
    return mappings[goalKey] || goalKey;
  }
}

/**
 * Service class for tariff analysis capabilities
 */
export class TariffAnalysisService extends EventEmitter {
  private model: TariffAnalysisModel;
  private policies: Map<string, TariffPolicy> = new Map();
  private sectors: Map<string, EconomicSector> = new Map();
  private scenarios: Map<string, TariffScenario> = new Map();
  private analysisResults: Map<string, TariffAnalysisResult> = new Map();
  private isInitialized: boolean = false;
  private defaultConfig: TariffAnalysisConfig = {
    analysisTimeHorizon: 'medium_term',
    includeSecondaryEffects: true,
    includeDistributionalImpacts: true,
    confidenceThreshold: 0.7,
    sensitivityAnalysis: true,
    scenarioBased: true,
    includePolicyRecommendations: true,
    modelType: 'partial_equilibrium',
    useHistoricalData: true,
    simulateRetaliations: true,
    supplyChainDepth: 2
  };
  
  /**
   * Create a new TariffAnalysisService
   */
  constructor() {
    super();
    this.model = new TariffAnalysisModel();
  }
  
  /**
   * Initialize the tariff analysis service
   * @param data Optional initial data to load
   */
  public async initialize(data?: {
    policies?: TariffPolicy[];
    sectors?: EconomicSector[];
    countries?: CountryTradeProfile[];
    tradeFlows?: TradeFlow[];
    scenarios?: TariffScenario[];
  }): Promise<void> {
    await this.model.initialize(data);
    
    if (data) {
      if (data.policies) {
        data.policies.forEach(policy => this.policies.set(policy.id, policy));
      }
      if (data.sectors) {
        data.sectors.forEach(sector => this.sectors.set(sector.id, sector));
      }
      if (data.scenarios) {
        data.scenarios.forEach(scenario => this.scenarios.set(scenario.id, scenario));
      }
    }
    
    this.isInitialized = true;
    this.emit('initialized');
  }
  
  /**
   * Create and register a new tariff policy
   * @param policy The tariff policy to create
   */
  public createPolicy(policy: Omit<TariffPolicy, 'id'>): TariffPolicy {
    this.validateInitialization();
    
    const id = `policy_${Date.now()}`;
    const newPolicy: TariffPolicy = {
      ...policy,
      id
    };
    
    this.policies.set(id, newPolicy);
    this.model.addPolicy(newPolicy);
    this.emit('policyCreated', newPolicy);
    
    return newPolicy;
  }
  
  /**
   * Update an existing tariff policy
   * @param policyId The ID of the policy to update
   * @param updates The updates to apply to the policy
   */
  public updatePolicy(policyId: string, updates: Partial<TariffPolicy>): TariffPolicy {
    this.validateInitialization();
    
    const policy = this.policies.get(policyId);
    if (!policy) {
      throw new Error(`Tariff policy with ID ${policyId} not found`);
    }
    
    const updatedPolicy = {
      ...policy,
      ...updates
    };
    
    this.policies.set(policyId, updatedPolicy);
    this.model.addPolicy(updatedPolicy);
    this.emit('policyUpdated', updatedPolicy);
    
    return updatedPolicy;
  }
  
  /**
   * Get a policy by ID
   * @param policyId The ID of the policy to retrieve
   */
  public getPolicy(policyId: string): TariffPolicy | undefined {
    this.validateInitialization();
    return this.policies.get(policyId);
  }
  
  /**
   * List all policies, optionally filtered by criteria
   * @param filter Optional filter criteria
   */
  public listPolicies(filter?: Partial<TariffPolicy>): TariffPolicy[] {
    this.validateInitialization();
    
    if (!filter) {
      return Array.from(this.policies.values());
    }
    
    return Array.from(this.policies.values()).filter(policy => {
      return Object.entries(filter).every(([key, value]) => {
        return policy[key as keyof TariffPolicy] === value;
      });
    });
  }
  
  /**
   * Register an economic sector
   * @param sector The economic sector to register
   */
  public registerSector(sector: EconomicSector): void {
    this.validateInitialization();
    this.sectors.set(sector.id, sector);
    this.model.addSector(sector);
    this.emit('sectorRegistered', sector);
  }
  
  /**
   * Analyze a tariff policy's impact on specific sectors
   * @param policyId The policy ID to analyze
   * @param sectorIds The sector IDs to analyze
   * @param config Optional analysis configuration
   */
  public analyzeTariffImpact(
    policyId: string,
    sectorIds: string[],
    config?: Partial<TariffAnalysisConfig>
  ): TariffAnalysisResult {
    this.validateInitialization();
    
    // Apply default config with any overrides
    const analysisConfig = {
      ...this.defaultConfig,
      ...(config || {})
    };
    
    const result = this.model.analyzeTariffImpact(policyId, sectorIds, analysisConfig);
    
    // Store the result
    const resultId = `analysis_${policyId}_${Date.now()}`;
    this.analysisResults.set(resultId, result);
    
    this.emit('analysisCompleted', {
      resultId,
      policyId,
      sectorIds,
      result
    });
    
    return result;
  }
  
  /**
   * Create a new tariff scenario
   * @param scenario The scenario to create
   */
  public createScenario(scenario: Omit<TariffScenario, 'id'>): TariffScenario {
    this.validateInitialization();
    
    const id = `scenario_${Date.now()}`;
    const newScenario: TariffScenario = {
      ...scenario,
      id
    };
    
    this.scenarios.set(id, newScenario);
    this.model.addScenario(newScenario);
    this.emit('scenarioCreated', newScenario);
    
    return newScenario;
  }
  
  /**
   * Compare multiple tariff scenarios
   * @param baselineScenarioId The baseline scenario ID
   * @param comparisonScenarioIds The comparison scenario IDs
   * @param metrics Optional specific metrics to compare
   */
  public compareScenarios(
    baselineScenarioId: string,
    comparisonScenarioIds: string[],
    metrics?: string[]
  ): ScenarioComparison {
    this.validateInitialization();
    
    const comparison = this.model.compareScenarios(
      baselineScenarioId,
      comparisonScenarioIds,
      metrics
    );
    
    this.emit('comparisonCompleted', {
      baselineScenarioId,
      comparisonScenarioIds,
      comparison
    });
    
    return comparison;
  }
  
  /**
   * Generate what-if scenarios for a policy
   * @param policyId The policy ID to use as baseline
   * @param variations The parameters to vary
   * @param count The number of scenarios to generate
   */
  public generateWhatIfScenarios(
    policyId: string,
    variations: { 
      parameter: string; 
      values: any[] | { min: number; max: number; steps: number } 
    }[],
    count: number = 5
  ): TariffScenario[] {
    this.validateInitialization();
    
    const scenarios = this.model.generateWhatIfScenarios(policyId, variations, count);
    
    scenarios.forEach(scenario => {
      this.scenarios.set(scenario.id, scenario);
    });
    
    this.emit('scenariosGenerated', {
      policyId,
      scenarios
    });
    
    return scenarios;
  }
  
  /**
   * Calculate optimal tariff rate for a specific sector and country
   * @param countryCode The country code
   * @param sectorId The sector ID
   * @param policyGoals The policy goals to optimize for
   */
  public calculateOptimalTariffRate(
    countryCode: string,
    sectorId: string,
    policyGoals: {
      revenueGeneration: number;
      domesticProtection: number;
      negotiationLeverage: number;
      consumerWelfare: number;
    }
  ): {
    optimalRate: number;
    confidence: number;
    rationale: string;
    sensitivity: {
      elasticityEffect: number;
      retaliationRisk: number;
    }
  } {
    this.validateInitialization();
    
    const result = this.model.calculateOptimalTariffRate(
      countryCode,
      sectorId,
      policyGoals
    );
    
    this.emit('optimalRateCalculated', {
      countryCode,
      sectorId,
      policyGoals,
      result
    });
    
    return result;
  }
  
  /**
   * Estimate potential retaliation to a tariff policy
   * @param policyId The policy ID
   */
  public estimateRetaliationMeasures(policyId: string): {
    likelyRetaliators: string[];
    retaliationPolicies: TariffPolicy[];
    estimatedImpact: {
      exportLoss: number;
      affectedSectors: string[];
      jobImpact: number;
    };
  } {
    this.validateInitialization();
    
    const result = this.model.estimateRetaliationMeasures(policyId);
    
    this.emit('retaliationEstimated', {
      policyId,
      result
    });
    
    return result;
  }
  
  /**
   * Get the direct trade impact of a tariff policy
   * @param policyId The policy ID
   */
  public getDirectTradeImpact(policyId: string): {
    importChanges: Record<string, number>;
    revenueGenerated: number;
    priceEffect: number;
    domesticProduction: number;
  } {
    this.validateInitialization();
    
    const result = this.model.getDirectTradeImpact(policyId);
    
    this.emit('tradeImpactCalculated', {
      policyId,
      result
    });
    
    return result;
  }
  
  private validateInitialization() {
    if (!this.isInitialized) {
      throw new Error('TariffAnalysisService must be initialized before use');
    }
  }
}