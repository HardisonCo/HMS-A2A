# Genetic Repair Engine

This module implements a genetic algorithm-based engine for evolving solutions to problems, with an extended hybrid version that incorporates recursive thinking for solution refinement.

## Overview

The Genetic Repair Engine offers the following key features:

- **Genetic Algorithm Foundation**: Uses selection, crossover, and mutation to evolve solutions
- **Recursive Thinking Enhancement**: Refines solutions through multi-step thinking (in hybrid version)
- **Constraint Handling**: Supports various constraint types
- **Customizable Fitness Functions**: Define domain-specific evaluation criteria
- **Cross-Language Integration**: TypeScript/JavaScript engine with Python recursive thinking

## Components

- **GeneticRepairEngine**: Core genetic algorithm implementation in TypeScript
- **HybridGeneticRepairEngine**: Extended engine with recursive thinking capabilities
- **EnhancedRecursiveThinkingChat**: Python implementation of recursive thinking
- **GeneticRecursiveAdapter**: Python adapter for integration with genetic engine

## Installation

1. Run the setup script:
   ```bash
   ./scripts/setup_hybrid_genetic_system.sh
   ```

2. Add your OpenRouter API key to the `.env` file:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Usage

### Using the Basic Genetic Engine

```typescript
import { GeneticRepairEngine, GeneticConstraint } from './src/genetic/genetic_repair_engine';

async function main() {
  // Initialize the genetic engine
  const geneticEngine = new GeneticRepairEngine();
  await geneticEngine.initialize();
  
  // Configure genetic parameters
  geneticEngine.setParameters({
    populationSize: 20,
    maxGenerations: 50,
    mutationRate: 0.1,
    crossoverRate: 0.7,
    elitismCount: 2
  });
  
  // Define candidate solutions
  const candidates = [
    `function detectIssue(system) { return system.status === 'error'; }`,
    `function detectIssue(system) { return system.errorCount > 0; }`
  ];
  
  // Define constraints
  const constraints: GeneticConstraint[] = [
    { type: 'must_contain', value: 'function detectIssue' },
    { type: 'must_contain', value: 'return' }
  ];
  
  // Define fitness function
  const fitnessFunction = async (solution: string): Promise<number> => {
    // Evaluate solution and return fitness score between 0 and 1
    // Higher is better
    return 0.5; // Example
  };
  
  // Evolve solution
  const result = await geneticEngine.evolve(
    candidates,
    constraints,
    fitnessFunction
  );
  
  console.log(`Solution: ${result.solution}`);
  console.log(`Fitness: ${result.fitness}`);
  console.log(`Generation: ${result.generation}`);
}

main().catch(console.error);
```

### Using the Hybrid Genetic-Recursive Engine

```typescript
import { HybridGeneticRepairEngine, HybridEngineConfig } from './src/genetic/hybrid_genetic_repair_engine';
import { GeneticConstraint } from './src/genetic/genetic_repair_engine';

async function main() {
  // Initialize the hybrid engine
  const hybridEngine = new HybridGeneticRepairEngine();
  await hybridEngine.initialize({
    apiKey: process.env.OPENROUTER_API_KEY,
    recursionRounds: 2
  });
  
  // Configure genetic parameters
  hybridEngine.setParameters({
    populationSize: 20,
    maxGenerations: 30,
    mutationRate: 0.1
  });
  
  // Define candidate solutions
  const candidates = [
    `function detectIssue(system) { return system.status === 'error'; }`,
    `function detectIssue(system) { return system.errorCount > 0; }`
  ];
  
  // Define constraints
  const constraints: GeneticConstraint[] = [
    { type: 'must_contain', value: 'function detectIssue' },
    { type: 'must_contain', value: 'return' }
  ];
  
  // Define fitness function
  const fitnessFunction = async (solution: string): Promise<number> => {
    // Evaluate solution and return fitness score between 0 and 1
    // Higher is better
    return 0.5; // Example
  };
  
  // Evolve solution using hybrid approach
  const result = await hybridEngine.hybridEvolve(
    candidates,
    constraints,
    fitnessFunction
  );
  
  console.log(`Solution: ${result.solution}`);
  console.log(`Fitness: ${result.fitness}`);
  console.log(`Recursive Improvements: ${result.recursiveImprovements}`);
}

main().catch(console.error);
```

## Constraints

Supported constraint types:

- `must_contain`: Solution must contain the specified string
- `must_not_contain`: Solution must not contain the specified string
- `min_length`: Solution must be at least the specified length
- `max_length`: Solution must not exceed the specified length

## Running Tests

```bash
npx ts-node tests/hybrid_genetic_test.ts
```

## Documentation

For detailed architecture information, see:
- [Hybrid Genetic-Recursive Architecture](../docs/hybrid_genetic_recursive_architecture.md)

## Dependencies

### TypeScript/JavaScript
- Node.js (v16+)
- dotenv (for API key management)

### Python (for hybrid mode)
- Python 3.8+
- requests
- python-dotenv