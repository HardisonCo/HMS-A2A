/**
 * Advanced Genetic Repair Engine
 * 
 * Extends the genetic repair engine with advanced genetic operators
 * for more sophisticated evolution.
 */

import { GeneticRepairEngine, GeneticSolution, GeneticConstraint, FitnessFunction } from '../genetic_repair_engine';
import { 
  AdvancedSelectionOperators, 
  AdvancedCrossoverOperators, 
  AdvancedMutationOperators,
  SelectionMethod,
  CrossoverMethod,
  MutationMethod,
  SelectionConfig,
  CrossoverConfig,
  MutationConfig
} from './advanced_operators';

/**
 * Configuration for the advanced genetic repair engine
 */
export interface AdvancedGeneticConfig {
  populationSize?: number;
  maxGenerations?: number;
  selection?: SelectionConfig;
  crossover?: CrossoverConfig;
  mutation?: MutationConfig;
  elitismCount?: number;
}

/**
 * Extended solution with additional metadata
 */
export interface AdvancedGeneticSolution extends GeneticSolution {
  convergenceRate: number;
  diversity: number;
  operatorsUsed: {
    selection: SelectionMethod;
    crossover: CrossoverMethod;
    mutation: MutationMethod;
  };
}

/**
 * Individual in the population
 */
interface Individual {
  dna: string;
  fitness: number;
  age?: number;
  diversity?: number;
}

/**
 * Population statistics
 */
interface PopulationStats {
  individuals: Individual[];
  generation: number;
  bestFitness: number;
  averageFitness: number;
  diversity: number;
  convergenceRate: number;
}

/**
 * Advanced genetic repair engine with enhanced genetic operators
 */
export class AdvancedGeneticRepairEngine extends GeneticRepairEngine {
  private config: AdvancedGeneticConfig;
  private defaultConfig: AdvancedGeneticConfig = {
    populationSize: 20,
    maxGenerations: 50,
    selection: {
      method: SelectionMethod.Tournament,
      tournamentSize: 3
    },
    crossover: {
      method: CrossoverMethod.MultiPoint,
      crossoverRate: 0.7,
      multiPointCount: 2
    },
    mutation: {
      method: MutationMethod.PointMutation,
      mutationRate: 0.1
    },
    elitismCount: 2
  };
  private generations: PopulationStats[] = [];
  
  /**
   * Constructor
   * @param config Advanced genetic configuration
   */
  constructor(config: AdvancedGeneticConfig = {}) {
    super();
    this.config = { ...this.defaultConfig, ...config };
    
    // Call setParameters to ensure base class parameters are set
    this.setParameters({
      populationSize: this.config.populationSize,
      maxGenerations: this.config.maxGenerations,
      elitismCount: this.config.elitismCount
    });
  }
  
  /**
   * Initialize the advanced genetic repair engine
   */
  async initialize(): Promise<void> {
    await super.initialize();
    
    console.log('Initializing Advanced Genetic Repair Engine');
    console.log(`Selection method: ${this.config.selection?.method}`);
    console.log(`Crossover method: ${this.config.crossover?.method}`);
    console.log(`Mutation method: ${this.config.mutation?.method}`);
    
    console.log('Advanced Genetic Repair Engine initialized successfully');
  }
  
  /**
   * Set advanced genetic parameters
   */
  setAdvancedParameters(config: AdvancedGeneticConfig): void {
    this.config = { ...this.config, ...config };
    
    // Update base class parameters too
    this.setParameters({
      populationSize: this.config.populationSize,
      maxGenerations: this.config.maxGenerations,
      elitismCount: this.config.elitismCount
    });
  }
  
  /**
   * Evolve a solution to a problem using advanced genetic operators
   */
  async advancedEvolve(
    candidateSolutions: string[],
    constraints: GeneticConstraint[] = [],
    fitnessFunction: FitnessFunction
  ): Promise<AdvancedGeneticSolution> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    console.log(`Starting advanced evolution with ${candidateSolutions.length} initial candidates`);
    
    // Reset generations
    this.generations = [];
    
