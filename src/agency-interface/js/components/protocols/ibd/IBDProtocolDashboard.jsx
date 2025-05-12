import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Card, Row, Col, Tabs, Tab, Button, Alert, Spinner } from 'react-bootstrap';
import { FaFlask, FaChartLine, FaUsers, FaDna, FaMicroscope, FaCloudUploadAlt } from 'react-icons/fa';

// Components
import BiomarkerThresholdEditor from './BiomarkerThresholdEditor';
import EndpointDefinitionEditor from './EndpointDefinitionEditor';
import IBDProtocolTimeline from './IBDProtocolTimeline';
import ClinicalScoresTrend from './ClinicalScoresTrend';
import ProtocolStructureViewer from './ProtocolStructureViewer';
import HPCIntegrationPanel from '../hpc/HPCIntegrationPanel';
import AIModulePanel from '../ai/AIModulePanel';
import MultiInstitutionDataSharingPanel from '../sharing/MultiInstitutionDataSharingPanel';

// Services
import ProtocolService from '../../../services/ProtocolService';

/**
 * IBD Protocol Dashboard Component
 * 
 * Comprehensive dashboard for IBD protocol management with
 * specialized visualizations and integration with HPC and AI modules
 */
const IBDProtocolDashboard = ({ protocolId, readOnly = false }) => {
  // State
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [protocol, setProtocol] = useState(null);
  const [ibdInfo, setIbdInfo] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [aiInsights, setAiInsights] = useState(null);
  const [hasHpc, setHasHpc] = useState(false);
  const [aiModuleType, setAiModuleType] = useState(null);
  
  // Services
  const protocolService = new ProtocolService();
  
  // Load protocol data
  useEffect(() => {
    async function loadProtocolData() {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch protocol data
        const protocolData = await protocolService.getProtocol(protocolId);
        setProtocol(protocolData);
        
        // Determine if protocol has HPC capabilities
        setHasHpc(protocolService.hasHPCCapabilities(protocolData));
        
        // Determine appropriate AI module type
        setAiModuleType(protocolService.getAppropriateAIModule(protocolData));
        
        // Fetch IBD-specific information
        const ibdData = await protocolService.getIBDProtocolInfo(protocolId);
        setIbdInfo(ibdData);
        
        setLoading(false);
      } catch (err) {
        setError(`Error loading protocol: ${err.message}`);
        setLoading(false);
      }
    }
    
    loadProtocolData();
  }, [protocolId]);
  
  // Generate AI insights
  const handleGenerateInsights = async () => {
    if (!protocol || !aiModuleType) return;
    
    try {
      setLoading(true);
      const insights = await protocolService.generateAIInsights(protocol);
      setAiInsights(insights);
      setLoading(false);
    } catch (err) {
      setError(`Error generating AI insights: ${err.message}`);
      setLoading(false);
    }
  };
  
  // Update biomarker thresholds
  const handleUpdateBiomarkerThresholds = async (thresholds) => {
    if (!protocol || readOnly) return;
    
    try {
      setLoading(true);
      const updated = await protocolService.updateBiomarkerThresholds(protocolId, thresholds);
      
      // Update local state
      setProtocol(prevState => ({
        ...prevState,
        configuration: {
          ...prevState.configuration,
          biomarkerThresholds: updated
        }
      }));
      
      setLoading(false);
    } catch (err) {
      setError(`Error updating biomarker thresholds: ${err.message}`);
      setLoading(false);
    }
  };
  
  // Update IBD settings
  const handleUpdateIBDSettings = async (settings) => {
    if (!protocol || readOnly) return;
    
    try {
      setLoading(true);
      const updated = await protocolService.updateIBDProtocolSettings(protocolId, settings);
      
      // Update local state
      setIbdInfo(updated);
      
      setLoading(false);
    } catch (err) {
      setError(`Error updating IBD settings: ${err.message}`);
      setLoading(false);
    }
  };
  
  // Render loading state
  if (loading && !protocol) {
    return (
      <div className="text-center p-5">
        <Spinner animation="border" role="status">
          <span className="sr-only">Loading...</span>
        </Spinner>
        <p className="mt-2">Loading protocol data...</p>
      </div>
    );
  }
  
  // Render error state
  if (error && !protocol) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error</Alert.Heading>
        <p>{error}</p>
      </Alert>
    );
  }
  
  // Render protocol dashboard
  return (
    <div className="ibd-protocol-dashboard">
      {/* Protocol Header */}
      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={8}>
              <h2>{protocol?.name || 'IBD Protocol'}</h2>
              <p className="text-muted">
                {protocol?.version ? `Version ${protocol.version}` : ''}
                {protocol?.status ? ` • ${protocol.status}` : ''}
                {protocol?.diseaseArea ? ` • ${protocol.diseaseArea}` : ''}
              </p>
            </Col>
            <Col md={4} className="text-right">
              {!readOnly && (
                <Button 
                  variant="primary" 
                  onClick={handleGenerateInsights}
                  disabled={!aiModuleType}
                >
                  <FaFlask className="mr-1" /> Generate AI Insights
                </Button>
              )}
            </Col>
          </Row>
        </Card.Body>
      </Card>
      
      {/* Error Alert */}
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {/* AI Insights Panel */}
      {aiInsights && (
        <Card className="mb-4">
          <Card.Header>
            <h5>
              <FaFlask className="mr-2" />
              AI Insights
              <small className="text-muted ml-2">
                {aiModuleType === 'cber' ? 'CBER.ai' : 'CDER.ai'} Analysis
              </small>
            </h5>
          </Card.Header>
          <Card.Body>
            <Row>
              {aiInsights.recommendations?.map((rec, index) => (
                <Col md={4} key={index}>
                  <Card className="h-100">
                    <Card.Body>
                      <h6>{rec.title}</h6>
                      <p>{rec.description}</p>
                      {rec.confidence && (
                        <div className="text-muted">
                          Confidence: {rec.confidence}%
                        </div>
                      )}
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card.Body>
        </Card>
      )}
      
      {/* Main Content Tabs */}
      <Tabs
        activeKey={activeTab}
        onSelect={setActiveTab}
        id="ibd-protocol-tabs"
        className="mb-4"
      >
        {/* Overview Tab */}
        <Tab eventKey="overview" title={<><FaChartLine className="mr-1" /> Overview</>}>
          <Row>
            <Col md={8}>
              <IBDProtocolTimeline protocol={protocol} ibdInfo={ibdInfo} />
            </Col>
            <Col md={4}>
              <Card className="mb-4">
                <Card.Header>
                  <h5>Protocol Details</h5>
                </Card.Header>
                <Card.Body>
                  <dl className="row">
                    <dt className="col-sm-5">Protocol Type</dt>
                    <dd className="col-sm-7">{protocol?.type || 'IBD Protocol'}</dd>
                    
                    <dt className="col-sm-5">Disease Area</dt>
                    <dd className="col-sm-7">{protocol?.diseaseArea || 'Inflammatory Bowel Disease'}</dd>
                    
                    <dt className="col-sm-5">Specific Disease</dt>
                    <dd className="col-sm-7">{protocol?.configuration?.specificDisease || 'Crohn\'s Disease'}</dd>
                    
                    <dt className="col-sm-5">Primary Endpoint</dt>
                    <dd className="col-sm-7">
                      {protocol?.configuration?.endpointDefinitions?.primaryEndpoint || 'Clinical Remission at Week 16'}
                    </dd>
                    
                    <dt className="col-sm-5">Duration</dt>
                    <dd className="col-sm-7">
                      {protocol?.configuration?.timing?.estimatedDuration || 52} weeks
                    </dd>
                    
                    <dt className="col-sm-5">Target Enrollment</dt>
                    <dd className="col-sm-7">
                      {protocol?.configuration?.general?.targetParticipants || 100} participants
                    </dd>
                  </dl>
                </Card.Body>
              </Card>
              
              {/* Biomarker Thresholds Card */}
              <Card className="mb-4">
                <Card.Header>
                  <h5>
                    <FaMicroscope className="mr-2" />
                    Biomarker Thresholds
                  </h5>
                </Card.Header>
                <Card.Body>
                  {protocol?.configuration?.biomarkerThresholds && (
                    <BiomarkerThresholdEditor 
                      thresholds={protocol.configuration.biomarkerThresholds}
                      onUpdate={handleUpdateBiomarkerThresholds}
                      readOnly={readOnly}
                    />
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>
        
        {/* Structure Tab */}
        <Tab eventKey="structure" title={<><FaDna className="mr-1" /> Protocol Structure</>}>
          <ProtocolStructureViewer 
            protocol={protocol} 
            ibdInfo={ibdInfo}
            readOnly={readOnly}
          />
        </Tab>
        
        {/* Endpoints Tab */}
        <Tab eventKey="endpoints" title={<><FaChartLine className="mr-1" /> Endpoints</>}>
          <Row>
            <Col md={8}>
              <Card className="mb-4">
                <Card.Header>
                  <h5>Endpoint Definitions</h5>
                </Card.Header>
                <Card.Body>
                  {protocol?.configuration?.endpointDefinitions && (
                    <EndpointDefinitionEditor
                      endpoints={protocol.configuration.endpointDefinitions}
                      onUpdate={(endpoints) => handleUpdateIBDSettings({ endpointDefinitions: endpoints })}
                      readOnly={readOnly}
                    />
                  )}
                </Card.Body>
              </Card>
            </Col>
            <Col md={4}>
              <Card className="mb-4">
                <Card.Header>
                  <h5>Clinical Scores</h5>
                </Card.Header>
                <Card.Body>
                  <ClinicalScoresTrend protocolId={protocolId} />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>
        
        {/* HPC Integration Tab - Only show if protocol has HPC capabilities */}
        {hasHpc && (
          <Tab eventKey="hpc" title={<><FaCloudUploadAlt className="mr-1" /> HPC Integration</>}>
            <HPCIntegrationPanel 
              protocol={protocol}
              protocolId={protocolId}
              readOnly={readOnly}
            />
          </Tab>
        )}
        
        {/* AI Module Tab - Only show if appropriate AI module is available */}
        {aiModuleType && (
          <Tab eventKey="ai" title={<><FaFlask className="mr-1" /> AI Module</>}>
            <AIModulePanel 
              protocol={protocol}
              protocolId={protocolId}
              aiModuleType={aiModuleType}
              insights={aiInsights}
              onGenerateInsights={handleGenerateInsights}
              readOnly={readOnly}
            />
          </Tab>
        )}
        
        {/* Multi-Institution Data Sharing Tab */}
        <Tab eventKey="sharing" title={<><FaUsers className="mr-1" /> Data Sharing</>}>
          <MultiInstitutionDataSharingPanel 
            protocol={protocol}
            protocolId={protocolId}
            readOnly={readOnly}
          />
        </Tab>
      </Tabs>
    </div>
  );
};

IBDProtocolDashboard.propTypes = {
  protocolId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  readOnly: PropTypes.bool
};

export default IBDProtocolDashboard;