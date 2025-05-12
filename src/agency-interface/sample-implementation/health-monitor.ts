/**
 * HealthMonitor Class
 * 
 * Core component of the self-healing system responsible for monitoring
 * the health of various system components and triggering recovery actions
 * when issues are detected.
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';

// Health status types
export enum HealthStatusType {
  HEALTHY = 'HEALTHY',
  DEGRADED = 'DEGRADED',
  UNHEALTHY = 'UNHEALTHY',
  UNKNOWN = 'UNKNOWN'
}

// Component metadata
export interface ComponentMetadata {
  name: string;
  type: string;
  description?: string;
  attributes: Record<string, any>;
}

// Health status
export interface HealthStatus {
  type: HealthStatusType;
  message?: string;
  timestamp: Date;
  metrics?: Record<string, any>;
}

// Component health
export interface ComponentHealth {
  id: string;
  metadata: ComponentMetadata;
  status: HealthStatus;
  history: HealthStatus[];
  lastUpdated: Date;
}

// Health dashboard
export interface HealthDashboard {
  overallHealth: HealthStatusType;
  componentCount: number;
  healthyCount: number;
  degradedCount: number;
  unhealthyCount: number;
  components: ComponentHealth[];
  lastUpdated: Date;
}

// Health monitoring options
export interface HealthMonitorOptions {
  historySize?: number;
  checkInterval?: number;
  autoRecover?: boolean;
}

// Health events
export enum HealthEvent {
  COMPONENT_REGISTERED = 'component.registered',
  COMPONENT_UNREGISTERED = 'component.unregistered',
  STATUS_CHANGED = 'status.changed',
  HEALTH_CHECK = 'health.check',
  RECOVERY_STARTED = 'recovery.started',
  RECOVERY_COMPLETED = 'recovery.completed',
}

/**
 * HealthMonitor class for tracking component health
 */
export class HealthMonitor extends EventEmitter {
  private components: Map<string, ComponentHealth> = new Map();
  private options: Required<HealthMonitorOptions>;
  private checkIntervalId?: NodeJS.Timeout;
  private recoveryInProgress: Set<string> = new Set();

  /**
   * Create a new HealthMonitor
   */
  constructor(options: HealthMonitorOptions = {}) {
    super();
    this.options = {
      historySize: options.historySize ?? 10,
      checkInterval: options.checkInterval ?? 60000, // 1 minute
      autoRecover: options.autoRecover ?? true,
    };

    // Start health check interval if interval is greater than 0
    if (this.options.checkInterval > 0) {
      this.startHealthCheck();
    }
  }

  /**
   * Start the health check interval
   */
  public startHealthCheck(): void {
    if (this.checkIntervalId) {
      clearInterval(this.checkIntervalId);
    }

    this.checkIntervalId = setInterval(() => {
      this.emit(HealthEvent.HEALTH_CHECK);
      this.checkAllComponentsHealth();
    }, this.options.checkInterval);
  }

  /**
   * Stop the health check interval
   */
  public stopHealthCheck(): void {
    if (this.checkIntervalId) {
      clearInterval(this.checkIntervalId);
      this.checkIntervalId = undefined;
    }
  }

  /**
   * Register a new component for health monitoring
   */
  public registerComponent(
    componentId: string, 
    metadata: ComponentMetadata,
    initialStatus: HealthStatus = {
      type: HealthStatusType.UNKNOWN,
      timestamp: new Date(),
    }
  ): void {
    if (this.components.has(componentId)) {
      throw new Error(`Component with ID ${componentId} is already registered`);
    }

    const componentHealth: ComponentHealth = {
      id: componentId,
      metadata,
      status: initialStatus,
      history: [initialStatus],
      lastUpdated: new Date(),
    };

    this.components.set(componentId, componentHealth);
    this.emit(HealthEvent.COMPONENT_REGISTERED, componentHealth);
  }

