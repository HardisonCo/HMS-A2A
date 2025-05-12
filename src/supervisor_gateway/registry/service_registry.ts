/**
 * Service Registry
 *
 * This class implements a centralized registry for service discovery,
 * registration, and health monitoring across the system.
 */

// Service status enum
export enum ServiceStatus {
  UP = 'UP',
  DOWN = 'DOWN',
  DEGRADED = 'DEGRADED',
  MAINTENANCE = 'MAINTENANCE',
  UNKNOWN = 'UNKNOWN'
}

// Service health check result interface
export interface HealthCheckResult {
  status: ServiceStatus;
  timestamp: number;
  details: {
    [key: string]: {
      status: ServiceStatus;
      message?: string;
      metrics?: {
        [key: string]: number;
      };
    };
  };
  version: string;
}

// Service instance interface
export interface ServiceInstance {
  id: string;
  name: string;
  description?: string;
  version: string;
  baseUrl: string;
  endpoints: {
    [key: string]: string;
  };
  healthCheckPath?: string;
  metadata: {
    [key: string]: any;
  };
  status: ServiceStatus;
  registeredAt: number;
  lastUpdatedAt: number;
  lastHealthCheck?: HealthCheckResult;
  dependencies?: string[];
  capabilities?: string[];
  tags?: string[];
}

// Service search criteria interface
export interface ServiceSearchCriteria {
  name?: string;
  status?: ServiceStatus;
  version?: string;
  tags?: string[];
  capabilities?: string[];
  metadata?: {
    [key: string]: any;
  };
}

// Registry change event types
export enum RegistryEventType {
  SERVICE_REGISTERED = 'SERVICE_REGISTERED',
  SERVICE_UPDATED = 'SERVICE_UPDATED',
  SERVICE_DEREGISTERED = 'SERVICE_DEREGISTERED',
  SERVICE_STATUS_CHANGED = 'SERVICE_STATUS_CHANGED'
}

// Registry change event interface
export interface RegistryEvent {
  type: RegistryEventType;
  serviceId: string;
  timestamp: number;
  data: any;
}

// Registry subscription interface
export interface RegistrySubscription {
  id: string;
  callback: (event: RegistryEvent) => void;
  filters?: {
    eventTypes?: RegistryEventType[];
    serviceIds?: string[];
    serviceNames?: string[];
  };
}

/**
 * Service Registry class
 * 
 * A centralized registry for service discovery, registration,
 * and health monitoring. It provides:
 * 
 * - Service registration and deregistration
 * - Service discovery
 * - Health check coordination
 * - Event notifications for registry changes
 * - Metadata management for services
 */
export class ServiceRegistry {
  private services: Map<string, ServiceInstance> = new Map();
  private subscriptions: Map<string, RegistrySubscription> = new Map();
  private healthCheckInterval: NodeJS.Timeout | null = null;
  private readonly defaultHealthCheckIntervalMs: number = 60000; // 1 minute
  
  constructor() {
    // Start health check monitoring
    this.startHealthChecks();
  }

