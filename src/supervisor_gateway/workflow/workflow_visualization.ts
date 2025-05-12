/**
 * Visualization service for workflows
 */

import { Workflow, Task, TaskStatus, WorkflowStatus } from './workflow_orchestrator';
import { ScopeLevel, WorkflowDomain } from './workflow_models';

/**
 * Options for workflow visualization
 */
export interface VisualizationOptions {
  showTimestamps?: boolean;      // Show task timestamps
  showDurations?: boolean;       // Show task durations
  showAgents?: boolean;          // Show assigned agents
  showStatus?: boolean;          // Show status indicators
  showDetails?: boolean;         // Show detailed information
  colorScheme?: string;          // Color scheme for visualization
  layout?: 'vertical' | 'horizontal'; // Layout direction
  includeMetadata?: boolean;     // Include metadata in visualization
  focusTaskId?: string;          // Task to focus on
  scale?: number;                // Scale factor for visualization
  format?: 'mermaid' | 'dot' | 'json'; // Output format
}

/**
 * Service for visualizing workflows
 */
export class WorkflowVisualizationService {
  /**
   * Creates a visualization of a workflow
   * @param workflow Workflow to visualize
   * @param options Visualization options
   * @returns Visualization in specified format
   */
  static createVisualization(workflow: Workflow, options: VisualizationOptions = {}): string {
    const format = options.format || 'mermaid';
    
    switch (format) {
      case 'mermaid':
        return this.createMermaidDiagram(workflow, options);
      case 'dot':
        return this.createDotDiagram(workflow, options);
      case 'json':
        return this.createJsonVisualization(workflow, options);
      default:
        return this.createMermaidDiagram(workflow, options);
    }
  }
  
