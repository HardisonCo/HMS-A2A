import React, { useState, useEffect } from 'react';
import { Box, Text, useInput } from 'ink';
import { Task, Color, Spinner } from '@inkjs/ui';

/**
 * Workstream interface representing a tracked implementation workstream
 */
interface Workstream {
  id: string;
  name: string;
  progress: number;  // 0.0 to 1.0
  status: 'not_started' | 'in_progress' | 'completed' | 'blocked';
  description?: string;
  dueDate?: Date;
  tasks?: WorkstreamTask[];
}

/**
 * Task within a workstream
 */
interface WorkstreamTask {
  id: string;
  name: string;
  completed: boolean;
  description?: string;
}

/**
 * Props for the ProgressWidget component
 */
interface ProgressWidgetProps {
  title?: string;
  workstreams: Workstream[];
  onClose?: () => void;
  width?: number;
  height?: number;
}

/**
 * A widget that displays implementation progress for tracked workstreams
 */
const ProgressWidget: React.FC<ProgressWidgetProps> = ({
  title = 'Implementation Progress',
  workstreams = [],
  onClose,
  width = 80,
  height = 20,
}) => {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [showDetailView, setShowDetailView] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Calculate overall progress as average of all workstreams
  const overallProgress = workstreams.length > 0
    ? workstreams.reduce((sum, w) => sum + w.progress, 0) / workstreams.length
    : 0;

  // Handle keyboard input
  useInput((input, key) => {
    if (key.escape) {
      onClose?.();
    } else if (key.return) {
      setShowDetailView(!showDetailView);
    } else if (key.upArrow) {
      setSelectedIndex(prev => 
        prev > 0 ? prev - 1 : workstreams.length - 1
      );
    } else if (key.downArrow) {
      setSelectedIndex(prev => 
        prev < workstreams.length - 1 ? prev + 1 : 0
      );
    } else if (input === 'd') {
      // Toggle detail view with 'd' key
      setShowDetailView(!showDetailView);
    }
  });

  // Get color based on progress
  const getProgressColor = (progress: number): Color => {
    if (progress >= 0.7) return 'green';
    if (progress >= 0.3) return 'yellow';
    return 'red';
  };

  // Get status description
  const getStatusDescription = (status: string): string => {
    switch (status) {
      case 'not_started': return 'Not Started';
      case 'in_progress': return 'In Progress';
      case 'completed': return 'Completed';
      case 'blocked': return 'Blocked';
      default: return status;
    }
  };

  // Get status color
  const getStatusColor = (status: string): Color => {
    switch (status) {
      case 'not_started': return 'gray';
      case 'in_progress': return 'blue';
      case 'completed': return 'green';
      case 'blocked': return 'red';
      default: return 'white';
    }
  };

  // Format progress percentage
  const formatProgress = (progress: number): string => {
    return `${Math.round(progress * 100)}%`;
  };

  // Get selected workstream
  const selectedWorkstream = workstreams[selectedIndex] || null;

  // Demo effect: simulate loading when changing selected workstream
  useEffect(() => {
    if (workstreams.length === 0) return;
    
    setIsLoading(true);
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 300);
    
    return () => clearTimeout(timer);
  }, [selectedIndex]);

  // Render progress bar
  const renderProgressBar = (progress: number, barWidth: number, color: Color) => {
    const filledWidth = Math.round(progress * barWidth);
    const emptyWidth = barWidth - filledWidth;
    
    return (
      <Box>
        <Text color={color}>{'█'.repeat(filledWidth)}</Text>
        <Text color="gray">{'░'.repeat(emptyWidth)}</Text>
      </Box>
    );
  };

  // Show loading spinner while loading
  if (isLoading) {
    return (
      <Box 
        flexDirection="column" 
        borderStyle="round" 
        borderColor="blue"
        width={width}
        height={height}
        padding={1}
      >
        <Box justifyContent="center" alignItems="center" flexGrow={1}>
          <Spinner type="dots" label="Loading workstream details..." />
        </Box>
      </Box>
    );
  }

  // Render detail view for selected workstream
  if (showDetailView && selectedWorkstream) {
    return (
      <Box 
        flexDirection="column" 
        borderStyle="round" 
        borderColor="blue"
        width={width}
        height={height}
        padding={1}
      >
        <Box marginBottom={1}>
          <Text bold color="cyan">{title} / {selectedWorkstream.name}</Text>
        </Box>
        
        <Box flexDirection="column" marginBottom={1}>
          <Text>
            Status: <Text color={getStatusColor(selectedWorkstream.status)}>
              {getStatusDescription(selectedWorkstream.status)}
            </Text>
          </Text>
          
          <Text>
            Progress: <Text color={getProgressColor(selectedWorkstream.progress)}>
              {formatProgress(selectedWorkstream.progress)}
            </Text>
          </Text>
          
          {selectedWorkstream.dueDate && (
            <Text>
              Due Date: <Text color={
                new Date() > selectedWorkstream.dueDate ? 'red' : 'blue'
              }>
                {selectedWorkstream.dueDate.toLocaleDateString()}
              </Text>
            </Text>
          )}
        </Box>
        
        <Box flexDirection="column" marginBottom={1}>
          <Text bold>Description:</Text>
          <Text>{selectedWorkstream.description || 'No description available.'}</Text>
        </Box>
        
        <Box flexDirection="column" marginBottom={1}>
          <Text bold>Tasks:</Text>
          {selectedWorkstream.tasks && selectedWorkstream.tasks.length > 0 ? (
            <Box flexDirection="column" marginLeft={2}>
              {selectedWorkstream.tasks.map(task => (
                <Task 
                  key={task.id}
                  label={task.name}
                  done={task.completed}
                  color={task.completed ? 'green' : 'yellow'}
                />
              ))}
            </Box>
          ) : (
            <Text color="gray">No tasks available.</Text>
          )}
        </Box>
        
        <Box marginTop={1}>
          <Text color="gray">
            Press <Text color="cyan">ESC</Text> to close, 
            <Text color="cyan"> ENTER</Text> to toggle view,
            <Text color="cyan"> ↑/↓</Text> to navigate
          </Text>
        </Box>
      </Box>
    );
  }

  // Render summary view
  return (
    <Box 
      flexDirection="column" 
      borderStyle="round" 
      borderColor="blue"
      width={width}
      height={height}
      padding={1}
    >
      <Box marginBottom={1}>
        <Text bold color="cyan">{title}</Text>
      </Box>
      
      <Box flexDirection="column" marginBottom={1}>
        <Text bold>Overall Progress:</Text>
        <Box>
          {renderProgressBar(overallProgress, 40, getProgressColor(overallProgress))}
          <Text> {formatProgress(overallProgress)}</Text>
        </Box>
      </Box>
      
      <Box flexDirection="column" flexGrow={1}>
        <Text bold>Workstreams:</Text>
        {workstreams.length > 0 ? (
          workstreams.map((workstream, index) => (
            <Box 
              key={workstream.id} 
              flexDirection="column"
              marginLeft={1}
              marginBottom={1}
              backgroundColor={index === selectedIndex ? 'blue' : undefined}
            >
              <Box>
                <Text 
                  color={index === selectedIndex ? 'white' : undefined}
                  bold={index === selectedIndex}
                >
                  {workstream.name}
                </Text>
                <Text> - </Text>
                <Text color={getStatusColor(workstream.status)}>
                  {getStatusDescription(workstream.status)}
                </Text>
              </Box>
              <Box>
                {renderProgressBar(
                  workstream.progress,
                  30,
                  index === selectedIndex 
                    ? 'white' 
                    : getProgressColor(workstream.progress)
                )}
                <Text> {formatProgress(workstream.progress)}</Text>
              </Box>
            </Box>
          ))
        ) : (
          <Text color="gray">No workstreams to display.</Text>
        )}
      </Box>
      
      <Box marginTop={1}>
        <Text color="gray">
          Press <Text color="cyan">ESC</Text> to close, 
          <Text color="cyan"> ENTER</Text> to view details,
          <Text color="cyan"> ↑/↓</Text> to navigate
        </Text>
      </Box>
    </Box>
  );
};

