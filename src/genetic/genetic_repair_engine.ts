/**
 * Genetic Repair Engine
 * 
 * Implements genetic algorithms for evolving optimal repair solutions
 * to issues detected in the system.
 */

export interface GeneticSolution {
  solution: string;
  fitness: number;
  generation: number;
}

export interface GeneticConstraint {
  type: 'must_contain' | 'must_not_contain' | 'min_length' | 'max_length';
  value: string | number;
}

export type FitnessFunction = (solution: string) => Promise<number>;

interface Individual {
  dna: string;
  fitness: number;
}

interface Population {
  individuals: Individual[];
  generation: number;
  bestFitness: number;
  averageFitness: number;
}

export class GeneticRepairEngine {
  private isInitialized: boolean = false;
  
  // Genetic algorithm parameters
  private populationSize: number = 20;
  private maxGenerations: number = 50;
  private mutationRate: number = 0.1;
  private crossoverRate: number = 0.7;
  private elitismCount: number = 2;
  private selectionMethod: 'tournament' | 'roulette' = 'tournament';
  private tournamentSize: number = 3;
  
  /**
   * Initialize the genetic repair engine
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) return;
    
    console.log('Initializing Genetic Repair Engine');
    this.isInitialized = true;
    console.log('Genetic Repair Engine initialized successfully');
  }
  
  /**
   * Set genetic algorithm parameters
   */
  setParameters(params: {
    populationSize?: number;
    maxGenerations?: number;
    mutationRate?: number;
    crossoverRate?: number;
    elitismCount?: number;
    selectionMethod?: 'tournament' | 'roulette';
    tournamentSize?: number;
  }): void {
    if (params.populationSize) this.populationSize = params.populationSize;
    if (params.maxGenerations) this.maxGenerations = params.maxGenerations;
    if (params.mutationRate) this.mutationRate = params.mutationRate;
    if (params.crossoverRate) this.crossoverRate = params.crossoverRate;
    if (params.elitismCount) this.elitismCount = params.elitismCount;
    if (params.selectionMethod) this.selectionMethod = params.selectionMethod;
    if (params.tournamentSize) this.tournamentSize = params.tournamentSize;
  }
  
  /**
   * Evolve a solution to a problem
   */
  async evolve(
    candidateSolutions: string[],
    constraints: GeneticConstraint[] = [],
    fitnessFunction: FitnessFunction
  ): Promise<GeneticSolution> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    console.log(`Starting evolution with ${candidateSolutions.length} initial candidates`);
    
    // Create initial population
    let population = await this.createInitialPopulation(candidateSolutions, fitnessFunction);
    
    // Evolution loop
    for (let gen = 0; gen < this.maxGenerations; gen++) {
      console.log(`Generation ${gen + 1}/${this.maxGenerations}`);
      
      // Apply constraints to filter invalid solutions
      population = this.applyConstraints(population, constraints);
      
      // Check if we have a solution with high enough fitness
      const bestIndividual = this.getBestIndividual(population);
      if (bestIndividual.fitness >= 0.95) {
        console.log(`Found solution with high fitness (${bestIndividual.fitness.toFixed(2)}) in generation ${gen + 1}`);
        return {
          solution: bestIndividual.dna,
          fitness: bestIndividual.fitness,
          generation: gen + 1
        };
      }
      
      // Create next generation
      population = await this.evolvePopulation(population, fitnessFunction);
      
      console.log(`Generation ${gen + 1} stats: Best fitness = ${population.bestFitness.toFixed(2)}, Avg fitness = ${population.averageFitness.toFixed(2)}`);
    }
    
    // Return the best individual from the final population
    const bestIndividual = this.getBestIndividual(population);
    