  /**
   * Creates a Mermaid.js flowchart diagram of a workflow
   * @param workflow Workflow to visualize
   * @param options Visualization options
   * @returns Mermaid.js diagram
   */
  private static createMermaidDiagram(workflow: Workflow, options: VisualizationOptions): string {
    const isVertical = options.layout !== 'horizontal';
    const direction = isVertical ? 'TD' : 'LR';
    
    let mermaid = `graph ${direction};\n`;
    
    // Add workflow title
    mermaid += `  workflowTitle["${workflow.name} (${workflow.status})"]:::classTitle;\n`;
    
    // Add nodes for all tasks
    for (const task of workflow.tasks.values()) {
      let styleClass = '';
      switch (task.status) {
        case TaskStatus.PENDING:
          styleClass = 'classPending';
          break;
        case TaskStatus.ASSIGNED:
          styleClass = 'classAssigned';
          break;
        case TaskStatus.RUNNING:
          styleClass = 'classRunning';
          break;
        case TaskStatus.COMPLETED:
          styleClass = 'classCompleted';
          break;
        case TaskStatus.FAILED:
          styleClass = 'classFailed';
          break;
        case TaskStatus.SKIPPED:
          styleClass = 'classSkipped';
          break;
        case TaskStatus.CANCELLED:
          styleClass = 'classCancelled';
          break;
      }
      
      // Create node label with task details
      let taskLabel = task.name;
      
      if (options.showDetails) {
        taskLabel += `<br>Type: ${task.type}`;
        if (task.agentType) {
          taskLabel += `<br>Agent: ${task.agentType}`;
        }
        
        if (task.assignedAgentId && options.showAgents) {
          taskLabel += `<br>Assigned: ${task.assignedAgentId}`;
        }
        
        if (options.showStatus) {
          taskLabel += `<br>Status: ${task.status}`;
        }
        
        if (task.startTime && options.showTimestamps) {
          const startTime = new Date(task.startTime).toLocaleTimeString();
          taskLabel += `<br>Started: ${startTime}`;
        }
        
        if (task.actualDuration && options.showDurations) {
          const durationSec = Math.round(task.actualDuration / 1000);
          taskLabel += `<br>Duration: ${durationSec}s`;
        }
      }
      
      // Add focused class if this is the focused task
      if (options.focusTaskId === task.id) {
        mermaid += `  ${task.id}["${taskLabel}"]:::${styleClass}Focused;\n`;
      } else {
        mermaid += `  ${task.id}["${taskLabel}"]:::${styleClass};\n`;
      }
    }
    
    // Add edges for task dependencies
    for (const task of workflow.tasks.values()) {
      // Dependencies
      for (const dependencyId of task.dependencies) {
        mermaid += `  ${dependencyId} --> ${task.id};\n`;
      }
      
      // Subtasks
      for (const subtaskId of task.subtasks) {
        mermaid += `  ${task.id} -.-> ${subtaskId};\n`;
      }
      
      // Fallback tasks
      if (task.fallbackTaskId) {
        mermaid += `  ${task.id} -. fallback .-> ${task.fallbackTaskId};\n`;
      }
    }
    
    // Add style definitions
    mermaid += '  classDef classTitle fill:#d4d4d4,stroke:#333333,color:#333333,font-weight:bold;\n';
    mermaid += '  classDef classPending fill:#fcf3cf,stroke:#f1c40f,color:#7d6608;\n';
    mermaid += '  classDef classAssigned fill:#d6eaf8,stroke:#3498db,color:#1a5276;\n';
    mermaid += '  classDef classRunning fill:#d4efdf,stroke:#2ecc71,color:#1d8348;\n';
    mermaid += '  classDef classCompleted fill:#a9dfbf,stroke:#27ae60,color:#145a32;\n';
    mermaid += '  classDef classFailed fill:#f5b7b1,stroke:#e74c3c,color:#7b241c;\n';
    mermaid += '  classDef classSkipped fill:#d5dbdb,stroke:#7f8c8d,color:#424949;\n';
    mermaid += '  classDef classCancelled fill:#d5d8dc,stroke:#566573,color:#212f3c;\n';
    
    // Add focused versions of classes
    mermaid += '  classDef classPendingFocused fill:#f9e79f,stroke:#f1c40f,color:#7d6608,font-weight:bold,stroke-width:3px;\n';
    mermaid += '  classDef classAssignedFocused fill:#aed6f1,stroke:#3498db,color:#1a5276,font-weight:bold,stroke-width:3px;\n';
    mermaid += '  classDef classRunningFocused fill:#abebc6,stroke:#2ecc71,color:#1d8348,font-weight:bold,stroke-width:3px;\n';
    mermaid += '  classDef classCompletedFocused fill:#7dcea0,stroke:#27ae60,color:#145a32,font-weight:bold,stroke-width:3px;\n';
    mermaid += '  classDef classFailedFocused fill:#f1948a,stroke:#e74c3c,color:#7b241c,font-weight:bold,stroke-width:3px;\n';
    mermaid += '  classDef classSkippedFocused fill:#b2babb,stroke:#7f8c8d,color:#424949,font-weight:bold,stroke-width:3px;\n';
    mermaid += '  classDef classCancelledFocused fill:#abb2b9,stroke:#566573,color:#212f3c,font-weight:bold,stroke-width:3px;\n';
    
    return mermaid;
  }
  
