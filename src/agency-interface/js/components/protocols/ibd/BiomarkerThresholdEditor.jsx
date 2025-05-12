import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Form, Button, Table, InputGroup } from 'react-bootstrap';
import { FaPlus, FaTrash, FaSave } from 'react-icons/fa';

/**
 * BiomarkerThresholdEditor Component
 * 
 * Allows editing of biomarker thresholds for IBD protocols
 */
const BiomarkerThresholdEditor = ({ thresholds, onUpdate, readOnly = false }) => {
  // State for edited thresholds
  const [editedThresholds, setEditedThresholds] = useState({});
  const [hasChanges, setHasChanges] = useState(false);
  const [newBiomarker, setNewBiomarker] = useState({ name: '', value: '' });
  
  // IBD-specific biomarker descriptions
  const biomarkerDescriptions = {
    'fecal_calprotectin': 'Fecal inflammatory marker (µg/g)',
    'CRP': 'C-Reactive Protein (mg/L)',
    'CDAI': 'Crohn\'s Disease Activity Index',
    'HBI': 'Harvey-Bradshaw Index',
    'fecal_lactoferrin': 'Fecal inflammatory marker (µg/mL)',
    'IL-6': 'Interleukin-6 cytokine (pg/mL)',
    'TNF-alpha': 'Tumor Necrosis Factor alpha (pg/mL)',
    'ASCA_IgA': 'Anti-Saccharomyces cerevisiae antibody IgA',
    'ASCA_IgG': 'Anti-Saccharomyces cerevisiae antibody IgG',
    'microbiome_diversity_index': 'Gut microbiome diversity measure',
    'metagenomic_risk_score': 'Metagenomics-based risk assessment'
  };
  
  // Initialize edited thresholds from props
  useEffect(() => {
    setEditedThresholds(thresholds || {});
  }, [thresholds]);
  
  // Handle threshold value change
  const handleThresholdChange = (biomarker, value) => {
    // Convert to number if possible
    const parsedValue = !isNaN(parseFloat(value)) ? parseFloat(value) : value;
    
    setEditedThresholds(prev => ({
      ...prev,
      [biomarker]: parsedValue
    }));
    
    setHasChanges(true);
  };
  
  // Handle adding a new biomarker
  const handleAddBiomarker = () => {
    if (!newBiomarker.name || !newBiomarker.value) return;
    
    // Convert to number if possible
    const parsedValue = !isNaN(parseFloat(newBiomarker.value)) 
      ? parseFloat(newBiomarker.value) 
      : newBiomarker.value;
    
    setEditedThresholds(prev => ({
      ...prev,
      [newBiomarker.name]: parsedValue
    }));
    
    // Reset form
    setNewBiomarker({ name: '', value: '' });
    setHasChanges(true);
  };
  
  // Handle removing a biomarker
  const handleRemoveBiomarker = (biomarker) => {
    setEditedThresholds(prev => {
      const updated = { ...prev };
      delete updated[biomarker];
      return updated;
    });
    
    setHasChanges(true);
  };
  
  // Handle saving changes
  const handleSave = () => {
    onUpdate(editedThresholds);
    setHasChanges(false);
  };
  
  return (
    <div className="biomarker-threshold-editor">
      {/* Biomarker Thresholds Table */}
      <Table striped bordered hover size="sm">
        <thead>
          <tr>
            <th>Biomarker</th>
            <th>Threshold</th>
            {!readOnly && <th width="80">Actions</th>}
          </tr>
        </thead>
        <tbody>
          {Object.entries(editedThresholds).map(([biomarker, value]) => (
            <tr key={biomarker}>
              <td>
                {biomarker}
                {biomarkerDescriptions[biomarker] && (
                  <small className="d-block text-muted">
                    {biomarkerDescriptions[biomarker]}
                  </small>
                )}
              </td>
              <td>
                {readOnly ? (
                  value
                ) : (
                  <Form.Control
                    type="text"
                    value={value}
                    onChange={(e) => handleThresholdChange(biomarker, e.target.value)}
                    size="sm"
                  />
                )}
              </td>
              {!readOnly && (
                <td className="text-center">
                  <Button
                    variant="outline-danger"
                    size="sm"
                    onClick={() => handleRemoveBiomarker(biomarker)}
                  >
                    <FaTrash />
                  </Button>
                </td>
              )}
            </tr>
          ))}
          
          {/* Empty state message */}
          {Object.keys(editedThresholds).length === 0 && (
            <tr>
              <td colSpan={readOnly ? 2 : 3} className="text-center">
                No biomarker thresholds defined
              </td>
            </tr>
          )}
        </tbody>
      </Table>
      
      {/* Add New Biomarker Form */}
      {!readOnly && (
        <>
          <h6>Add Biomarker</h6>
          <Form.Row className="align-items-end mb-3">
            <div className="col-md-5 mb-2 mb-md-0">
              <Form.Group controlId="biomarkerName" className="mb-0">
                <Form.Label>Biomarker</Form.Label>
                <Form.Control
                  type="text"
                  value={newBiomarker.name}
                  onChange={(e) => setNewBiomarker(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., CRP"
                  size="sm"
                />
              </Form.Group>
            </div>
            <div className="col-md-5 mb-2 mb-md-0">
              <Form.Group controlId="biomarkerValue" className="mb-0">
                <Form.Label>Threshold</Form.Label>
                <Form.Control
                  type="text"
                  value={newBiomarker.value}
                  onChange={(e) => setNewBiomarker(prev => ({ ...prev, value: e.target.value }))}
                  placeholder="e.g., 5"
                  size="sm"
                />
              </Form.Group>
            </div>
            <div className="col-md-2">
              <Button
                variant="success"
                size="sm"
                block
                onClick={handleAddBiomarker}
                disabled={!newBiomarker.name || !newBiomarker.value}
              >
                <FaPlus className="mr-1" /> Add
              </Button>
            </div>
          </Form.Row>
          
          {/* Save Changes Button */}
          <div className="text-right">
            <Button
              variant="primary"
              onClick={handleSave}
              disabled={!hasChanges}
            >
              <FaSave className="mr-1" /> Save Changes
            </Button>
          </div>
        </>
      )}
    </div>
  );
};

BiomarkerThresholdEditor.propTypes = {
  thresholds: PropTypes.object.isRequired,
  onUpdate: PropTypes.func.isRequired,
  readOnly: PropTypes.bool
};

export default BiomarkerThresholdEditor;