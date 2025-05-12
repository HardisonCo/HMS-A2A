import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Card, Button, Table, Form, Alert, Row, Col, Badge, Spinner, Modal } from 'react-bootstrap';
import { FaPlus, FaTrash, FaEdit, FaBuilding, FaUserShield, FaUsers, FaLink, FaUnlink, FaExchangeAlt, FaLock, FaLockOpen } from 'react-icons/fa';

// Service
import ProtocolService from '../../../services/ProtocolService';

/**
 * MultiInstitutionDataSharingPanel Component
 * 
 * Panel for managing multi-institution data sharing for clinical trials
 * Supports federated learning approach for secure data sharing
 */
const MultiInstitutionDataSharingPanel = ({ protocol, protocolId, readOnly = false }) => {
  // State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [dataSharingEnabled, setDataSharingEnabled] = useState(false);
  const [institutions, setInstitutions] = useState([]);
  const [showAddInstitutionModal, setShowAddInstitutionModal] = useState(false);
  const [showEditInstitutionModal, setShowEditInstitutionModal] = useState(false);
  const [editingInstitution, setEditingInstitution] = useState(null);
  const [federatedModelStatus, setFederatedModelStatus] = useState('inactive');
  
  // New institution form
  const [newInstitution, setNewInstitution] = useState({
    id: '',
    name: '',
    role: 'contributor',
    dataAccessLevel: 'limited'
  });
  
  // Privacy settings
  const [privacySettings, setPrivacySettings] = useState({
    method: 'differentialPrivacy',
    epsilon: 2.0,
    delta: 1e-5
  });
  
  // Protocol service
  const protocolService = new ProtocolService();
  
  // Initialize from protocol data
  useEffect(() => {
    if (protocol) {
      // Check if data sharing is configured
      const hasDataSharing = protocol.configuration && 
                            protocol.configuration.multiInstitutionDataSharing &&
                            protocol.configuration.multiInstitutionDataSharing.enabled;
      
      setDataSharingEnabled(hasDataSharing || false);
      
      // Initialize institutions if available
      if (hasDataSharing && protocol.configuration.multiInstitutionDataSharing.institutions) {
        const institutionsList = Object.entries(protocol.configuration.multiInstitutionDataSharing.institutions)
          .map(([id, data]) => ({
            id,
            name: data.name,
            role: data.role,
            dataAccessLevel: data.dataAccessLevel,
            status: 'connected' // Default status
          }));
        
        setInstitutions(institutionsList);
      }
      
      // Initialize privacy settings if available
      if (hasDataSharing && protocol.configuration.multiInstitutionDataSharing.privacyProtection) {
        setPrivacySettings(protocol.configuration.multiInstitutionDataSharing.privacyProtection);
      }
      
      // Mock federated model status
      if (hasDataSharing) {
        setFederatedModelStatus('active');
      }
    }
  }, [protocol]);
  
  // Handle enabling/disabling data sharing
  const handleToggleDataSharing = async () => {
    if (readOnly) return;
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      if (!dataSharingEnabled) {
        // Initialize with primary institution
        const initialInstitutions = [
          {
            id: 'primary',
            name: 'Primary Research Center',
            role: 'coordinator',
            dataAccessLevel: 'full'
          }
        ];
        
        // Call API to initialize data sharing
        await protocolService.initializeDataSharing(protocolId, initialInstitutions);
        
        // Update local state
        setDataSharingEnabled(true);
        setInstitutions(initialInstitutions.map(inst => ({
          ...inst,
          status: 'connected'
        })));
        
        setSuccess('Multi-institution data sharing has been enabled');
      } else {
        // In a real application, you would call an API to disable data sharing
        // For now, just update local state
        setDataSharingEnabled(false);
        setInstitutions([]);
        setFederatedModelStatus('inactive');
        
        setSuccess('Multi-institution data sharing has been disabled');
      }
      
      setLoading(false);
    } catch (err) {
      setError(`Error: ${err.message}`);
      setLoading(false);
    }
  };
  
  // Handle showing add institution modal
  const handleShowAddInstitutionModal = () => {
    setNewInstitution({
      id: '',
      name: '',
      role: 'contributor',
      dataAccessLevel: 'limited'
    });
    
    setShowAddInstitutionModal(true);
  };
  
  // Handle adding an institution
  const handleAddInstitution = async () => {
    if (!newInstitution.id || !newInstitution.name) return;
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      // Check for duplicate ID
      if (institutions.some(inst => inst.id === newInstitution.id)) {
        setError(`An institution with ID "${newInstitution.id}" already exists`);
        setLoading(false);
        return;
      }
      
      // Add new institution
      const updatedInstitutions = [...institutions, {
        ...newInstitution,
        status: 'connecting' // Initial status
      }];
      
      // Call API to update institutions
      await protocolService.initializeDataSharing(protocolId, updatedInstitutions);
      
      // Update local state - simulate connection after 1 second
      setTimeout(() => {
        setInstitutions(updatedInstitutions.map(inst => 
          inst.id === newInstitution.id 
            ? { ...inst, status: 'connected' } 
            : inst
        ));
      }, 1000);
      
      // Close modal
      setShowAddInstitutionModal(false);
      
      // Update institutions state for immediate feedback
      setInstitutions(updatedInstitutions);
      
      setSuccess(`Institution "${newInstitution.name}" has been added`);
      setLoading(false);
    } catch (err) {
      setError(`Error: ${err.message}`);
      setLoading(false);
    }
  };
  
  // Handle showing edit institution modal
  const handleShowEditInstitutionModal = (institution) => {
    setEditingInstitution(institution);
    setShowEditInstitutionModal(true);
  };
  
  // Handle updating an institution
  const handleUpdateInstitution = async () => {
    if (!editingInstitution) return;
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      // Update institution in list
      const updatedInstitutions = institutions.map(inst => 
        inst.id === editingInstitution.id ? editingInstitution : inst
      );
      
      // Call API to update institutions
      await protocolService.initializeDataSharing(protocolId, updatedInstitutions);
      
      // Update local state
      setInstitutions(updatedInstitutions);
      
      // Close modal
      setShowEditInstitutionModal(false);
      
      setSuccess(`Institution "${editingInstitution.name}" has been updated`);
      setLoading(false);
    } catch (err) {
      setError(`Error: ${err.message}`);
      setLoading(false);
    }
  };
  
  // Handle removing an institution
  const handleRemoveInstitution = async (institutionId) => {
    if (readOnly) return;
    
    // Prevent removing primary institution
    if (institutionId === 'primary') {
      setError('The primary institution cannot be removed');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      // Remove institution from list
      const updatedInstitutions = institutions.filter(inst => inst.id !== institutionId);
      
      // Call API to update institutions
      await protocolService.initializeDataSharing(protocolId, updatedInstitutions);
      
      // Update local state
      setInstitutions(updatedInstitutions);
      
      setSuccess('Institution has been removed');
      setLoading(false);
    } catch (err) {
      setError(`Error: ${err.message}`);
      setLoading(false);
    }
  };
  
  // Handle toggling institution connection status
  const handleToggleConnectionStatus = async (institutionId) => {
    if (readOnly) return;
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      // Update institution status
      const updatedInstitutions = institutions.map(inst => {
        if (inst.id === institutionId) {
          const newStatus = inst.status === 'connected' ? 'disconnected' : 'connected';
          return { ...inst, status: newStatus };
        }
        return inst;
      });
      
      // Call API to update institutions (in a real app)
      // For now, just update local state
      setInstitutions(updatedInstitutions);
      
      setSuccess('Institution connection status has been updated');
      setLoading(false);
    } catch (err) {
      setError(`Error: ${err.message}`);
      setLoading(false);
    }
  };
  
  // Handle updating privacy settings
  const handleUpdatePrivacySettings = async () => {
    if (readOnly) return;
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      // Call API to update privacy settings (in a real app)
      // For now, just update local state
      setTimeout(() => {
        setSuccess('Privacy settings have been updated');
        setLoading(false);
      }, 1000);
    } catch (err) {
      setError(`Error: ${err.message}`);
      setLoading(false);
    }
  };
  
  // Handle starting/stopping federated model
  const handleToggleFederatedModel = async () => {
    if (readOnly) return;
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      // Toggle status
      const newStatus = federatedModelStatus === 'active' ? 'inactive' : 'active';
      
      // Call API to update status (in a real app)
      // For now, just update local state
      setTimeout(() => {
        setFederatedModelStatus(newStatus);
        setSuccess(`Federated model is now ${newStatus}`);
        setLoading(false);
      }, 1000);
    } catch (err) {
      setError(`Error: ${err.message}`);
      setLoading(false);
    }
  };
  
  // Get institution role badge
  const getInstitutionRoleBadge = (role) => {
    switch (role) {
      case 'coordinator':
        return <Badge variant="primary">Coordinator</Badge>;
      case 'contributor':
        return <Badge variant="success">Contributor</Badge>;
      case 'monitor':
        return <Badge variant="info">Monitor</Badge>;
      default:
        return <Badge variant="secondary">{role}</Badge>;
    }
  };
  
  // Get institution access level badge
  const getInstitutionAccessLevelBadge = (level) => {
    switch (level) {
      case 'full':
        return <Badge variant="danger">Full Access</Badge>;
      case 'limited':
        return <Badge variant="warning">Limited Access</Badge>;
      case 'restricted':
        return <Badge variant="secondary">Restricted Access</Badge>;
      default:
        return <Badge variant="secondary">{level}</Badge>;
    }
  };
  
  // Get institution status badge
  const getInstitutionStatusBadge = (status) => {
    switch (status) {
      case 'connected':
        return <Badge variant="success">Connected</Badge>;
      case 'connecting':
        return <Badge variant="warning">Connecting...</Badge>;
      case 'disconnected':
        return <Badge variant="danger">Disconnected</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };
  
  // Render
  return (
    <div className="multi-institution-data-sharing-panel">
      {/* Loading Spinner */}
      {loading && (
        <div className="text-center my-3">
          <Spinner animation="border" role="status" size="sm" className="mr-2" />
          <span>Loading...</span>
        </div>
      )}
      
      {/* Error Alert */}
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {/* Success Alert */}
      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}
      
      {/* Data Sharing Toggle */}
      <Card className="mb-4">
        <Card.Header>
          <h5 className="d-flex align-items-center">
            <FaExchangeAlt className="mr-2" />
            Multi-Institution Data Sharing
            {dataSharingEnabled && (
              <Badge variant="success" className="ml-2">Enabled</Badge>
            )}
          </h5>
        </Card.Header>
        <Card.Body>
          <p>
            Enable secure data sharing between multiple institutions for this IBD protocol.
            Data sharing uses a federated learning approach to keep data at the source institution
            while still enabling collaborative analysis.
          </p>
          
          <div className="text-center">
            <Button
              variant={dataSharingEnabled ? "danger" : "success"}
              disabled={loading || readOnly}
              onClick={handleToggleDataSharing}
            >
              {dataSharingEnabled ? (
                <>
                  <FaUnlink className="mr-1" /> Disable Data Sharing
                </>
              ) : (
                <>
                  <FaLink className="mr-1" /> Enable Data Sharing
                </>
              )}
            </Button>
          </div>
        </Card.Body>
      </Card>
      
      {/* Institutions Management - Only shown when data sharing is enabled */}
      {dataSharingEnabled && (
        <Card className="mb-4">
          <Card.Header>
            <h5 className="d-flex align-items-center justify-content-between">
              <span>
                <FaBuilding className="mr-2" />
                Participating Institutions
              </span>
              {!readOnly && (
                <Button
                  variant="success"
                  size="sm"
                  onClick={handleShowAddInstitutionModal}
                  disabled={loading}
                >
                  <FaPlus className="mr-1" /> Add Institution
                </Button>
              )}
            </h5>
          </Card.Header>
          <Card.Body className="p-0">
            <Table striped hover responsive className="mb-0">
              <thead>
                <tr>
                  <th>Institution</th>
                  <th>Role</th>
                  <th>Access Level</th>
                  <th>Status</th>
                  {!readOnly && <th>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {institutions.length > 0 ? (
                  institutions.map(institution => (
                    <tr key={institution.id}>
                      <td>
                        <strong>{institution.name}</strong>
                        <div className="text-muted small">ID: {institution.id}</div>
                      </td>
                      <td>{getInstitutionRoleBadge(institution.role)}</td>
                      <td>{getInstitutionAccessLevelBadge(institution.dataAccessLevel)}</td>
                      <td>{getInstitutionStatusBadge(institution.status)}</td>
                      {!readOnly && (
                        <td>
                          <Button
                            variant="outline-secondary"
                            size="sm"
                            className="mr-1"
                            onClick={() => handleShowEditInstitutionModal(institution)}
                            disabled={loading}
                          >
                            <FaEdit />
                          </Button>
                          <Button
                            variant={institution.status === 'connected' ? "outline-danger" : "outline-success"}
                            size="sm"
                            className="mr-1"
                            onClick={() => handleToggleConnectionStatus(institution.id)}
                            disabled={loading || institution.status === 'connecting'}
                            title={institution.status === 'connected' ? "Disconnect" : "Connect"}
                          >
                            {institution.status === 'connected' ? <FaUnlink /> : <FaLink />}
                          </Button>
                          {institution.id !== 'primary' && (
                            <Button
                              variant="outline-danger"
                              size="sm"
                              onClick={() => handleRemoveInstitution(institution.id)}
                              disabled={loading}
                              title="Remove"
                            >
                              <FaTrash />
                            </Button>
                          )}
                        </td>
                      )}
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={readOnly ? 4 : 5} className="text-center">
                      No institutions configured
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
      )}
      
      {/* Privacy Settings - Only shown when data sharing is enabled */}
      {dataSharingEnabled && (
        <Row>
          <Col md={6}>
            <Card className="mb-4">
              <Card.Header>
                <h5>
                  <FaUserShield className="mr-2" />
                  Privacy Protection
                </h5>
              </Card.Header>
              <Card.Body>
                <Form>
                  <Form.Group>
                    <Form.Label>Privacy Method</Form.Label>
                    <Form.Control
                      as="select"
                      value={privacySettings.method}
                      onChange={(e) => setPrivacySettings({ ...privacySettings, method: e.target.value })}
                      disabled={readOnly}
                    >
                      <option value="differentialPrivacy">Differential Privacy</option>
                      <option value="federated">Federated Learning</option>
                      <option value="hybrid">Hybrid Approach</option>
                    </Form.Control>
                    <Form.Text className="text-muted">
                      The method used to protect patient privacy during data sharing
                    </Form.Text>
                  </Form.Group>
                  
                  {privacySettings.method === 'differentialPrivacy' && (
                    <>
                      <Form.Group>
                        <Form.Label>Epsilon Value (ε)</Form.Label>
                        <Form.Control
                          type="number"
                          step="0.1"
                          min="0.1"
                          max="10"
                          value={privacySettings.epsilon}
                          onChange={(e) => setPrivacySettings({ ...privacySettings, epsilon: parseFloat(e.target.value) })}
                          disabled={readOnly}
                        />
                        <Form.Text className="text-muted">
                          Controls privacy level - lower values mean stronger privacy (recommended: 1.0-3.0)
                        </Form.Text>
                      </Form.Group>
                      
                      <Form.Group>
                        <Form.Label>Delta Value (δ)</Form.Label>
                        <Form.Control
                          type="number"
                          step="0.00001"
                          min="0.00001"
                          max="0.1"
                          value={privacySettings.delta}
                          onChange={(e) => setPrivacySettings({ ...privacySettings, delta: parseFloat(e.target.value) })}
                          disabled={readOnly}
                        />
                        <Form.Text className="text-muted">
                          Probability of privacy failure (recommended: 1e-5 or smaller)
                        </Form.Text>
                      </Form.Group>
                    </>
                  )}
                  
                  {!readOnly && (
                    <Button
                      variant="primary"
                      onClick={handleUpdatePrivacySettings}
                      disabled={loading}
                    >
                      Update Privacy Settings
                    </Button>
                  )}
                </Form>
              </Card.Body>
            </Card>
          </Col>
          <Col md={6}>
            <Card className="mb-4">
              <Card.Header>
                <h5>
                  <FaUsers className="mr-2" />
                  Federated Model
                </h5>
              </Card.Header>
              <Card.Body>
                <div className="d-flex align-items-center mb-3">
                  <div>
                    <h6>Status</h6>
                    <Badge 
                      variant={federatedModelStatus === 'active' ? 'success' : 'danger'}
                      className="py-1 px-2"
                    >
                      {federatedModelStatus === 'active' ? (
                        <>
                          <FaLock className="mr-1" /> Active
                        </>
                      ) : (
                        <>
                          <FaLockOpen className="mr-1" /> Inactive
                        </>
                      )}
                    </Badge>
                  </div>
                  
                  {!readOnly && (
                    <Button
                      variant={federatedModelStatus === 'active' ? 'outline-danger' : 'outline-success'}
                      className="ml-auto"
                      onClick={handleToggleFederatedModel}
                      disabled={loading || institutions.length < 2}
                    >
                      {federatedModelStatus === 'active' ? 'Stop Model' : 'Start Model'}
                    </Button>
                  )}
                </div>
                
                {institutions.length < 2 && (
                  <Alert variant="warning">
                    At least 2 connected institutions are required to start the federated model
                  </Alert>
                )}
                
                <h6>Shared Data</h6>
                <Form.Group>
                  <div className="mb-2">
                    <Form.Check
                      type="checkbox"
                      id="share-clinical"
                      label="Clinical Data"
                      checked
                      disabled={true}
                    />
                  </div>
                  <div className="mb-2">
                    <Form.Check
                      type="checkbox"
                      id="share-biomarker"
                      label="Biomarker Data"
                      checked
                      disabled={true}
                    />
                  </div>
                  <div className="mb-2">
                    <Form.Check
                      type="checkbox"
                      id="share-imaging"
                      label="Imaging Data"
                      checked
                      disabled={true}
                    />
                  </div>
                  <div>
                    <Form.Check
                      type="checkbox"
                      id="share-pro"
                      label="Patient Reported Outcomes"
                      checked
                      disabled={true}
                    />
                  </div>
                </Form.Group>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
      
      {/* Add Institution Modal */}
      <Modal
        show={showAddInstitutionModal}
        onHide={() => setShowAddInstitutionModal(false)}
        backdrop="static"
      >
        <Modal.Header closeButton>
          <Modal.Title>Add Institution</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group>
              <Form.Label>Institution ID</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g., site_1"
                value={newInstitution.id}
                onChange={(e) => setNewInstitution({ ...newInstitution, id: e.target.value })}
                disabled={loading}
              />
              <Form.Text className="text-muted">
                Unique identifier for the institution (no spaces)
              </Form.Text>
            </Form.Group>
            
            <Form.Group>
              <Form.Label>Institution Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g., Research Hospital"
                value={newInstitution.name}
                onChange={(e) => setNewInstitution({ ...newInstitution, name: e.target.value })}
                disabled={loading}
              />
            </Form.Group>
            
            <Form.Group>
              <Form.Label>Role</Form.Label>
              <Form.Control
                as="select"
                value={newInstitution.role}
                onChange={(e) => setNewInstitution({ ...newInstitution, role: e.target.value })}
                disabled={loading}
              >
                <option value="coordinator">Coordinator</option>
                <option value="contributor">Contributor</option>
                <option value="monitor">Monitor</option>
              </Form.Control>
            </Form.Group>
            
            <Form.Group>
              <Form.Label>Data Access Level</Form.Label>
              <Form.Control
                as="select"
                value={newInstitution.dataAccessLevel}
                onChange={(e) => setNewInstitution({ ...newInstitution, dataAccessLevel: e.target.value })}
                disabled={loading}
              >
                <option value="full">Full Access</option>
                <option value="limited">Limited Access</option>
                <option value="restricted">Restricted Access</option>
              </Form.Control>
              <Form.Text className="text-muted">
                Determines what data this institution can access from other participants
              </Form.Text>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={() => setShowAddInstitutionModal(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={handleAddInstitution}
            disabled={loading || !newInstitution.id || !newInstitution.name}
          >
            Add Institution
          </Button>
        </Modal.Footer>
      </Modal>
      
      {/* Edit Institution Modal */}
      <Modal
        show={showEditInstitutionModal}
        onHide={() => setShowEditInstitutionModal(false)}
        backdrop="static"
      >
        <Modal.Header closeButton>
          <Modal.Title>Edit Institution</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {editingInstitution && (
            <Form>
              <Form.Group>
                <Form.Label>Institution ID</Form.Label>
                <Form.Control
                  type="text"
                  value={editingInstitution.id}
                  disabled
                />
                <Form.Text className="text-muted">
                  Institution ID cannot be changed
                </Form.Text>
              </Form.Group>
              
              <Form.Group>
                <Form.Label>Institution Name</Form.Label>
                <Form.Control
                  type="text"
                  value={editingInstitution.name}
                  onChange={(e) => setEditingInstitution({ ...editingInstitution, name: e.target.value })}
                  disabled={loading}
                />
              </Form.Group>
              
              <Form.Group>
                <Form.Label>Role</Form.Label>
                <Form.Control
                  as="select"
                  value={editingInstitution.role}
                  onChange={(e) => setEditingInstitution({ ...editingInstitution, role: e.target.value })}
                  disabled={loading || editingInstitution.id === 'primary'}
                >
                  <option value="coordinator">Coordinator</option>
                  <option value="contributor">Contributor</option>
                  <option value="monitor">Monitor</option>
                </Form.Control>
                {editingInstitution.id === 'primary' && (
                  <Form.Text className="text-muted">
                    Primary institution must be a coordinator
                  </Form.Text>
                )}
              </Form.Group>
              
              <Form.Group>
                <Form.Label>Data Access Level</Form.Label>
                <Form.Control
                  as="select"
                  value={editingInstitution.dataAccessLevel}
                  onChange={(e) => setEditingInstitution({ ...editingInstitution, dataAccessLevel: e.target.value })}
                  disabled={loading || editingInstitution.id === 'primary'}
                >
                  <option value="full">Full Access</option>
                  <option value="limited">Limited Access</option>
                  <option value="restricted">Restricted Access</option>
                </Form.Control>
                {editingInstitution.id === 'primary' && (
                  <Form.Text className="text-muted">
                    Primary institution must have full access
                  </Form.Text>
                )}
              </Form.Group>
            </Form>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={() => setShowEditInstitutionModal(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={handleUpdateInstitution}
            disabled={loading || !editingInstitution || !editingInstitution.name}
          >
            Update Institution
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

MultiInstitutionDataSharingPanel.propTypes = {
  protocol: PropTypes.object,
  protocolId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  readOnly: PropTypes.bool
};

export default MultiInstitutionDataSharingPanel;