  /**
   * Creates a DOT diagram of a workflow for use with Graphviz
   * @param workflow Workflow to visualize
   * @param options Visualization options
   * @returns DOT diagram
   */
  private static createDotDiagram(workflow: Workflow, options: VisualizationOptions): string {
    const isVertical = options.layout !== 'horizontal';
    const rankdir = isVertical ? 'TB' : 'LR';
    
    let dot = 'digraph Workflow {\n';
    dot += `  rankdir=${rankdir};\n`;
    dot += '  node [shape=box, style=filled, fontname="Arial"];\n';
    dot += '  edge [fontname="Arial"];\n\n';
    
    // Add workflow title
    dot += `  workflowTitle [label="${workflow.name} (${workflow.status})", shape=plaintext, fontsize=16, fontcolor="#333333"];\n\n`;
    
    // Add nodes for all tasks
    for (const task of workflow.tasks.values()) {
      let fillColor = '';
      let fontColor = '';
      let extraStyle = '';
      
      switch (task.status) {
        case TaskStatus.PENDING:
          fillColor = '#fcf3cf';
          fontColor = '#7d6608';
          break;
        case TaskStatus.ASSIGNED:
          fillColor = '#d6eaf8';
          fontColor = '#1a5276';
          break;
        case TaskStatus.RUNNING:
          fillColor = '#d4efdf';
          fontColor = '#1d8348';
          break;
        case TaskStatus.COMPLETED:
          fillColor = '#a9dfbf';
          fontColor = '#145a32';
          break;
        case TaskStatus.FAILED:
          fillColor = '#f5b7b1';
          fontColor = '#7b241c';
          break;
        case TaskStatus.SKIPPED:
          fillColor = '#d5dbdb';
          fontColor = '#424949';
          break;
        case TaskStatus.CANCELLED:
          fillColor = '#d5d8dc';
          fontColor = '#212f3c';
          break;
      }
      
      // Create node label with task details
      let taskLabel = task.name;
      
      if (options.showDetails) {
        taskLabel += `\\nType: ${task.type}`;
        if (task.agentType) {
          taskLabel += `\\nAgent: ${task.agentType}`;
        }
        
        if (task.assignedAgentId && options.showAgents) {
          taskLabel += `\\nAssigned: ${task.assignedAgentId}`;
        }
        
        if (options.showStatus) {
          taskLabel += `\\nStatus: ${task.status}`;
        }
        
        if (task.startTime && options.showTimestamps) {
          const startTime = new Date(task.startTime).toLocaleTimeString();
          taskLabel += `\\nStarted: ${startTime}`;
        }
        
        if (task.actualDuration && options.showDurations) {
          const durationSec = Math.round(task.actualDuration / 1000);
          taskLabel += `\\nDuration: ${durationSec}s`;
        }
      }
      
      // Add focused style if this is the focused task
      if (options.focusTaskId === task.id) {
        extraStyle = ', penwidth=3.0, fontsize=12, fontweight=bold';
      }
      
      dot += `  "${task.id}" [label="${taskLabel}", fillcolor="${fillColor}", fontcolor="${fontColor}"${extraStyle}];\n`;
    }
    
    dot += '\n';
    
    // Add edges for task dependencies
    for (const task of workflow.tasks.values()) {
      // Dependencies
      for (const dependencyId of task.dependencies) {
        dot += `  "${dependencyId}" -> "${task.id}";\n`;
      }
      
      // Subtasks
      for (const subtaskId of task.subtasks) {
        dot += `  "${task.id}" -> "${subtaskId}" [style=dashed];\n`;
      }
      
      // Fallback tasks
      if (task.fallbackTaskId) {
        dot += `  "${task.id}" -> "${task.fallbackTaskId}" [style=dashed, label="fallback"];\n`;
      }
    }
    
    dot += '}\n';
    
    return dot;
  }
  
