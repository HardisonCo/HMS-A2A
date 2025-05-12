import * as d3 from 'd3';
import { Solution, Population, EvolutionMetrics } from '../genetic/types';

/**
 * Visualization component for genetic algorithm evolution
 * Provides real-time visualization of population statistics,
 * fitness trends, diversity metrics, and convergence rates
 */
export class GeneticVisualizer {
  private container: HTMLElement;
  private fitnessChart: any;
  private diversityChart: any;
  private populationView: any;
  private convergenceIndicator: any;
  private historyData: EvolutionMetrics[] = [];
  private options: VisualizationOptions;

  /**
   * @param containerId - ID of the HTML element to render visualizations
   * @param options - Configuration options for visualizations
   */
  constructor(containerId: string, options: VisualizationOptions = defaultOptions) {
    const containerElement = document.getElementById(containerId);
    if (!containerElement) {
      throw new Error(`Container element with ID ${containerId} not found`);
    }
    
    this.container = containerElement;
    this.options = { ...defaultOptions, ...options };
    this.initializeVisualization();
  }

  /**
   * Initialize the visualization components
   */
  private initializeVisualization(): void {
    // Create container elements
    const fitnessContainer = document.createElement('div');
    fitnessContainer.className = 'fitness-chart';
    
    const diversityContainer = document.createElement('div');
    diversityContainer.className = 'diversity-chart';
    
    const populationContainer = document.createElement('div');
    populationContainer.className = 'population-view';
    
    const convergenceContainer = document.createElement('div');
    convergenceContainer.className = 'convergence-indicator';
    
    // Append to main container
    this.container.appendChild(fitnessContainer);
    this.container.appendChild(diversityContainer);
    this.container.appendChild(populationContainer);
    this.container.appendChild(convergenceContainer);
    
    // Initialize charts
    this.initializeFitnessChart(fitnessContainer);
    this.initializeDiversityChart(diversityContainer);
    this.initializePopulationView(populationContainer);
    this.initializeConvergenceIndicator(convergenceContainer);
  }

  /**
   * Initialize the fitness trend chart
   * @param container - Container element for the chart
   */
  private initializeFitnessChart(container: HTMLElement): void {
    const width = container.clientWidth;
    const height = 200;
    
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);
      
    // Set up axes
    const xScale = d3.scaleLinear().range([40, width - 20]);
    const yScale = d3.scaleLinear().range([height - 30, 20]);
    