  /**
   * Registers a new service instance
   * 
   * @param service Service instance to register
   * @returns The registered service with generated ID if one wasn't provided
   */
  public registerService(service: Omit<ServiceInstance, 'id' | 'registeredAt' | 'lastUpdatedAt'>): ServiceInstance {
    // Generate service ID if not provided
    const serviceId = service.id || `service-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const now = Date.now();
    
    // Create the full service instance
    const newService: ServiceInstance = {
      ...(service as any),
      id: serviceId,
      status: service.status || ServiceStatus.UNKNOWN,
      registeredAt: now,
      lastUpdatedAt: now
    };
    
    // Store in registry
    this.services.set(serviceId, newService);
    
    // Emit registration event
    this.emitEvent({
      type: RegistryEventType.SERVICE_REGISTERED,
      serviceId,
      timestamp: now,
      data: newService
    });
    
    return newService;
  }
  
  /**
   * Updates an existing service
   * 
   * @param serviceId ID of the service to update
   * @param updates Partial service data to update
   * @returns Updated service instance or null if not found
   */
  public updateService(serviceId: string, updates: Partial<ServiceInstance>): ServiceInstance | null {
    if (!this.services.has(serviceId)) {
      return null;
    }
    
    const existingService = this.services.get(serviceId)!;
    const now = Date.now();
    
    // Create updated service
    const updatedService: ServiceInstance = {
      ...existingService,
      ...updates,
      id: serviceId, // Ensure ID can't be changed
      registeredAt: existingService.registeredAt, // Preserve original registration
      lastUpdatedAt: now
    };
    
    // Store updated service
    this.services.set(serviceId, updatedService);
    
    // Emit update event
    this.emitEvent({
      type: RegistryEventType.SERVICE_UPDATED,
      serviceId,
      timestamp: now,
      data: updatedService
    });
    
    return updatedService;
  }
  
  /**
   * Deregisters a service
   * 
   * @param serviceId ID of the service to deregister
   * @returns True if service was found and deregistered, false otherwise
   */
  public deregisterService(serviceId: string): boolean {
    if (!this.services.has(serviceId)) {
      return false;
    }
    
    const service = this.services.get(serviceId)!;
    this.services.delete(serviceId);
    
    // Emit deregistration event
    this.emitEvent({
      type: RegistryEventType.SERVICE_DEREGISTERED,
      serviceId,
      timestamp: Date.now(),
      data: service
    });
    
    return true;
  }
  
  /**
   * Gets a service by its ID
   * 
   * @param serviceId ID of the service to retrieve
   * @returns Service instance or null if not found
   */
  public getService(serviceId: string): ServiceInstance | null {
    return this.services.has(serviceId) ? this.services.get(serviceId)! : null;
  }
  
  /**
   * Searches for services matching the given criteria
   * 
   * @param criteria Search criteria to filter services
   * @returns Array of matching service instances
   */
  public findServices(criteria: ServiceSearchCriteria): ServiceInstance[] {
    return Array.from(this.services.values()).filter(service => {
      // Check service name
      if (criteria.name && !service.name.includes(criteria.name)) {
        return false;
      }
      
      // Check service status
      if (criteria.status && service.status !== criteria.status) {
        return false;
      }
      
      // Check service version
      if (criteria.version && service.version !== criteria.version) {
        return false;
      }
      
      // Check service tags
      if (criteria.tags && criteria.tags.length > 0) {
        if (!service.tags || !criteria.tags.every(tag => service.tags!.includes(tag))) {
          return false;
        }
      }
      
      // Check service capabilities
      if (criteria.capabilities && criteria.capabilities.length > 0) {
        if (!service.capabilities || !criteria.capabilities.every(cap => service.capabilities!.includes(cap))) {
          return false;
        }
      }
      
      // Check metadata
      if (criteria.metadata) {
        const metadataKeys = Object.keys(criteria.metadata);
        if (metadataKeys.length > 0) {
          for (const key of metadataKeys) {
            if (!service.metadata || service.metadata[key] !== criteria.metadata[key]) {
              return false;
            }
          }
        }
      }
      
      return true;
    });
  }
  
  /**
   * Updates the status of a service
   * 
   * @param serviceId ID of the service to update
   * @param status New status
   * @param healthCheck Optional health check result
   * @returns Updated service or null if not found
   */
  public updateServiceStatus(
    serviceId: string, 
    status: ServiceStatus, 
    healthCheck?: HealthCheckResult
  ): ServiceInstance | null {
    if (!this.services.has(serviceId)) {
      return null;
    }
    
    const service = this.services.get(serviceId)!;
    const previousStatus = service.status;
    const now = Date.now();
    
    // Update service with new status and optional health check
    const updatedService: ServiceInstance = {
      ...service,
      status,
      lastUpdatedAt: now,
      lastHealthCheck: healthCheck || service.lastHealthCheck
    };
    
    this.services.set(serviceId, updatedService);
    
    // Only emit status change event if status actually changed
    if (previousStatus !== status) {
      this.emitEvent({
        type: RegistryEventType.SERVICE_STATUS_CHANGED,
        serviceId,
        timestamp: now,
        data: {
          service: updatedService,
          previousStatus,
          newStatus: status
        }
      });
    }
    
    return updatedService;
  }
  
  /**
   * Performs a health check on a specific service
   * 
   * @param serviceId ID of the service to check
   * @returns Promise resolving to the health check result
   */
  public async checkServiceHealth(serviceId: string): Promise<HealthCheckResult | null> {
    const service = this.getService(serviceId);
    if (!service || !service.healthCheckPath) {
      return null;
    }
    
    try {
      // Construct health check URL
      const healthCheckUrl = `${service.baseUrl}${service.healthCheckPath}`;
      
      // Perform HTTP request to health check endpoint
      // In a real implementation, this would use fetch or another HTTP client
      // For this implementation, we'll simulate a response
      const simulatedResponse = await this.simulateHealthCheck(service);
      
      // Update service with health check result
      this.updateServiceStatus(serviceId, simulatedResponse.status, simulatedResponse);
      
      return simulatedResponse;
    } catch (error) {
      // Handle health check failure
      const failedHealthCheck: HealthCheckResult = {
        status: ServiceStatus.DOWN,
        timestamp: Date.now(),
        details: {
          error: {
            status: ServiceStatus.DOWN,
            message: `Health check failed: ${error.message || 'Unknown error'}`
          }
        },
        version: service.version
      };
      
      // Update service with failed health check
      this.updateServiceStatus(serviceId, ServiceStatus.DOWN, failedHealthCheck);
      
      return failedHealthCheck;
    }
  }
  
  /**
   * Subscribe to registry events
   * 
   * @param callback Function to call when events occur
   * @param filters Optional filters to limit which events trigger the callback
   * @returns Subscription ID used to unsubscribe
   */
  public subscribe(
    callback: (event: RegistryEvent) => void,
    filters?: {
      eventTypes?: RegistryEventType[];
      serviceIds?: string[];
      serviceNames?: string[];
    }
  ): string {
    const subscriptionId = `subscription-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    this.subscriptions.set(subscriptionId, {
      id: subscriptionId,
      callback,
      filters
    });
    
    return subscriptionId;
  }
  
