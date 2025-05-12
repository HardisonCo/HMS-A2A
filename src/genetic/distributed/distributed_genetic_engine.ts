import { Chromosome } from '../chromosome';
import { FitnessFunction, GeneticAlgorithmOptions, SelectionMethod } from '../types';
import { AdvancedGeneticRepairEngine } from '../advanced/advanced_genetic_repair_engine';
import { DistributedCluster } from './distributed_cluster';
import { logger } from '../../utils/logger';

/**
 * DistributedGeneticEngine - A high-level engine that uses distributed computing
 * for genetic algorithm operations.
 * 
 * Extends the AdvancedGeneticRepairEngine to maintain the same interface
 * but distributes computations across multiple nodes.
 */
export class DistributedGeneticEngine extends AdvancedGeneticRepairEngine {
  private cluster: DistributedCluster;
  private isReady: boolean = false;
  private workerCount: number;

  /**
   * Create a new distributed genetic engine
   * 
   * @param options Genetic algorithm options
   * @param basePort Base port for the coordinator node
   * @param workerCount Number of worker nodes to create
   * @param autoScaling Whether to enable auto-scaling
   */
  constructor(
    options: GeneticAlgorithmOptions = {},
    basePort: number = 9000,
    workerCount: number = 2,
    autoScaling: boolean = true
  ) {
    super(options);
    this.workerCount = workerCount;
    
    // Initialize the distributed cluster
    this.cluster = new DistributedCluster(
      basePort,
      workerCount,
      this, // Pass this engine to workers for local computations
      autoScaling
    );
    
    // Set up cluster event handlers
    this.setupClusterEvents();
    
    logger.info(`Initialized distributed genetic engine with ${workerCount} workers`);
  }

  /**
   * Set up event handlers for the cluster
   */
  private setupClusterEvents(): void {
    this.cluster.on('ready', () => {
      this.isReady = true;
      logger.info('Distributed genetic engine is ready');
    });
    
    this.cluster.on('notReady', () => {
      this.isReady = false;
      logger.warn('Distributed genetic engine is not ready');
    });
    
    this.cluster.on('error', (error) => {
      logger.error(`Distributed genetic engine error: ${error}`);
    });
    
    this.cluster.on('shutdown', () => {
      this.isReady = false;
      logger.info('Distributed genetic engine shut down');
    });
  }

  /**
   * Get the status of the distributed cluster
   */
  public getClusterStatus(): any {
    return this.cluster.getClusterStatus();
  }

  /**
   * Check if the distributed engine is ready
   */
  public isClusterReady(): boolean {
    return this.isReady;
  }

  /**
   * Scale the cluster to a specific number of worker nodes
   */
  public scaleCluster(workerCount: number): void {
    this.workerCount = workerCount;
    this.cluster.scaleToWorkerCount(workerCount);
  }

  /**
   * Add a worker node to the cluster
   */
  public addWorker(): string {
    const workerId = this.cluster.startWorkerNode();
    this.workerCount++;
    return workerId;
  }

  /**
   * Override the evaluatePopulation method to use distributed computing
   */
  public async evaluatePopulation(
    population: Chromosome[],
    fitnessFunction: FitnessFunction
  ): Promise<Chromosome[]> {
    // If cluster is not ready, fall back to local computation
    if (!this.isReady) {
      logger.warn('Cluster not ready, using local population evaluation');
      return super.evaluatePopulation(population, fitnessFunction);
    }
    
    try {
      const result = await this.cluster.evaluatePopulation(population, fitnessFunction);
      return result;
    } catch (error) {
      logger.error(`Error in distributed population evaluation: ${error}`);
      // Fall back to local computation on error
      return super.evaluatePopulation(population, fitnessFunction);
    }
  }