  /**
   * Unregister a component from health monitoring
   */
  public unregisterComponent(componentId: string): void {
    if (!this.components.has(componentId)) {
      throw new Error(`Component with ID ${componentId} is not registered`);
    }

    const component = this.components.get(componentId)!;
    this.components.delete(componentId);
    this.emit(HealthEvent.COMPONENT_UNREGISTERED, component);
  }

  /**
   * Update the health status of a component
   */
  public updateComponentStatus(
    componentId: string,
    status: HealthStatus
  ): void {
    if (!this.components.has(componentId)) {
      throw new Error(`Component with ID ${componentId} is not registered`);
    }

    const component = this.components.get(componentId)!;
    const oldStatus = component.status;

    // Update status
    component.status = status;
    component.lastUpdated = new Date();

    // Add to history, keeping only the configured number of entries
    component.history.unshift(status);
    if (component.history.length > this.options.historySize) {
      component.history = component.history.slice(0, this.options.historySize);
    }

    // Update the component in the map
    this.components.set(componentId, component);

    // Emit status changed event if the status type has changed
    if (oldStatus.type !== status.type) {
      this.emit(HealthEvent.STATUS_CHANGED, {
        component,
        oldStatus,
        newStatus: status,
      });

      // If status changed to unhealthy and auto-recover is enabled, trigger recovery
      if (
        status.type === HealthStatusType.UNHEALTHY && 
        this.options.autoRecover &&
        !this.recoveryInProgress.has(componentId)
      ) {
        this.triggerRecovery(componentId);
      }
    }
  }

  /**
   * Get the health status of a component
   */
  public getComponentStatus(componentId: string): HealthStatus {
    if (!this.components.has(componentId)) {
      throw new Error(`Component with ID ${componentId} is not registered`);
    }

    return this.components.get(componentId)!.status;
  }

  /**
   * Get a component's full health information
   */
  public getComponent(componentId: string): ComponentHealth {
    if (!this.components.has(componentId)) {
      throw new Error(`Component with ID ${componentId} is not registered`);
    }

    return this.components.get(componentId)!;
  }

  /**
   * Get all registered components
   */
  public getAllComponents(): ComponentHealth[] {
    return Array.from(this.components.values());
  }

  /**
   * Check health of all components
   */
  public checkAllComponentsHealth(): void {
    for (const componentId of this.components.keys()) {
      this.checkComponentHealth(componentId);
    }
  }

  /**
   * Check health of a specific component
   * This method would typically call out to the component's health check endpoint
   * or use metrics to determine health. For this example, it's a placeholder.
   */
  public checkComponentHealth(componentId: string): void {
    // In a real implementation, this would call the component's health check
    // or analyze metrics to determine health status.
    
    // For this example, we'll just leave the current status unchanged
    const component = this.getComponent(componentId);
    
    // Update the last check timestamp
    this.updateComponentStatus({
      ...component.status,
      timestamp: new Date(),
    }, componentId);
  }

  /**
   * Trigger recovery for a component
   */
  public async triggerRecovery(componentId: string): Promise<boolean> {
    if (!this.components.has(componentId)) {
      throw new Error(`Component with ID ${componentId} is not registered`);
    }

    const component = this.components.get(componentId)!;

    // Don't start recovery if already in progress
    if (this.recoveryInProgress.has(componentId)) {
      return false;
    }

    try {
      // Mark recovery as in progress
      this.recoveryInProgress.add(componentId);
      
      // Emit recovery started event
      this.emit(HealthEvent.RECOVERY_STARTED, { componentId, component });
      
      // In a real implementation, this would call out to specific recovery strategies
      // For this example, we'll simulate a successful recovery
      
      // Wait a moment to simulate recovery taking time
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update status to healthy
      this.updateComponentStatus({
        type: HealthStatusType.HEALTHY,
        message: 'Recovered automatically',
        timestamp: new Date(),
      }, componentId);
      
      // Emit recovery completed event
      this.emit(HealthEvent.RECOVERY_COMPLETED, { 
        componentId, 
        component: this.getComponent(componentId),
        success: true 
      });
      
      return true;
    } catch (error) {
      // Emit recovery completed event with failure
      this.emit(HealthEvent.RECOVERY_COMPLETED, { 
        componentId, 
        component: this.getComponent(componentId),
        success: false,
        error
      });
      
      return false;
    } finally {
      // Mark recovery as complete
      this.recoveryInProgress.delete(componentId);
    }
  }

