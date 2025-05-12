/**
 * Fitness Worker
 * 
 * Worker thread for parallel fitness evaluation in the genetic algorithm.
 */

import { parentPort, workerData } from 'worker_threads';

/**
 * Main worker function that evaluates fitness for a batch of solutions
 */
async function evaluateFitness() {
  // Extract worker data
  const { solutions, fitnessFunction } = workerData;
  
  // Deserialize the fitness function
  let fitnessFn;
  try {
    // Convert the serialized function string back to a function
    // Note: This requires that the function can be safely deserialized
    // and doesn't rely on closures or external context
    fitnessFn = eval(`(${fitnessFunction})`);
  } catch (error) {
    parentPort.postMessage({
      error: `Failed to deserialize fitness function: ${error.message}`
    });
    return;
  }
  
  try {
    // Evaluate each solution in the batch
    const results = [];
    
    for (let i = 0; i < solutions.length; i++) {
      const solution = solutions[i];
      
      try {
        // Apply the fitness function
        const fitness = await fitnessFn(solution);
        
        // Store result
        results.push({
          index: i,
          solution,
          fitness,
          error: null
        });
        
        // Report progress
        if (parentPort) {
          parentPort.postMessage({
            type: 'progress',
            current: i + 1,
            total: solutions.length,
            fitness
          });
        }
      } catch (error) {
        // Handle errors for individual solutions
        results.push({
          index: i,
          solution,
          fitness: 0,
          error: error.message
        });
        
        // Report error
        if (parentPort) {
          parentPort.postMessage({
            type: 'error',
            index: i,
            message: error.message
          });
        }
      }
    }
    
    // Send all results back to the main thread
    if (parentPort) {
      parentPort.postMessage({
        type: 'complete',
        results
      });
    }
  } catch (error) {
    // Handle errors for the entire batch
    if (parentPort) {
      parentPort.postMessage({
        error: error.message
      });
    }
  }
}

// Start the evaluation
evaluateFitness().catch(error => {
  if (parentPort) {
    parentPort.postMessage({
      error: error.message
    });
  }
});