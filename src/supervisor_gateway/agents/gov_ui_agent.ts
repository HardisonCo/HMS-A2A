/**
 * Gov UI Agent Implementation
 * 
 * This agent specializes in user interface interactions related to government systems.
 * It handles user queries, visualizes policy data, and provides user-friendly interfaces
 * for government information.
 */

import { BaseAgent } from './base_agent';
import { Message } from '../communication/message';
import { KnowledgeBaseManager } from '../knowledge/knowledge_base_manager';
import { Tool } from '../tools/tool_types';

/**
 * Structure for a UI component descriptor
 */
export interface UIComponentDescriptor {
  type: string;
  id: string;
  props: Record<string, any>;
  children?: UIComponentDescriptor[];
}

/**
 * Structure for a visualization descriptor
 */
export interface VisualizationDescriptor {
  type: 'chart' | 'table' | 'tree' | 'timeline' | 'map';
  id: string;
  title: string;
  data: any;
  config: Record<string, any>;
}

/**
 * Specialized agent for government user interface interactions
 */
export class GovUIAgent extends BaseAgent {
  /**
   * Creates a new GovUIAgent
   * 
   * @param id - Unique identifier for this agent
   * @param knowledgeBaseManager - The knowledge base manager for accessing domain knowledge
   */
  constructor(
    id: string, 
    knowledgeBaseManager: KnowledgeBaseManager
  ) {
    super(id, 'gov-ui', knowledgeBaseManager);
    
    // Register specialized UI tools
    this.registerUITools();
  }
  
  /**
   * Registers UI-specific tools
   */
  private registerUITools() {
    // Register visualization generation tool
    this.registerTool({
      id: 'visualization_generator',
      name: 'Visualization Generator Tool',
      description: 'Generates visualization descriptors based on data',
      execute: async (params: any) => {
        return this.generateVisualization(
          params.data,
          params.type,
          params.title,
          params.config
        );
      }
    });
    
    // Register UI component generation tool
    this.registerTool({
      id: 'ui_component_generator',
      name: 'UI Component Generator Tool',
      description: 'Generates UI component descriptors based on content',
      execute: async (params: any) => {
        return this.generateUIComponent(
          params.type,
          params.content,
          params.config
        );
      }
    });
    
    // Register query transformation tool
    this.registerTool({
      id: 'query_transformer',
      name: 'Query Transformer Tool',
      description: 'Transforms natural language queries into structured queries',
      execute: async (params: any) => {
        return this.transformQuery(
          params.query,
          params.context
        );
      }
    });
  }
  