    // Create initial population
    let population = await this.createInitialPopulation(candidateSolutions, fitnessFunction);
    
    // Evolution loop
    for (let gen = 0; gen < this.maxGenerations; gen++) {
      console.log(`Generation ${gen + 1}/${this.maxGenerations}`);
      
      // Apply constraints to filter invalid solutions
      population = this.applyConstraints(population, constraints);
      
      // Calculate population statistics
      const stats = this.calculatePopulationStats(population);
      this.generations.push(stats);
      
      // Check if we have a solution with high enough fitness
      const bestIndividual = this.getBestIndividual(population);
      if (bestIndividual.fitness >= 0.95) {
        console.log(`Found solution with high fitness (${bestIndividual.fitness.toFixed(2)}) in generation ${gen + 1}`);
        
        return this.createAdvancedSolution(
          bestIndividual.dna,
          bestIndividual.fitness,
          gen + 1
        );
      }
      
      // Adapt operators based on population statistics (optional)
      if (gen > 0 && gen % 5 === 0) {
        this.adaptOperators(stats);
      }
      
      // Create next generation
      population = await this.advancedEvolvePopulation(population, fitnessFunction);
      
      console.log(`Generation ${gen + 1} stats: Best fitness = ${population.bestFitness.toFixed(2)}, Avg fitness = ${population.averageFitness.toFixed(2)}, Diversity = ${population.diversity.toFixed(2)}`);
    }
    
    // Return the best individual from the final population
    const bestIndividual = this.getBestIndividual(population);
    
