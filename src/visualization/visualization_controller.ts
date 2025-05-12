import { GeneticVisualizer } from './genetic_visualizer';
import { 
  GeneticVisualizationAdapter,
  RecursiveThinkingVisualizationAdapter,
  HybridVisualizationAdapter
} from './data_adapters';
import { 
  WebSocketCommunicator
} from '../genetic/communication/websocket_communicator';

/**
 * Controller for the visualization system
 * Coordinates visualization updates between genetic and recursive thinking components
 * Provides a central interface for visualization management
 */
export class VisualizationController {
  private geneticVisualizer: GeneticVisualizer | null = null;
  private hybridAdapter: HybridVisualizationAdapter;
  private communicator: WebSocketCommunicator;
  private isEnabled: boolean = false;
  private autoUpdateInterval: NodeJS.Timeout | null = null;
  private updateFrequency: number = 1000; // ms
  private containerId: string | null = null;
  
  /**
   * @param communicator - WebSocket communicator for data streaming
   * @param options - Visualization controller options
   */
  constructor(
    communicator: WebSocketCommunicator, 
    options: VisualizationControllerOptions = {}
  ) {
    this.communicator = communicator;
    this.hybridAdapter = new HybridVisualizationAdapter(
      options.maxGeneticHistory || 100,
      options.maxThinkingHistory || 50
    );
    this.updateFrequency = options.updateFrequency || 1000;
    
    // Attach event listeners for communication events
    this.attachEventListeners();
  }
  
  /**
   * Initialize the visualization UI
   * @param containerId - ID of the HTML container for visualization
   * @param options - Visualization options
   */
  public initialize(containerId: string, options: VisualizationOptions = {}): void {
    if (typeof window === 'undefined') {
      console.warn('VisualizationController: Visualization is only available in browser environments');
      return;
    }
    
    this.containerId = containerId;
    this.geneticVisualizer = new GeneticVisualizer(containerId, options);
    this.isEnabled = true;
    
    // Start auto-update if frequency is set
    if (this.updateFrequency > 0) {
      this.startAutoUpdate();
    }
    
    console.log(`VisualizationController: Initialized with container ${containerId}`);
  }
  
  /**
   * Start auto-updating visualization
   */
  public startAutoUpdate(): void {
    if (!this.isEnabled) {
      console.warn('VisualizationController: Visualization is not enabled');
      return;
    }
    
    if (this.autoUpdateInterval) {
      clearInterval(this.autoUpdateInterval);
    }
    
    this.autoUpdateInterval = setInterval(() => {
      this.updateVisualization();
    }, this.updateFrequency);
    
    console.log(`VisualizationController: Auto-update started with frequency ${this.updateFrequency}ms`);
  }
  
  /**
   * Stop auto-updating visualization
   */
  public stopAutoUpdate(): void {
    if (this.autoUpdateInterval) {
      clearInterval(this.autoUpdateInterval);
      this.autoUpdateInterval = null;
      console.log('VisualizationController: Auto-update stopped');
    }
  }
  
  /**
   * Update the visualization with current data
   */
  public updateVisualization(): void {
    if (!this.isEnabled || !this.geneticVisualizer) {
      return;
    }
    
    // Get latest data from adapters
    const geneticAdapter = this.hybridAdapter.getGeneticAdapter();
    const geneticMetrics = geneticAdapter.getFitnessTrendData();
    
    if (geneticMetrics.length === 0) {
      return; // No data to visualize
    }
    
    // Get latest population
    const evolutionHistory = geneticAdapter.getEvolutionHistory();
    const latestPopulation = evolutionHistory.bestSolutions.length > 0 ?
      [evolutionHistory.bestSolutions[evolutionHistory.bestSolutions.length - 1]] : [];
    
    // Get latest metrics
    const latestMetric = evolutionHistory.metrics[evolutionHistory.metrics.length - 1];
    
    // Update visualization
    if (latestMetric && latestPopulation.length > 0) {
      this.geneticVisualizer.updateVisualization(latestMetric, latestPopulation);
    }
    
    console.debug('VisualizationController: Visualization updated');
  }
  
  /**
   * Handle evolution data from WebSocket
   * @param data - Evolution data from WebSocket
   */
  private handleEvolutionData(data: any): void {
    const { metrics, population, operationStats } = data;
    
    if (metrics) {
      this.hybridAdapter.getGeneticAdapter().addEvolutionMetrics(metrics);
    }
    
    if (population) {
      this.hybridAdapter.getGeneticAdapter().addPopulationSnapshot(population);
    }
    
    if (operationStats) {
      this.hybridAdapter.getGeneticAdapter().addOperationStats(operationStats);
    }
    
    // Trigger visualization update if not in auto-update mode
    if (this.isEnabled && !this.autoUpdateInterval) {
      this.updateVisualization();
    }
  }
  
  /**
   * Handle thinking data from WebSocket
   * @param data - Thinking data from WebSocket
   */
  private handleThinkingData(data: any): void {
    const { stats } = data;
    
    if (stats) {
      this.hybridAdapter.getThinkingAdapter().addThinkingStats(stats);
    }
  }
  
