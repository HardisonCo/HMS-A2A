import { 
  EconomicFitnessFunctionRegistry,
  EconomicScenario,
  TimeHorizon
} from '../economic_fitness_functions';
import { 
  FitnessEvaluationService, 
  FitnessEvaluationOptions 
} from '../fitness_evaluation_service';
import { 
  PolicyEvaluator,
  PolicySolution
} from '../policy_evaluation_utils';
import { 
  EconomicDomain, 
  StrategyType 
} from '../economic_strategy_optimizer';

/**
 * Simple test script to demonstrate the fitness evaluation system
 */
async function runFitnessFunctionTest() {
  console.log('Starting fitness function test...');
  
  try {
    // Initialize the registry
    const registry = EconomicFitnessFunctionRegistry.getInstance();
    await registry.initialize();
    console.log('Fitness function registry initialized');
    
    // List available fitness functions
    const functions = registry.listFitnessFunctions();
    console.log(`Registered ${functions.length} fitness functions:`);
    functions.forEach(fn => console.log(`- ${fn.name}: ${fn.description}`));
    
    // Initialize the evaluation service
    const evaluationService = FitnessEvaluationService.getInstance();
    await evaluationService.initialize();
    console.log('Fitness evaluation service initialized');
    
    // Create a sample policy solution
    const sampleSolution = {
      taxRateAdjustment: -0.02,                // 2% tax cut
      governmentSpendingChange: 0.01,          // 1% increase in government spending
      deficitTargetPercent: 3.5,               // 3.5% deficit target
      interestRateAdjustment: -0.005,          // 0.5% interest rate cut
      implementationMonths: 6,                 // 6-month implementation timeline
      regulatoryChangeLevel: 0.3,              // Moderate regulatory changes
      budgetPercentGDP: 0.3,                   // 0.3% of GDP budget allocation
      controversyLevel: 0.4,                   // Moderate controversy
      bipartisanSupport: 0.6,                  // Reasonable bipartisan support
      publicBenefit: 0.7                       // High public benefit
    };
    
    // Define evaluation options
    const evaluationOptions: FitnessEvaluationOptions = {
      scenario: EconomicScenario.RECESSION,
      timeHorizon: TimeHorizon.SHORT_TERM,
      useCache: true,
      currentIndicators: {
        gdpGrowth: -0.02,             // -2% GDP growth
        inflation: 0.015,             // 1.5% inflation
        unemployment: 0.07,           // 7% unemployment
        interestRate: 0.02,           // 2% interest rate
        governmentDebt: 0.85,         // 85% debt-to-GDP ratio
        consumerConfidence: 0.4       // Low consumer confidence
      }
    };
    
    // Evaluate the solution
    console.log('Evaluating recession response policy...');
    const result = await evaluationService.evaluateFitness(sampleSolution, evaluationOptions);
    
    // Display the results
    console.log('\nFitness Evaluation Results:');
    console.log(`Overall Fitness: ${(result.overallFitness * 100).toFixed(1)}%`);
    console.log(`Implementation Feasibility: ${(result.implementationFeasibility * 100).toFixed(1)}%`);
    console.log(`Political Feasibility: ${(result.politicalFeasibility * 100).toFixed(1)}%`);
    
    console.log('\nMetric Scores:');
    for (const [metric, score] of result.metricScores.entries()) {
      console.log(`${metric}: ${(score * 100).toFixed(1)}%`);
    }
    
    // Test the policy evaluator
    console.log('\nTesting Policy Evaluator...');
    const policyEvaluator = PolicyEvaluator.getInstance();
    await policyEvaluator.initialize();
    
    // Create a test policy
    const testPolicy: PolicySolution = {
      id: 'test-policy-1',
      name: 'Recession Response Package',
      description: 'A comprehensive fiscal and monetary policy package to combat recession',
      domain: EconomicDomain.Fiscal,
      strategyType: StrategyType.RecessionResponse,
      parameters: sampleSolution,
      timeHorizon: TimeHorizon.SHORT_TERM,
      constraints: {},
      metadata: {}
    };
    
    // Evaluate the test policy
    const policyResult = await policyEvaluator.evaluatePolicy(testPolicy, {
      scenario: EconomicScenario.RECESSION,
      currentIndicators: evaluationOptions.currentIndicators as Record<string, number>,
      useCache: true
    });
    
    // Display policy evaluation results
    console.log('\nPolicy Evaluation Results:');
    console.log(`Policy: ${policyResult.policy.name}`);
    console.log(`Overall Score: ${policyResult.overallScore.toFixed(1)}/100`);
    
    console.log('\nScores by Category:');
    console.log(`Economic Impact: ${policyResult.scores.economic.toFixed(1)}/100`);
    console.log(`Implementation Feasibility: ${policyResult.scores.implementation.toFixed(1)}/100`);
    console.log(`Political Feasibility: ${policyResult.scores.political.toFixed(1)}/100`);
    console.log(`Time Feasibility: ${policyResult.scores.time.toFixed(1)}/100`);
    
    console.log('\nStrengths:');
    policyResult.strengths.forEach(strength => console.log(`- ${strength}`));
    
    console.log('\nWeaknesses:');
    policyResult.weaknesses.forEach(weakness => console.log(`- ${weakness}`));
    
    // Test policy variants
    console.log('\nTesting Policy Variants...');
    
    // Create a template policy
    const templatePolicy = policyEvaluator.createPolicySolutionTemplate(
      StrategyType.FiscalPolicyOptimization,
      EconomicDomain.Fiscal
    );
    
    // Create variants with different tax rate adjustments
    const taxRateVariants = policyEvaluator.createPolicyVariants(
      templatePolicy,
      'taxRateAdjustment',
      [-0.03, -0.02, -0.01, 0, 0.01, 0.02, 0.03]
    );
    
    // Evaluate and rank the variants
    console.log(`Created ${taxRateVariants.length} policy variants with different tax rates`);
    console.log('Evaluating and ranking variants...');
    
    const rankedVariants = await policyEvaluator.evaluateAndRankPolicies(
      taxRateVariants,
      {
        scenario: EconomicScenario.RECESSION,
        currentIndicators: evaluationOptions.currentIndicators as Record<string, number>
      }
    );
    
    // Display ranking results
    console.log('\nPolicy Variants Ranked by Overall Score:');
    rankedVariants.forEach((variant, index) => {
      console.log(`${index + 1}. ${variant.policy.name} - ${variant.overallScore.toFixed(1)}/100`);
      console.log(`   Tax Rate Adjustment: ${variant.policy.parameters.taxRateAdjustment}`);
      console.log(`   Key Strength: ${variant.strengths[0]}`);
    });
    
    console.log('\nFitness function test completed successfully');
  } catch (error) {
    console.error('Error in fitness function test:', error);
  }
}

// Only run if this file is executed directly
if (require.main === module) {
  runFitnessFunctionTest().catch(console.error);
}

export { runFitnessFunctionTest };