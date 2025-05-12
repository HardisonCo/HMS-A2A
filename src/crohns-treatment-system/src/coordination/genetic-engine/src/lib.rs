/*!
Genetic Engine for Crohn's Disease Treatment System

This library provides genetic algorithm implementations for optimizing
treatment plans for Crohn's disease patients based on their biomarkers,
genetic profile, and treatment history.
*/

use std::sync::Arc;
use thiserror::Error;

mod chromosome;
mod config;
mod fitness;
mod models;
mod operations;
mod population;
mod verification;

#[cfg(feature = "python")]
pub mod ffi;

#[cfg(feature = "wasm")]
pub mod wasm_bindings;

// Re-exports
pub use chromosome::{Chromosome, TreatmentChromosome};
pub use config::GeneticConfig;
pub use fitness::{FitnessContext, FitnessEvaluator, TreatmentFitnessContext};
pub use models::{
    AdverseEvent, BiomarkerInfluence, Patient, PatientData, Treatment, TreatmentHistory,
    TreatmentPlan, TreatmentVerification,
};
pub use operations::{crossover, mutation, selection};
pub use population::Population;
pub use verification::TreatmentVerifier;

/// Errors that can occur in the genetic engine
#[derive(Error, Debug)]
pub enum GeneticEngineError {
    #[error("Invalid chromosome: {0}")]
    InvalidChromosome(String),

    #[error("Invalid population: {0}")]
    InvalidPopulation(String),

    #[error("Fitness evaluation failed: {0}")]
    FitnessEvaluation(String),

    #[error("Optimization failed: {0}")]
    OptimizationFailed(String),

    #[error("Configuration error: {0}")]
    ConfigError(String),

    #[error("Serialization error: {0}")]
    SerializationError(String),

    #[error("Verification error: {0}")]
    VerificationError(String),
}

/// Result type for genetic engine operations
pub type Result<T> = std::result::Result<T, GeneticEngineError>;

/// The main genetic engine for treatment optimization
pub struct GeneticEngine {
    config: GeneticConfig,
    fitness_evaluator: Arc<dyn FitnessEvaluator>,
    verifier: TreatmentVerifier,
}

impl GeneticEngine {
    /// Create a new genetic engine with the given configuration
    pub fn new(config: GeneticConfig) -> Self {
        let fitness_evaluator = Arc::new(fitness::DefaultFitnessEvaluator::new());
        let verifier = TreatmentVerifier::new();

        GeneticEngine {
            config,
            fitness_evaluator,
            verifier,
        }
    }

    /// Create a new genetic engine with default configuration
    pub fn default() -> Self {
        Self::new(GeneticConfig::default())
    }

    /// Optimize a treatment plan for a patient
    pub fn optimize_treatment(&self, patient: PatientData) -> TreatmentPlan {
        let context = TreatmentFitnessContext::new(patient);
        let mut population = self.initialize_population(&context);

        for _ in 0..self.config.generations {
            population = self.evolve_population(population, &context);
        }

        // Get the best chromosome
        let best = population.get_best().unwrap();
        let treatment_plan = best.to_treatment_plan();
        
        // Verify the treatment plan
        let verification = self.verify_treatment(treatment_plan.clone());
        if !verification.is_valid {
            log::warn!("Generated treatment plan did not pass verification: {:?}", verification);
        }

        treatment_plan
    }

    /// Verify a treatment plan for safety and efficacy
    pub fn verify_treatment(&self, treatment: TreatmentPlan) -> TreatmentVerification {
        self.verifier.verify_treatment_plan(&treatment)
    }

    /// Initialize the population for genetic algorithm
    fn initialize_population(&self, context: &TreatmentFitnessContext) -> Population<TreatmentChromosome> {
        let mut population = Population::new(self.config.population_size);
        
        for _ in 0..self.config.population_size {
            let chromosome = TreatmentChromosome::random(context);
            population.add(chromosome);
        }

        // Calculate initial fitness
        for i in 0..population.size() {
            if let Some(chromosome) = population.get_mut(i) {
                let fitness = self.fitness_evaluator.evaluate(chromosome, context);
                chromosome.set_fitness(fitness);
            }
        }

        population
    }

