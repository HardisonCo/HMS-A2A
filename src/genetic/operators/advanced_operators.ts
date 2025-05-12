/**
 * Advanced Genetic Operators
 * 
 * This module provides advanced genetic operators for the genetic repair engine,
 * including multi-point crossover, uniform crossover, tournament selection,
 * rank selection, and advanced mutation operators.
 */

/**
 * Available selection methods
 */
export enum SelectionMethod {
  Tournament = 'tournament',
  Roulette = 'roulette',
  Rank = 'rank',
  SteadyState = 'steady_state',
  Elitism = 'elitism'
}

/**
 * Available crossover methods
 */
export enum CrossoverMethod {
  SinglePoint = 'single_point',
  MultiPoint = 'multi_point',
  Uniform = 'uniform',
  ArithmeticText = 'arithmetic_text',
  SemanticAware = 'semantic_aware'
}

/**
 * Available mutation methods
 */
export enum MutationMethod {
  PointMutation = 'point_mutation',
  SwapMutation = 'swap_mutation',
  InsertMutation = 'insert_mutation',
  DeleteMutation = 'delete_mutation',
  ScrambleMutation = 'scramble_mutation',
  PatternBasedMutation = 'pattern_based_mutation'
}

/**
 * Properties for individuals in the population
 */
export interface IndividualProperties {
  dna: string;
  fitness: number;
  fitnessRank?: number;
  age?: number;
}

/**
 * Advanced selection operator configuration
 */
export interface SelectionConfig {
  method: SelectionMethod;
  tournamentSize?: number;
  elitismCount?: number;
  rankSelectionPressure?: number;
  steadyStateReplacement?: number;
}

/**
 * Advanced crossover operator configuration
 */
export interface CrossoverConfig {
  method: CrossoverMethod;
  crossoverRate: number;
  multiPointCount?: number;
  uniformRate?: number;
  semanticGroups?: string[][];
}

/**
 * Advanced mutation operator configuration
 */
export interface MutationConfig {
  method: MutationMethod;
  mutationRate: number;
  scrambleSize?: number;
  patternMap?: Map<string, string>;
}

/**
 * Advanced selection operators
 */
export class AdvancedSelectionOperators {
  /**
   * Select individuals from a population using the specified selection method
   * @param population Array of individuals
   * @param count Number of individuals to select
   * @param config Selection configuration
   * @returns Selected individuals
   */
  static select<T extends IndividualProperties>(
    population: T[],
    count: number,
    config: SelectionConfig
  ): T[] {
    switch (config.method) {
      case SelectionMethod.Tournament:
        return this.tournamentSelection(population, count, config.tournamentSize || 3);
      case SelectionMethod.Roulette:
        return this.rouletteSelection(population, count);
      case SelectionMethod.Rank:
        return this.rankSelection(population, count, config.rankSelectionPressure || 1.5);
      case SelectionMethod.SteadyState:
        return this.steadyStateSelection(population, count, config.steadyStateReplacement || 0.2);
      case SelectionMethod.Elitism:
        return this.elitismSelection(population, count, config.elitismCount || 2);
      default:
        throw new Error(`Unsupported selection method: ${config.method}`);
    }
  }
  
  /**
   * Tournament selection
   * @param population Array of individuals
   * @param count Number of individuals to select
   * @param tournamentSize Size of each tournament
   * @returns Selected individuals
   */
  private static tournamentSelection<T extends IndividualProperties>(
    population: T[],
    count: number,
    tournamentSize: number
  ): T[] {
    const selected: T[] = [];
    
    for (let i = 0; i < count; i++) {
      // Select random individuals for the tournament
      const tournament: T[] = [];
      for (let j = 0; j < tournamentSize; j++) {
        const randomIndex = Math.floor(Math.random() * population.length);
        tournament.push(population[randomIndex]);
      }
      
      // Select the best individual from the tournament
      const winner = tournament.reduce(
        (best, current) => current.fitness > best.fitness ? current : best,
        tournament[0]
      );
      
      selected.push(winner);
    }
    
    return selected;
  }
  