  /**
   * Get a health dashboard summary
   */
  public getHealthDashboard(): HealthDashboard {
    const components = this.getAllComponents();
    
    const healthyCount = components.filter(c => c.status.type === HealthStatusType.HEALTHY).length;
    const degradedCount = components.filter(c => c.status.type === HealthStatusType.DEGRADED).length;
    const unhealthyCount = components.filter(c => c.status.type === HealthStatusType.UNHEALTHY).length;
    
    // Determine overall health
    let overallHealth = HealthStatusType.HEALTHY;
    if (unhealthyCount > 0) {
      overallHealth = HealthStatusType.UNHEALTHY;
    } else if (degradedCount > 0) {
      overallHealth = HealthStatusType.DEGRADED;
    } else if (components.length === 0) {
      overallHealth = HealthStatusType.UNKNOWN;
    }
    
    return {
      overallHealth,
      componentCount: components.length,
      healthyCount,
      degradedCount,
      unhealthyCount,
      components,
      lastUpdated: new Date(),
    };
  }
}

/**
 * CircuitBreaker class for protecting against cascading failures
 */
export class CircuitBreaker {
  // Circuit states
  public static readonly CLOSED = 'CLOSED';  // Working normally
  public static readonly OPEN = 'OPEN';      // Not allowing calls
  public static readonly HALF_OPEN = 'HALF_OPEN'; // Testing if working
  
  private state: string = CircuitBreaker.CLOSED;
  private failures: number = 0;
  private lastFailure?: Date;
  private lastSuccess?: Date;
  private resetTimeout?: NodeJS.Timeout;
  
  private readonly id: string;
  private readonly failureThreshold: number;
  private readonly resetTimeoutMs: number;
  private readonly monitorCallback?: (state: string) => void;

  /**
   * Create a new CircuitBreaker
   */
  constructor({
    id = uuidv4(),
    failureThreshold = 3,
    resetTimeoutMs = 10000,
    monitorCallback,
  }: {
    id?: string;
    failureThreshold?: number;
    resetTimeoutMs?: number;
    monitorCallback?: (state: string) => void;
  } = {}) {
    this.id = id;
    this.failureThreshold = failureThreshold;
    this.resetTimeoutMs = resetTimeoutMs;
    this.monitorCallback = monitorCallback;
  }

  /**
   * Execute a function with circuit breaker protection
   */
  public async execute<T>(func: () => Promise<T>): Promise<T> {
    if (this.state === CircuitBreaker.OPEN) {
      throw new Error(`Circuit ${this.id} is OPEN - refusing to execute`);
    }
    
    try {
      const result = await func();
      this.recordSuccess();
      return result;
    } catch (error) {
      this.recordFailure();
      throw error;
    }
  }

  /**
   * Record a successful execution
   */
  private recordSuccess(): void {
    this.failures = 0;
    this.lastSuccess = new Date();
    
    if (this.state === CircuitBreaker.HALF_OPEN) {
      this.setState(CircuitBreaker.CLOSED);
      if (this.resetTimeout) {
        clearTimeout(this.resetTimeout);
        this.resetTimeout = undefined;
      }
    }
  }

  /**
   * Record a failed execution
   */
  private recordFailure(): void {
    this.failures += 1;
    this.lastFailure = new Date();
    
    if (this.failures >= this.failureThreshold && this.state === CircuitBreaker.CLOSED) {
      this.trip();
    }
  }