  /**
   * Override the evolveGeneration method to use distributed computing
   */
  public async evolveGeneration(
    population: Chromosome[],
    fitnessFunction: FitnessFunction,
    options?: Partial<GeneticAlgorithmOptions>
  ): Promise<Chromosome[]> {
    // Merge options with defaults
    const mergedOptions = {
      ...this.options,
      ...options
    };
    
    // If cluster is not ready, fall back to local computation
    if (!this.isReady) {
      logger.warn('Cluster not ready, using local evolution');
      return super.evolveGeneration(population, fitnessFunction, mergedOptions);
    }
    
    try {
      const result = await this.cluster.evolveGeneration(population, fitnessFunction, mergedOptions);
      return result;
    } catch (error) {
      logger.error(`Error in distributed evolution: ${error}`);
      // Fall back to local computation on error
      return super.evolveGeneration(population, fitnessFunction, mergedOptions);
    }
  }

  /**
   * Run the genetic algorithm for a specified number of generations
   * or until a target fitness is reached.
   */
  public async run(
    initialPopulation: Chromosome[],
    fitnessFunction: FitnessFunction,
    generations: number = 100,
    targetFitness: number = Infinity,
    options?: Partial<GeneticAlgorithmOptions>
  ): Promise<{
    solution: Chromosome;
    generations: number;
    history: { best: number; average: number; worst: number; diversity: number }[];
  }> {
    // Initialize history
    const history: { best: number; average: number; worst: number; diversity: number }[] = [];
    
    // Use the current population or create a new one
    let population = initialPopulation.length > 0
      ? initialPopulation
      : this.generateInitialPopulation();
    
    // Evaluate initial population
    population = await this.evaluatePopulation(population, fitnessFunction);
    
    // Track the best solution
    let bestSolution = this.findBestChromosome(population);
    let bestFitness = bestSolution ? bestSolution.fitness : -Infinity;
    
    // Add initial state to history
    history.push(this.calculatePopulationStatistics(population));
    
    // Evolve for the specified number of generations
    for (let generation = 0; generation < generations; generation++) {
      // Evolve the next generation
      population = await this.evolveGeneration(population, fitnessFunction, options);
      
      // Find the best chromosome in the current population
      const currentBest = this.findBestChromosome(population);
      const currentBestFitness = currentBest ? currentBest.fitness : -Infinity;
      
      // Update the best solution if we found a better one
      if (currentBestFitness > bestFitness) {
        bestSolution = currentBest;
        bestFitness = currentBestFitness;
      }
      
      // Add this generation's stats to history
      history.push(this.calculatePopulationStatistics(population));
      
      // Check if we've reached the target fitness
      if (bestFitness >= targetFitness) {
        logger.info(`Target fitness ${targetFitness} reached at generation ${generation}`);
        break;
      }
      
      // Log progress every 10 generations
      if (generation % 10 === 0) {
        logger.info(`Generation ${generation}: Best fitness = ${bestFitness}`);
      }
    }
    
    return {
      solution: bestSolution,
      generations: history.length - 1, // Subtract 1 because we include initial state
      history
    };
  }

  /**
   * Calculate population statistics
   */
  private calculatePopulationStatistics(population: Chromosome[]): {
    best: number;
    average: number;
    worst: number;
    diversity: number;
  } {
    if (population.length === 0) {
      return { best: 0, average: 0, worst: 0, diversity: 0 };
    }
    
    // Calculate fitness stats
    const fitnesses = population.map(c => c.fitness);
    const best = Math.max(...fitnesses);
    const worst = Math.min(...fitnesses);
    const average = fitnesses.reduce((sum, fitness) => sum + fitness, 0) / population.length;
    
    // Calculate diversity (using normalized standard deviation)
    const meanFitness = average;
    const squaredDifferences = fitnesses.map(fitness => Math.pow(fitness - meanFitness, 2));
    const variance = squaredDifferences.reduce((sum, diff) => sum + diff, 0) / population.length;
    const stdDev = Math.sqrt(variance);
    
    // Normalize diversity to 0-1 range
    const diversity = meanFitness === 0 ? 0 : stdDev / Math.abs(meanFitness);
    
    return {
      best,
      average,
      worst,
      diversity
    };
  }

  /**
   * Stop the distributed engine and shut down the cluster
   */
  public stop(): void {
    this.cluster.stop();
  }
}