  /**
   * Roulette wheel selection
   * @param population Array of individuals
   * @param count Number of individuals to select
   * @returns Selected individuals
   */
  private static rouletteSelection<T extends IndividualProperties>(
    population: T[],
    count: number
  ): T[] {
    const selected: T[] = [];
    const totalFitness = population.reduce((sum, individual) => sum + individual.fitness, 0);
    
    for (let i = 0; i < count; i++) {
      let randomValue = Math.random() * totalFitness;
      
      for (const individual of population) {
        randomValue -= individual.fitness;
        if (randomValue <= 0) {
          selected.push(individual);
          break;
        }
      }
      
      // Fallback if no individual selected (shouldn't happen but just in case)
      if (selected.length <= i) {
        const randomIndex = Math.floor(Math.random() * population.length);
        selected.push(population[randomIndex]);
      }
    }
    
    return selected;
  }
  
  /**
   * Rank selection
   * @param population Array of individuals
   * @param count Number of individuals to select
   * @param selectionPressure Selection pressure parameter (1.0-2.0)
   * @returns Selected individuals
   */
  private static rankSelection<T extends IndividualProperties>(
    population: T[],
    count: number,
    selectionPressure: number
  ): T[] {
    const selected: T[] = [];
    
    // Sort population by fitness and assign ranks
    const sortedPopulation = [...population].sort((a, b) => b.fitness - a.fitness);
    sortedPopulation.forEach((individual, index) => {
      individual.fitnessRank = index;
    });
    
    // Calculate rank probabilities
    const n = sortedPopulation.length;
    let totalRankProbability = 0;
    const rankProbabilities: number[] = [];
    
    for (let i = 0; i < n; i++) {
      // Linear ranking formula with selection pressure
      const rankProbability = 2 - selectionPressure + (2 * (selectionPressure - 1) * (n - 1 - i)) / (n - 1);
      rankProbabilities.push(rankProbability);
      totalRankProbability += rankProbability;
    }
    
    // Select individuals based on rank probabilities
    for (let i = 0; i < count; i++) {
      let randomValue = Math.random() * totalRankProbability;
      let sum = 0;
      
      for (let j = 0; j < n; j++) {
        sum += rankProbabilities[j];
        if (randomValue <= sum) {
          selected.push(sortedPopulation[j]);
          break;
        }
      }
      
      // Fallback if no individual selected
      if (selected.length <= i) {
        const randomIndex = Math.floor(Math.random() * sortedPopulation.length);
        selected.push(sortedPopulation[randomIndex]);
      }
    }
    
    return selected;
  }
  
  /**
   * Steady-state selection
   * @param population Array of individuals
   * @param count Number of individuals to select
   * @param replacement Replacement rate (0.0-1.0)
   * @returns Selected individuals
   */
  private static steadyStateSelection<T extends IndividualProperties>(
    population: T[],
    count: number,
    replacement: number
  ): T[] {
    // Sort population by fitness
    const sortedPopulation = [...population].sort((a, b) => b.fitness - a.fitness);
    
    // Number of individuals to replace
    const replaceCount = Math.floor(count * replacement);
    
    // Select the best individuals to keep
    const selected = sortedPopulation.slice(0, count - replaceCount);
    
    // Fill the rest with tournament selection from the remaining population
    const remaining = sortedPopulation.slice(count - replaceCount);
    if (remaining.length > 0) {
      const tournamentSelected = this.tournamentSelection(
        remaining,
        replaceCount,
        Math.min(3, remaining.length)
      );
      selected.push(...tournamentSelected);
    }
    
    return selected;
  }
  
  /**
   * Elitism selection
   * @param population Array of individuals
   * @param count Number of individuals to select
   * @param elitismCount Number of best individuals to select
   * @returns Selected individuals
   */
  private static elitismSelection<T extends IndividualProperties>(
    population: T[],
    count: number,
    elitismCount: number
  ): T[] {
    // Sort population by fitness
    const sortedPopulation = [...population].sort((a, b) => b.fitness - a.fitness);
    
    // Select the best individuals
    const elites = sortedPopulation.slice(0, Math.min(elitismCount, count));
    
    // Fill the rest with tournament selection
    if (elites.length < count) {
      const remaining = count - elites.length;
      const tournamentSelected = this.tournamentSelection(
        population,
        remaining,
        3
      );
      elites.push(...tournamentSelected);
    }
    
    return elites;
  }
}

/**
 * Advanced crossover operators
 */