  /**
   * Trip the circuit breaker (change to OPEN state)
   */
  private trip(): void {
    this.setState(CircuitBreaker.OPEN);
    
    // Set timeout to try again (move to HALF_OPEN after resetTimeoutMs)
    this.resetTimeout = setTimeout(() => {
      this.setState(CircuitBreaker.HALF_OPEN);
    }, this.resetTimeoutMs);
  }

  /**
   * Set the circuit breaker state
   */
  private setState(state: string): void {
    this.state = state;
    if (this.monitorCallback) {
      this.monitorCallback(state);
    }
  }

  /**
   * Get the current state
   */
  public getState(): string {
    return this.state;
  }

  /**
   * Get failures count
   */
  public getFailureCount(): number {
    return this.failures;
  }

  /**
   * Reset the circuit breaker to CLOSED state
   */
  public reset(): void {
    if (this.resetTimeout) {
      clearTimeout(this.resetTimeout);
      this.resetTimeout = undefined;
    }
    
    this.failures = 0;
    this.setState(CircuitBreaker.CLOSED);
  }
}

/**
 * RecoveryStrategy interface
 */
export interface RecoveryStrategy {
  /**
   * Check if this strategy can recover the given component
   */
  canRecover(componentId: string, status: HealthStatus): boolean;
  
  /**
   * Attempt to recover the component
   */
  recover(componentId: string, component: ComponentHealth): Promise<boolean>;
}

/**
 * RestartRecoveryStrategy - recovers components by restarting them
 */
export class RestartRecoveryStrategy implements RecoveryStrategy {
  private restartableComponents: Set<string>;
  
  constructor(restartableComponents: string[] = []) {
    this.restartableComponents = new Set(restartableComponents);
  }
  
  public canRecover(componentId: string, status: HealthStatus): boolean {
    return this.restartableComponents.has(componentId) && 
           status.type === HealthStatusType.UNHEALTHY;
  }
  
  public async recover(componentId: string, component: ComponentHealth): Promise<boolean> {
    if (!this.canRecover(componentId, component.status)) {
      return false;
    }
    
    console.log(`Restarting component ${componentId}`);
    
    // In a real implementation, this would actually restart the component
    // For this example, we'll just simulate a restart
    
    // Simulate restart delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Return success
    return true;
  }
}

/**
 * ReconfigureRecoveryStrategy - recovers components by reconfiguring them
 */
export class ReconfigureRecoveryStrategy implements RecoveryStrategy {
  public canRecover(componentId: string, status: HealthStatus): boolean {
    // In a real implementation, this would check if the component is
    // reconfigurable and if the status indicates a configuration issue
    return status.type === HealthStatusType.DEGRADED;
  }
  
  public async recover(componentId: string, component: ComponentHealth): Promise<boolean> {
    if (!this.canRecover(componentId, component.status)) {
      return false;
    }
    
    console.log(`Reconfiguring component ${componentId}`);
    
    // In a real implementation, this would actually reconfigure the component
    // For this example, we'll just simulate reconfiguration
    
    // Simulate reconfiguration delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Return success
    return true;
  }
}

/**
 * FailoverRecoveryStrategy - recovers components by activating a failover
 */
export class FailoverRecoveryStrategy implements RecoveryStrategy {
  private failoverMappings: Map<string, string>;
  
  constructor(failoverMappings: Record<string, string> = {}) {
    this.failoverMappings = new Map(Object.entries(failoverMappings));
  }
  
  public canRecover(componentId: string, status: HealthStatus): boolean {
    return this.failoverMappings.has(componentId) && 
           status.type === HealthStatusType.UNHEALTHY;
  }
  
  public async recover(componentId: string, component: ComponentHealth): Promise<boolean> {
    if (!this.canRecover(componentId, component.status)) {
      return false;
    }
    
    const failoverComponentId = this.failoverMappings.get(componentId)!;
    console.log(`Activating failover from ${componentId} to ${failoverComponentId}`);
    
    // In a real implementation, this would actually activate the failover
    // For this example, we'll just simulate failover activation
    
    // Simulate failover delay
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Return success
    return true;
  }
}

