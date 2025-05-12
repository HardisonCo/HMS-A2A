//! Core implementation of the genetic algorithm engine
//! 
//! This module contains the core types and functionality for running
//! genetic algorithm-based optimization of Crohn's disease treatment plans.

use std::time::{Duration, Instant};
use std::sync::{Arc, Mutex};
use std::collections::HashMap;

use crate::representation::{TreatmentChromosome, PatientContext};
use crate::operations::{Crossover, Mutation, Selection};
use crate::fitness::FitnessFunction;

/// Configuration for the genetic algorithm engine
#[derive(Clone, Debug)]
pub struct GeneticConfig {
    /// Size of the population
    pub population_size: usize,
    /// Maximum number of generations to run
    pub max_generations: usize,
    /// Probability of mutation
    pub mutation_rate: f64,
    /// Probability of crossover
    pub crossover_rate: f64,
    /// Fitness threshold for early termination
    pub fitness_threshold: Option<f64>,
    /// Maximum runtime in seconds
    pub max_runtime: Option<u64>,
    /// Enable parallel fitness evaluation
    pub parallel_fitness: bool,
    /// Number of elites to preserve in each generation
    pub elite_count: usize,
    /// Random seed for reproducibility
    pub random_seed: Option<u64>,
}

impl Default for GeneticConfig {
    fn default() -> Self {
        Self {
            population_size: 100,
            max_generations: 50,
            mutation_rate: 0.1,
            crossover_rate: 0.8,
            fitness_threshold: Some(0.95),
            max_runtime: Some(60),
            parallel_fitness: true,
            elite_count: 5,
            random_seed: None,
        }
    }
}

/// Statistics about the genetic algorithm run
#[derive(Clone, Debug)]
pub struct GeneticStats {
    /// Number of generations executed
    pub generations: usize,
    /// Best fitness achieved
    pub best_fitness: f64,
    /// Average fitness in final generation
    pub avg_fitness: f64,
    /// Time taken for the optimization
    pub runtime: Duration,
    /// Reason for termination
    pub termination_reason: TerminationReason,
}

/// Reason for algorithm termination
#[derive(Clone, Debug)]
pub enum TerminationReason {
    /// Reached maximum number of generations
    MaxGenerations,
    /// Reached fitness threshold
    FitnessThreshold,
    /// Reached maximum runtime
    MaxRuntime,
    /// Manually stopped
    ManualStop,
}

/// A single individual in the population
#[derive(Clone, Debug)]
pub struct Individual {
    /// The chromosome representing a treatment plan
    pub chromosome: TreatmentChromosome,
    /// The fitness value (higher is better)
    pub fitness: f64,
}

impl Individual {
    /// Create a new individual with the given chromosome
    pub fn new(chromosome: TreatmentChromosome) -> Self {
        Self {
            chromosome,
            fitness: 0.0,
        }
    }
}

/// A population of individuals
#[derive(Clone, Debug)]
pub struct Population {
    /// The individuals in the population
    pub individuals: Vec<Individual>,
    /// The current generation number
    pub generation: usize,
    /// The best individual found so far
    pub best_individual: Option<Individual>,
}

impl Population {
    /// Create a new population with the given individuals
    pub fn new(individuals: Vec<Individual>) -> Self {
        Self {
            individuals,
            generation: 0,
            best_individual: None,
        }
    }

    /// Get the average fitness of the population
    pub fn average_fitness(&self) -> f64 {
        if self.individuals.is_empty() {
            return 0.0;
        }
        let sum: f64 = self.individuals.iter().map(|i| i.fitness).sum();
        sum / self.individuals.len() as f64
    }

    /// Update the best individual if appropriate
    pub fn update_best(&mut self) {
        let current_best = self.individuals.iter()
            .max_by(|a, b| a.fitness.partial_cmp(&b.fitness).unwrap())
            .map(|i| i.clone());
        
        match (&self.best_individual, &current_best) {
            (None, Some(_)) => self.best_individual = current_best,
            (Some(best), Some(current)) if current.fitness > best.fitness => {
                self.best_individual = current_best
            },
            _ => {}
        }
    }
}

/// Evolution strategy trait
pub trait Evolution {
    /// Evolve the population for one generation
    fn evolve(&self, population: &mut Population, context: &PatientContext);
}