export class AdvancedCrossoverOperators {
  /**
   * Perform crossover between two parents using the specified method
   * @param parent1 First parent
   * @param parent2 Second parent
   * @param config Crossover configuration
   * @returns Child solution
   */
  static crossover(
    parent1: string,
    parent2: string,
    config: CrossoverConfig
  ): string {
    // Only perform crossover based on the crossover rate
    if (Math.random() >= config.crossoverRate) {
      // No crossover, return one of the parents
      return Math.random() < 0.5 ? parent1 : parent2;
    }
    
    switch (config.method) {
      case CrossoverMethod.SinglePoint:
        return this.singlePointCrossover(parent1, parent2);
      case CrossoverMethod.MultiPoint:
        return this.multiPointCrossover(
          parent1,
          parent2,
          config.multiPointCount || 2
        );
      case CrossoverMethod.Uniform:
        return this.uniformCrossover(
          parent1,
          parent2,
          config.uniformRate || 0.5
        );
      case CrossoverMethod.ArithmeticText:
        return this.arithmeticTextCrossover(parent1, parent2);
      case CrossoverMethod.SemanticAware:
        return this.semanticAwareCrossover(
          parent1,
          parent2,
          config.semanticGroups || []
        );
      default:
        throw new Error(`Unsupported crossover method: ${config.method}`);
    }
  }
  
  /**
   * Single-point crossover
   * @param parent1 First parent
   * @param parent2 Second parent
   * @returns Child solution
   */
  private static singlePointCrossover(parent1: string, parent2: string): string {
    const crossoverPoint = Math.floor(Math.random() * Math.min(parent1.length, parent2.length));
    return parent1.substring(0, crossoverPoint) + parent2.substring(crossoverPoint);
  }
  
  /**
   * Multi-point crossover
   * @param parent1 First parent
   * @param parent2 Second parent
   * @param pointCount Number of crossover points
   * @returns Child solution
   */
  private static multiPointCrossover(
    parent1: string,
    parent2: string,
    pointCount: number
  ): string {
    const minLength = Math.min(parent1.length, parent2.length);
    
    // Generate crossover points
    const points: number[] = [];
    for (let i = 0; i < pointCount; i++) {
      points.push(Math.floor(Math.random() * minLength));
    }
    
    // Sort points
    points.sort((a, b) => a - b);
    
    // Perform crossover
    let result = '';
    let startIndex = 0;
    let useParent1 = true;
    
    for (const point of points) {
      const parent = useParent1 ? parent1 : parent2;
      result += parent.substring(startIndex, point);
      startIndex = point;
      useParent1 = !useParent1;
    }
    
    // Add the last segment
    const parent = useParent1 ? parent1 : parent2;
    result += parent.substring(startIndex);
    
    return result;
  }
  
  /**
   * Uniform crossover
   * @param parent1 First parent
   * @param parent2 Second parent
   * @param uniformRate Probability of selecting from parent1
   * @returns Child solution
   */
  private static uniformCrossover(
    parent1: string,
    parent2: string,
    uniformRate: number
  ): string {
    const parent1Chars = parent1.split('');
    const parent2Chars = parent2.split('');
    const resultChars: string[] = [];
    
    const maxLength = Math.max(parent1Chars.length, parent2Chars.length);
    
    for (let i = 0; i < maxLength; i++) {
      if (i >= parent1Chars.length) {
        resultChars.push(parent2Chars[i]);
      } else if (i >= parent2Chars.length) {
        resultChars.push(parent1Chars[i]);
      } else {
        resultChars.push(Math.random() < uniformRate ? parent1Chars[i] : parent2Chars[i]);
      }
    }
    
    return resultChars.join('');
  }
  