/**
 * RecoveryRegistry - manages available recovery strategies
 */
export class RecoveryRegistry {
  private strategies: RecoveryStrategy[] = [];
  
  /**
   * Register a recovery strategy
   */
  public registerStrategy(strategy: RecoveryStrategy): void {
    this.strategies.push(strategy);
  }
  
  /**
   * Find an appropriate recovery strategy for a component
   */
  public findStrategy(componentId: string, status: HealthStatus): RecoveryStrategy | null {
    for (const strategy of this.strategies) {
      if (strategy.canRecover(componentId, status)) {
        return strategy;
      }
    }
    
    return null;
  }
  
  /**
   * Get all registered strategies
   */
  public getAllStrategies(): RecoveryStrategy[] {
    return [...this.strategies];
  }
}

/**
 * SelfHealingSystem - combines all components for self-healing
 */
export class SelfHealingSystem {
  private readonly healthMonitor: HealthMonitor;
  private readonly recoveryRegistry: RecoveryRegistry;
  private readonly circuitBreakers: Map<string, CircuitBreaker> = new Map();
  
  /**
   * Create a new SelfHealingSystem
   */
  constructor(options: HealthMonitorOptions = {}) {
    this.healthMonitor = new HealthMonitor(options);
    this.recoveryRegistry = new RecoveryRegistry();
    
    // Setup event handlers for auto recovery
    this.healthMonitor.on(HealthEvent.STATUS_CHANGED, async (event) => {
      if (event.newStatus.type === HealthStatusType.UNHEALTHY) {
        await this.attemptRecovery(event.component.id);
      }
    });
  }
  
  /**
   * Get the health monitor
   */
  public getHealthMonitor(): HealthMonitor {
    return this.healthMonitor;
  }
  
  /**
   * Get the recovery registry
   */
  public getRecoveryRegistry(): RecoveryRegistry {
    return this.recoveryRegistry;
  }
  
  /**
   * Register a circuit breaker
   */
  public registerCircuitBreaker(name: string, options: any = {}): CircuitBreaker {
    const circuitBreaker = new CircuitBreaker({
      id: name,
      ...options,
      monitorCallback: (state) => {
        // Update component health based on circuit breaker state
        if (this.healthMonitor.getComponent(name)) {
          const healthStatus: HealthStatus = {
            type: state === CircuitBreaker.CLOSED 
              ? HealthStatusType.HEALTHY 
              : state === CircuitBreaker.OPEN 
                ? HealthStatusType.UNHEALTHY 
                : HealthStatusType.DEGRADED,
            message: `Circuit breaker is ${state}`,
            timestamp: new Date(),
          };
          
          this.healthMonitor.updateComponentStatus(name, healthStatus);
        }
      }
    });
    
    this.circuitBreakers.set(name, circuitBreaker);
    return circuitBreaker;
  }
  
  /**
   * Get a circuit breaker by name
   */
  public getCircuitBreaker(name: string): CircuitBreaker | undefined {
    return this.circuitBreakers.get(name);
  }
  
  /**
   * Attempt to recover a component
   */
  public async attemptRecovery(componentId: string): Promise<boolean> {
    const component = this.healthMonitor.getComponent(componentId);
    const strategy = this.recoveryRegistry.findStrategy(componentId, component.status);
    
    if (!strategy) {
      console.log(`No recovery strategy found for component ${componentId}`);
      return false;
    }
    
    try {
      const success = await strategy.recover(componentId, component);
      
      if (success) {
        // Update component status
        this.healthMonitor.updateComponentStatus({
          type: HealthStatusType.HEALTHY,
          message: 'Recovered successfully',
          timestamp: new Date(),
        }, componentId);
      }
      
      return success;
    } catch (error) {
      console.error(`Error recovering component ${componentId}:`, error);
      return false;
    }
  }
  