    return this.createAdvancedSolution(
      bestIndividual.dna,
      bestIndividual.fitness,
      this.maxGenerations
    );
  }
  
  /**
   * Create initial population from candidate solutions
   */
  protected async createInitialPopulation(
    candidateSolutions: string[],
    fitnessFunction: FitnessFunction
  ): Promise<PopulationStats> {
    const individuals: Individual[] = [];
    
    // Add the candidate solutions to the population
    for (const solution of candidateSolutions) {
      const fitness = await fitnessFunction(solution);
      individuals.push({ dna: solution, fitness, age: 0 });
    }
    
    // If we need more individuals, generate variants of the solutions
    while (individuals.length < this.populationSize) {
      const randomIndex = Math.floor(Math.random() * candidateSolutions.length);
      const baseSolution = candidateSolutions[randomIndex];
      
      // Use advanced mutation for more variety
      const variant = AdvancedMutationOperators.mutate(
        baseSolution,
        {
          method: this.config.mutation?.method || MutationMethod.PointMutation,
          mutationRate: 1.0 // Always mutate for diversity
        }
      );
      
      const fitness = await fitnessFunction(variant);
      individuals.push({ dna: variant, fitness, age: 0 });
    }
    
    // Calculate population statistics
    return this.calculatePopulationStats({ individuals, generation: 0 } as PopulationStats);
  }
  
  /**
   * Evolve population to next generation using advanced operators
   */
  protected async advancedEvolvePopulation(
    population: PopulationStats,
    fitnessFunction: FitnessFunction
  ): Promise<PopulationStats> {
    const newIndividuals: Individual[] = [];
    
    // Elitism: keep the best individuals
    const sortedIndividuals = [...population.individuals].sort((a, b) => b.fitness - a.fitness);
    const elitismCount = this.config.elitismCount || 2;
    
    for (let i = 0; i < elitismCount && i < sortedIndividuals.length; i++) {
      // Increment age for elite individuals
      newIndividuals.push({
        ...sortedIndividuals[i],
        age: (sortedIndividuals[i].age || 0) + 1
      });
    }
    
    // Create new individuals through selection, crossover, and mutation
    while (newIndividuals.length < this.populationSize) {
      // Selection
      const parents = AdvancedSelectionOperators.select(
        population.individuals,
        2,
        this.config.selection || { method: SelectionMethod.Tournament, tournamentSize: 3 }
      );
      
      if (parents.length < 2) {
        // Fallback if selection fails
        continue;
      }
      
      // Crossover
      const child = AdvancedCrossoverOperators.crossover(
        parents[0].dna,
        parents[1].dna,
        this.config.crossover || { method: CrossoverMethod.MultiPoint, crossoverRate: 0.7, multiPointCount: 2 }
      );
      
      // Mutation
      const mutated = AdvancedMutationOperators.mutate(
        child,
        this.config.mutation || { method: MutationMethod.PointMutation, mutationRate: 0.1 }
      );
      
      // Calculate fitness
      const fitness = await fitnessFunction(mutated);
      newIndividuals.push({ dna: mutated, fitness, age: 0 });
    }
    
    // Calculate new population statistics
    return this.calculatePopulationStats({
      individuals: newIndividuals,
      generation: population.generation + 1
    } as PopulationStats);
  }
  
  /**
   * Calculate population statistics
   */
  protected calculatePopulationStats(population: PopulationStats): PopulationStats {
    const individuals = population.individuals;
    
    // Calculate fitness statistics
    const bestFitness = Math.max(...individuals.map(i => i.fitness));
    const averageFitness = individuals.reduce((sum, i) => sum + i.fitness, 0) / individuals.length;
    
    // Calculate diversity
    const uniqueDna = new Set(individuals.map(i => i.dna));
    const diversity = uniqueDna.size / individuals.length;
    
    // Calculate convergence rate (if more than one generation)
    let convergenceRate = 0;
    
    if (this.generations.length > 0) {
      const prevGeneration = this.generations[this.generations.length - 1];
      convergenceRate = (bestFitness - prevGeneration.bestFitness) / prevGeneration.bestFitness;
    }
    
    return {
      individuals,
      generation: population.generation,
      bestFitness,
      averageFitness,
      diversity,
      convergenceRate
    };
  }
  
  /**
   * Adapt operators based on population statistics
   */
  protected adaptOperators(stats: PopulationStats): void {
    // If diversity is low, increase mutation rate
    if (stats.diversity < 0.3) {
      const currentRate = this.config.mutation?.mutationRate || 0.1;
      const newRate = Math.min(0.5, currentRate * 1.5);
      
      if (this.config.mutation) {
        this.config.mutation.mutationRate = newRate;
      }
      
      console.log(`Adapting mutation rate to ${newRate.toFixed(2)} due to low diversity`);
    }
    
    // If convergence rate is very low, change crossover method
    if (Math.abs(stats.convergenceRate) < 0.01 && stats.generation > 10) {
      // Try different crossover method
      if (this.config.crossover) {
        if (this.config.crossover.method === CrossoverMethod.SinglePoint) {
          this.config.crossover.method = CrossoverMethod.MultiPoint;
        } else if (this.config.crossover.method === CrossoverMethod.MultiPoint) {
          this.config.crossover.method = CrossoverMethod.Uniform;
        } else {
          this.config.crossover.method = CrossoverMethod.SinglePoint;
        }
        
        console.log(`Adapting crossover method to ${this.config.crossover.method} due to low convergence`);
      }
    }
  }
  
  /**
   * Create advanced solution object
   */
  protected createAdvancedSolution(
    solution: string,
    fitness: number,
    generation: number
  ): AdvancedGeneticSolution {
    // Calculate average diversity and convergence rate
    let totalDiversity = 0;
    let totalConvergenceRate = 0;
    
    for (const gen of this.generations) {
      totalDiversity += gen.diversity;
      totalConvergenceRate += gen.convergenceRate;
    }
    
    const avgDiversity = totalDiversity / this.generations.length;
    const avgConvergenceRate = totalConvergenceRate / Math.max(1, this.generations.length - 1);
    
    return {
      solution,
      fitness,
      generation,
      convergenceRate: avgConvergenceRate,
      diversity: avgDiversity,
      operatorsUsed: {
        selection: this.config.selection?.method || SelectionMethod.Tournament,
        crossover: this.config.crossover?.method || CrossoverMethod.MultiPoint,
        mutation: this.config.mutation?.method || MutationMethod.PointMutation
      }
    };
  }
}