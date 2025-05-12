/**
 * Health Types
 * 
 * Defines the types and interfaces for the health monitoring system.
 */

import { AgentId } from '../communication/message';

/**
 * Enumeration of health states.
 */
export enum HealthState {
  Healthy = 'healthy',
  Degraded = 'degraded',
  Unhealthy = 'unhealthy'
}

/**
 * Interface for health status information.
 */
export interface HealthStatus {
  /**
   * The ID of the agent this health status is for.
   */
  agentId: AgentId;
  
  /**
   * The current health state of the agent.
   */
  state: HealthState;
  
  /**
   * The timestamp when this health status was generated.
   */
  timestamp: string;
  
  /**
   * Detailed health information.
   */
  details: Record<string, any>;
}

/**
 * Interface for component health check.
 */
export interface ComponentHealth {
  /**
   * The name of the component.
   */
  component: string;
  
  /**
   * The current health state of the component.
   */
  state: HealthState;
  
  /**
   * A message describing the health state.
   */
  message?: string;
  
  /**
   * The timestamp when this health check was performed.
   */
  timestamp: string;
  
  /**
   * Additional details about the component's health.
   */
  details?: Record<string, any>;
}

/**
 * Interface for service health check.
 */
export interface ServiceHealth {
  /**
   * The name of the service.
   */
  service: string;
  
  /**
   * The current health state of the service.
   */
  state: HealthState;
  
  /**
   * The response time of the service in milliseconds.
   */
  responseTime?: number;
  
  /**
   * The uptime of the service in seconds.
   */
  uptime?: number;
  
  /**
   * A message describing the health state.
   */
  message?: string;
  
  /**
   * The timestamp when this health check was performed.
   */
  timestamp: string;
}

/**
 * Interface for resource health check.
 */
export interface ResourceHealth {
  /**
   * The name of the resource.
   */
  resource: string;
  
  /**
   * The type of resource (e.g., "database", "api", "filesystem").
   */
  resourceType: string;
  
  /**
   * The current health state of the resource.
   */
  state: HealthState;
  
  /**
   * The availability percentage of the resource.
   */
  availability?: number;
  
  /**
   * The timestamp when this health check was performed.
   */
  timestamp: string;
  
  /**
   * Additional details about the resource's health.
   */
  details?: Record<string, any>;
}

/**
 * Interface for system health status.
 */
export interface SystemHealthStatus {
  /**
   * The overall health state of the system.
   */
  state: HealthState;
  
  /**
   * The timestamp when this health status was generated.
   */
  timestamp: string;
  
  /**
   * A list of agent health statuses.
   */
  agents: HealthStatus[];
  
  /**
   * A list of component health checks.
   */
  components: ComponentHealth[];
  
  /**
   * A list of service health checks.
   */
  services: ServiceHealth[];
  
  /**
   * A list of resource health checks.
   */
  resources: ResourceHealth[];
}