    /// Evolve the population using genetic operators
    fn evolve_population(
        &self,
        population: Population<TreatmentChromosome>,
        context: &TreatmentFitnessContext,
    ) -> Population<TreatmentChromosome> {
        let mut new_population = Population::new(self.config.population_size);

        // Elitism: Keep the best chromosomes
        for i in 0..self.config.elitism_count {
            if let Some(chromosome) = population.get_best_n(i) {
                new_population.add(chromosome.clone());
            }
        }

        // Generate the rest of the population
        while new_population.size() < self.config.population_size {
            // Selection
            let parent1 = selection::tournament_selection(
                &population,
                self.config.tournament_size,
            );
            let parent2 = selection::tournament_selection(
                &population,
                self.config.tournament_size,
            );

            if let (Some(p1), Some(p2)) = (parent1, parent2) {
                // Crossover
                let (mut child1, mut child2) = if rand::random::<f64>() < self.config.crossover_rate {
                    crossover::single_point_crossover(p1, p2)
                } else {
                    (p1.clone(), p2.clone())
                };

                // Mutation
                mutation::mutate_chromosome(&mut child1, self.config.mutation_rate);
                mutation::mutate_chromosome(&mut child2, self.config.mutation_rate);

                // Calculate fitness
                let fitness1 = self.fitness_evaluator.evaluate(&child1, context);
                child1.set_fitness(fitness1);

                let fitness2 = self.fitness_evaluator.evaluate(&child2, context);
                child2.set_fitness(fitness2);

                // Add to new population
                new_population.add(child1);
                if new_population.size() < self.config.population_size {
                    new_population.add(child2);
                }
            }
        }

        new_population
    }

    /// Get alternative treatment plans
    pub fn get_treatment_alternatives(&self, treatment: TreatmentPlan) -> Vec<TreatmentPlan> {
        // Implementation will generate alternatives by modifying the given treatment plan
        let mut alternatives = Vec::new();
        
        // This is a simplified implementation to generate alternatives
        // A more sophisticated approach would use the genetic algorithm
        let context = TreatmentFitnessContext::new(treatment.patient.clone());
        let chromosome = TreatmentChromosome::from_treatment_plan(&treatment);
        
        for _ in 0..3 {
            let mut alt_chromosome = chromosome.clone();
            mutation::mutate_chromosome(&mut alt_chromosome, 0.3);  // Higher mutation rate for diversity
            
            let fitness = self.fitness_evaluator.evaluate(&alt_chromosome, &context);
            alt_chromosome.set_fitness(fitness);
            
            let alt_treatment = alt_chromosome.to_treatment_plan();
            alternatives.push(alt_treatment);
        }
        
        alternatives
    }

    /// Evaluate biomarkers for their significance in treatment response
    pub fn evaluate_biomarkers(&self, biomarker_data: BiomarkerData) -> BiomarkerAnalysis {
        // Implementation will analyze the impact of different biomarkers on treatment response
        BiomarkerAnalysis {
            patient_id: biomarker_data.patient_id,
            biomarker_scores: biomarker_data.markers.iter()
                .map(|marker| BiomarkerScore {
                    biomarker: marker.name.clone(),
                    impact_score: self.calculate_biomarker_impact(marker),
                    confidence: 0.75, // Placeholder
                    relevant_medications: vec!["Ustekinumab".into(), "Vedolizumab".into()], // Placeholder
                })
                .collect(),
            overall_genetic_risk: 0.65, // Placeholder
        }
    }
    
    /// Calculate the impact of a biomarker on treatment response
    fn calculate_biomarker_impact(&self, marker: &Biomarker) -> f64 {
        // This is a simplified implementation
        // A more sophisticated approach would use machine learning models
        match marker.name.as_str() {
            "NOD2" => 0.85,
            "IL23R" => 0.75,
            "ATG16L1" => 0.70,
            "IRGM" => 0.65,
            "LRRK2" => 0.60,
            _ => 0.50,
        }
    }
    
    /// Simulate the outcome of a treatment plan for a patient
    pub fn simulate_treatment_outcome(
        &self,
        patient: PatientData,
        treatment: TreatmentPlan,
    ) -> TreatmentOutcomeSimulation {
        // Implementation will simulate the expected outcome of the treatment
        let context = TreatmentFitnessContext::new(patient.clone());
        let chromosome = TreatmentChromosome::from_treatment_plan(&treatment);
        let fitness = self.fitness_evaluator.evaluate(&chromosome, &context);
        
        // Convert fitness to a more detailed outcome simulation
        let response_probability = fitness;
        let remission_probability = fitness * 0.8; // Simplified calculation
        
        let adverse_events = self.predict_adverse_events(&patient, &treatment);
        
        TreatmentOutcomeSimulation {
            patient_id: patient.patient_id,
            treatment_plan: treatment,
            response_probability,
            remission_probability,
            predicted_biomarker_changes: vec![
                BiomarkerChange {
                    biomarker: "CDAI".into(),
                    current_value: patient.clinical_data.disease_activity.cdai as f64,
                    predicted_value: patient.clinical_data.disease_activity.cdai as f64 * (1.0 - fitness * 0.5),
                    unit: "score".into(),
                },
                BiomarkerChange {
                    biomarker: "fecal_calprotectin".into(),
                    current_value: patient.clinical_data.disease_activity.fecal_calprotectin,
                    predicted_value: patient.clinical_data.disease_activity.fecal_calprotectin * (1.0 - fitness * 0.6),
                    unit: "µg/g".into(),
                },
                BiomarkerChange {
                    biomarker: "CRP".into(),
                    current_value: patient.clinical_data.disease_activity.crp,
                    predicted_value: patient.clinical_data.disease_activity.crp * (1.0 - fitness * 0.4),
                    unit: "mg/L".into(),
                },
            ],
            adverse_events,
            confidence: 0.7, // Placeholder
        }
    }
    
