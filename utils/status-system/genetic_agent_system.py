#!/usr/bin/env python3
"""
HMS Genetic Agent System
This script implements a genetic agent system that uses the repository analyzer
to monitor system status and evolve solutions to fix issues.
"""

import argparse
import json
import os
import sys
import time
import datetime
import subprocess
import signal
import random
import uuid
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Import other scripts
import repository_analyzer
import status_tracker
import environment_monitor
import docs_integrator

# Constants
REPOS_DIR = Path("SYSTEM-COMPONENTS")
DATA_DIR = Path("data")
GENETIC_DIR = Path("data/genetic")
LOGS_DIR = Path("logs")

class GeneticAgent:
    """Genetic Agent class representing an AI agent with evolvable traits"""
    
    def __init__(self, name: str, role: str, traits: Optional[Dict[str, float]] = None):
        """Initialize a genetic agent"""
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.generation = 1
        self.fitness = 0.0
        self.traits = traits or self.generate_random_traits()
        self.specializations = []
        self.knowledge = {}
        self.solutions = []
        
    def generate_random_traits(self) -> Dict[str, float]:
        """Generate random traits for a new agent"""
        return {
            "problem_detection": random.uniform(0.5, 1.0),
            "solution_generation": random.uniform(0.5, 1.0),
            "accuracy": random.uniform(0.5, 1.0),
            "efficiency": random.uniform(0.5, 1.0),
            "creativity": random.uniform(0.5, 1.0),
            "learning_rate": random.uniform(0.5, 1.0),
            "collaboration": random.uniform(0.5, 1.0),
            "adaptability": random.uniform(0.5, 1.0),
            "specialization": random.uniform(0.5, 1.0)
        }
        
    def calculate_fitness(self, success_rate: float, complexity: float, importance: float) -> float:
        """Calculate agent fitness based on performance"""
        # Basic fitness calculation
        weights = {
            "problem_detection": 0.15,
            "solution_generation": 0.2,
            "accuracy": 0.15,
            "efficiency": 0.1,
            "creativity": 0.1,
            "learning_rate": 0.1,
            "collaboration": 0.05,
            "adaptability": 0.1,
            "specialization": 0.05
        }
        
        base_fitness = sum(self.traits[trait] * weights[trait] for trait in weights)
        
        # Adjust fitness based on performance
        performance_adjustment = success_rate * 0.6 + (1 - complexity) * 0.2 + importance * 0.2
        
        # Calculate final fitness
        self.fitness = base_fitness * performance_adjustment
        return self.fitness
        
    def mutate(self, mutation_rate: float = 0.1, mutation_strength: float = 0.2) -> None:
        """Mutate agent traits"""
        for trait in self.traits:
            if random.random() < mutation_rate:
                # Apply mutation
                change = random.uniform(-mutation_strength, mutation_strength)
                self.traits[trait] = max(0.0, min(1.0, self.traits[trait] + change))
                
        # Increment generation
        self.generation += 1
        
    def crossover(self, other: 'GeneticAgent') -> 'GeneticAgent':
        """Create a new agent through genetic crossover"""
        # Create offspring name
        offspring_name = f"{self.name[:3]}-{other.name[:3]}"
        
        # Create offspring role
        if random.random() < 0.5:
            offspring_role = self.role
        else:
            offspring_role = other.role
            
        # Create new agent
        offspring = GeneticAgent(offspring_name, offspring_role, {})
        
        # Perform crossover for each trait
        for trait in self.traits:
            if random.random() < 0.5:
                offspring.traits[trait] = self.traits[trait]
            else:
                offspring.traits[trait] = other.traits[trait]
                
        # Inherit knowledge and specializations
        offspring.specializations = list(set(self.specializations + other.specializations))
        
        # Combine parent knowledge
        offspring.knowledge = {**self.knowledge, **other.knowledge}
        
        return offspring
        
    def specialize(self, area: str) -> None:
        """Specialize agent in a specific area"""
        if area not in self.specializations:
            self.specializations.append(area)
            
            # Boost relevant traits
            if area == "security":
                self.traits["problem_detection"] = min(1.0, self.traits["problem_detection"] * 1.2)
                self.traits["accuracy"] = min(1.0, self.traits["accuracy"] * 1.1)
                
            elif area == "performance":
                self.traits["efficiency"] = min(1.0, self.traits["efficiency"] * 1.2)
                self.traits["solution_generation"] = min(1.0, self.traits["solution_generation"] * 1.1)
                
            elif area == "documentation":
                self.traits["accuracy"] = min(1.0, self.traits["accuracy"] * 1.1)
                self.traits["creativity"] = min(1.0, self.traits["creativity"] * 1.2)
                
            elif area == "testing":
                self.traits["problem_detection"] = min(1.0, self.traits["problem_detection"] * 1.1)
                self.traits["accuracy"] = min(1.0, self.traits["accuracy"] * 1.2)
                
            elif area == "architecture":
                self.traits["creativity"] = min(1.0, self.traits["creativity"] * 1.2)
                self.traits["solution_generation"] = min(1.0, self.traits["solution_generation"] * 1.1)
                
            # Update specialization trait
            self.traits["specialization"] = min(1.0, self.traits["specialization"] * 1.1)
        
    def learn(self, knowledge: Dict[str, Any]) -> None:
        """Learn new knowledge"""
        # Update knowledge
        self.knowledge.update(knowledge)
        
        # Boost learning rate
        self.traits["learning_rate"] = min(1.0, self.traits["learning_rate"] * 1.05)
        
    def generate_solution(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a solution for a problem"""
        # Solution quality is influenced by agent traits
        problem_type = problem.get("type", "unknown")
        problem_severity = problem.get("severity", "medium")
        
        # Determine solution effectiveness based on traits and knowledge
        relevant_knowledge = any(k for k in self.knowledge if k in problem_type)
        specialized = problem_type in self.specializations
        
        base_effectiveness = (
            self.traits["solution_generation"] * 0.4 +
            self.traits["accuracy"] * 0.3 +
            self.traits["creativity"] * 0.3
        )
        
        # Adjust effectiveness based on specialization and knowledge
        if specialized:
            base_effectiveness *= 1.3
        if relevant_knowledge:
            base_effectiveness *= 1.2
            
        # Add some randomness
        effectiveness = min(1.0, base_effectiveness * random.uniform(0.8, 1.2))
        
        # Generate solution
        solution = {
            "id": str(uuid.uuid4()),
            "problem_id": problem.get("id"),
            "problem_type": problem_type,
            "agent_id": self.id,
            "agent_name": self.name,
            "agent_role": self.role,
            "timestamp": datetime.datetime.now().isoformat(),
            "effectiveness": effectiveness,
            "description": f"Solution generated by agent {self.name} with effectiveness {effectiveness:.2f}",
            "steps": self.generate_solution_steps(problem, effectiveness),
            "metadata": {
                "generation": self.generation,
                "fitness": self.fitness,
                "specialized": specialized,
                "relevant_knowledge": relevant_knowledge
            }
        }
        
        # Add to agent's solutions
        self.solutions.append(solution)
        
        return solution
    
    def generate_solution_steps(self, problem: Dict[str, Any], effectiveness: float) -> List[str]:
        """Generate steps for a solution based on problem type"""
        problem_type = problem.get("type", "unknown")
        component = problem.get("component", "unknown")
        description = problem.get("description", "")
        
        steps = []
        
        if problem_type == "security":
            steps = [
                f"Analyze security vulnerability in {component}",
                "Identify affected components and potential impact",
                "Implement security patch to fix vulnerability",
                "Update dependencies to secure versions",
                "Add security tests to prevent regression"
            ]
        elif problem_type == "performance":
            steps = [
                f"Profile {component} to identify performance bottlenecks",
                "Optimize critical code paths for better performance",
                "Implement caching where appropriate",
                "Reduce resource usage and improve efficiency",
                "Add performance benchmarks to track improvements"
            ]
        elif problem_type == "documentation":
            steps = [
                f"Review existing documentation for {component}",
                "Identify missing or outdated sections",
                "Update documentation with correct information",
                "Add examples and usage instructions",
                "Ensure documentation matches current implementation"
            ]
        elif problem_type == "testing":
            steps = [
                f"Analyze test coverage for {component}",
                "Identify missing test cases for critical functionality",
                "Implement additional tests to improve coverage",
                "Fix failing tests to ensure passing test suite",
                "Set up continuous testing to prevent regression"
            ]
        elif problem_type == "build":
            steps = [
                f"Analyze build failure in {component}",
                "Identify dependency issues or compilation errors",
                "Fix build configuration or code issues",
                "Ensure consistent build environment across systems",
                "Add build verification tests"
            ]
        else:
            steps = [
                f"Analyze issue in {component}",
                "Identify root cause of the problem",
                "Develop solution approach",
                "Implement necessary changes",
                "Verify solution effectiveness"
            ]
        
        # Adjust steps based on effectiveness
        if effectiveness < 0.5:
            # Lower effectiveness means less detailed/comprehensive solutions
            steps = steps[:3]
            steps.append("Review solution with team for improvements")
        
        return steps
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "generation": self.generation,
            "fitness": self.fitness,
            "traits": self.traits,
            "specializations": self.specializations,
            "knowledge_areas": list(self.knowledge.keys()),
            "solutions_count": len(self.solutions)
        }


class GeneticAgentSystem:
    """Genetic Agent System for repository analysis and issue resolution"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the genetic agent system"""
        self.config = config or {
            "population_size": 5,
            "mutation_rate": 0.1,
            "mutation_strength": 0.2,
            "crossover_rate": 0.7,
            "selection_pressure": 0.8,
            "max_generations": 100,
            "convergence_threshold": 0.01,
            "fitness_threshold": 0.7
        }
        
        self.population = []
        self.generation = 1
        self.best_fitness = 0.0
        self.problems = []
        self.solutions = []
        self.running = False
        
        # Initialize components
        self.repo_analyzer = repository_analyzer.RepositoryAnalyzer()
        self.status_tracker = status_tracker.StatusTracker()
        
        # Ensure directories
        self.ensure_directories()
        
    def ensure_directories(self) -> None:
        """Ensure required directories exist"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        GENETIC_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    def initialize_population(self) -> None:
        """Initialize the genetic agent population"""
        # Define roles
        roles = [
            "Monitor", 
            "Optimizer", 
            "Defender", 
            "Executor", 
            "Coordinator", 
            "Researcher"
        ]
        
        # Create agents for each role
        self.population = []
        for role in roles:
            # Base name on role
            name = f"{role[:3]}{random.randint(1000, 9999)}"
            
            # Create agent
            agent = GeneticAgent(name, role)
            
            # Add initial specialization based on role
            if role == "Monitor":
                agent.specialize("testing")
            elif role == "Optimizer":
                agent.specialize("performance")
            elif role == "Defender":
                agent.specialize("security")
            elif role == "Executor":
                agent.specialize("build")
            elif role == "Coordinator":
                agent.specialize("architecture")
            elif role == "Researcher":
                agent.specialize("documentation")
            
            # Add to population
            self.population.append(agent)
            
        print(f"Initialized population with {len(self.population)} agents")
    
    def detect_problems(self) -> List[Dict[str, Any]]:
        """Detect problems in repositories using the repository analyzer"""
        print("Detecting problems in repositories...")
        
        # Get all components
        components = self.repo_analyzer.list_repositories()
        
        # Analyze repositories
        problems = []
        for component in components:
            try:
                # Analyze repository
                analysis = self.repo_analyzer.analyze_repository(component)
                
                # Extract issues
                for section in ["git_status", "test_status", "documentation_status", "build_status", "security_status", "dependency_status"]:
                    if section in analysis and "issues" in analysis[section]:
                        for issue in analysis[section]["issues"]:
                            # Determine problem type from section
                            problem_type = section.replace("_status", "")
                            
                            # Determine severity based on section status
                            section_status = analysis[section].get("status", "UNKNOWN")
                            if section_status == "UNHEALTHY":
                                severity = "high"
                            elif section_status == "DEGRADED":
                                severity = "medium"
                            else:
                                severity = "low"
                                
                            # Create problem
                            problem = {
                                "id": str(uuid.uuid4()),
                                "component": component,
                                "type": problem_type,
                                "description": issue,
                                "severity": severity,
                                "timestamp": datetime.datetime.now().isoformat(),
                                "status": "detected",
                                "assignee": None
                            }
                            
                            problems.append(problem)
            except Exception as e:
                print(f"Error analyzing repository {component}: {str(e)}")
                
        # Update problems list
        self.problems = problems
                
        print(f"Detected {len(problems)} problems")
        return problems
    
    def assign_problems(self) -> List[Dict[str, Any]]:
        """Assign problems to agents based on fitness and specialization"""
        print("Assigning problems to agents...")
        
        # Get unassigned problems
        unassigned = [p for p in self.problems if p["status"] == "detected"]
        
        if not unassigned:
            print("No unassigned problems found")
            return []
            
        # Assignments
        assignments = []
        
        # Assign each problem to the most suitable agent
        for problem in unassigned:
            # Find best agent for this problem
            best_agent = None
            best_score = -1
            
            for agent in self.population:
                # Calculate assignment score
                score = self.calculate_assignment_score(agent, problem)
                
                if score > best_score:
                    best_score = score
                    best_agent = agent
            
            if best_agent:
                # Update problem
                problem["status"] = "assigned"
                problem["assignee"] = best_agent.id
                
                assignments.append({
                    "problem_id": problem["id"],
                    "agent_id": best_agent.id,
                    "agent_name": best_agent.name,
                    "agent_role": best_agent.role,
                    "score": best_score,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
        print(f"Assigned {len(assignments)} problems to agents")
        return assignments
    
    def calculate_assignment_score(self, agent: GeneticAgent, problem: Dict[str, Any]) -> float:
        """Calculate how well an agent is suited to solve a problem"""
        problem_type = problem.get("type", "unknown")
        
        # Base score on relevant traits
        score = (
            agent.traits["problem_detection"] * 0.3 +
            agent.traits["solution_generation"] * 0.4 +
            agent.traits["accuracy"] * 0.3
        )
        
        # Bonus for specialization
        if problem_type in agent.specializations:
            score *= 1.5
            
        # Bonus for relevant knowledge
        if any(k for k in agent.knowledge if k in problem_type):
            score *= 1.2
            
        # Penalty for agents with too many assigned problems
        assigned_count = sum(1 for p in self.problems if p.get("assignee") == agent.id)
        if assigned_count > 3:
            score /= (assigned_count - 2)
            
        return score
    
    def generate_solutions(self) -> List[Dict[str, Any]]:
        """Generate solutions for assigned problems"""
        print("Generating solutions for assigned problems...")
        
        # Solutions
        new_solutions = []
        
        # Process each assigned problem
        for problem in self.problems:
            if problem["status"] == "assigned":
                # Find the assigned agent
                agent_id = problem["assignee"]
                agent = next((a for a in self.population if a.id == agent_id), None)
                
                if agent:
                    # Generate solution
                    solution = agent.generate_solution(problem)
                    
                    # Update problem status
                    problem["status"] = "solved"
                    
                    # Add to solutions
                    self.solutions.append(solution)
                    new_solutions.append(solution)
                    
        print(f"Generated {len(new_solutions)} solutions")
        return new_solutions
    
    def evaluate_solutions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Evaluate solution effectiveness and update agent fitness"""
        print("Evaluating solutions and updating agent fitness...")
        
        # Results
        results = {
            "successful": [],
            "partially_successful": [],
            "unsuccessful": []
        }
        
        # Evaluate each solution
        for solution in self.solutions:
            # Only evaluate solutions that haven't been evaluated
            if solution.get("evaluated", False):
                continue
                
            # Get effectiveness
            effectiveness = solution.get("effectiveness", 0.0)
            
            # Determine success level
            if effectiveness >= 0.8:
                success_level = "successful"
            elif effectiveness >= 0.5:
                success_level = "partially_successful"
            else:
                success_level = "unsuccessful"
                
            # Add to results
            solution["success_level"] = success_level
            solution["evaluated"] = True
            results[success_level].append(solution)
            
            # Update agent fitness
            agent_id = solution.get("agent_id")
            agent = next((a for a in self.population if a.id == agent_id), None)
            
            if agent:
                # Get problem
                problem_id = solution.get("problem_id")
                problem = next((p for p in self.problems if p["id"] == problem_id), None)
                
                if problem:
                    # Calculate problem complexity (0.3-1.0)
                    complexity = 0.3 + (0.7 * (1.0 if problem.get("severity") == "high" else
                                               0.6 if problem.get("severity") == "medium" else 0.3))
                    
                    # Calculate problem importance (0.5-1.0)
                    importance = 0.5 + (0.5 * (1.0 if problem.get("severity") == "high" else
                                               0.7 if problem.get("severity") == "medium" else 0.4))
                    
                    # Calculate success rate (0.0-1.0)
                    success_rate = effectiveness
                    
                    # Update agent fitness
                    fitness = agent.calculate_fitness(success_rate, complexity, importance)
                    print(f"Agent {agent.name} fitness: {fitness:.4f}")
                    
                    # Update best fitness
                    if fitness > self.best_fitness:
                        self.best_fitness = fitness
                    
        print(f"Evaluated {sum(len(r) for r in results.values())} solutions")
        print(f"Successful: {len(results['successful'])}, Partially successful: {len(results['partially_successful'])}, Unsuccessful: {len(results['unsuccessful'])}")
        
        return results
    
    def evolve_population(self) -> Dict[str, Any]:
        """Evolve the agent population based on fitness"""
        print(f"Evolving population (Generation {self.generation})...")
        
        # Sort population by fitness
        self.population.sort(key=lambda a: a.fitness, reverse=True)
        
        # Get top performers
        elite_count = max(1, int(len(self.population) * 0.2))
        elite = self.population[:elite_count]
        
        # Create new population starting with elite (unchanged)
        new_population = elite.copy()
        
        # Fill rest of population through crossover and mutation
        while len(new_population) < len(self.population):
            # Select parents using tournament selection
            parent1 = self.select_parent()
            parent2 = self.select_parent()
            
            # Perform crossover
            if random.random() < self.config["crossover_rate"] and parent1 != parent2:
                offspring = parent1.crossover(parent2)
            else:
                # Clone parent1
                offspring = GeneticAgent(parent1.name, parent1.role, dict(parent1.traits))
                offspring.specializations = parent1.specializations.copy()
                offspring.knowledge = dict(parent1.knowledge)
                
            # Perform mutation
            offspring.mutate(self.config["mutation_rate"], self.config["mutation_strength"])
            
            # Add to new population
            new_population.append(offspring)
            
        # Replace population
        self.population = new_population
        
        # Increment generation
        self.generation += 1
        
        # Results
        results = {
            "generation": self.generation,
            "population_size": len(self.population),
            "best_fitness": self.best_fitness,
            "avg_fitness": sum(a.fitness for a in self.population) / len(self.population),
            "elite_count": elite_count
        }
        
        print(f"Population evolved to generation {self.generation}")
        print(f"Best fitness: {results['best_fitness']:.4f}, Average fitness: {results['avg_fitness']:.4f}")
        
        return results
    
    def select_parent(self) -> GeneticAgent:
        """Select a parent using tournament selection"""
        tournament_size = 3
        candidates = random.sample(self.population, min(tournament_size, len(self.population)))
        return max(candidates, key=lambda a: a.fitness)
    
    def run_generation(self) -> Dict[str, Any]:
        """Run a complete generation cycle"""
        print(f"Running generation {self.generation}...")
        
        # Step 1: Detect problems
        problems = self.detect_problems()
        
        # Step 2: Assign problems to agents
        assignments = self.assign_problems()
        
        # Step 3: Generate solutions
        solutions = self.generate_solutions()
        
        # Step 4: Evaluate solutions
        evaluation = self.evaluate_solutions()
        
        # Step 5: Evolve population
        evolution = self.evolve_population()
        
        # Generate generation summary
        summary = {
            "generation": self.generation - 1,  # Just completed
            "timestamp": datetime.datetime.now().isoformat(),
            "problems_detected": len(problems),
            "problems_assigned": len(assignments),
            "solutions_generated": len(solutions),
            "successful_solutions": len(evaluation["successful"]),
            "partially_successful_solutions": len(evaluation["partially_successful"]),
            "unsuccessful_solutions": len(evaluation["unsuccessful"]),
            "best_fitness": self.best_fitness,
            "avg_fitness": evolution["avg_fitness"],
            "best_agents": [a.to_dict() for a in sorted(self.population, key=lambda x: x.fitness, reverse=True)[:3]]
        }
        
        # Save generation summary
        self.save_generation_summary(summary)
        
        return summary
    
    def save_generation_summary(self, summary: Dict[str, Any]) -> None:
        """Save generation summary to file"""
        # Create file path
        file_path = os.path.join(GENETIC_DIR, f"generation_{summary['generation']}.json")
        
        # Save data
        with open(file_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        # Also save as latest
        latest_path = os.path.join(GENETIC_DIR, "latest_generation.json")
        with open(latest_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"Generation summary saved to: {file_path}")
    
    def save_population(self) -> None:
        """Save current population to file"""
        # Create file path
        file_path = os.path.join(GENETIC_DIR, f"population_gen_{self.generation}.json")
        
        # Convert population to serializable format
        population_data = [agent.to_dict() for agent in self.population]
        
        # Save data
        with open(file_path, 'w') as f:
            json.dump(population_data, f, indent=2)
            
        # Also save as latest
        latest_path = os.path.join(GENETIC_DIR, "latest_population.json")
        with open(latest_path, 'w') as f:
            json.dump(population_data, f, indent=2)
            
        print(f"Population saved to: {file_path}")
    
    def run_evolution(self, generations: int = 10) -> Dict[str, Any]:
        """Run the genetic algorithm for a specified number of generations"""
        print(f"Running genetic evolution for {generations} generations...")
        
        # Initialize population if needed
        if not self.population:
            self.initialize_population()
            
        # Run generations
        for _ in range(generations):
            # Run generation
            summary = self.run_generation()
            
            # Save population
            self.save_population()
            
            # Check for convergence
            if self.check_convergence():
                print("Convergence reached, stopping evolution")
                break
                
        # Final summary
        final_summary = {
            "total_generations": self.generation - 1,
            "best_fitness": self.best_fitness,
            "total_problems": len(self.problems),
            "total_solutions": len(self.solutions),
            "success_rate": len([s for s in self.solutions if s.get("success_level") == "successful"]) / max(1, len(self.solutions)),
            "best_agent": max(self.population, key=lambda a: a.fitness).to_dict()
        }
        
        return final_summary
    
    def check_convergence(self) -> bool:
        """Check if the genetic algorithm has converged"""
        # Simple convergence check: best fitness is above threshold
        return self.best_fitness >= self.config["fitness_threshold"]
    
    def generate_visualization(self) -> Dict[str, Any]:
        """Generate visualization data for the genetic agent system"""
        print("Generating visualization data...")
        
        # Basic statistics
        stats = {
            "generation": self.generation - 1,
            "population_size": len(self.population),
            "best_fitness": self.best_fitness,
            "avg_fitness": sum(a.fitness for a in self.population) / max(1, len(self.population)),
            "problem_count": len(self.problems),
            "solution_count": len(self.solutions),
            "success_rate": len([s for s in self.solutions if s.get("success_level") == "successful"]) / max(1, len(self.solutions))
        }
        
        # Agent network
        agents = []
        for agent in self.population:
            agent_data = agent.to_dict()
            agent_data["solutions"] = [
                {
                    "id": s["id"],
                    "problem_id": s["problem_id"],
                    "effectiveness": s["effectiveness"],
                    "success_level": s.get("success_level", "unknown")
                }
                for s in agent.solutions
            ]
            agents.append(agent_data)
            
        # Problem categories
        problem_categories = {}
        for problem in self.problems:
            category = problem.get("type", "unknown")
            if category not in problem_categories:
                problem_categories[category] = 0
            problem_categories[category] += 1
            
        # Solution effectiveness
        solution_effectiveness = {
            "successful": len([s for s in self.solutions if s.get("success_level") == "successful"]),
            "partially_successful": len([s for s in self.solutions if s.get("success_level") == "partially_successful"]),
            "unsuccessful": len([s for s in self.solutions if s.get("success_level") == "unsuccessful"]),
            "unknown": len([s for s in self.solutions if s.get("success_level") is None])
        }
        
        # Agent specializations
        specializations = {}
        for agent in self.population:
            for spec in agent.specializations:
                if spec not in specializations:
                    specializations[spec] = 0
                specializations[spec] += 1
                
        # Combined visualization data
        visualization = {
            "timestamp": datetime.datetime.now().isoformat(),
            "stats": stats,
            "agents": agents,
            "problem_categories": problem_categories,
            "solution_effectiveness": solution_effectiveness,
            "specializations": specializations
        }
        
        # Save visualization data
        file_path = os.path.join(GENETIC_DIR, "visualization.json")
        with open(file_path, 'w') as f:
            json.dump(visualization, f, indent=2)
            
        print(f"Visualization data saved to: {file_path}")
        
        return visualization
    
    def start_conversation(self, problem_id: Optional[str] = None, agents_count: int = 3) -> Dict[str, Any]:
        """Start a conversation between agents about a problem or the system in general"""
        print("Starting agent conversation...")
        
        # Select problem if provided
        problem = None
        if problem_id:
            problem = next((p for p in self.problems if p["id"] == problem_id), None)
            
        # If no problem specified or found, pick a random one
        if not problem and self.problems:
            problem = random.choice(self.problems)
            
        # Select agents to participate
        if problem:
            # First add the agent assigned to the problem if any
            participants = []
            if problem.get("assignee"):
                assignee = next((a for a in self.population if a.id == problem["assignee"]), None)
                if assignee:
                    participants.append(assignee)
                    
            # Add other agents based on fitness and relevance
            remaining = [a for a in self.population if a not in participants]
            
            # Sort by relevance to the problem
            remaining.sort(key=lambda a: self.calculate_assignment_score(a, problem), reverse=True)
            
            # Add top agents
            participants.extend(remaining[:agents_count - len(participants)])
        else:
            # Select highest fitness agents
            participants = sorted(self.population, key=lambda a: a.fitness, reverse=True)[:agents_count]
            
        # Ensure we have enough participants
        if len(participants) < 2:
            print("Not enough agents for a conversation")
            return {"error": "Not enough agents for a conversation"}
            
        # Generate conversation
        conversation = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "problem": problem,
            "participants": [a.to_dict() for a in participants],
            "messages": []
        }
        
        # Generate opening messages
        if problem:
            # First message from assignee or highest fitness agent
            first_agent = participants[0]
            conversation["messages"].append({
                "agent_id": first_agent.id,
                "agent_name": first_agent.name,
                "agent_role": first_agent.role,
                "content": f"I've been analyzing the {problem['type']} issue in {problem['component']}: \"{problem['description']}\". My initial assessment suggests this is a {problem['severity']} severity issue that requires our attention.",
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            # Response from second agent
            second_agent = participants[1]
            conversation["messages"].append({
                "agent_id": second_agent.id,
                "agent_name": second_agent.name,
                "agent_role": second_agent.role,
                "content": f"I've reviewed this {problem['type']} issue as well. Based on my analysis, I believe we should approach this methodically. What specific aspects of this issue are most concerning to you?",
                "timestamp": datetime.datetime.now().isoformat()
            })
        else:
            # General system health conversation
            first_agent = participants[0]
            conversation["messages"].append({
                "agent_id": first_agent.id,
                "agent_name": first_agent.name,
                "agent_role": first_agent.role,
                "content": "I've been monitoring our system health metrics, and I've noticed some patterns we should discuss. Our overall health status shows several areas that could benefit from optimization.",
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            # Response from second agent
            second_agent = participants[1]
            conversation["messages"].append({
                "agent_id": second_agent.id,
                "agent_name": second_agent.name,
                "agent_role": second_agent.role,
                "content": "I agree with your assessment. My analysis shows that we could improve several key areas through targeted optimization. What specific metrics are you most concerned about?",
                "timestamp": datetime.datetime.now().isoformat()
            })
            
        # Continue conversation with solution discussion
        third_agent = participants[2] if len(participants) > 2 else participants[0]
        
        if problem:
            # Find any solutions for this problem
            solutions = [s for s in self.solutions if s.get("problem_id") == problem["id"]]
            
            if solutions:
                # Discuss existing solution
                solution = solutions[0]
                solution_agent = next((a for a in participants if a.id == solution.get("agent_id")), participants[0])
                
                # Message from solution agent
                conversation["messages"].append({
                    "agent_id": solution_agent.id,
                    "agent_name": solution_agent.name,
                    "agent_role": solution_agent.role,
                    "content": f"I've developed a solution approach for this issue with an estimated effectiveness of {solution['effectiveness']:.2f}. The key steps involve: {', '.join(solution['steps'][:3])}...",
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
                # Response from third agent
                conversation["messages"].append({
                    "agent_id": third_agent.id,
                    "agent_name": third_agent.name,
                    "agent_role": third_agent.role,
                    "content": f"I've reviewed your solution approach and believe it's on the right track. I'd suggest adding additional validation steps to ensure the issue is fully resolved. Have you considered potential side effects on related components?",
                    "timestamp": datetime.datetime.now().isoformat()
                })
            else:
                # Discuss potential solutions
                conversation["messages"].append({
                    "agent_id": third_agent.id,
                    "agent_name": third_agent.name,
                    "agent_role": third_agent.role,
                    "content": f"Based on my analysis, I believe we should approach this {problem['type']} issue by first thoroughly investigating the root cause in {problem['component']}. Once we understand that, we can develop a targeted solution strategy.",
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
                # Response from first agent
                conversation["messages"].append({
                    "agent_id": first_agent.id,
                    "agent_name": first_agent.name,
                    "agent_role": first_agent.role,
                    "content": "I agree with that approach. Let me work on developing a comprehensive solution based on our collective analysis. I'll incorporate our combined expertise to ensure we address all aspects of this issue effectively.",
                    "timestamp": datetime.datetime.now().isoformat()
                })
        else:
            # General system improvement discussion
            conversation["messages"].append({
                "agent_id": third_agent.id,
                "agent_name": third_agent.name,
                "agent_role": third_agent.role,
                "content": "I've been analyzing patterns across our codebase, and I've identified several opportunities for improvement. Specifically, we should focus on enhancing test coverage and documentation completeness across critical components.",
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            # Response from first agent about learning
            conversation["messages"].append({
                "agent_id": first_agent.id,
                "agent_name": first_agent.name,
                "agent_role": first_agent.role,
                "content": "That's valuable insight. I'll incorporate that into my knowledge base and adjust my monitoring parameters accordingly. By collaborating and combining our specialized perspectives, we can continue to evolve and improve our system health metrics.",
                "timestamp": datetime.datetime.now().isoformat()
            })
            
        # Closing from second agent
        conversation["messages"].append({
            "agent_id": second_agent.id,
            "agent_name": second_agent.name,
            "agent_role": second_agent.role,
            "content": "This has been a productive exchange. I believe our genetic traits are evolving effectively to better address these types of challenges. Let's implement our agreed approach and reconvene to evaluate the results.",
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Save conversation
        file_path = os.path.join(GENETIC_DIR, f"conversation_{conversation['id']}.json")
        with open(file_path, 'w') as f:
            json.dump(conversation, f, indent=2)
            
        print(f"Conversation saved to: {file_path}")
        
        return conversation


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="HMS Genetic Agent System")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")
    
    # init command
    init_parser = subparsers.add_parser("init", help="Initialize genetic agent system")
    init_parser.add_argument("--population", type=int, default=5, help="Initial population size")
    
    # detect command
    subparsers.add_parser("detect", help="Detect problems in repositories")
    
    # evolve command
    evolve_parser = subparsers.add_parser("evolve", help="Run genetic evolution")
    evolve_parser.add_argument("--generations", type=int, default=10, help="Number of generations to evolve")
    
    # visualize command
    subparsers.add_parser("visualize", help="Generate visualization data")
    
    # conversation command
    conversation_parser = subparsers.add_parser("conversation", help="Generate agent conversation")
    conversation_parser.add_argument("--problem", help="Problem ID to discuss (optional)")
    conversation_parser.add_argument("--agents", type=int, default=3, help="Number of agents to participate")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create system
    system = GeneticAgentSystem()
    
    # Execute command
    if args.command == "init":
        system.config["population_size"] = args.population
        system.initialize_population()
        system.save_population()
        print(f"Initialized genetic agent system with {args.population} agents")
        
    elif args.command == "detect":
        problems = system.detect_problems()
        print(json.dumps(problems, indent=2))
        
    elif args.command == "evolve":
        summary = system.run_evolution(args.generations)
        print(json.dumps(summary, indent=2))
        
    elif args.command == "visualize":
        visualization = system.generate_visualization()
        print(json.dumps(visualization, indent=2))
        
    elif args.command == "conversation":
        conversation = system.start_conversation(args.problem, args.agents)
        print(json.dumps(conversation, indent=2))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()