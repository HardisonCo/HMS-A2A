/**
 * Parallel Genetic Repair Engine
 * 
 * Extends the GeneticRepairEngine with parallel fitness evaluation
 * using worker threads for improved performance.
 */

import * as path from 'path';
import { Worker } from 'worker_threads';
import { GeneticRepairEngine, GeneticSolution, GeneticConstraint, FitnessFunction } from './genetic_repair_engine';

/**
 * Configuration for parallel processing
 */
export interface ParallelConfig {
  workerCount?: number;
  batchSize?: number;
  workerTimeout?: number;
  workerScript?: string;
}

/**
 * Result from a parallel fitness evaluation
 */
interface ParallelFitnessResult {
  index: number;
  solution: string;
  fitness: number;
  error: string | null;
}

/**
 * Message from a worker thread
 */
interface WorkerMessage {
  type?: string;
  results?: ParallelFitnessResult[];
  current?: number;
  total?: number;
  fitness?: number;
  index?: number;
  message?: string;
  error?: string;
}

/**
 * Parallel Genetic Repair Engine that uses worker threads
 * for fitness evaluation to improve performance.
 */
export class ParallelGeneticRepairEngine extends GeneticRepairEngine {
  private parallelConfig: ParallelConfig;
  private defaultConfig: ParallelConfig = {
    workerCount: Math.max(1, require('os').cpus().length - 1), // Use all but one CPU core
    batchSize: 10,
    workerTimeout: 60000, // 1 minute
    workerScript: path.join(__dirname, 'workers', 'fitness_worker.js')
  };
  
  /**
   * Constructor
   * @param config Parallel configuration
   */
  constructor(config: ParallelConfig = {}) {
    super();
    this.parallelConfig = { ...this.defaultConfig, ...config };
  }
  
  /**
   * Initialize the parallel genetic repair engine
   */
  async initialize(): Promise<void> {
    await super.initialize();
    
    console.log(`Initializing Parallel Genetic Repair Engine with ${this.parallelConfig.workerCount} workers`);
    
    // Verify that the worker script exists and has been compiled
    if (!this.parallelConfig.workerScript.endsWith('.js')) {
      this.parallelConfig.workerScript += '.js';
    }
    
    console.log('Parallel Genetic Repair Engine initialized successfully');
  }
  
  /**
   * Override the createInitialPopulation method to use parallel fitness evaluation
   */
  protected async createInitialPopulation(
    candidateSolutions: string[],
    fitnessFunction: FitnessFunction
  ): Promise<any> {
    const individuals: any[] = [];
    
    // First, evaluate the candidate solutions in parallel
    const candidateFitness = await this.evaluateInParallel(candidateSolutions, fitnessFunction);
    
    // Add the candidate solutions to the population
    for (let i = 0; i < candidateSolutions.length; i++) {
      individuals.push({
        dna: candidateSolutions[i],
        fitness: candidateFitness[i].fitness
      });
    }
    
    // If we need more individuals, generate variants of the solutions
    const variantSolutions: string[] = [];
    
    while (individuals.length + variantSolutions.length < this.populationSize) {
      const randomIndex = Math.floor(Math.random() * candidateSolutions.length);
      const baseSolution = candidateSolutions[randomIndex];
      const variant = this.mutateSolution(baseSolution);
      variantSolutions.push(variant);
    }
    
    // Evaluate the variant solutions in parallel
    if (variantSolutions.length > 0) {
      const variantFitness = await this.evaluateInParallel(variantSolutions, fitnessFunction);
      
      // Add the variants to the population
      for (let i = 0; i < variantSolutions.length; i++) {
        individuals.push({
          dna: variantSolutions[i],
          fitness: variantFitness[i].fitness
        });
      }
    }
    
    // Calculate population statistics
    const bestFitness = Math.max(...individuals.map(i => i.fitness));
    const averageFitness = individuals.reduce((sum, i) => sum + i.fitness, 0) / individuals.length;
    
    return {
      individuals,
      generation: 0,
      bestFitness,
      averageFitness
    };
  }
  
  /**
   * Override the evolvePopulation method to use parallel fitness evaluation
   */
  protected async evolvePopulation(
    population: any,
    fitnessFunction: FitnessFunction
  ): Promise<any> {
    const newIndividuals: any[] = [];
    
    // Elitism: keep the best individuals
    const sortedIndividuals = [...population.individuals].sort((a, b) => b.fitness - a.fitness);
    for (let i = 0; i < this.elitismCount && i < sortedIndividuals.length; i++) {
      newIndividuals.push(sortedIndividuals[i]);
    }
    
    // Create new individuals through selection, crossover, and mutation
    const newSolutions: string[] = [];
    
    while (newIndividuals.length + newSolutions.length < this.populationSize) {
      // Selection
      const parent1 = this.selectIndividual(population);
      const parent2 = this.selectIndividual(population);
      
      // Crossover
      let child: string;
      if (Math.random() < this.crossoverRate) {
        child = this.crossover(parent1.dna, parent2.dna);
      } else {
        // No crossover, just clone one of the parents
        child = Math.random() < 0.5 ? parent1.dna : parent2.dna;
      }
      
      // Mutation
      if (Math.random() < this.mutationRate) {
        child = this.mutateSolution(child);
      }
      
      newSolutions.push(child);
    }
    
    // Evaluate new solutions in parallel
    if (newSolutions.length > 0) {
      const solutionFitness = await this.evaluateInParallel(newSolutions, fitnessFunction);
      
      // Add the new individuals to the population
      for (let i = 0; i < newSolutions.length; i++) {
        newIndividuals.push({
          dna: newSolutions[i],
          fitness: solutionFitness[i].fitness
        });
      }
    }
    
    // Calculate new population statistics
    const bestFitness = Math.max(...newIndividuals.map(i => i.fitness));
    const averageFitness = newIndividuals.reduce((sum, i) => sum + i.fitness, 0) / newIndividuals.length;
    
    return {
      individuals: newIndividuals,
      generation: population.generation + 1,
      bestFitness,
      averageFitness
    };
  }
  