  /**
   * Arithmetic text crossover (for text-based solutions)
   * @param parent1 First parent
   * @param parent2 Second parent
   * @returns Child solution
   */
  private static arithmeticTextCrossover(parent1: string, parent2: string): string {
    // Split into lines
    const parent1Lines = parent1.split('\n');
    const parent2Lines = parent2.split('\n');
    
    const resultLines: string[] = [];
    const maxLines = Math.max(parent1Lines.length, parent2Lines.length);
    
    for (let i = 0; i < maxLines; i++) {
      if (i >= parent1Lines.length) {
        resultLines.push(parent2Lines[i]);
      } else if (i >= parent2Lines.length) {
        resultLines.push(parent1Lines[i]);
      } else {
        // For each line, choose the parent with higher "quality"
        const line1 = parent1Lines[i];
        const line2 = parent2Lines[i];
        
        // Simple heuristic: prefer the longer line, or choose randomly if equal
        if (line1.length > line2.length) {
          resultLines.push(line1);
        } else if (line2.length > line1.length) {
          resultLines.push(line2);
        } else {
          resultLines.push(Math.random() < 0.5 ? line1 : line2);
        }
      }
    }
    
    return resultLines.join('\n');
  }
  
  /**
   * Semantic-aware crossover (preserves semantic blocks)
   * @param parent1 First parent
   * @param parent2 Second parent
   * @param semanticGroups Array of semantic group patterns
   * @returns Child solution
   */
  private static semanticAwareCrossover(
    parent1: string,
    parent2: string,
    semanticGroups: string[][]
  ): string {
    if (semanticGroups.length === 0) {
      // Fallback to multi-point crossover if no semantic groups provided
      return this.multiPointCrossover(parent1, parent2, 2);
    }
    
    // Find semantic blocks in both parents
    const parent1Blocks = this.findSemanticBlocks(parent1, semanticGroups);
    const parent2Blocks = this.findSemanticBlocks(parent2, semanticGroups);
    
    // Combine blocks
    let result = parent1;
    
    for (const [blockType, blocks] of Object.entries(parent2Blocks)) {
      if (Math.random() < 0.5) {
        for (const block of blocks) {
          if (Math.random() < 0.3) {
            // Replace a matching block in parent1 with this block from parent2
            const blockRegex = new RegExp(this.escapeRegExp(block), 'g');
            if (result.match(blockRegex)) {
              result = result.replace(blockRegex, block);
            } else {
              // If no match, try to append to the end
              result += '\n' + block;
            }
          }
        }
      }
    }
    
    return result;
  }
  
  /**
   * Find semantic blocks in a solution
   * @param solution Solution to analyze
   * @param semanticGroups Array of semantic group patterns
   * @returns Object mapping block types to arrays of blocks
   */
  private static findSemanticBlocks(
    solution: string,
    semanticGroups: string[][]
  ): Record<string, string[]> {
    const blocks: Record<string, string[]> = {};
    
    for (const group of semanticGroups) {
      const blockType = group[0];
      blocks[blockType] = [];
      
      for (let i = 1; i < group.length; i++) {
        const pattern = group[i];
        
        try {
          const regex = new RegExp(pattern, 'g');
          const matches = solution.match(regex);
          
          if (matches) {
            blocks[blockType].push(...matches);
          }
        } catch (error) {
          console.error(`Invalid regex pattern: ${pattern}`, error);
        }
      }
    }
    
    return blocks;
  }
  
  /**
   * Escape special characters in a string for use in a regular expression
   * @param string String to escape
   * @returns Escaped string
   */
  private static escapeRegExp(string: string): string {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
}

/**
 * Advanced mutation operators
 */
export class AdvancedMutationOperators {
  /**
   * Mutate a solution using the specified method
   * @param solution Solution to mutate
   * @param config Mutation configuration
   * @returns Mutated solution
   */
  static mutate(
    solution: string,
    config: MutationConfig
  ): string {
    // Only perform mutation based on the mutation rate
    if (Math.random() >= config.mutationRate) {
      return solution;
    }
    
    switch (config.method) {
      case MutationMethod.PointMutation:
        return this.pointMutation(solution);
      case MutationMethod.SwapMutation:
        return this.swapMutation(solution);
      case MutationMethod.InsertMutation:
        return this.insertMutation(solution);
      case MutationMethod.DeleteMutation:
        return this.deleteMutation(solution);
      case MutationMethod.ScrambleMutation:
        return this.scrambleMutation(solution, config.scrambleSize || 5);
      case MutationMethod.PatternBasedMutation:
        return this.patternBasedMutation(solution, config.patternMap || new Map());
      default:
        throw new Error(`Unsupported mutation method: ${config.method}`);
    }
  }
  