  /**
   * Unsubscribe from registry events
   * 
   * @param subscriptionId ID of the subscription to remove
   * @returns True if subscription was found and removed, false otherwise
   */
  public unsubscribe(subscriptionId: string): boolean {
    if (!this.subscriptions.has(subscriptionId)) {
      return false;
    }
    
    this.subscriptions.delete(subscriptionId);
    return true;
  }
  
  /**
   * Start periodic health checks for all registered services
   * 
   * @param intervalMs Interval between health checks in milliseconds
   */
  public startHealthChecks(intervalMs: number = this.defaultHealthCheckIntervalMs): void {
    // Clear any existing interval
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    
    // Start new interval
    this.healthCheckInterval = setInterval(() => {
      this.checkAllServicesHealth();
    }, intervalMs);
  }
  
  /**
   * Stop periodic health checks
   */
  public stopHealthChecks(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }
  
  /**
   * Get all registered services
   * 
   * @returns Array of all service instances
   */
  public getAllServices(): ServiceInstance[] {
    return Array.from(this.services.values());
  }
  
  /**
   * Get registry statistics
   * 
   * @returns Registry statistics
   */
  public getStatistics(): {
    totalServices: number;
    servicesByStatus: { [status in ServiceStatus]: number };
    healthyServicePercentage: number;
  } {
    const services = Array.from(this.services.values());
    const totalServices = services.length;
    
    // Count services by status
    const servicesByStatus = services.reduce((counts, service) => {
      counts[service.status] = (counts[service.status] || 0) + 1;
      return counts;
    }, {} as { [status in ServiceStatus]: number });
    
    // Ensure all statuses are represented
    Object.values(ServiceStatus).forEach(status => {
      if (!servicesByStatus[status]) {
        servicesByStatus[status] = 0;
      }
    });
    
    // Calculate healthy percentage
    const healthyServices = (servicesByStatus[ServiceStatus.UP] || 0);
    const healthyServicePercentage = totalServices > 0 
      ? (healthyServices / totalServices) * 100 
      : 0;
    
    return {
      totalServices,
      servicesByStatus,
      healthyServicePercentage
    };
  }
  
  /**
   * Generate dependency graph for registered services
   * 
   * @returns Object representing service dependencies
   */
  public generateDependencyGraph(): {
    nodes: { id: string; name: string; status: ServiceStatus }[];
    edges: { source: string; target: string }[];
  } {
    const services = Array.from(this.services.values());
    
    // Create nodes
    const nodes = services.map(service => ({
      id: service.id,
      name: service.name,
      status: service.status
    }));
    
    // Create edges
    const edges: { source: string; target: string }[] = [];
    
    services.forEach(service => {
      if (service.dependencies && service.dependencies.length > 0) {
        service.dependencies.forEach(dependencyId => {
          if (this.services.has(dependencyId)) {
            edges.push({
              source: service.id,
              target: dependencyId
            });
          }
        });
      }
    });
    
    return { nodes, edges };
  }
  