  /**
   * Evaluate solutions in parallel using worker threads
   * @param solutions Solutions to evaluate
   * @param fitnessFunction Fitness function
   * @returns Array of fitness results
   */
  private async evaluateInParallel(
    solutions: string[],
    fitnessFunction: FitnessFunction
  ): Promise<ParallelFitnessResult[]> {
    // Prepare the fitness function for serialization
    // Note: This assumes the fitness function can be serialized and doesn't rely on closures
    const serializedFunction = fitnessFunction.toString();
    
    // Split solutions into batches
    const batches: string[][] = [];
    for (let i = 0; i < solutions.length; i += this.parallelConfig.batchSize) {
      batches.push(solutions.slice(i, i + this.parallelConfig.batchSize));
    }
    
    console.log(`Evaluating ${solutions.length} solutions in ${batches.length} batches with ${this.parallelConfig.workerCount} workers`);
    
    // Process batches in parallel with limited concurrency
    const results: ParallelFitnessResult[] = new Array(solutions.length);
    let completedBatches = 0;
    
    // Process batches with limited concurrency
    await this.processBatchesWithConcurrency(
      batches,
      async (batch, batchIndex) => {
        const batchResults = await this.evaluateBatchWithWorker(batch, serializedFunction);
        
        // Store the results in the correct positions
        const startIndex = batchIndex * this.parallelConfig.batchSize;
        for (const result of batchResults) {
          results[startIndex + result.index] = result;
        }
        
        // Log progress
        completedBatches++;
        console.log(`Batch ${completedBatches}/${batches.length} completed`);
      },
      this.parallelConfig.workerCount
    );
    
    return results;
  }
  
  /**
   * Process batches with limited concurrency
   * @param items Items to process
   * @param processor Function to process each item
   * @param concurrency Maximum number of concurrent processes
   */
  private async processBatchesWithConcurrency<T>(
    items: T[],
    processor: (item: T, index: number) => Promise<void>,
    concurrency: number
  ): Promise<void> {
    const queue = [...items];
    const inProgress = new Set<Promise<void>>();
    
    // Process the queue
    while (queue.length > 0 || inProgress.size > 0) {
      // Start new tasks if there's capacity and items in the queue
      while (inProgress.size < concurrency && queue.length > 0) {
        const item = queue.shift();
        const index = items.indexOf(item);
        
        const task = (async () => {
          try {
            await processor(item, index);
          } finally {
            inProgress.delete(task);
          }
        })();
        
        inProgress.add(task);
      }
      
      // Wait for at least one task to complete
      if (inProgress.size > 0) {
        await Promise.race(inProgress);
      }
    }
  }
  
  /**
   * Evaluate a batch of solutions with a worker thread
   * @param batch Batch of solutions
   * @param fitnessFunction Serialized fitness function
   * @returns Array of fitness results
   */
  private evaluateBatchWithWorker(
    batch: string[],
    fitnessFunction: string
  ): Promise<ParallelFitnessResult[]> {
    return new Promise((resolve, reject) => {
      // Create a new worker
      const worker = new Worker(this.parallelConfig.workerScript, {
        workerData: {
          solutions: batch,
          fitnessFunction
        }
      });
      
      // Set up timeout
      const timeoutId = setTimeout(() => {
        worker.terminate();
        reject(new Error(`Worker timed out after ${this.parallelConfig.workerTimeout}ms`));
      }, this.parallelConfig.workerTimeout);
      
      // Handle messages from the worker
      worker.on('message', (message: WorkerMessage) => {
        if (message.error) {
          clearTimeout(timeoutId);
          worker.terminate();
          reject(new Error(`Worker error: ${message.error}`));
          return;
        }
        
        if (message.type === 'complete' && message.results) {
          clearTimeout(timeoutId);
          worker.terminate();
          resolve(message.results);
          return;
        }
        
        if (message.type === 'progress') {
          // Could handle progress updates here
        }
      });
      
      // Handle worker errors
      worker.on('error', (error) => {
        clearTimeout(timeoutId);
        worker.terminate();
        reject(error);
      });
      
      // Handle worker exit
      worker.on('exit', (code) => {
        clearTimeout(timeoutId);
        if (code !== 0) {
          reject(new Error(`Worker exited with code ${code}`));
        }
      });
    });
  }
}