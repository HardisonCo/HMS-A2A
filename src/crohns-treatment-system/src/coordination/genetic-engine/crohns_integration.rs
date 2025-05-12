//! Crohn's disease specific integration for the genetic engine
//!
//! This module extends the genetic algorithm engine with specialized
//! functionality for optimizing Crohn's disease treatments based on
//! patient biomarkers, disease characteristics, and treatment history.

use std::collections::HashMap;
use std::sync::Arc;

use crate::core::{GeneticEngine, GeneticConfig, Individual, Population};
use crate::representation::{TreatmentChromosome, TreatmentGene, PatientContext};
use crate::fitness::FitnessFunction;

/// Biomarker types important for Crohn's disease treatment
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum BiomarkerType {
    /// NOD2 genetic variant
    NOD2,
    /// ATG16L1 genetic variant
    ATG16L1,
    /// IL23R genetic variant
    IL23R,
    /// LRRK2-MUC19 risk alleles
    LRRK2MUC19,
    /// Fecal calprotectin level
    FecalCalprotectin,
    /// C-reactive protein level
    CRP,
    /// Erythrocyte sedimentation rate
    ESR,
    /// Microbial diversity
    MicrobialDiversity,
    /// F. prausnitzii abundance
    FPrausnitzii,
    /// E. coli abundance
    EColi,
    /// Other biomarker (with string identifier)
    Other(String),
}

/// Biomarker value (can be categorical or numerical)
#[derive(Clone, Debug)]
pub enum BiomarkerValue {
    /// Categorical value (e.g. "variant", "normal")
    Categorical(String),
    /// Numerical value with unit
    Numerical(f64, String),
}

/// Detailed patient profile for Crohn's disease
#[derive(Clone, Debug)]
pub struct CrohnsPatientProfile {
    /// Basic patient context
    pub basic_context: PatientContext,
    /// Biomarker data
    pub biomarkers: HashMap<BiomarkerType, BiomarkerValue>,
    /// Previous treatments and responses
    pub treatment_history: Vec<TreatmentHistoryEntry>,
    /// Disease duration in months
    pub disease_duration: u32,
    /// Extraintestinal manifestations
    pub extraintestinal_manifestations: Vec<String>,
    /// Comorbidities
    pub comorbidities: Vec<String>,
}

/// Entry in treatment history
#[derive(Clone, Debug)]
pub struct TreatmentHistoryEntry {
    /// Medication used
    pub medication: String,
    /// Response to treatment
    pub response: TreatmentResponse,
    /// Duration of treatment in days
    pub duration: u32,
    /// Any adverse events
    pub adverse_events: Vec<String>,
}

/// Response to treatment
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum TreatmentResponse {
    /// Complete response
    Complete,
    /// Partial response
    Partial,
    /// No response
    None,
    /// Adverse reaction
    Adverse,
}

/// Crohn's disease specific treatment chromosome
#[derive(Clone, Debug)]
pub struct CrohnsTreatmentChromosome {
    /// Base treatment chromosome
    pub base: TreatmentChromosome,
    /// Biomarker-specific adjustments
    pub biomarker_weights: HashMap<BiomarkerType, f64>,
    /// Treatment adherence probability
    pub adherence_probability: f64,
    /// Expected side effect risk
    pub side_effect_risk: f64,
}

impl CrohnsTreatmentChromosome {
    /// Create a new Crohn's treatment chromosome
    pub fn new(base: TreatmentChromosome) -> Self {
        Self {
            base,
            biomarker_weights: HashMap::new(),
            adherence_probability: 0.85, // Default value
            side_effect_risk: 0.15,      // Default value
        }
    }
    
    /// Add a biomarker weight
    pub fn with_biomarker_weight(mut self, biomarker: BiomarkerType, weight: f64) -> Self {
        self.biomarker_weights.insert(biomarker, weight);
        self
    }
    
    /// Set the adherence probability
    pub fn with_adherence_probability(mut self, probability: f64) -> Self {
        self.adherence_probability = probability;
        self
    }
    
    /// Set the side effect risk
    pub fn with_side_effect_risk(mut self, risk: f64) -> Self {
        self.side_effect_risk = risk;
        self
    }
}

/// Fitness function that evaluates Crohn's treatment effectiveness
pub struct CrohnsTreatmentFitness {
    /// Weight for efficacy component
    efficacy_weight: f64,
    /// Weight for safety component
    safety_weight: f64,
    /// Weight for adherence component
    adherence_weight: f64,
    /// Weight for cost component
    cost_weight: f64,
}