  /**
   * Attach event listeners to WebSocket communicator
   */
  private attachEventListeners(): void {
    // This assumes the WebSocketCommunicator has events for evolution and thinking data
    // Implement these if they don't exist
    this.communicator.on('evolutionData', this.handleEvolutionData.bind(this));
    this.communicator.on('thinkingData', this.handleThinkingData.bind(this));
    
    // Handle websocket connection events
    this.communicator.on('connect', () => {
      console.log('VisualizationController: WebSocket connected');
    });
    
    this.communicator.on('disconnect', () => {
      console.log('VisualizationController: WebSocket disconnected');
    });
  }
  
  /**
   * Reset visualization data
   */
  public reset(): void {
    this.hybridAdapter.reset();
    
    if (this.geneticVisualizer) {
      this.geneticVisualizer.reset();
    }
    
    console.log('VisualizationController: Visualization data reset');
  }
  
  /**
   * Resize the visualization
   */
  public resize(): void {
    if (this.isEnabled && this.geneticVisualizer) {
      this.geneticVisualizer.resize();
      console.log('VisualizationController: Visualization resized');
    }
  }
  
  /**
   * Enable visualization
   */
  public enable(): void {
    this.isEnabled = true;
    
    if (this.containerId && !this.geneticVisualizer) {
      this.geneticVisualizer = new GeneticVisualizer(this.containerId);
    }
    
    console.log('VisualizationController: Visualization enabled');
  }
  
  /**
   * Disable visualization
   */
  public disable(): void {
    this.isEnabled = false;
    this.stopAutoUpdate();
    console.log('VisualizationController: Visualization disabled');
  }
  
  /**
   * Check if visualization is enabled
   * @returns Whether visualization is enabled
   */
  public isVisualizationEnabled(): boolean {
    return this.isEnabled;
  }
  
  /**
   * Get metrics summary for display or logging
   * @returns Summary of metrics
   */
  public getMetricsSummary(): MetricsSummary {
    const hybridMetrics = this.hybridAdapter.getHybridMetrics();
    
    return {
      genetic: {
        totalGenerations: hybridMetrics.geneticStats.totalGenerations,
        bestFitness: hybridMetrics.geneticStats.bestFitness,
        convergenceRate: hybridMetrics.geneticStats.convergenceRate,
        diversityScore: hybridMetrics.geneticStats.diversityScore
      },
      thinking: {
        totalProcesses: hybridMetrics.thinkingStats.totalThinkingProcesses,
        averageSteps: hybridMetrics.thinkingStats.averageStepCount,
        averageImprovement: hybridMetrics.thinkingStats.averageImprovementScore,
        tokensPerSecond: hybridMetrics.thinkingStats.tokensPerSecond
      },
      hybrid: {
        synergy: hybridMetrics.hybridEfficiency.hybridSynergy,
        totalImprovementScore: hybridMetrics.hybridEfficiency.totalImprovementScore
      }
    };
  }
  
  /**
   * Export visualization data as JSON
   * @returns JSON string of visualization data
   */
  public exportData(): string {
    const geneticData = this.hybridAdapter.getGeneticAdapter().getEvolutionHistory();
    const thinkingData = this.hybridAdapter.getThinkingAdapter().getThinkingProcessData();
    const hybridMetrics = this.hybridAdapter.getHybridMetrics();
    
    const exportData = {
      timestamp: new Date().toISOString(),
      geneticData,
      thinkingData,
      hybridMetrics
    };
    
    return JSON.stringify(exportData, null, 2);
  }
  
  /**
   * Save visualization data to file (browser only)
   * @param filename - Name of the file to save
   * @returns Promise that resolves when the file is saved
   */
  public saveData(filename: string = 'visualization_data.json'): Promise<void> {
    if (typeof window === 'undefined') {
      return Promise.reject(new Error('saveData is only available in browser environments'));
    }
    
    const data = this.exportData();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    return new Promise((resolve, reject) => {
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        resolve();
      }, 100);
    });
  }
}

/**
 * Options for visualization controller
 */
export interface VisualizationControllerOptions {
  /** Maximum number of genetic history points to store */
  maxGeneticHistory?: number;
  /** Maximum number of thinking history points to store */
  maxThinkingHistory?: number;
  /** Frequency of auto-updates in milliseconds (0 to disable) */
  updateFrequency?: number;
}

/**
 * Visualization options
 */
export interface VisualizationOptions {
  /** Color scheme for visualization */
  colorScheme?: string[];
  /** Whether to show tooltips */
  showTooltips?: boolean;
  /** Animation duration in milliseconds */
  animationDuration?: number;
  /** Whether to show legends */
  showLegends?: boolean;
}

/**
 * Summary of metrics
 */
export interface MetricsSummary {
  genetic: {
    totalGenerations: number;
    bestFitness: number;
    convergenceRate: number;
    diversityScore: number;
  };
  thinking: {
    totalProcesses: number;
    averageSteps: number;
    averageImprovement: number;
    tokensPerSecond: number;
  };
  hybrid: {
    synergy: number;
    totalImprovementScore: number;
  };
}