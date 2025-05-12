import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Form, Button, Card, InputGroup, ListGroup } from 'react-bootstrap';
import { FaPlus, FaTrash, FaSave, FaArrowUp, FaArrowDown } from 'react-icons/fa';

/**
 * EndpointDefinitionEditor Component
 * 
 * Allows editing of primary and secondary endpoints for IBD protocols
 */
const EndpointDefinitionEditor = ({ endpoints, onUpdate, readOnly = false }) => {
  // State for edited endpoints
  const [primaryEndpoint, setPrimaryEndpoint] = useState('');
  const [secondaryEndpoints, setSecondaryEndpoints] = useState([]);
  const [newEndpoint, setNewEndpoint] = useState('');
  const [hasChanges, setHasChanges] = useState(false);
  
  // Common IBD endpoints for suggestions
  const commonIBDEndpoints = [
    'clinical_remission_week_16',
    'mucosal_healing_week_16',
    'clinical_response_week_8',
    'corticosteroid_free_remission_week_24',
    'fecal_calprotectin_normalization_week_8',
    'quality_of_life_improvement_week_16',
    'sustained_remission_week_52',
    'endoscopic_healing_week_24',
    'histologic_remission_week_16',
    'biomarker_normalization_week_8'
  ];
  
  // IBD endpoint descriptions
  const endpointDescriptions = {
    'clinical_remission_week_16': 'CDAI < 150 or HBI < 5 at Week 16',
    'mucosal_healing_week_16': 'Absence of ulcerations at Week 16 colonoscopy',
    'clinical_response_week_8': 'Decrease in CDAI ≥ 100 points at Week 8',
    'corticosteroid_free_remission_week_24': 'Clinical remission without corticosteroids at Week 24',
    'fecal_calprotectin_normalization_week_8': 'Fecal calprotectin < 250 μg/g at Week 8',
    'quality_of_life_improvement_week_16': 'IBDQ increase ≥ 16 points at Week 16',
    'sustained_remission_week_52': 'Clinical remission at both Week 16 and Week 52',
    'endoscopic_healing_week_24': 'SES-CD score < 3 at Week 24',
    'histologic_remission_week_16': 'Absence of neutrophil infiltration in Week 16 biopsies',
    'biomarker_normalization_week_8': 'Normalization of CRP (< 5 mg/L) at Week 8'
  };
  
  // Initialize from props
  useEffect(() => {
    if (endpoints) {
      setPrimaryEndpoint(endpoints.primaryEndpoint || '');
      setSecondaryEndpoints(endpoints.secondaryEndpoints || []);
    }
  }, [endpoints]);
  
  // Handle primary endpoint change
  const handlePrimaryEndpointChange = (value) => {
    setPrimaryEndpoint(value);
    setHasChanges(true);
  };
  
  // Handle adding a secondary endpoint
  const handleAddSecondaryEndpoint = () => {
    if (!newEndpoint || secondaryEndpoints.includes(newEndpoint)) return;
    
    setSecondaryEndpoints(prev => [...prev, newEndpoint]);
    setNewEndpoint('');
    setHasChanges(true);
  };
  
  // Handle removing a secondary endpoint
  const handleRemoveSecondaryEndpoint = (index) => {
    setSecondaryEndpoints(prev => prev.filter((_, i) => i !== index));
    setHasChanges(true);
  };
  
  // Handle moving a secondary endpoint up or down
  const handleMoveSecondaryEndpoint = (index, direction) => {
    if (
      (direction === 'up' && index === 0) || 
      (direction === 'down' && index === secondaryEndpoints.length - 1)
    ) {
      return;
    }
    
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    const updatedEndpoints = [...secondaryEndpoints];
    const endpoint = updatedEndpoints[index];
    
    updatedEndpoints.splice(index, 1); // Remove from old position
    updatedEndpoints.splice(newIndex, 0, endpoint); // Insert at new position
    
    setSecondaryEndpoints(updatedEndpoints);
    setHasChanges(true);
  };
  
  // Handle saving changes
  const handleSave = () => {
    onUpdate({
      primaryEndpoint,
      secondaryEndpoints
    });
    
    setHasChanges(false);
  };
  
  // Get description for an endpoint
  const getEndpointDescription = (endpoint) => {
    return endpointDescriptions[endpoint] || '';
  };
  
  return (
    <div className="endpoint-definition-editor">
      {/* Primary Endpoint */}
      <Card className="mb-4">
        <Card.Header>
          <h5>Primary Endpoint</h5>
        </Card.Header>
        <Card.Body>
          {readOnly ? (
            <div>
              <h6>{primaryEndpoint}</h6>
              {getEndpointDescription(primaryEndpoint) && (
                <p className="text-muted">
                  {getEndpointDescription(primaryEndpoint)}
                </p>
              )}
            </div>
          ) : (
            <>
              <Form.Group>
                <Form.Label>Primary Endpoint</Form.Label>
                <Form.Control
                  as="select"
                  value={primaryEndpoint}
                  onChange={(e) => handlePrimaryEndpointChange(e.target.value)}
                >
                  <option value="">-- Select Primary Endpoint --</option>
                  {commonIBDEndpoints.map(endpoint => (
                    <option key={endpoint} value={endpoint}>
                      {endpoint}
                    </option>
                  ))}
                </Form.Control>
                {primaryEndpoint && getEndpointDescription(primaryEndpoint) && (
                  <Form.Text className="text-muted">
                    {getEndpointDescription(primaryEndpoint)}
                  </Form.Text>
                )}
              </Form.Group>
            </>
          )}
        </Card.Body>
      </Card>
      
      {/* Secondary Endpoints */}
      <Card>
        <Card.Header>
          <h5>Secondary Endpoints</h5>
        </Card.Header>
        <Card.Body>
          {/* Secondary Endpoints List */}
          {secondaryEndpoints.length > 0 ? (
            <ListGroup className="mb-3">
              {secondaryEndpoints.map((endpoint, index) => (
                <ListGroup.Item key={index} className="d-flex align-items-center">
                  <div className="flex-grow-1">
                    <div>{endpoint}</div>
                    {getEndpointDescription(endpoint) && (
                      <small className="text-muted">
                        {getEndpointDescription(endpoint)}
                      </small>
                    )}
                  </div>
                  {!readOnly && (
                    <div className="ml-auto d-flex">
                      <Button
                        variant="outline-secondary"
                        size="sm"
                        className="mr-1"
                        onClick={() => handleMoveSecondaryEndpoint(index, 'up')}
                        disabled={index === 0}
                      >
                        <FaArrowUp />
                      </Button>
                      <Button
                        variant="outline-secondary"
                        size="sm"
                        className="mr-1"
                        onClick={() => handleMoveSecondaryEndpoint(index, 'down')}
                        disabled={index === secondaryEndpoints.length - 1}
                      >
                        <FaArrowDown />
                      </Button>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleRemoveSecondaryEndpoint(index)}
                      >
                        <FaTrash />
                      </Button>
                    </div>
                  )}
                </ListGroup.Item>
              ))}
            </ListGroup>
          ) : (
            <p className="text-center text-muted">No secondary endpoints defined</p>
          )}
          
          {/* Add Secondary Endpoint Form */}
          {!readOnly && (
            <>
              <h6>Add Secondary Endpoint</h6>
              <Form.Row className="align-items-end mb-3">
                <div className="col-md-10 mb-2 mb-md-0">
                  <Form.Group controlId="secondaryEndpoint" className="mb-0">
                    <Form.Control
                      as="select"
                      value={newEndpoint}
                      onChange={(e) => setNewEndpoint(e.target.value)}
                    >
                      <option value="">-- Select Secondary Endpoint --</option>
                      {commonIBDEndpoints
                        .filter(endpoint => 
                          endpoint !== primaryEndpoint && 
                          !secondaryEndpoints.includes(endpoint)
                        )
                        .map(endpoint => (
                          <option key={endpoint} value={endpoint}>
                            {endpoint}
                          </option>
                        ))
                      }
                    </Form.Control>
                    {newEndpoint && getEndpointDescription(newEndpoint) && (
                      <Form.Text className="text-muted">
                        {getEndpointDescription(newEndpoint)}
                      </Form.Text>
                    )}
                  </Form.Group>
                </div>
                <div className="col-md-2">
                  <Button
                    variant="success"
                    size="sm"
                    block
                    onClick={handleAddSecondaryEndpoint}
                    disabled={!newEndpoint || secondaryEndpoints.includes(newEndpoint)}
                  >
                    <FaPlus className="mr-1" /> Add
                  </Button>
                </div>
              </Form.Row>
            </>
          )}
          
          {/* Save Changes Button */}
          {!readOnly && (
            <div className="text-right">
              <Button
                variant="primary"
                onClick={handleSave}
                disabled={!hasChanges}
              >
                <FaSave className="mr-1" /> Save Changes
              </Button>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

EndpointDefinitionEditor.propTypes = {
  endpoints: PropTypes.shape({
    primaryEndpoint: PropTypes.string,
    secondaryEndpoints: PropTypes.array
  }),
  onUpdate: PropTypes.func.isRequired,
  readOnly: PropTypes.bool
};

export default EndpointDefinitionEditor;