export default ProgressWidget;

/**
 * Example usage:
 * 
 * const workstreams = [
 *   {
 *     id: '1',
 *     name: 'Self-Healing System',
 *     progress: 0.65,
 *     status: 'in_progress',
 *     description: 'Implement self-healing capabilities with circuit breakers and recovery strategies',
 *     dueDate: new Date('2023-06-15'),
 *     tasks: [
 *       { id: '1-1', name: 'Implement health monitoring', completed: true },
 *       { id: '1-2', name: 'Add circuit breaker pattern', completed: true },
 *       { id: '1-3', name: 'Create recovery strategies', completed: false },
 *       { id: '1-4', name: 'Integrate with event system', completed: false }
 *     ]
 *   },
 *   {
 *     id: '2',
 *     name: 'A2A Communication',
 *     progress: 0.40,
 *     status: 'in_progress',
 *     description: 'Implement agent-to-agent communication protocol',
 *     dueDate: new Date('2023-06-30'),
 *     tasks: [
 *       { id: '2-1', name: 'Define message format', completed: true },
 *       { id: '2-2', name: 'Implement agent registry', completed: true },
 *       { id: '2-3', name: 'Create routing system', completed: false },
 *       { id: '2-4', name: 'Add security features', completed: false }
 *     ]
 *   }
 * ];
 * 
 * <ProgressWidget workstreams={workstreams} onClose={() => setShowProgress(false)} />
 */