/// The main genetic algorithm engine
pub struct GeneticEngine {
    /// Configuration for the genetic algorithm
    config: GeneticConfig,
    /// The crossover operator
    crossover: Box<dyn Crossover>,
    /// The mutation operator
    mutation: Box<dyn Mutation>,
    /// The selection operator
    selection: Box<dyn Selection>,
    /// The fitness function
    fitness: Box<dyn FitnessFunction>,
    /// The evolution strategy
    evolution: Box<dyn Evolution>,
    /// Flag to stop the algorithm
    stop_flag: Arc<Mutex<bool>>,
}

impl GeneticEngine {
    /// Create a new genetic engine with the given configuration
    pub fn new(config: GeneticConfig) -> Self {
        // Actual implementations will be provided in later phases
        // These are just placeholders
        Self {
            config,
            crossover: Box::new(crate::operations::SinglePointCrossover::new()),
            mutation: Box::new(crate::operations::TreatmentMutation::new(0.1)),
            selection: Box::new(crate::operations::TournamentSelection::new(3)),
            fitness: Box::new(crate::fitness::CombinedFitness::new()),
            evolution: Box::new(StandardEvolution {}),
            stop_flag: Arc::new(Mutex::new(false)),
        }
    }

    /// Set the crossover operator
    pub fn with_crossover(mut self, crossover: Box<dyn Crossover>) -> Self {
        self.crossover = crossover;
        self
    }

    /// Set the mutation operator
    pub fn with_mutation(mut self, mutation: Box<dyn Mutation>) -> Self {
        self.mutation = mutation;
        self
    }

    /// Set the selection operator
    pub fn with_selection(mut self, selection: Box<dyn Selection>) -> Self {
        self.selection = selection;
        self
    }

    /// Set the fitness function
    pub fn with_fitness(mut self, fitness: Box<dyn FitnessFunction>) -> Self {
        self.fitness = fitness;
        self
    }

    /// Set the evolution strategy
    pub fn with_evolution(mut self, evolution: Box<dyn Evolution>) -> Self {
        self.evolution = evolution;
        self
    }

    /// Run the genetic algorithm optimization
    pub fn optimize(&self, initial_population: Population, context: &PatientContext) -> (Population, GeneticStats) {
        let start_time = Instant::now();
        let mut population = initial_population;
        
        // Initialize stop flag
        let mut stop_flag = self.stop_flag.lock().unwrap();
        *stop_flag = false;
        drop(stop_flag);
        
        // Initialize termination reason
        let mut termination_reason = TerminationReason::MaxGenerations;
        
        // Main optimization loop
        while population.generation < self.config.max_generations {
            // Check if we should stop
            let stop_flag = self.stop_flag.lock().unwrap();
            if *stop_flag {
                termination_reason = TerminationReason::ManualStop;
                break;
            }
            drop(stop_flag);
            
            // Check if we've exceeded the maximum runtime
            if let Some(max_runtime) = self.config.max_runtime {
                if start_time.elapsed().as_secs() > max_runtime {
                    termination_reason = TerminationReason::MaxRuntime;
                    break;
                }
            }
            
            // Evolve the population for one generation
            self.evolution.evolve(&mut population, context);
            population.generation += 1;
            
            // Update the best individual
            population.update_best();
            
            // Check if we've reached the fitness threshold
            if let Some(threshold) = self.config.fitness_threshold {
                if let Some(best) = &population.best_individual {
                    if best.fitness >= threshold {
                        termination_reason = TerminationReason::FitnessThreshold;
                        break;
                    }
                }
            }
        }
        
        // Calculate statistics
        let stats = GeneticStats {
            generations: population.generation,
            best_fitness: population.best_individual.as_ref().map_or(0.0, |i| i.fitness),
            avg_fitness: population.average_fitness(),
            runtime: start_time.elapsed(),
            termination_reason,
        };
        
        (population, stats)
    }
    
    /// Stop the optimization
    pub fn stop(&self) {
        let mut stop_flag = self.stop_flag.lock().unwrap();
        *stop_flag = true;
    }
}

/// Standard evolution strategy
struct StandardEvolution {}

impl Evolution for StandardEvolution {
    fn evolve(&self, population: &mut Population, context: &PatientContext) {
        // This is just a placeholder implementation
        // The actual implementation will be provided in later phases
    }
}