  /**
   * Process incoming messages directed to this agent
   * 
   * @param message - The message to process
   * @returns A response message
   */
  async processMessage(message: Message): Promise<Message> {
    try {
      // Log message receipt
      this.logger.info(`GovUIAgent received message: ${message.messageType} - ${message.content.query_type}`);
      
      // Process based on query type
      switch (message.content.query_type) {
        case 'generate_visualization':
          return this.handleVisualizationRequest(message);
          
        case 'generate_ui_component':
          return this.handleUIComponentRequest(message);
          
        case 'transform_query':
          return this.handleQueryTransformation(message);
          
        case 'policy_visualization':
          return this.handlePolicyVisualization(message);
          
        case 'dashboard_request':
          return this.handleDashboardRequest(message);
          
        default:
          // Fall back to base agent processing for generic queries
          return super.processMessage(message);
      }
    } catch (error) {
      this.logger.error(`Error processing message in GovUIAgent: ${error.message}`);
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Error processing message: ${error.message}`
      );
    }
  }
  
  /**
   * Handles requests to generate visualizations
   */
  private async handleVisualizationRequest(message: Message): Promise<Message> {
    const { data, type, title, config } = message.content.body;
    
    // Validate required parameters
    if (!data || !type) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Visualization generation requires data and type parameters'
      );
    }
    
    try {
      // Generate visualization descriptor
      const visualization = await this.generateVisualization(
        data,
        type,
        title || 'Untitled Visualization',
        config || {}
      );
      
      // Return the visualization descriptor
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { visualization }
      );
    } catch (error) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Visualization generation error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles requests to generate UI components
   */
  private async handleUIComponentRequest(message: Message): Promise<Message> {
    const { type, content, config } = message.content.body;
    
    // Validate required parameters
    if (!type || !content) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'UI component generation requires type and content parameters'
      );
    }
    
    try {
      // Generate UI component descriptor
      const component = await this.generateUIComponent(
        type,
        content,
        config || {}
      );
      
      // Return the UI component descriptor
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { component }
      );
    } catch (error) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `UI component generation error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles natural language query transformation
   */
  private async handleQueryTransformation(message: Message): Promise<Message> {
    const { query, context } = message.content.body;
    
    // Validate required parameters
    if (!query) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Query transformation requires a query parameter'
      );
    }
    
    try {
      // Transform the query
      const transformedQuery = await this.transformQuery(
        query,
        context || {}
      );
      
      // Return the transformed query
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { transformedQuery }
      );
    } catch (error) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Query transformation error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles policy visualization requests
   */
  private async handlePolicyVisualization(message: Message): Promise<Message> {
    const { policy, visualization_type } = message.content.body;
    
    // Validate required parameters
    if (!policy) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Policy visualization requires a policy parameter'
      );
    }
    
    try {
      // Generate policy visualization descriptors
      const visualizations = await this.generatePolicyVisualizations(
        policy,
        visualization_type || 'comprehensive'
      );
      
      // Return the visualizations
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { visualizations }
      );
    } catch (error) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Policy visualization error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles dashboard generation requests
   */
  private async handleDashboardRequest(message: Message): Promise<Message> {
    const { dashboard_type, filters, config } = message.content.body;
    
    // Validate required parameters
    if (!dashboard_type) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Dashboard generation requires a dashboard_type parameter'
      );
    }
    
    try {
      // Generate dashboard components
      const dashboard = await this.generateDashboard(
        dashboard_type,
        filters || {},
        config || {}
      );
      
      // Return the dashboard descriptor
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { dashboard }
      );
    } catch (error) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Dashboard generation error: ${error.message}`
      );
    }
  }
  
  /**
   * Generates a visualization descriptor based on data and configuration
   */
  private async generateVisualization(
    data: any,
    type: string,
    title: string,
    config: Record<string, any>
  ): Promise<VisualizationDescriptor> {
    // Normalize visualization type
    const visualizationType = this.normalizeVisualizationType(type);
    
    // Generate a unique ID for the visualization
    const id = `viz-${visualizationType}-${Date.now()}`;
    
    // Create the visualization descriptor
    const visualization: VisualizationDescriptor = {
      type: visualizationType,
      id,
      title,
      data,
      config: { ...this.getDefaultConfig(visualizationType), ...config }
    };
    
    return visualization;
  }
  
  /**
   * Generates a UI component descriptor based on content and configuration
   */
  private async generateUIComponent(
    type: string,
    content: any,
    config: Record<string, any>
  ): Promise<UIComponentDescriptor> {
    // Generate a unique ID for the component
    const id = `ui-${type.toLowerCase()}-${Date.now()}`;
    
    // Create the component descriptor based on type
    let component: UIComponentDescriptor;
    
    switch (type.toLowerCase()) {
      case 'card':
        component = {
          type: 'Card',
          id,
          props: {
            title: content.title || 'Card',
            content: content.body || '',
            ...config
          }
        };
        break;
        
      case 'table':
        component = {
          type: 'Table',
          id,
          props: {
            headers: content.headers || [],
            rows: content.rows || [],
            ...config
          }
        };
        break;
        
      case 'form':
        component = {
          type: 'Form',
          id,
          props: {
            title: content.title || 'Form',
            fields: content.fields || [],
            submitLabel: content.submitLabel || 'Submit',
            ...config
          }
        };
        break;
        
      case 'alert':
        component = {
          type: 'Alert',
          id,
          props: {
            type: content.alertType || 'info',
            message: content.message || '',
            dismissible: content.dismissible !== undefined ? content.dismissible : true,
            ...config
          }
        };
        break;
        
      case 'tabs':
        component = {
          type: 'Tabs',
          id,
          props: {
            tabs: content.tabs || [],
            activeTab: content.activeTab || 0,
            ...config
          }
        };
        break;
        
      default:
        // Default to generic component
        component = {
          type: type || 'div',
          id,
          props: {
            ...content,
            ...config
          }
        };
    }
    
    return component;
  }
  
  /**
   * Transforms a natural language query into a structured query
   */
  private async transformQuery(
    query: string,
    context: Record<string, any>
  ): Promise<any> {
    // Simple query transformation - in a real implementation, this would use NLP or similar
    const lowercaseQuery = query.toLowerCase();
    
    // Detect query intent
    let intent = 'general';
    let domain = 'general';
    let action = 'search';
    
    // Extract intent
    if (lowercaseQuery.includes('policy') || lowercaseQuery.includes('regulation')) {
      intent = 'policy';
    } else if (lowercaseQuery.includes('data') || lowercaseQuery.includes('statistics')) {
      intent = 'data';
    } else if (lowercaseQuery.includes('form') || lowercaseQuery.includes('submit')) {
      intent = 'form';
      action = 'request';
    } else if (lowercaseQuery.includes('status') || lowercaseQuery.includes('update')) {
      intent = 'status';
    }
    
    // Extract domain
    if (lowercaseQuery.includes('health') || lowercaseQuery.includes('medical')) {
      domain = 'healthcare';
    } else if (lowercaseQuery.includes('economic') || lowercaseQuery.includes('business')) {
      domain = 'economic';
    } else if (lowercaseQuery.includes('education') || lowercaseQuery.includes('school')) {
      domain = 'education';
    }
    
    // Extract time context
    let timeframe = 'current';
    if (lowercaseQuery.includes('history') || lowercaseQuery.includes('past')) {
      timeframe = 'past';
    } else if (lowercaseQuery.includes('future') || lowercaseQuery.includes('upcoming')) {
      timeframe = 'future';
    }
    
    // Extract entities (simple implementation)
    const entities = this.extractEntities(query);
    
    // Create structured query
    const structuredQuery = {
      intent,
      domain,
      action,
      timeframe,
      entities,
      originalQuery: query,
      context: { ...context }
    };
    
    return structuredQuery;
  }
  
  /**
   * Generates visualizations for a policy
   */
  private async generatePolicyVisualizations(
    policy: any,
    visualizationType: string
  ): Promise<VisualizationDescriptor[]> {
    const visualizations: VisualizationDescriptor[] = [];
    
    // Generate different visualizations based on the type
    if (visualizationType === 'comprehensive' || visualizationType === 'timeline') {
      // Timeline visualization
      visualizations.push({
        type: 'timeline',
        id: `timeline-${policy.id}`,
        title: `Implementation Timeline: ${policy.name}`,
        data: this.generateTimelineData(policy),
        config: {
          height: 300,
          showLabels: true,
          colorScale: 'category10'
        }
      });
    }
    
    if (visualizationType === 'comprehensive' || visualizationType === 'stakeholder') {
      // Stakeholder impact visualization
      visualizations.push({
        type: 'chart',
        id: `stakeholder-${policy.id}`,
        title: `Stakeholder Impact: ${policy.name}`,
        data: this.generateStakeholderData(policy),
        config: {
          type: 'bar',
          height: 300,
          xAxisLabel: 'Stakeholder',
          yAxisLabel: 'Impact Score'
        }
      });
    }
    
    if (visualizationType === 'comprehensive' || visualizationType === 'crossdomain') {
      // Cross-domain impact visualization
      visualizations.push({
        type: 'chart',
        id: `cross-domain-${policy.id}`,
        title: `Cross-Domain Impact: ${policy.name}`,
        data: this.generateCrossDomainData(policy),
        config: {
          type: 'radar',
          height: 300,
          legend: true
        }
      });
    }
    
    if (visualizationType === 'comprehensive' || visualizationType === 'measures') {
      // Policy measures table
      visualizations.push({
        type: 'table',
        id: `measures-${policy.id}`,
        title: `Policy Measures: ${policy.name}`,
        data: this.generateMeasuresTableData(policy),
        config: {
          pagination: true,
          sortable: true,
          pageSize: 5
        }
      });
    }
    
    return visualizations;
  }
  
  /**
   * Generates a dashboard descriptor based on type and filters
   */
  private async generateDashboard(
    dashboardType: string,
    filters: Record<string, any>,
    config: Record<string, any>
  ): Promise<any> {
    const dashboard = {
      id: `dashboard-${dashboardType.toLowerCase()}-${Date.now()}`,
      title: this.getDashboardTitle(dashboardType),
      layout: 'grid',
      filters: this.generateDashboardFilters(dashboardType, filters),
      components: await this.generateDashboardComponents(dashboardType, filters, config)
    };
    
    return dashboard;
  }
  
  /**
   * Gets the dashboard title based on type
   */
  private getDashboardTitle(dashboardType: string): string {
    switch (dashboardType.toLowerCase()) {
      case 'policy':
        return 'Policy Dashboard';
      case 'regulatory':
        return 'Regulatory Compliance Dashboard';
      case 'economic':
        return 'Economic Indicators Dashboard';
      case 'healthcare':
        return 'Healthcare Policy Dashboard';
      default:
        return `${dashboardType.charAt(0).toUpperCase() + dashboardType.slice(1)} Dashboard`;
    }
  }
  
  /**
   * Generates dashboard filters based on type and configuration
   */
  private generateDashboardFilters(
    dashboardType: string,
    filters: Record<string, any>
  ): any[] {
    const dashboardFilters = [];
    
    // Common filters
    dashboardFilters.push({
      id: 'date-range',
      type: 'dateRange',
      label: 'Date Range',
      value: filters.dateRange || { start: '2023-01-01', end: '2023-12-31' }
    });
    
    // Type-specific filters
    switch (dashboardType.toLowerCase()) {
      case 'policy':
        dashboardFilters.push({
          id: 'policy-domain',
          type: 'select',
          label: 'Policy Domain',
          options: ['All', 'Healthcare', 'Economic', 'Education', 'Environmental'],
          value: filters.domain || 'All'
        });
        dashboardFilters.push({
          id: 'policy-status',
          type: 'select',
          label: 'Policy Status',
          options: ['All', 'Draft', 'In Review', 'Approved', 'Implemented'],
          value: filters.status || 'All'
        });
        break;
        
      case 'regulatory':
        dashboardFilters.push({
          id: 'compliance-level',
          type: 'select',
          label: 'Compliance Level',
          options: ['All', 'Compliant', 'Partially Compliant', 'Non-Compliant'],
          value: filters.complianceLevel || 'All'
        });
        dashboardFilters.push({
          id: 'framework',
          type: 'select',
          label: 'Regulatory Framework',
          options: ['All', 'Federal', 'State', 'Local', 'International'],
          value: filters.framework || 'All'
        });
        break;
        
      case 'economic':
        dashboardFilters.push({
          id: 'region',
          type: 'select',
          label: 'Region',
          options: ['National', 'Northeast', 'Midwest', 'South', 'West'],
          value: filters.region || 'National'
        });
        dashboardFilters.push({
          id: 'sector',
          type: 'select',
          label: 'Sector',
          options: ['All', 'Manufacturing', 'Services', 'Technology', 'Healthcare'],
          value: filters.sector || 'All'
        });
        break;
    }
    
    return dashboardFilters;
  }
  
  /**
   * Generates dashboard components based on type and filters
   */
  private async generateDashboardComponents(
    dashboardType: string,
    filters: Record<string, any>,
    config: Record<string, any>
  ): Promise<any[]> {
    const components = [];
    
    // Generate components based on dashboard type
    switch (dashboardType.toLowerCase()) {
      case 'policy':
        // Summary card
        components.push({
          id: 'policy-summary',
          type: 'component',
          component: await this.generateUIComponent('card', {
            title: 'Policy Overview',
            body: 'Summary of policy metrics and key performance indicators.'
          }, { width: 'full' })
        });
        
        // Policy status chart
        components.push({
          id: 'policy-status-chart',
          type: 'visualization',
          visualization: await this.generateVisualization(
            this.generateMockChartData('pie', 4),
            'chart',
            'Policy Status Distribution',
            { type: 'pie', legend: true, width: 'half' }
          )
        });
        
        // Policy domain chart
        components.push({
          id: 'policy-domain-chart',
          type: 'visualization',
          visualization: await this.generateVisualization(
            this.generateMockChartData('bar', 5),
            'chart',
            'Policies by Domain',
            { type: 'bar', width: 'half' }
          )
        });
        
        // Policy table
        components.push({
          id: 'policy-table',
          type: 'component',
          component: await this.generateUIComponent('table', {
            headers: ['ID', 'Name', 'Domain', 'Status', 'Last Updated', 'Actions'],
            rows: this.generateMockTableData(10, 6)
          }, { pagination: true, width: 'full' })
        });
        break;
        
      case 'regulatory':
        // Compliance summary card
        components.push({
          id: 'compliance-summary',
          type: 'component',
          component: await this.generateUIComponent('card', {
            title: 'Compliance Summary',
            body: 'Overview of regulatory compliance metrics and risk indicators.'
          }, { width: 'full' })
        });
        
        // Compliance by framework chart
        components.push({
          id: 'compliance-framework-chart',
          type: 'visualization',
          visualization: await this.generateVisualization(
            this.generateMockChartData('bar', 4),
            'chart',
            'Compliance by Framework',
            { type: 'bar', stacked: true, width: 'half' }
          )
        });
        
        // Compliance trend chart
        components.push({
          id: 'compliance-trend-chart',
          type: 'visualization',
          visualization: await this.generateVisualization(
            this.generateMockChartData('line', 12),
            'chart',
            'Compliance Trend',
            { type: 'line', width: 'half' }
          )
        });
        
        // Regulatory requirements table
        components.push({
          id: 'regulatory-table',
          type: 'component',
          component: await this.generateUIComponent('table', {
            headers: ['Requirement', 'Framework', 'Status', 'Due Date', 'Risk Level', 'Actions'],
            rows: this.generateMockTableData(10, 6)
          }, { pagination: true, width: 'full' })
        });
        break;
        
      case 'economic':
        // Economic indicators card
        components.push({
          id: 'economic-indicators',
          type: 'component',
          component: await this.generateUIComponent('card', {
            title: 'Economic Indicators',
            body: 'Summary of key economic indicators and policy impacts.'
          }, { width: 'full' })
        });
        
        // Economic trend chart
        components.push({
          id: 'economic-trend-chart',
          type: 'visualization',
          visualization: await this.generateVisualization(
            this.generateMockChartData('line', 24),
            'chart',
            'Economic Indicators Trend',
            { type: 'line', multiSeries: true, width: 'full' }
          )
        });
        
        // Regional comparison chart
        components.push({
          id: 'regional-comparison-chart',
          type: 'visualization',
          visualization: await this.generateVisualization(
            this.generateMockChartData('bar', 5),
            'chart',
            'Regional Comparison',
            { type: 'bar', grouped: true, width: 'half' }
          )
        });
        
        // Sector performance chart
        components.push({
          id: 'sector-performance-chart',
          type: 'visualization',
          visualization: await this.generateVisualization(
            this.generateMockChartData('radar', 5),
            'chart',
            'Sector Performance',
            { type: 'radar', width: 'half' }
          )
        });
        break;
        
      default:
        // Default dashboard components
        components.push({
          id: 'default-summary',
          type: 'component',
          component: await this.generateUIComponent('card', {
            title: `${dashboardType} Dashboard`,
            body: `Summary of ${dashboardType.toLowerCase()} metrics and performance indicators.`
          }, { width: 'full' })
        });
        
        // Generic chart
        components.push({
          id: 'default-chart',
          type: 'visualization',
          visualization: await this.generateVisualization(
            this.generateMockChartData('bar', 5),
            'chart',
            `${dashboardType} Metrics`,
            { type: 'bar', width: 'full' }
          )
        });
        
        // Generic table
        components.push({
          id: 'default-table',
          type: 'component',
          component: await this.generateUIComponent('table', {
            headers: ['ID', 'Name', 'Type', 'Status', 'Date', 'Actions'],
            rows: this.generateMockTableData(10, 6)
          }, { pagination: true, width: 'full' })
        });
    }
    
    return components;
  }
  
  /**
   * Normalizes the visualization type to a supported type
   */
  private normalizeVisualizationType(type: string): VisualizationDescriptor['type'] {
    type = type.toLowerCase();
    
    if (['pie', 'bar', 'line', 'scatter', 'radar'].includes(type)) {
      return 'chart';
    } else if (['grid', 'matrix'].includes(type)) {
      return 'table';
    } else if (['hierarchy', 'org'].includes(type)) {
      return 'tree';
    } else if (['gantt', 'schedule'].includes(type)) {
      return 'timeline';
    } else if (['geo', 'world', 'country'].includes(type)) {
      return 'map';
    }
    
    // If the type is already one of the supported types, return it
    if (['chart', 'table', 'tree', 'timeline', 'map'].includes(type)) {
      return type as VisualizationDescriptor['type'];
    }
    
    // Default to table for unsupported types
    return 'table';
  }
  
  /**
   * Gets the default configuration for a visualization type
   */
  private getDefaultConfig(type: VisualizationDescriptor['type']): Record<string, any> {
    switch (type) {
      case 'chart':
        return {
          type: 'bar',
          height: 300,
          width: 500,
          legend: false,
          animations: true
        };
      case 'table':
        return {
          pagination: true,
          pageSize: 10,
          sortable: true,
          filterable: true
        };
      case 'tree':
        return {
          height: 400,
          width: 600,
          nodeSize: 30,
          orientation: 'vertical'
        };
      case 'timeline':
        return {
          height: 200,
          showLabels: true,
          zoomable: true
        };
      case 'map':
        return {
          height: 400,
          width: 600,
          projection: 'mercator',
          zoomable: true
        };
      default:
        return {};
    }
  }
  
  /**
   * Extracts entities from a query string
   */
  private extractEntities(query: string): any[] {
    const entities = [];
    
    // Very simple entity extraction - in a real implementation, this would use NER or similar
    // Look for capitalized words that might be entities
    const matches = query.match(/\b[A-Z][a-zA-Z]*\b/g);
    if (matches) {
      matches.forEach(match => {
        entities.push({
          type: 'unknown',
          value: match,
          confidence: 0.7
        });
      });
    }
    
    // Look for dates
    const dateMatches = query.match(/\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b/gi);
    if (dateMatches) {
      dateMatches.forEach(match => {
        entities.push({
          type: 'date',
          value: match,
          confidence: 0.9
        });
      });
    }
    
    // Look for percentages
    const percentMatches = query.match(/\b\d+(?:\.\d+)?%\b/g);
    if (percentMatches) {
      percentMatches.forEach(match => {
        entities.push({
          type: 'percentage',
          value: match,
          confidence: 0.95
        });
      });
    }
    
    return entities;
  }
  
  /**
   * Generates timeline data for a policy
   */
  private generateTimelineData(policy: any): any {
    const timelineData = {
      events: []
    };
    
    // Policy creation event
    timelineData.events.push({
      date: policy.metadata?.created_at || new Date().toISOString(),
      title: 'Policy Created',
      description: `Initial creation of ${policy.name}`,
      type: 'milestone'
    });
    
    // Policy measure events
    if (policy.measures && Array.isArray(policy.measures)) {
      policy.measures.forEach((measure, index) => {
        // Create mock implementation date (future date from creation)
        const creationDate = new Date(policy.metadata?.created_at || new Date());
        const implementationDate = new Date(creationDate);
        implementationDate.setMonth(implementationDate.getMonth() + (index + 1) * 3); // Each measure 3 months apart
        
        timelineData.events.push({
          date: implementationDate.toISOString(),
          title: `Implement: ${measure.name}`,
          description: measure.description,
          type: 'task',
          duration: measure.timeline || '3 months'
        });
      });
    }
    
    // Add review events
    const creationDate = new Date(policy.metadata?.created_at || new Date());
    const reviewDate = new Date(creationDate);
    reviewDate.setFullYear(reviewDate.getFullYear() + 1); // Review after 1 year
    
    timelineData.events.push({
      date: reviewDate.toISOString(),
      title: 'Annual Policy Review',
      description: `Comprehensive review of ${policy.name} implementation and outcomes`,
      type: 'milestone'
    });
    
    return timelineData;
  }
  
  /**
   * Generates stakeholder data for a policy
   */
  private generateStakeholderData(policy: any): any {
    const stakeholderData = {
      labels: [],
      datasets: [
        {
          label: 'Impact Score',
          data: []
        }
      ]
    };
    
    // Convert stakeholders to chart data
    if (policy.stakeholders && Array.isArray(policy.stakeholders)) {
      policy.stakeholders.forEach(stakeholder => {
        stakeholderData.labels.push(stakeholder.name);
        
        // Convert sentiment to numeric score
        let score = 0;
        switch (stakeholder.sentiment) {
          case 'positive':
            score = 0.8;
            break;
          case 'neutral':
            score = 0.5;
            break;
          case 'negative':
            score = 0.2;
            break;
          case 'mixed':
            score = 0.5;
            break;
          default:
            score = 0.5;
        }
        
        stakeholderData.datasets[0].data.push(score);
      });
    }
    
    return stakeholderData;
  }
  
  /**
   * Generates cross-domain impact data for a policy
   */
  private generateCrossDomainData(policy: any): any {
    const crossDomainData = {
      labels: [],
      datasets: [
        {
          label: 'Impact Severity',
          data: []
        }
      ]
    };
    
    // Convert cross-domain impacts to chart data
    if (policy.cross_domain_impacts && Array.isArray(policy.cross_domain_impacts)) {
      policy.cross_domain_impacts.forEach(impact => {
        crossDomainData.labels.push(impact.domain);
        
        // Convert severity to numeric score
        let score = 0;
        switch (impact.severity) {
          case 'high':
            score = 0.8;
            break;
          case 'medium':
            score = 0.5;
            break;
          case 'low':
            score = 0.2;
            break;
          default:
            score = 0.5;
        }
        
        crossDomainData.datasets[0].data.push(score);
      });
    }
    
    return crossDomainData;
  }
  
  /**
   * Generates measures table data for a policy
   */
  private generateMeasuresTableData(policy: any): any {
    const tableData = {
      headers: ['Name', 'Description', 'Timeline', 'Resources', 'Expected Outcomes'],
      rows: []
    };
    
    // Convert measures to table rows
    if (policy.measures && Array.isArray(policy.measures)) {
      policy.measures.forEach(measure => {
        tableData.rows.push([
          measure.name,
          measure.description,
          measure.timeline || 'Not specified',
          measure.resources_required || 'Not specified',
          (measure.expected_outcomes || []).join(', ')
        ]);
      });
    }
    
    return tableData;
  }
  
  /**
   * Generates mock chart data for testing and development
   */
  private generateMockChartData(chartType: string, dataPoints: number): any {
    const mockData: any = {
      labels: [],
      datasets: []
    };
    
    // Generate labels based on chart type
    if (chartType === 'pie') {
      mockData.labels = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E'].slice(0, dataPoints);
    } else if (chartType === 'line') {
      // Date labels for line charts
      for (let i = 0; i < dataPoints; i++) {
        const date = new Date();
        date.setMonth(date.getMonth() - (dataPoints - i - 1));
        mockData.labels.push(date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }));
      }
    } else {
      // Default labels
      for (let i = 0; i < dataPoints; i++) {
        mockData.labels.push(`Item ${i + 1}`);
      }
    }
    
    // Generate datasets based on chart type
    if (chartType === 'radar') {
      mockData.datasets = [
        {
          label: 'Series A',
          data: Array.from({ length: dataPoints }, () => Math.floor(Math.random() * 100)),
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgba(75, 192, 192, 1)'
        },
        {
          label: 'Series B',
          data: Array.from({ length: dataPoints }, () => Math.floor(Math.random() * 100)),
          backgroundColor: 'rgba(153, 102, 255, 0.2)',
          borderColor: 'rgba(153, 102, 255, 1)'
        }
      ];
    } else if (chartType === 'multiSeries' || chartType === 'line') {
      mockData.datasets = [
        {
          label: 'Series A',
          data: Array.from({ length: dataPoints }, () => Math.floor(Math.random() * 100)),
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)'
        },
        {
          label: 'Series B',
          data: Array.from({ length: dataPoints }, () => Math.floor(Math.random() * 100)),
          borderColor: 'rgba(153, 102, 255, 1)',
          backgroundColor: 'rgba(153, 102, 255, 0.2)'
        }
      ];
    } else {
      mockData.datasets = [
        {
          label: 'Values',
          data: Array.from({ length: dataPoints }, () => Math.floor(Math.random() * 100)),
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)'
          ].slice(0, dataPoints)
        }
      ];
    }
    
    return mockData;
  }
  
  /**
   * Generates mock table data for testing and development
   */
  private generateMockTableData(rows: number, columns: number): any[][] {
    const tableData = [];
    
    for (let i = 0; i < rows; i++) {
      const row = [];
      
      // First column is usually an ID
      row.push(`ID-${i + 1}`);
      
      // Generate remaining columns
      for (let j = 1; j < columns; j++) {
        if (j === columns - 1 && columns > 2) {
          // Last column is often an action column
          row.push('View | Edit | Delete');
        } else if (j === columns - 2 && columns > 3) {
          // Second to last column is often a date
          const date = new Date();
          date.setDate(date.getDate() - Math.floor(Math.random() * 30));
          row.push(date.toLocaleDateString());
        } else {
          // Other columns are generic data
          row.push(`Data ${i + 1}-${j + 1}`);
        }
      }
      
      tableData.push(row);
    }
    
    return tableData;
  }
}