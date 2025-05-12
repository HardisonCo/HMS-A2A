/**
 * Hybrid Genetic Repair Engine with Recursive Thinking
 * 
 * Extends the GeneticRepairEngine with recursive thinking capabilities
 * for improved solution refinement.
 */

import { spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { GeneticRepairEngine, GeneticSolution, GeneticConstraint, FitnessFunction } from './genetic_repair_engine';

/**
 * Interface for hybrid solution results
 */
export interface HybridGeneticSolution extends GeneticSolution {
  recursiveImprovements: number;
  thinkingRounds: number;
  thinkingHistory?: any[];
}

/**
 * Configuration for the hybrid engine
 */
export interface HybridEngineConfig {
  pythonPath?: string;
  recursiveScriptPath?: string;
  apiKey?: string;
  recursionRounds?: number;
  verbose?: boolean;
}

/**
 * Hybrid Genetic Repair Engine that combines genetic algorithms
 * with recursive thinking for solution refinement.
 */
export class HybridGeneticRepairEngine extends GeneticRepairEngine {
  private isHybridInitialized: boolean = false;
  private config: HybridEngineConfig = {
    pythonPath: 'python3',
    recursiveScriptPath: path.join(__dirname, '..', 'recursive_thinking', 'cli.py'),
    recursionRounds: 2,
    verbose: true
  };
  
  /**
   * Initialize the hybrid genetic repair engine
   */
  async initialize(config?: HybridEngineConfig): Promise<void> {
    // Initialize the base genetic engine
    await super.initialize();
    
    if (this.isHybridInitialized) return;
    
    console.log('Initializing Hybrid Genetic Repair Engine');
    
    // Update config with any provided values
    if (config) {
      this.config = { ...this.config, ...config };
    }
    
    // Verify Python script exists
    if (!fs.existsSync(this.config.recursiveScriptPath)) {
      throw new Error(`Recursive thinking script not found at ${this.config.recursiveScriptPath}`);
    }
    
    this.isHybridInitialized = true;
    console.log('Hybrid Genetic Repair Engine initialized successfully');
  }
  
  /**
   * Evolve a solution using the hybrid approach
   */
  async hybridEvolve(
    candidateSolutions: string[],
    constraints: GeneticConstraint[] = [],
    fitnessFunction: FitnessFunction
  ): Promise<HybridGeneticSolution> {
    if (!this.isHybridInitialized) {
      await this.initialize();
    }
    
    console.log(`Starting hybrid evolution with ${candidateSolutions.length} initial candidates`);

    // First, run the genetic algorithm to get an initial solution
    const geneticSolution = await super.evolve(candidateSolutions, constraints, fitnessFunction);
    
    console.log(`Initial genetic solution found with fitness ${geneticSolution.fitness}`);
    
    // Then use recursive thinking to refine the solution
    const refinedSolution = await this.refineWithRecursiveThinking(
      geneticSolution.solution,
      constraints,
      fitnessFunction
    );
    
    // Evaluate the refined solution
    const refinedFitness = await fitnessFunction(refinedSolution.solution);
    
    console.log(`Refined solution fitness: ${refinedFitness}`);
    
    // If the refined solution is better, use it; otherwise, keep the genetic solution
    if (refinedFitness > geneticSolution.fitness) {
      console.log('Recursive thinking improved the solution');
      return {
        solution: refinedSolution.solution,
        fitness: refinedFitness,
        generation: geneticSolution.generation,
        recursiveImprovements: 1,
        thinkingRounds: refinedSolution.thinkingRounds,
        thinkingHistory: refinedSolution.thinkingHistory
      };
    } else {
      console.log('Genetic solution retained as it has higher fitness');
      return {
        solution: geneticSolution.solution,
        fitness: geneticSolution.fitness,
        generation: geneticSolution.generation,
        recursiveImprovements: 0,
        thinkingRounds: refinedSolution.thinkingRounds,
        thinkingHistory: refinedSolution.thinkingHistory
      };
    }
  }
  
  /**
   * Refine a solution using recursive thinking
   */
  private async refineWithRecursiveThinking(
    solution: string,
    constraints: GeneticConstraint[],
    fitnessFunction: FitnessFunction
  ): Promise<{ 
    solution: string; 
    thinkingRounds: number; 
    thinkingHistory?: any[];
  }> {
    return new Promise((resolve, reject) => {
      // Create a temporary input file for the Python script
      const tempInputFile = path.join(process.cwd(), 'temp_genetic_input.json');
      const tempOutputFile = path.join(process.cwd(), 'temp_genetic_output.json');
      
      // Prepare input data
      const inputData = {
        candidates: [solution],
        constraints: constraints,
        fitness_function: 'external'  // The Python adapter will use this as a placeholder
      };
      
      // Write input data to file
      fs.writeFileSync(tempInputFile, JSON.stringify(inputData, null, 2));
      
      // Remove any existing output file
      if (fs.existsSync(tempOutputFile)) {
        fs.unlinkSync(tempOutputFile);
      }
      
      // Build command arguments
      const args = [
        this.config.recursiveScriptPath,
        '--input', tempInputFile,
        '--output', tempOutputFile,
        '--rounds', this.config.recursionRounds.toString()
      ];
      
      if (this.config.apiKey) {
        args.push('--api-key', this.config.apiKey);
      }
      
      if (!this.config.verbose) {
        args.push('--quiet');
      }
      
      // Spawn Python process
      const pythonProcess = spawn(this.config.pythonPath, args);
      
      let stdoutData = '';
      let stderrData = '';
      
      pythonProcess.stdout.on('data', (data) => {
        stdoutData += data.toString();
        if (this.config.verbose) {
          console.log(`[Python] ${data.toString().trim()}`);
        }
      });
      
      pythonProcess.stderr.on('data', (data) => {
        stderrData += data.toString();
        console.error(`[Python Error] ${data.toString().trim()}`);
      });
      
      pythonProcess.on('close', (code) => {
        // Clean up input file
        if (fs.existsSync(tempInputFile)) {
          fs.unlinkSync(tempInputFile);
        }
        
        if (code !== 0) {
          reject(new Error(`Python process exited with code ${code}: ${stderrData}`));
          return;
        }
        
        // Check if output file exists
        if (!fs.existsSync(tempOutputFile)) {
          reject(new Error('Python process did not produce output file'));
          return;
        }
        
        try {
          // Read and parse output file
          const outputData = JSON.parse(fs.readFileSync(tempOutputFile, 'utf-8'));
          
          // Clean up output file
          fs.unlinkSync(tempOutputFile);
          
          // Create result object
          const result = {
            solution: outputData.solution,
            thinkingRounds: outputData.rounds,
            thinkingHistory: outputData.history
          };
          
          resolve(result);
        } catch (error) {
          reject(new Error(`Failed to parse Python output: ${error.message}`));
        }
      });
    });
  }
  
  /**
   * Create a fitness function adapter for the Python script
   */
  static createPythonFitnessAdapter(
    fitnessFunction: FitnessFunction
  ): (candidates: string[]) => Promise<number[]> {
    return async (candidates: string[]) => {
      const results: number[] = [];
      
      for (const candidate of candidates) {
        const fitness = await fitnessFunction(candidate);
        results.push(fitness);
      }
      
      return results;
    };
  }
}