impl CrohnsTreatmentFitness {
    /// Create a new fitness function with default weights
    pub fn new() -> Self {
        Self {
            efficacy_weight: 0.5,
            safety_weight: 0.25,
            adherence_weight: 0.15,
            cost_weight: 0.1,
        }
    }
    
    /// Create a new fitness function with custom weights
    pub fn with_weights(
        efficacy_weight: f64, 
        safety_weight: f64, 
        adherence_weight: f64, 
        cost_weight: f64
    ) -> Self {
        Self {
            efficacy_weight,
            safety_weight,
            adherence_weight,
            cost_weight,
        }
    }
    
    /// Calculate the efficacy score based on biomarkers and treatment
    fn calculate_efficacy(&self, chromosome: &CrohnsTreatmentChromosome, profile: &CrohnsPatientProfile) -> f64 {
        // This is a placeholder implementation that will be expanded
        // In a real implementation, we would use biomarker data to predict treatment efficacy
        
        // For now, return a dummy value
        0.75
    }
    
    /// Calculate the safety score based on patient characteristics and treatment
    fn calculate_safety(&self, chromosome: &CrohnsTreatmentChromosome, profile: &CrohnsPatientProfile) -> f64 {
        // This is a placeholder implementation that will be expanded
        // In a real implementation, we would predict adverse event likelihood
        
        // For now, return a dummy value
        0.85
    }
    
    /// Calculate the adherence score based on treatment complexity
    fn calculate_adherence(&self, chromosome: &CrohnsTreatmentChromosome) -> f64 {
        // This is a placeholder implementation that will be expanded
        // In a real implementation, we would consider dosing frequency, pill burden, etc.
        
        // For now, return the predefined adherence probability
        chromosome.adherence_probability
    }
    
    /// Calculate the cost score
    fn calculate_cost(&self, chromosome: &CrohnsTreatmentChromosome) -> f64 {
        // This is a placeholder implementation that will be expanded
        // In a real implementation, we would calculate actual cost
        
        // For now, return a dummy value
        0.65
    }
}

impl FitnessFunction for CrohnsTreatmentFitness {
    fn calculate_fitness(&self, individual: &mut Individual, context: &dyn std::any::Any) -> f64 {
        // Try to downcast the context to CrohnsPatientProfile
        if let Some(profile) = context.downcast_ref::<CrohnsPatientProfile>() {
            // Try to downcast the chromosome to CrohnsTreatmentChromosome
            if let Some(crohns_chromosome) = individual.chromosome.attributes.get("crohns") {
                if let Some(crohns_chromosome) = crohns_chromosome.downcast_ref::<CrohnsTreatmentChromosome>() {
                    // Calculate component scores
                    let efficacy = self.calculate_efficacy(crohns_chromosome, profile);
                    let safety = self.calculate_safety(crohns_chromosome, profile);
                    let adherence = self.calculate_adherence(crohns_chromosome);
                    let cost = self.calculate_cost(crohns_chromosome);
                    
                    // Calculate weighted sum
                    let fitness = 
                        self.efficacy_weight * efficacy +
                        self.safety_weight * safety +
                        self.adherence_weight * adherence +
                        self.cost_weight * cost;
                    
                    return fitness;
                }
            }
            
            // If we can't downcast, return a low fitness
            return 0.1;
        }
        
        // If we can't downcast the context, return a very low fitness
        0.01
    }
}

/// Factory for creating optimized treatment plans for Crohn's patients
pub struct CrohnsTreatmentOptimizer {
    /// Genetic engine instance
    engine: GeneticEngine,
    /// Additional configuration
    config: CrohnsOptimizerConfig,
}

/// Configuration for the Crohn's treatment optimizer
#[derive(Clone, Debug)]
pub struct CrohnsOptimizerConfig {
    /// Number of generations to run
    pub generations: usize,
    /// Size of the population
    pub population_size: usize,
    /// Whether to use personalized biomarker weighting
    pub use_biomarker_weighting: bool,
    /// Whether to consider treatment history
    pub consider_treatment_history: bool,
    /// Whether to optimize for adherence
    pub optimize_for_adherence: bool,
    /// Maximum number of medications in a treatment plan
    pub max_medications: usize,
}

impl Default for CrohnsOptimizerConfig {
    fn default() -> Self {
        Self {
            generations: 50,
            population_size: 100,
            use_biomarker_weighting: true,
            consider_treatment_history: true,
            optimize_for_adherence: true,
            max_medications: 3,
        }
    }
}