  /**
   * Point mutation (replace a random character)
   * @param solution Solution to mutate
   * @returns Mutated solution
   */
  private static pointMutation(solution: string): string {
    if (solution.length === 0) {
      return solution;
    }
    
    const chars = solution.split('');
    const randomIndex = Math.floor(Math.random() * chars.length);
    chars[randomIndex] = this.getRandomChar();
    
    return chars.join('');
  }
  
  /**
   * Swap mutation (swap two random characters)
   * @param solution Solution to mutate
   * @returns Mutated solution
   */
  private static swapMutation(solution: string): string {
    if (solution.length <= 1) {
      return solution;
    }
    
    const chars = solution.split('');
    const index1 = Math.floor(Math.random() * chars.length);
    let index2 = Math.floor(Math.random() * chars.length);
    
    // Ensure different indices
    while (index2 === index1) {
      index2 = Math.floor(Math.random() * chars.length);
    }
    
    // Swap characters
    const temp = chars[index1];
    chars[index1] = chars[index2];
    chars[index2] = temp;
    
    return chars.join('');
  }
  
  /**
   * Insert mutation (insert a random character)
   * @param solution Solution to mutate
   * @returns Mutated solution
   */
  private static insertMutation(solution: string): string {
    const chars = solution.split('');
    const randomIndex = Math.floor(Math.random() * (chars.length + 1));
    chars.splice(randomIndex, 0, this.getRandomChar());
    
    return chars.join('');
  }
  
  /**
   * Delete mutation (delete a random character)
   * @param solution Solution to mutate
   * @returns Mutated solution
   */
  private static deleteMutation(solution: string): string {
    if (solution.length <= 1) {
      return solution;
    }
    
    const chars = solution.split('');
    const randomIndex = Math.floor(Math.random() * chars.length);
    chars.splice(randomIndex, 1);
    
    return chars.join('');
  }
  
  /**
   * Scramble mutation (randomly reorder a subset of characters)
   * @param solution Solution to mutate
   * @param scrambleSize Size of the segment to scramble
   * @returns Mutated solution
   */
  private static scrambleMutation(solution: string, scrambleSize: number): string {
    if (solution.length <= 1) {
      return solution;
    }
    
    const chars = solution.split('');
    const maxStart = Math.max(0, chars.length - scrambleSize);
    const startIndex = Math.floor(Math.random() * maxStart);
    const endIndex = Math.min(startIndex + scrambleSize, chars.length);
    
    // Extract segment to scramble
    const segment = chars.slice(startIndex, endIndex);
    
    // Scramble the segment
    for (let i = segment.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const temp = segment[i];
      segment[i] = segment[j];
      segment[j] = temp;
    }
    
    // Replace segment in solution
    chars.splice(startIndex, endIndex - startIndex, ...segment);
    
    return chars.join('');
  }
  
  /**
   * Pattern-based mutation (replace patterns according to a map)
   * @param solution Solution to mutate
   * @param patternMap Map of patterns to replacements
   * @returns Mutated solution
   */
  private static patternBasedMutation(solution: string, patternMap: Map<string, string>): string {
    if (patternMap.size === 0) {
      return solution;
    }
    
    let result = solution;
    const patterns = Array.from(patternMap.keys());
    
    // Randomly select a pattern to apply
    const randomIndex = Math.floor(Math.random() * patterns.length);
    const pattern = patterns[randomIndex];
    const replacement = patternMap.get(pattern) || '';
    
    try {
      // Check if the pattern is a regular expression
      if (pattern.startsWith('/') && pattern.includes('/', 1)) {
        const lastSlashIndex = pattern.lastIndexOf('/');
        const flags = pattern.substring(lastSlashIndex + 1);
        const regexPattern = pattern.substring(1, lastSlashIndex);
        const regex = new RegExp(regexPattern, flags);
        
        result = result.replace(regex, replacement);
      } else {
        // Simple string replacement
        result = result.replace(pattern, replacement);
      }
    } catch (error) {
      console.error(`Error applying pattern mutation: ${error}`);
    }
    
    return result;
  }
  
  /**
   * Get a random character for mutation
   */
  private static getRandomChar(): string {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:_-+=(){}[]<>?!@#$%^&*|\\/"\'';
    return chars.charAt(Math.floor(Math.random() * chars.length));
  }
}