  /**
   * Creates a JSON visualization of a workflow
   * @param workflow Workflow to visualize
   * @param options Visualization options
   * @returns JSON visualization
   */
  private static createJsonVisualization(workflow: Workflow, options: VisualizationOptions): string {
    const visualization = {
      workflow: {
        id: workflow.id,
        name: workflow.name,
        description: workflow.description,
        status: workflow.status,
        executionMode: workflow.executionMode,
        coordinationStrategy: workflow.coordinationStrategy,
        createdAt: workflow.createdAt,
        startedAt: workflow.startedAt,
        completedAt: workflow.completedAt,
        progress: workflow.getStatistics().progress
      },
      tasks: Array.from(workflow.tasks.values()).map(task => {
        const taskJson: any = {
          id: task.id,
          name: task.name,
          description: task.description,
          type: task.type,
          status: task.status,
          agentType: task.agentType,
          assignedAgentId: task.assignedAgentId,
          priority: task.priority,
          dependencies: task.dependencies,
          subtasks: task.subtasks,
          fallbackTaskId: task.fallbackTaskId
        };
        
        if (options.showTimestamps) {
          taskJson.startTime = task.startTime;
          taskJson.endTime = task.endTime;
        }
        
        if (options.showDurations) {
          taskJson.estimatedDuration = task.estimatedDuration;
          taskJson.actualDuration = task.actualDuration;
        }
        
        if (options.includeMetadata) {
          taskJson.metadata = task.metadata;
        }
        
        return taskJson;
      }),
      edges: []
    };
    
    // Add edges
    const edges: any[] = [];
    
    for (const task of workflow.tasks.values()) {
      // Dependencies
      for (const dependencyId of task.dependencies) {
        edges.push({
          from: dependencyId,
          to: task.id,
          type: 'dependency'
        });
      }
      
      // Subtasks
      for (const subtaskId of task.subtasks) {
        edges.push({
          from: task.id,
          to: subtaskId,
          type: 'subtask'
        });
      }
      
      // Fallback tasks
      if (task.fallbackTaskId) {
        edges.push({
          from: task.id,
          to: task.fallbackTaskId,
          type: 'fallback'
        });
      }
    }
    
    visualization.edges = edges;
    
    return JSON.stringify(visualization, null, 2);
  }
  
  /**
   * Creates a task dependency graph visualization
   * @param workflow Workflow to visualize
   * @returns Mermaid.js diagram of task dependencies
   */
  static createDependencyGraph(workflow: Workflow): string {
    let mermaid = 'graph TD;\n';
    
    // Add nodes for all tasks
    for (const task of workflow.tasks.values()) {
      mermaid += `  ${task.id}["${task.name}"];\n`;
    }
    
    // Add edges for dependencies
    for (const task of workflow.tasks.values()) {
      for (const dependencyId of task.dependencies) {
        mermaid += `  ${dependencyId} -->|required by| ${task.id};\n`;
      }
    }
    
    return mermaid;
  }
  
  /**
   * Creates a workflow status timeline
   * @param workflow Workflow to visualize
   * @returns Mermaid.js timeline diagram
   */
  static createStatusTimeline(workflow: Workflow): string {
    // Sort tasks by start time
    const sortedTasks = Array.from(workflow.tasks.values())
      .filter(task => task.startTime)
      .sort((a, b) => (a.startTime || 0) - (b.startTime || 0));
    
    if (sortedTasks.length === 0) {
      return 'No tasks with recorded start times';
    }
    
    let timeline = 'gantt\n';
    timeline += '    title Workflow Timeline\n';
    timeline += '    dateFormat X\n'; // Use Unix timestamp format
    timeline += '    axisFormat %H:%M:%S\n';
    
    // Define sections based on task types or agent types
    const sections = new Map<string, Task[]>();
    
    for (const task of sortedTasks) {
      const sectionKey = task.agentType || task.type;
      if (!sections.has(sectionKey)) {
        sections.set(sectionKey, []);
      }
      sections.get(sectionKey)?.push(task);
    }
    
    // Add timeline entries
    for (const [section, tasks] of sections.entries()) {
      timeline += `    section ${section}\n`;
      
      for (const task of tasks) {
        if (!task.startTime) continue;
        
        const startTime = task.startTime;
        const endTime = task.endTime || Date.now();
        const taskStatus = this.getStatusWithEmoji(task.status);
        
        timeline += `    ${task.name} (${taskStatus}): ${startTime}, ${endTime}\n`;
      }
    }
    
    return timeline;
  }
  
