//! Genetic Algorithm Engine for Crohn's Disease Treatment Optimization
//! 
//! This module provides a genetic algorithm-based system for optimizing 
//! treatment protocols for Crohn's disease patients, based on individual
//! patient characteristics, biomarkers, and treatment history.

pub mod core;
pub mod representation;
pub mod operations;
pub mod fitness;
pub mod optimization;
pub mod verification;
pub mod ffi;

// Re-export commonly used types
pub use core::{
    GeneticEngine, 
    GeneticConfig, 
    Population, 
    Individual, 
    Evolution,
    GeneticStats
};

pub use representation::{
    TreatmentPlan,
    TreatmentChromosome,
    TreatmentGene,
    PatientContext
};

pub use operations::{
    Crossover,
    Mutation,
    Selection,
    SinglePointCrossover,
    UniformCrossover,
    TreatmentMutation,
    TournamentSelection
};

pub use fitness::{
    FitnessFunction,
    TreatmentEfficacyFitness,
    TreatmentSafetyFitness,
    CombinedFitness
};

/// Initializes the genetic engine with default configuration
pub fn initialize() -> GeneticEngine {
    GeneticEngine::new(GeneticConfig::default())
}

/// Initializes the genetic engine with custom configuration
pub fn initialize_with_config(config: GeneticConfig) -> GeneticEngine {
    GeneticEngine::new(config)
}