    // Add axes
    const xAxis = svg.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0, ${height - 30})`);
      
    const yAxis = svg.append('g')
      .attr('class', 'y-axis')
      .attr('transform', 'translate(40, 0)');
      
    // Add lines for best, average, and worst fitness
    const bestLine = d3.line<EvolutionMetrics>()
      .x((d, i) => xScale(i))
      .y(d => yScale(d.bestFitness));
      
    const avgLine = d3.line<EvolutionMetrics>()
      .x((d, i) => xScale(i))
      .y(d => yScale(d.averageFitness));
      
    const worstLine = d3.line<EvolutionMetrics>()
      .x((d, i) => xScale(i))
      .y(d => yScale(d.worstFitness));
    
    // Add paths
    const bestPath = svg.append('path')
      .attr('class', 'best-fitness')
      .attr('fill', 'none')
      .attr('stroke', '#2c93c8')
      .attr('stroke-width', 2);
      
    const avgPath = svg.append('path')
      .attr('class', 'avg-fitness')
      .attr('fill', 'none')
      .attr('stroke', '#a1d99b')
      .attr('stroke-width', 1.5);
      
    const worstPath = svg.append('path')
      .attr('class', 'worst-fitness')
      .attr('fill', 'none')
      .attr('stroke', '#e6550d')
      .attr('stroke-width', 1.5);
      
    // Add legend
    const legend = svg.append('g')
      .attr('class', 'legend')
      .attr('transform', `translate(${width - 120}, 10)`);
      
    // Best fitness
    legend.append('line')
      .attr('x1', 0)
      .attr('y1', 5)
      .attr('x2', 20)
      .attr('y2', 5)
      .attr('stroke', '#2c93c8')
      .attr('stroke-width', 2);
      
    legend.append('text')
      .attr('x', 25)
      .attr('y', 9)
      .text('Best')
      .style('font-size', '10px');
      
    // Average fitness
    legend.append('line')
      .attr('x1', 0)
      .attr('y1', 20)
      .attr('x2', 20)
      .attr('y2', 20)
      .attr('stroke', '#a1d99b')
      .attr('stroke-width', 1.5);
      
    legend.append('text')
      .attr('x', 25)
      .attr('y', 24)
      .text('Average')
      .style('font-size', '10px');
      
    // Worst fitness
    legend.append('line')
      .attr('x1', 0)
      .attr('y1', 35)
      .attr('x2', 20)
      .attr('y2', 35)
      .attr('stroke', '#e6550d')
      .attr('stroke-width', 1.5);
      
    legend.append('text')
      .attr('x', 25)
      .attr('y', 39)
      .text('Worst')
      .style('font-size', '10px');
      
    // Add title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .text('Fitness Over Generations');
      
    // Store references for updates
    this.fitnessChart = {
      svg,
      xScale,
      yScale,
      xAxis,
      yAxis,
      bestPath,
      avgPath,
      worstPath,
      bestLine,
      avgLine,
      worstLine
    };
  }

  /**
   * Initialize the diversity chart
   * @param container - Container element for the chart
   */
  private initializeDiversityChart(container: HTMLElement): void {
    const width = container.clientWidth;
    const height = 150;
    
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);
      
    // Set up axes
    const xScale = d3.scaleLinear().range([40, width - 20]);
    const yScale = d3.scaleLinear().range([height - 30, 20]);
    
    // Add axes
    const xAxis = svg.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0, ${height - 30})`);
      
    const yAxis = svg.append('g')
      .attr('class', 'y-axis')
      .attr('transform', 'translate(40, 0)');
      
    // Add diversity line
    const diversityLine = d3.line<EvolutionMetrics>()
      .x((d, i) => xScale(i))
      .y(d => yScale(d.diversityScore));
      
    const diversityPath = svg.append('path')
      .attr('class', 'diversity-score')
      .attr('fill', 'none')
      .attr('stroke', '#7b3294')
      .attr('stroke-width', 2);
      
    // Add title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .text('Population Diversity');
      
    // Store references for updates
    this.diversityChart = {
      svg,
      xScale,
      yScale,
      xAxis,
      yAxis,
      diversityPath,
      diversityLine
    };
  }

  /**
   * Initialize the population view
   * @param container - Container element for the view
   */
  private initializePopulationView(container: HTMLElement): void {
    const width = container.clientWidth;
    const height = 150;
    
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);
      
    // Add title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .text('Current Population');
      
    // Store reference for updates
    this.populationView = {
      svg,
      width,
      height,
      cellSize: 10,
      maxCells: Math.floor((width - 40) / 10)
    };
  }

  /**
   * Initialize the convergence indicator
   * @param container - Container element for the indicator
   */
  private initializeConvergenceIndicator(container: HTMLElement): void {
    const width = container.clientWidth;
    const height = 80;
    
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);
      
    // Add background
    svg.append('rect')
      .attr('x', 40)
      .attr('y', 30)
      .attr('width', width - 60)
      .attr('height', 20)
      .attr('fill', '#f0f0f0')
      .attr('rx', 3)
      .attr('ry', 3);
      
    // Add progress indicator
    const indicator = svg.append('rect')
      .attr('x', 40)
      .attr('y', 30)
      .attr('width', 0)
      .attr('height', 20)
      .attr('fill', '#7b3294')
      .attr('rx', 3)
      .attr('ry', 3);
      
    // Add title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .text('Convergence Progress');
      
    // Add text indicator
    const text = svg.append('text')
      .attr('x', width / 2)
      .attr('y', 65)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('0%');
      
    // Store references for updates
    this.convergenceIndicator = {
      svg,
      indicator,
      text,
      width: width - 60
    };
  }

  /**
   * Update the visualization with new evolution metrics
   * @param metrics - Current evolution metrics
   * @param population - Current population
   */
  public updateVisualization(metrics: EvolutionMetrics, population: Population): void {
    this.historyData.push(metrics);
    
    // Update charts with new data
    this.updateFitnessChart();
    this.updateDiversityChart();
    this.updatePopulationView(population);
    this.updateConvergenceIndicator(metrics.convergenceRate);
  }

  /**
   * Update the fitness chart with current data
   */
  private updateFitnessChart(): void {
    const { xScale, yScale, xAxis, yAxis, bestPath, avgPath, worstPath, 
            bestLine, avgLine, worstLine } = this.fitnessChart;
    
    // Update scales
    xScale.domain([0, this.historyData.length - 1]);
    
    const maxFitness = d3.max(this.historyData, d => d.bestFitness) || 1;
    const minFitness = d3.min(this.historyData, d => d.worstFitness) || 0;
    const padding = (maxFitness - minFitness) * 0.1;
    
    yScale.domain([
      Math.max(0, minFitness - padding),
      maxFitness + padding
    ]);
    
    // Update axes
    xAxis.call(d3.axisBottom(xScale).ticks(5).tickFormat(d => `${d}`));
    yAxis.call(d3.axisLeft(yScale).ticks(5));
    
    // Update paths
    bestPath.attr('d', bestLine(this.historyData));
    avgPath.attr('d', avgLine(this.historyData));
    worstPath.attr('d', worstLine(this.historyData));
  }

  /**
   * Update the diversity chart with current data
   */
  private updateDiversityChart(): void {
    const { xScale, yScale, xAxis, yAxis, diversityPath, diversityLine } = this.diversityChart;
    
    // Update scales
    xScale.domain([0, this.historyData.length - 1]);
    
    const maxDiversity = d3.max(this.historyData, d => d.diversityScore) || 1;
    yScale.domain([0, maxDiversity * 1.1]);
    
    // Update axes
    xAxis.call(d3.axisBottom(xScale).ticks(5).tickFormat(d => `${d}`));
    yAxis.call(d3.axisLeft(yScale).ticks(5));
    
    // Update path
    diversityPath.attr('d', diversityLine(this.historyData));
  }

  /**
   * Update the population view with current population
   * @param population - Current population
   */
  private updatePopulationView(population: Population): void {
    const { svg, width, height, cellSize, maxCells } = this.populationView;
    
    // Clear existing visualization
    svg.selectAll('.population-cell').remove();
    
    // Calculate max number of individuals to show
    const numIndividuals = Math.min(population.length, maxCells);
    
    // Sort population by fitness (descending)
    const sortedPopulation = [...population].sort((a, b) => b.fitness - a.fitness);
    
    // Get color scale based on fitness values
    const minFitness = sortedPopulation[numIndividuals - 1].fitness;
    const maxFitness = sortedPopulation[0].fitness;
    
    const colorScale = d3.scaleSequential(d3.interpolateViridis)
      .domain([minFitness, maxFitness]);
    
    // Create cells for each individual
    for (let i = 0; i < numIndividuals; i++) {
      const individual = sortedPopulation[i];
      
      svg.append('rect')
        .attr('class', 'population-cell')
        .attr('x', 40 + i * cellSize)
        .attr('y', 30)
        .attr('width', cellSize - 1)
        .attr('height', cellSize * 8)
        .attr('fill', colorScale(individual.fitness))
        .append('title')
        .text(`Fitness: ${individual.fitness.toFixed(4)}`);
    }
    
    // Add color legend
    svg.selectAll('.legend-item').remove();
    
    const legendWidth = 120;
    const legendHeight = 10;
    const legendX = width - legendWidth - 20;
    const legendY = height - 30;
    
    // Create gradient for legend
    const defs = svg.append('defs');
    
    const gradient = defs.append('linearGradient')
      .attr('id', 'fitness-gradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '100%')
      .attr('y2', '0%');
      
    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', colorScale(minFitness));
      
    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', colorScale(maxFitness));
    
    // Add legend rectangle
    svg.append('rect')
      .attr('class', 'legend-item')
      .attr('x', legendX)
      .attr('y', legendY)
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', 'url(#fitness-gradient)');
    
    // Add legend labels
    svg.append('text')
      .attr('class', 'legend-item')
      .attr('x', legendX)
      .attr('y', legendY - 5)
      .style('font-size', '10px')
      .style('text-anchor', 'start')
      .text(`${minFitness.toFixed(2)}`);
      
    svg.append('text')
      .attr('class', 'legend-item')
      .attr('x', legendX + legendWidth)
      .attr('y', legendY - 5)
      .style('font-size', '10px')
      .style('text-anchor', 'end')
      .text(`${maxFitness.toFixed(2)}`);
  }

  /**
   * Update the convergence indicator
   * @param convergenceRate - Current convergence rate (0-1)
   */
  private updateConvergenceIndicator(convergenceRate: number): void {
    const { indicator, text, width } = this.convergenceIndicator;
    
    // Update indicator width
    indicator.attr('width', width * convergenceRate);
    
    // Update text
    text.text(`${(convergenceRate * 100).toFixed(1)}%`);
  }

  /**
   * Reset the visualization data
   */
  public reset(): void {
    this.historyData = [];
    this.updateFitnessChart();
    this.updateDiversityChart();
  }

  /**
   * Resize the visualization based on container size
   */
  public resize(): void {
    // Remove existing visualizations
    this.container.innerHTML = '';
    
    // Reinitialize
    this.initializeVisualization();
    
    // Redraw with existing data
    if (this.historyData.length > 0) {
      this.updateFitnessChart();
      this.updateDiversityChart();
    }
  }
}

/**
 * Options for genetic visualization
 */
export interface VisualizationOptions {
  /** Color scheme for charts */
  colorScheme?: string[];
  /** Whether to show tooltips */
  showTooltips?: boolean;
  /** Animation duration in ms */
  animationDuration?: number;
  /** Whether to show legends */
  showLegends?: boolean;
}

/**
 * Default visualization options
 */
const defaultOptions: VisualizationOptions = {
  colorScheme: ['#2c93c8', '#a1d99b', '#e6550d', '#7b3294'],
  showTooltips: true,
  animationDuration: 300,
  showLegends: true
};