impl CrohnsTreatmentOptimizer {
    /// Create a new optimizer with default configuration
    pub fn new() -> Self {
        let mut genetic_config = GeneticConfig::default();
        let crohns_config = CrohnsOptimizerConfig::default();
        
        // Adjust genetic config based on Crohn's config
        genetic_config.max_generations = crohns_config.generations;
        genetic_config.population_size = crohns_config.population_size;
        
        // Create the genetic engine
        let engine = GeneticEngine::new(genetic_config)
            .with_fitness(Box::new(CrohnsTreatmentFitness::new()));
        
        Self {
            engine,
            config: crohns_config,
        }
    }
    
    /// Create a new optimizer with custom configuration
    pub fn with_config(config: CrohnsOptimizerConfig) -> Self {
        let mut genetic_config = GeneticConfig::default();
        
        // Adjust genetic config based on Crohn's config
        genetic_config.max_generations = config.generations;
        genetic_config.population_size = config.population_size;
        
        // Create the genetic engine
        let engine = GeneticEngine::new(genetic_config)
            .with_fitness(Box::new(CrohnsTreatmentFitness::new()));
        
        Self {
            engine,
            config,
        }
    }
    
    /// Optimize a treatment plan for a patient
    pub fn optimize_treatment(&self, profile: &CrohnsPatientProfile) -> Option<CrohnsTreatmentChromosome> {
        // Create initial population based on patient profile
        let initial_population = self.create_initial_population(profile);
        
        // Run the optimization
        let (final_population, _stats) = self.engine.optimize(initial_population, profile);
        
        // Extract the best treatment
        if let Some(best_individual) = final_population.best_individual {
            if let Some(crohns_attr) = best_individual.chromosome.attributes.get("crohns") {
                if let Some(crohns_chromosome) = crohns_attr.downcast_ref::<CrohnsTreatmentChromosome>() {
                    return Some(crohns_chromosome.clone());
                }
            }
        }
        
        None
    }
    
    /// Create an initial population based on patient profile
    fn create_initial_population(&self, profile: &CrohnsPatientProfile) -> Population {
        // This is a simplified implementation
        // In a real implementation, we would generate diverse treatment options
        // based on the patient profile, biomarkers, and treatment history
        
        // For now, we generate some basic treatment plans
        let mut individuals = Vec::with_capacity(self.config.population_size);
        
        for _ in 0..self.config.population_size {
            // Create a simple treatment chromosome
            let base_chromosome = TreatmentChromosome::new(vec![
                TreatmentGene::new(
                    crate::representation::Medication::Upadacitinib,
                    15.0,
                    crate::representation::DosageUnit::Mg,
                    crate::representation::Frequency::Daily,
                    30
                ),
            ]);
            
            // Create the Crohn's-specific chromosome
            let crohns_chromosome = CrohnsTreatmentChromosome::new(base_chromosome.clone())
                .with_biomarker_weight(BiomarkerType::NOD2, 0.8)
                .with_biomarker_weight(BiomarkerType::IL23R, 0.7)
                .with_adherence_probability(0.85)
                .with_side_effect_risk(0.15);
            
            // Add to the attributes
            let mut individual = Individual::new(base_chromosome);
            individual.chromosome.attributes.insert(
                "crohns".to_string(), 
                Box::new(crohns_chromosome) as Box<dyn std::any::Any>
            );
            
            individuals.push(individual);
        }
        
        Population::new(individuals)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_crohns_treatment_chromosome() {
        // Create a base treatment chromosome
        let base = TreatmentChromosome::new(vec![
            TreatmentGene::new(
                crate::representation::Medication::Upadacitinib,
                15.0,
                crate::representation::DosageUnit::Mg,
                crate::representation::Frequency::Daily,
                30
            ),
        ]);
        
        // Create a Crohn's treatment chromosome
        let crohns = CrohnsTreatmentChromosome::new(base)
            .with_biomarker_weight(BiomarkerType::NOD2, 0.8)
            .with_adherence_probability(0.9)
            .with_side_effect_risk(0.1);
        
        // Verify biomarker weights
        assert_eq!(crohns.biomarker_weights.get(&BiomarkerType::NOD2), Some(&0.8));
        
        // Verify adherence probability
        assert_eq!(crohns.adherence_probability, 0.9);
        
        // Verify side effect risk
        assert_eq!(crohns.side_effect_risk, 0.1);
    }
    
    #[test]
    fn test_crohns_optimizer_creation() {
        // Create with default config
        let optimizer = CrohnsTreatmentOptimizer::new();
        assert_eq!(optimizer.config.population_size, 100);
        
        // Create with custom config
        let config = CrohnsOptimizerConfig {
            population_size: 200,
            ..CrohnsOptimizerConfig::default()
        };
        let optimizer = CrohnsTreatmentOptimizer::with_config(config);
        assert_eq!(optimizer.config.population_size, 200);
    }
}