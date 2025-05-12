import React from 'react';
import PropTypes from 'prop-types';
import { Card } from 'react-bootstrap';

/**
 * IBDProtocolTimeline Component
 * 
 * Displays a timeline visualization of an IBD protocol's assessments and timepoints
 */
const IBDProtocolTimeline = ({ protocol, ibdInfo }) => {
  // Extract assessment schedule from protocol or defaults
  const getAssessmentSchedule = () => {
    if (protocol?.configuration?.requiredAssessments) {
      return protocol.configuration.requiredAssessments;
    }
    
    // Default IBD assessment schedule
    return {
      'colonoscopy': ['baseline', 'week_16'],
      'blood_tests': ['baseline', 'week_4', 'week_8', 'week_16', 'week_24'],
      'stool_tests': ['baseline', 'week_4', 'week_8', 'week_16', 'week_24'],
      'clinical_scores': ['baseline', 'week_4', 'week_8', 'week_16', 'week_24']
    };
  };
  
  // Get all unique timepoints from assessments
  const getAllTimepoints = () => {
    const assessments = getAssessmentSchedule();
    const timepointsSet = new Set();
    
    Object.values(assessments).forEach(timepoints => {
      timepoints.forEach(timepoint => timepointsSet.add(timepoint));
    });
    
    // Sort timepoints
    return Array.from(timepointsSet).sort((a, b) => {
      if (a === 'baseline') return -1;
      if (b === 'baseline') return 1;
      
      // Extract week number for comparison
      const weekA = parseInt(a.replace('week_', ''));
      const weekB = parseInt(b.replace('week_', ''));
      
      return weekA - weekB;
    });
  };
  
  // Format timepoint for display
  const formatTimepoint = (timepoint) => {
    if (timepoint === 'baseline') return 'Baseline';
    return timepoint.replace('week_', 'Week ');
  };
  
  // Get assessment types
  const getAssessmentTypes = () => {
    return Object.keys(getAssessmentSchedule());
  };
  
  // Check if an assessment is scheduled at a timepoint
  const hasAssessment = (assessmentType, timepoint) => {
    const schedule = getAssessmentSchedule();
    return schedule[assessmentType]?.includes(timepoint) || false;
  };
  
  // Get assessment icon/badge
  const getAssessmentBadge = (assessmentType) => {
    switch (assessmentType) {
      case 'colonoscopy':
        return { 
          label: 'Endo', 
          color: '#dc3545', 
          title: 'Endoscopic Assessment (Colonoscopy)'
        };
      case 'blood_tests':
        return { 
          label: 'Blood', 
          color: '#007bff', 
          title: 'Blood Tests (CRP, CBC, Chemistry)'
        };
      case 'stool_tests':
        return { 
          label: 'Stool', 
          color: '#6c757d', 
          title: 'Stool Tests (Calprotectin, Lactoferrin)'
        };
      case 'clinical_scores':
        return { 
          label: 'Score', 
          color: '#28a745', 
          title: 'Clinical Scores (CDAI, HBI)'
        };
      case 'imaging':
        return { 
          label: 'Image', 
          color: '#6610f2', 
          title: 'Imaging (MRI, CT)'
        };
      case 'patient_reported':
        return { 
          label: 'PRO', 
          color: '#fd7e14', 
          title: 'Patient Reported Outcomes'
        };
      default:
        return { 
          label: assessmentType.charAt(0).toUpperCase(), 
          color: '#6c757d',
          title: assessmentType
        };
    }
  };
  
  // Generate row for an assessment type
  const renderAssessmentRow = (assessmentType) => {
    const timepoints = getAllTimepoints();
    const badge = getAssessmentBadge(assessmentType);
    
    return (
      <tr key={assessmentType}>
        <td className="assessment-type">
          <div 
            className="assessment-badge"
            style={{ backgroundColor: badge.color }}
            title={badge.title}
          >
            {badge.label}
          </div>
          <span className="assessment-name">{badge.title}</span>
        </td>
        {timepoints.map(timepoint => (
          <td key={timepoint} className="text-center">
            {hasAssessment(assessmentType, timepoint) && (
              <div 
                className="assessment-dot"
                style={{ backgroundColor: badge.color }}
                title={`${badge.title} at ${formatTimepoint(timepoint)}`}
              />
            )}
          </td>
        ))}
      </tr>
    );
  };
  
  // Render endpoint markers
  const renderEndpointMarkers = () => {
    const timepoints = getAllTimepoints();
    const primaryEndpoint = protocol?.configuration?.endpointDefinitions?.primaryEndpoint || '';
    const secondaryEndpoints = protocol?.configuration?.endpointDefinitions?.secondaryEndpoints || [];
    
    // Extract timepoint from endpoint
    const getTimepointFromEndpoint = (endpoint) => {
      const match = endpoint.match(/week_(\d+)$/);
      return match ? `week_${match[1]}` : null;
    };
    
    // Primary endpoint timepoint
    const primaryEndpointTimepoint = getTimepointFromEndpoint(primaryEndpoint);
    
    // Secondary endpoints timepoints
    const secondaryEndpointTimepoints = secondaryEndpoints
      .map(getTimepointFromEndpoint)
      .filter(Boolean);
    
    return (
      <tr className="endpoint-markers">
        <td>Endpoints</td>
        {timepoints.map(timepoint => (
          <td key={timepoint} className="text-center position-relative">
            {primaryEndpointTimepoint === timepoint && (
              <div 
                className="primary-endpoint-marker"
                title="Primary Endpoint"
              >
                P
              </div>
            )}
            {secondaryEndpointTimepoints.includes(timepoint) && (
              <div 
                className="secondary-endpoint-marker"
                title="Secondary Endpoint"
              >
                S
              </div>
            )}
          </td>
        ))}
      </tr>
    );
  };
  
  const timepoints = getAllTimepoints();
  const assessmentTypes = getAssessmentTypes();
  
  return (
    <Card className="mb-4">
      <Card.Header>
        <h5>Protocol Timeline</h5>
      </Card.Header>
      <Card.Body className="p-0">
        <div className="ibd-protocol-timeline">
          <style>{`
            .ibd-protocol-timeline {
              overflow-x: auto;
            }
            .ibd-protocol-timeline table {
              width: 100%;
              min-width: 600px;
              border-collapse: collapse;
            }
            .ibd-protocol-timeline th, .ibd-protocol-timeline td {
              padding: 10px;
              border-bottom: 1px solid #dee2e6;
              vertical-align: middle;
            }
            .ibd-protocol-timeline th {
              background-color: #f8f9fa;
              font-weight: 600;
              text-align: center;
            }
            .ibd-protocol-timeline .assessment-type {
              min-width: 150px;
              display: flex;
              align-items: center;
            }
            .ibd-protocol-timeline .assessment-badge {
              color: white;
              border-radius: 4px;
              padding: 2px 5px;
              font-size: 0.75rem;
              font-weight: bold;
              margin-right: 8px;
              min-width: 40px;
              text-align: center;
            }
            .ibd-protocol-timeline .assessment-name {
              font-size: 0.85rem;
            }
            .ibd-protocol-timeline .assessment-dot {
              width: 12px;
              height: 12px;
              border-radius: 50%;
              margin: 0 auto;
            }
            .ibd-protocol-timeline .timeline-progress {
              height: 4px;
              background-color: #e9ecef;
              position: relative;
              margin: 10px 0;
            }
            .ibd-protocol-timeline .primary-endpoint-marker {
              position: absolute;
              top: -10px;
              left: 50%;
              transform: translateX(-50%);
              background-color: #dc3545;
              color: white;
              border-radius: 50%;
              width: 20px;
              height: 20px;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 0.75rem;
              font-weight: bold;
            }
            .ibd-protocol-timeline .secondary-endpoint-marker {
              position: absolute;
              top: -10px;
              left: 50%;
              transform: translateX(-50%);
              background-color: #fd7e14;
              color: white;
              border-radius: 50%;
              width: 20px;
              height: 20px;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 0.75rem;
              font-weight: bold;
            }
            .ibd-protocol-timeline .endpoint-markers td {
              border-top: 2px solid #dee2e6;
              background-color: #f8f9fa;
            }
          `}</style>
          
          <table>
            <thead>
              <tr>
                <th>Assessment</th>
                {timepoints.map(timepoint => (
                  <th key={timepoint}>{formatTimepoint(timepoint)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {assessmentTypes.map(assessmentType => 
                renderAssessmentRow(assessmentType)
              )}
              {renderEndpointMarkers()}
            </tbody>
          </table>
        </div>
      </Card.Body>
    </Card>
  );
};

IBDProtocolTimeline.propTypes = {
  protocol: PropTypes.object,
  ibdInfo: PropTypes.object
};

export default IBDProtocolTimeline;