    /// Predict potential adverse events based on patient profile and treatment
    fn predict_adverse_events(
        &self,
        patient: &PatientData,
        treatment: &TreatmentPlan,
    ) -> Vec<PredictedAdverseEvent> {
        let mut adverse_events = Vec::new();
        
        // Simplified adverse event prediction based on medication
        for medication in &treatment.treatment_plan {
            match medication.medication.as_str() {
                "Infliximab" => {
                    // Check if patient has history of infusion reactions
                    let has_history = patient.treatment_history.iter().any(|th| {
                        th.medication == "Infliximab" && 
                        th.adverse_events.iter().any(|ae| ae.contains("infusion"))
                    });
                    
                    if has_history {
                        adverse_events.push(PredictedAdverseEvent {
                            event_type: "Infusion reaction".into(),
                            probability: 0.4,
                            severity: "Moderate".into(),
                        });
                    } else {
                        adverse_events.push(PredictedAdverseEvent {
                            event_type: "Infusion reaction".into(),
                            probability: 0.1,
                            severity: "Mild".into(),
                        });
                    }
                },
                "Azathioprine" => {
                    adverse_events.push(PredictedAdverseEvent {
                        event_type: "Nausea".into(),
                        probability: 0.2,
                        severity: "Mild".into(),
                    });
                    adverse_events.push(PredictedAdverseEvent {
                        event_type: "Bone marrow suppression".into(),
                        probability: 0.05,
                        severity: "Severe".into(),
                    });
                },
                "Ustekinumab" => {
                    adverse_events.push(PredictedAdverseEvent {
                        event_type: "Injection site reaction".into(),
                        probability: 0.15,
                        severity: "Mild".into(),
                    });
                },
                _ => {}
            }
        }
        
        adverse_events
    }
}

/// Biomarker data for analysis
#[derive(Clone, Debug)]
pub struct BiomarkerData {
    pub patient_id: String,
    pub markers: Vec<Biomarker>,
}

/// Individual biomarker
#[derive(Clone, Debug)]
pub struct Biomarker {
    pub name: String,
    pub value: f64,
    pub zygosity: Option<String>,
}

/// Biomarker analysis results
#[derive(Clone, Debug)]
pub struct BiomarkerAnalysis {
    pub patient_id: String,
    pub biomarker_scores: Vec<BiomarkerScore>,
    pub overall_genetic_risk: f64,
}

/// Score for individual biomarker
#[derive(Clone, Debug)]
pub struct BiomarkerScore {
    pub biomarker: String,
    pub impact_score: f64,
    pub confidence: f64,
    pub relevant_medications: Vec<String>,
}

/// Treatment outcome simulation
#[derive(Clone, Debug)]
pub struct TreatmentOutcomeSimulation {
    pub patient_id: String,
    pub treatment_plan: TreatmentPlan,
    pub response_probability: f64,
    pub remission_probability: f64,
    pub predicted_biomarker_changes: Vec<BiomarkerChange>,
    pub adverse_events: Vec<PredictedAdverseEvent>,
    pub confidence: f64,
}

/// Predicted biomarker change
#[derive(Clone, Debug)]
pub struct BiomarkerChange {
    pub biomarker: String,
    pub current_value: f64,
    pub predicted_value: f64,
    pub unit: String,
}

/// Predicted adverse event
#[derive(Clone, Debug)]
pub struct PredictedAdverseEvent {
    pub event_type: String,
    pub probability: f64,
    pub severity: String,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_engine_creation() {
        let engine = GeneticEngine::default();
        assert_eq!(engine.config.population_size, 100);
        assert_eq!(engine.config.generations, 50);
    }

    #[test]
    fn test_engine_with_custom_config() {
        let config = GeneticConfig {
            population_size: 50,
            generations: 25,
            mutation_rate: 0.05,
            crossover_rate: 0.8,
            elitism_count: 2,
            tournament_size: 5,
        };
        let engine = GeneticEngine::new(config.clone());
        assert_eq!(engine.config.population_size, config.population_size);
        assert_eq!(engine.config.generations, config.generations);
        assert_eq!(engine.config.mutation_rate, config.mutation_rate);
        assert_eq!(engine.config.crossover_rate, config.crossover_rate);
        assert_eq!(engine.config.elitism_count, config.elitism_count);
        assert_eq!(engine.config.tournament_size, config.tournament_size);
    }
}