  /**
   * Creates a task status summary
   * @param workflow Workflow to summarize
   * @returns Mermaid.js pie chart of task statuses
   */
  static createStatusSummary(workflow: Workflow): string {
    // Count tasks by status
    const statusCounts = new Map<TaskStatus, number>();
    for (const status of Object.values(TaskStatus)) {
      statusCounts.set(status as TaskStatus, 0);
    }
    
    for (const task of workflow.tasks.values()) {
      const count = statusCounts.get(task.status) || 0;
      statusCounts.set(task.status, count + 1);
    }
    
    let pieChart = 'pie\n';
    pieChart += '    title Task Status Summary\n';
    
    for (const [status, count] of statusCounts.entries()) {
      if (count > 0) {
        pieChart += `    "${status}" : ${count}\n`;
      }
    }
    
    return pieChart;
  }
  
  /**
   * Creates an agent allocation visualization
   * @param workflow Workflow to visualize
   * @returns Mermaid.js diagram of agent allocations
   */
  static createAgentAllocationChart(workflow: Workflow): string {
    // Group tasks by assigned agent
    const agentTasks = new Map<string, Task[]>();
    
    for (const task of workflow.tasks.values()) {
      if (task.assignedAgentId) {
        if (!agentTasks.has(task.assignedAgentId)) {
          agentTasks.set(task.assignedAgentId, []);
        }
        agentTasks.get(task.assignedAgentId)?.push(task);
      }
    }
    
    let mermaid = 'graph TD;\n';
    
    // Add nodes for agents
    for (const agentId of agentTasks.keys()) {
      const tasks = agentTasks.get(agentId) || [];
      const taskCount = tasks.length;
      
      mermaid += `  ${agentId}["Agent: ${agentId}<br>Tasks: ${taskCount}"]:::classAgent;\n`;
    }
    
    // Add nodes for tasks and connect to agents
    for (const [agentId, tasks] of agentTasks.entries()) {
      for (const task of tasks) {
        let styleClass = '';
        switch (task.status) {
          case TaskStatus.COMPLETED:
            styleClass = 'classCompleted';
            break;
          case TaskStatus.RUNNING:
            styleClass = 'classRunning';
            break;
          case TaskStatus.FAILED:
            styleClass = 'classFailed';
            break;
          default:
            styleClass = 'classPending';
        }
        
        mermaid += `  ${task.id}["${task.name}<br>Status: ${task.status}"]:::${styleClass};\n`;
        mermaid += `  ${agentId} --> ${task.id};\n`;
      }
    }
    
    // Add style definitions
    mermaid += '  classDef classAgent fill:#f5f5f5,stroke:#333333,color:#333333;\n';
    mermaid += '  classDef classPending fill:#fcf3cf,stroke:#f1c40f,color:#7d6608;\n';
    mermaid += '  classDef classRunning fill:#d4efdf,stroke:#2ecc71,color:#1d8348;\n';
    mermaid += '  classDef classCompleted fill:#a9dfbf,stroke:#27ae60,color:#145a32;\n';
    mermaid += '  classDef classFailed fill:#f5b7b1,stroke:#e74c3c,color:#7b241c;\n';
    
    return mermaid;
  }
  
  /**
   * Gets a status string with emoji
   * @param status Task status
   * @returns Status string with emoji
   */
  private static getStatusWithEmoji(status: TaskStatus): string {
    switch (status) {
      case TaskStatus.PENDING:
        return '⏳ Pending';
      case TaskStatus.ASSIGNED:
        return '📋 Assigned';
      case TaskStatus.RUNNING:
        return '▶️ Running';
      case TaskStatus.COMPLETED:
        return '✅ Completed';
      case TaskStatus.FAILED:
        return '❌ Failed';
      case TaskStatus.SKIPPED:
        return '⏭️ Skipped';
      case TaskStatus.CANCELLED:
        return '🚫 Cancelled';
      default:
        return status;
    }
  }
}

export default WorkflowVisualizationService;