  /**
   * Initialize the self-healing system with standard recovery strategies
   */
  public initializeWithDefaults(): void {
    // Register standard recovery strategies
    this.recoveryRegistry.registerStrategy(new RestartRecoveryStrategy([
      'web-server',
      'api-server',
      'database-connection-pool'
    ]));
    
    this.recoveryRegistry.registerStrategy(new ReconfigureRecoveryStrategy());
    
    this.recoveryRegistry.registerStrategy(new FailoverRecoveryStrategy({
      'primary-database': 'secondary-database',
      'primary-cache': 'secondary-cache'
    }));
  }
}

// Example usage:
async function example() {
  const selfHealing = new SelfHealingSystem({
    checkInterval: 30000, // Check every 30 seconds
    autoRecover: true
  });
  
  // Initialize with default strategies
  selfHealing.initializeWithDefaults();
  
  const healthMonitor = selfHealing.getHealthMonitor();
  
  // Register some components
  healthMonitor.registerComponent('web-server', {
    name: 'Web Server',
    type: 'server',
    description: 'Main web server',
    attributes: { port: 8080 }
  });
  
  healthMonitor.registerComponent('api-server', {
    name: 'API Server',
    type: 'server',
    description: 'REST API server',
    attributes: { port: 3000 }
  });
  
  healthMonitor.registerComponent('database', {
    name: 'Database',
    type: 'database',
    description: 'PostgreSQL database',
    attributes: { host: 'localhost', port: 5432 }
  });
  
  // Register circuit breakers
  selfHealing.registerCircuitBreaker('api-client', {
    failureThreshold: 3,
    resetTimeoutMs: 5000
  });
  
  selfHealing.registerCircuitBreaker('database-client', {
    failureThreshold: 5,
    resetTimeoutMs: 10000
  });
  
  // Simulate a component failing
  console.log('Simulating API server failure...');
  
  healthMonitor.updateComponentStatus({
    type: HealthStatusType.UNHEALTHY,
    message: 'Connection timeout',
    timestamp: new Date(),
  }, 'api-server');
  
  // Wait for recovery to happen
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Print health dashboard
  console.log('Health Dashboard:', JSON.stringify(healthMonitor.getHealthDashboard(), null, 2));
  
  // Simulate circuit breaker tripping
  const apiCircuitBreaker = selfHealing.getCircuitBreaker('api-client')!;
  
  try {
    await apiCircuitBreaker.execute(async () => {
      throw new Error('API request failed');
    });
  } catch (e) {
    console.log('API request failed, recorded failure');
  }
  
  try {
    await apiCircuitBreaker.execute(async () => {
      throw new Error('API request failed');
    });
  } catch (e) {
    console.log('API request failed, recorded failure');
  }
  
  try {
    await apiCircuitBreaker.execute(async () => {
      throw new Error('API request failed');
    });
  } catch (e) {
    console.log('API request failed, recorded failure');
  }
  
  console.log('Circuit breaker state:', apiCircuitBreaker.getState());
  
  try {
    await apiCircuitBreaker.execute(async () => {
      return 'This should not be called';
    });
  } catch (e) {
    console.log('Circuit is open, request blocked');
  }
  
  // Wait for circuit to go to half-open
  console.log('Waiting for circuit breaker reset timeout...');
  await new Promise(resolve => setTimeout(resolve, 10000));
  
  console.log('Circuit breaker state:', apiCircuitBreaker.getState());
  
  // Try a successful request
  try {
    const result = await apiCircuitBreaker.execute(async () => {
      return 'Request succeeded';
    });
    console.log('Request result:', result);
  } catch (e) {
    console.log('Request failed:', e);
  }
  
  console.log('Circuit breaker state:', apiCircuitBreaker.getState());
  
  // Print final health dashboard
  console.log('Final Health Dashboard:', JSON.stringify(healthMonitor.getHealthDashboard(), null, 2));
}

// Uncomment to run the example
// example().catch(console.error);