  /**
   * Clean up resources when registry is no longer needed
   */
  public destroy(): void {
    this.stopHealthChecks();
    this.services.clear();
    this.subscriptions.clear();
  }
  
  // Private methods
  
  /**
   * Checks health for all registered services that have a health check path
   */
  private async checkAllServicesHealth(): Promise<void> {
    const serviceIds = Array.from(this.services.keys()).filter(
      id => this.services.get(id)!.healthCheckPath
    );
    
    // Run health checks in parallel
    await Promise.all(
      serviceIds.map(id => this.checkServiceHealth(id))
    );
  }
  
  /**
   * Simulates a health check for testing purposes
   * 
   * @param service Service to check
   * @returns Simulated health check result
   */
  private async simulateHealthCheck(service: ServiceInstance): Promise<HealthCheckResult> {
    // In a real implementation, this would call the actual health check endpoint
    // For simulation, we'll randomly assign statuses with a bias toward UP
    
    // 80% chance of UP, 10% DEGRADED, 5% DOWN, 5% MAINTENANCE
    const random = Math.random();
    let status: ServiceStatus;
    
    if (random < 0.8) {
      status = ServiceStatus.UP;
    } else if (random < 0.9) {
      status = ServiceStatus.DEGRADED;
    } else if (random < 0.95) {
      status = ServiceStatus.DOWN;
    } else {
      status = ServiceStatus.MAINTENANCE;
    }
    
    // Generate simulated component statuses
    const details: HealthCheckResult['details'] = {
      database: {
        status: Math.random() < 0.9 ? ServiceStatus.UP : ServiceStatus.DEGRADED,
        message: 'Database connection pool is healthy',
        metrics: {
          connectionPoolSize: Math.floor(Math.random() * 50) + 10,
          activeConnections: Math.floor(Math.random() * 20),
          queryResponseTimeMs: Math.floor(Math.random() * 50)
        }
      },
      cache: {
        status: Math.random() < 0.95 ? ServiceStatus.UP : ServiceStatus.DEGRADED,
        message: 'Cache system is operating normally',
        metrics: {
          hitRatio: Math.random() * 0.9 + 0.1,
          itemCount: Math.floor(Math.random() * 1000),
          evictionCount: Math.floor(Math.random() * 10)
        }
      },
      api: {
        status: status,
        message: status === ServiceStatus.UP 
          ? 'API endpoints are responsive' 
          : 'API is experiencing slowdowns',
        metrics: {
          requestsPerMinute: Math.floor(Math.random() * 1000),
          averageResponseTimeMs: Math.floor(Math.random() * 200),
          errorRate: Math.random() * (status === ServiceStatus.UP ? 0.01 : 0.1)
        }
      }
    };
    
    return {
      status,
      timestamp: Date.now(),
      details,
      version: service.version
    };
  }
  
  /**
   * Emits an event to all matching subscribers
   * 
   * @param event Event to emit
   */
  private emitEvent(event: RegistryEvent): void {
    for (const subscription of this.subscriptions.values()) {
      // Skip if subscription has event type filters and this event type isn't included
      if (subscription.filters?.eventTypes && 
          !subscription.filters.eventTypes.includes(event.type)) {
        continue;
      }
      
      // Skip if subscription has service ID filters and this service ID isn't included
      if (subscription.filters?.serviceIds && 
          !subscription.filters.serviceIds.includes(event.serviceId)) {
        continue;
      }
      
      // Skip if subscription has service name filters
      if (subscription.filters?.serviceNames) {
        const service = this.services.get(event.serviceId);
        if (!service || !subscription.filters.serviceNames.includes(service.name)) {
          continue;
        }
      }
      
      // Event passes all filters, call the subscription callback
      try {
        subscription.callback(event);
      } catch (error) {
        console.error(`Error in registry subscription callback (ID: ${subscription.id}):`, error);
      }
    }
  }
}