    return {
      solution: bestIndividual.dna,
      fitness: bestIndividual.fitness,
      generation: this.maxGenerations
    };
  }
  
  /**
   * Create the initial population from candidate solutions
   */
  private async createInitialPopulation(
    candidateSolutions: string[],
    fitnessFunction: FitnessFunction
  ): Promise<Population> {
    const individuals: Individual[] = [];
    
    // Add the candidate solutions to the population
    for (const solution of candidateSolutions) {
      const fitness = await fitnessFunction(solution);
      individuals.push({ dna: solution, fitness });
    }
    
    // If we need more individuals, generate variants of the solutions
    while (individuals.length < this.populationSize) {
      const randomIndex = Math.floor(Math.random() * candidateSolutions.length);
      const baseSolution = candidateSolutions[randomIndex];
      const variant = this.mutateSolution(baseSolution);
      const fitness = await fitnessFunction(variant);
      individuals.push({ dna: variant, fitness });
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
   * Apply constraints to filter invalid solutions
   */
  private applyConstraints(
    population: Population,
    constraints: GeneticConstraint[]
  ): Population {
    if (constraints.length === 0) {
      return population;
    }
    
    const validIndividuals = population.individuals.filter(individual => {
      return constraints.every(constraint => {
        switch (constraint.type) {
          case 'must_contain':
            return individual.dna.includes(constraint.value as string);
          case 'must_not_contain':
            return !individual.dna.includes(constraint.value as string);
          case 'min_length':
            return individual.dna.length >= (constraint.value as number);
          case 'max_length':
            return individual.dna.length <= (constraint.value as number);
          default:
            return true;
        }
      });
    });
    
    // If no individuals meet the constraints, return the original population
    if (validIndividuals.length === 0) {
      return population;
    }
    
    // Calculate new population statistics
    const bestFitness = Math.max(...validIndividuals.map(i => i.fitness));
    const averageFitness = validIndividuals.reduce((sum, i) => sum + i.fitness, 0) / validIndividuals.length;
    
    return {
      individuals: validIndividuals,
      generation: population.generation,
      bestFitness,
      averageFitness
    };
  }
  
  /**
   * Evolve the population to the next generation
   */
  private async evolvePopulation(
    population: Population,
    fitnessFunction: FitnessFunction
  ): Promise<Population> {
    const newIndividuals: Individual[] = [];
    
    // Elitism: keep the best individuals
    const sortedIndividuals = [...population.individuals].sort((a, b) => b.fitness - a.fitness);
    for (let i = 0; i < this.elitismCount && i < sortedIndividuals.length; i++) {
      newIndividuals.push(sortedIndividuals[i]);
    }
    
    // Create new individuals through selection, crossover, and mutation
    while (newIndividuals.length < this.populationSize) {
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
      
      // Calculate fitness
      const fitness = await fitnessFunction(child);
      newIndividuals.push({ dna: child, fitness });
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
   * Select an individual using the configured selection method
   */
  private selectIndividual(population: Population): Individual {
    if (this.selectionMethod === 'tournament') {
      return this.tournamentSelection(population);
    } else {
      return this.rouletteSelection(population);
    }
  }
  
  /**
   * Tournament selection
   */
  private tournamentSelection(population: Population): Individual {
    const tournament: Individual[] = [];
    
    // Select random individuals for the tournament
    for (let i = 0; i < this.tournamentSize; i++) {
      const randomIndex = Math.floor(Math.random() * population.individuals.length);
      tournament.push(population.individuals[randomIndex]);
    }
    
    // Return the fittest individual from the tournament
    return this.getBestIndividual({ ...population, individuals: tournament });
  }
  
  /**
   * Roulette wheel selection
   */
  private rouletteSelection(population: Population): Individual {
    const totalFitness = population.individuals.reduce((sum, individual) => sum + individual.fitness, 0);
    let randomValue = Math.random() * totalFitness;
    
    for (const individual of population.individuals) {
      randomValue -= individual.fitness;
      if (randomValue <= 0) {
        return individual;
      }
    }
    
    // If we get here, return a random individual
    const randomIndex = Math.floor(Math.random() * population.individuals.length);
    return population.individuals[randomIndex];
  }
  
  /**
   * Perform crossover between two parent solutions
   */
  private crossover(parent1: string, parent2: string): string {
    // Simple single-point crossover
    const crossoverPoint = Math.floor(Math.random() * Math.min(parent1.length, parent2.length));
    return parent1.substring(0, crossoverPoint) + parent2.substring(crossoverPoint);
  }
  
  /**
   * Mutate a solution
   */
  private mutateSolution(solution: string): string {
    // For text-based solutions, we can perform various types of mutations:
    // 1. Replace a random character
    // 2. Insert a random character
    // 3. Delete a random character
    // 4. Swap two characters
    
    if (solution.length === 0) {
      return solution;
    }
    
    const mutationType = Math.floor(Math.random() * 4);
    const chars = solution.split('');
    
    switch (mutationType) {
      case 0: // Replace
        const replaceIndex = Math.floor(Math.random() * chars.length);
        chars[replaceIndex] = this.getRandomChar();
        break;
      
      case 1: // Insert
        const insertIndex = Math.floor(Math.random() * (chars.length + 1));
        chars.splice(insertIndex, 0, this.getRandomChar());
        break;
      
      case 2: // Delete
        if (chars.length > 1) {
          const deleteIndex = Math.floor(Math.random() * chars.length);
          chars.splice(deleteIndex, 1);
        }
        break;
      
      case 3: // Swap
        if (chars.length > 1) {
          const index1 = Math.floor(Math.random() * chars.length);
          let index2 = Math.floor(Math.random() * chars.length);
          
          // Make sure we select a different index
          while (index2 === index1) {
            index2 = Math.floor(Math.random() * chars.length);
          }
          
          // Swap characters
          const temp = chars[index1];
          chars[index1] = chars[index2];
          chars[index2] = temp;
        }
        break;
    }
    
    return chars.join('');
  }
  
  /**
   * Get a random character for mutation
   */
  private getRandomChar(): string {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:_-+=(){}[]<>?!@#$%^&*|\\/"\'';
    return chars.charAt(Math.floor(Math.random() * chars.length));
  }
  
  /**
   * Get the best individual from a population
   */
  private getBestIndividual(population: Population): Individual {
    return population.individuals.reduce(
      (best, current) => current.fitness > best.fitness ? current : best,
      population.individuals[0]
    );
  }
}