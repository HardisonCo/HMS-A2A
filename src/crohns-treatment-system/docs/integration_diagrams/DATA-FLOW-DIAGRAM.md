# Data Flow Diagram for Crohn's Treatment System

## System-Level Data Flow

```mermaid
flowchart TB
    %% Define main data stores
    Database[(Patient Database)]
    TrialDB[(Trial Database)]
    KnowledgeDB[(Knowledge Base)]
    
    %% Define external entities
    Patient[Patient]
    Clinician[Clinician]
    Researcher[Researcher]
    EHRSystem[EHR System]
    
    %% Define processes
    DataIngestion[Data Ingestion]
    DataTransformation[Data Transformation]
    TreatmentOptimization[Treatment Optimization]
    TrialExecution[Adaptive Trial Execution]
    Visualization[Results Visualization]
    SelfHealing[Self-Healing System]
    
    %% Define data flows - External to System
    Patient -- Patient Information --> DataIngestion
    EHRSystem -- Health Records --> DataIngestion
    Clinician -- Trial Protocol --> TrialExecution
    Clinician -- Treatment Request --> TreatmentOptimization
    Researcher -- Analysis Parameters --> Visualization
    
    %% Define data flows - Internal
    DataIngestion -- Raw Patient Data --> DataTransformation
    DataTransformation -- Standardized Patient Profile --> Database
    Database -- Patient Profile --> TreatmentOptimization
    Database -- Patient Cohort --> TrialExecution
    TreatmentOptimization -- Treatment Plan --> Clinician
    TreatmentOptimization -- Treatment Metrics --> KnowledgeDB
    TrialExecution -- Trial Results --> TrialDB
    TrialDB -- Trial Data --> Visualization
    Visualization -- Visual Reports --> Clinician
    Visualization -- Visual Reports --> Researcher
    
    %% Define self-healing connections
    SelfHealing -. Monitors .-> DataIngestion
    SelfHealing -. Monitors .-> DataTransformation
    SelfHealing -. Monitors .-> TreatmentOptimization
    SelfHealing -. Monitors .-> TrialExecution
    SelfHealing -. Monitors .-> Visualization
    
    %% Define knowledge base connections
    KnowledgeDB -- Domain Knowledge --> TreatmentOptimization
    KnowledgeDB -- Domain Knowledge --> TrialExecution
    TrialExecution -- New Insights --> KnowledgeDB
    
    %% Define styles
    classDef process fill:#afd6ff,stroke:#0066cc,stroke-width:2px,color:#000000;
    classDef entity fill:#ffe6cc,stroke:#ff9933,stroke-width:2px,color:#000000;
    classDef datastore fill:#e6ffcc,stroke:#66cc00,stroke-width:2px,color:#000000;
    
    class DataIngestion,DataTransformation,TreatmentOptimization,TrialExecution,Visualization,SelfHealing process;
    class Patient,Clinician,Researcher,EHRSystem entity;
    class Database,TrialDB,KnowledgeDB datastore;
```

## Detailed Data Transformation Flow

```mermaid
flowchart LR
    %% Define data sources
    CSV[CSV Files]
    JSON[JSON Files]
    EHR[EHR Systems]
    FHIR[FHIR API]
    
    %% Define transformation processes
    Extraction[Data Extraction]
    Validation[Data Validation]
    Normalization[Data Normalization]
    Enrichment[Data Enrichment]
    Formatting[Format Conversion]
    
    %% Define destinations
    PP[Patient Profiles]
    GE[Genetic Engine Format]
    TF[Trial Format]
    
    %% Define data flows
    CSV --> Extraction
    JSON --> Extraction
    EHR --> Extraction
    FHIR --> Extraction
    
    Extraction --> Validation
    Validation --> Normalization
    Normalization --> Enrichment
    Enrichment --> Formatting
    
    Formatting --> PP
    PP --> GE
    PP --> TF
    
    %% Define additional processes
    BiomarkerProc[Biomarker Processing]
    TreatmentProc[Treatment History Processing]
    
    Validation --> BiomarkerProc
    BiomarkerProc --> Normalization
    Validation --> TreatmentProc
    TreatmentProc --> Normalization
    
    %% Define styles
    classDef source fill:#f9d3e3,stroke:#db7093,stroke-width:2px,color:#000000;
    classDef process fill:#bbdaff,stroke:#4e7fba,stroke-width:2px,color:#000000;
    classDef destination fill:#d8f8e1,stroke:#48a868,stroke-width:2px,color:#000000;
    
    class CSV,JSON,EHR,FHIR source;
    class Extraction,Validation,Normalization,Enrichment,Formatting,BiomarkerProc,TreatmentProc process;
    class PP,GE,TF destination;
```

## Genetic Algorithm Optimization Flow

```mermaid
flowchart TD
    %% Define inputs
    PatientData[Patient Data]
    BiomarkerData[Biomarker Data]
    TreatmentHistory[Treatment History]
    
    %% Define genetic algorithm processes
    Initialization[Population Initialization]
    FitnessEval[Fitness Evaluation]
    Selection[Selection]
    Crossover[Crossover]
    Mutation[Mutation]
    Termination{Termination\nCriteria Met?}
    
    %% Define outputs
    TreatmentPlan[Optimized Treatment Plan]
    
    %% Define flows
    PatientData --> Initialization
    BiomarkerData --> Initialization
    TreatmentHistory --> Initialization
    
    Initialization --> FitnessEval
    FitnessEval --> Selection
    Selection --> Crossover
    Crossover --> Mutation
    Mutation --> FitnessEval
    FitnessEval --> Termination
    
    Termination -- No --> Selection
    Termination -- Yes --> TreatmentPlan
    
    %% Define subprocess details
    subgraph FitnessComponents[Fitness Calculation Components]
        Efficacy[Efficacy Score]
        Safety[Safety Score]
        Adherence[Adherence Score]
        Cost[Cost Score]
        
        CombinedFitness[Combined Fitness Score]
        
        Efficacy --> CombinedFitness
        Safety --> CombinedFitness
        Adherence --> CombinedFitness
        Cost --> CombinedFitness
    end
    
    FitnessEval --> FitnessComponents
    FitnessComponents --> FitnessEval
    
    %% Define styles
    classDef input fill:#ffcccc,stroke:#ff6666,stroke-width:2px,color:#000000;
    classDef process fill:#ccccff,stroke:#6666ff,stroke-width:2px,color:#000000;
    classDef decision fill:#ffffcc,stroke:#ffff66,stroke-width:2px,color:#000000;
    classDef output fill:#ccffcc,stroke:#66ff66,stroke-width:2px,color:#000000;
    classDef subproc fill:#f8f8f8,stroke:#cccccc,stroke-width:1px,color:#000000;
    
    class PatientData,BiomarkerData,TreatmentHistory input;
    class Initialization,FitnessEval,Selection,Crossover,Mutation process;
    class Termination decision;
    class TreatmentPlan output;
    class FitnessComponents,Efficacy,Safety,Adherence,Cost,CombinedFitness subproc;
```

## Adaptive Trial Execution Flow

```mermaid
flowchart TD
    %% Define inputs
    Protocol[Trial Protocol]
    PatientCohort[Patient Cohort]
    
    %% Define trial processes
    InitialAlloc[Initial Patient Allocation]
    TreatmentAssign[Treatment Assignment]
    InterimAnalysis{Interim\nAnalysis}
    AdaptiveDecision[Adaptation Decision]
    ContinueTrial{Continue\nTrial?}
    FinalAnalysis[Final Analysis]
    
    %% Define outputs
    TrialResults[Trial Results]
    
    %% Define flows
    Protocol --> InitialAlloc
    PatientCohort --> InitialAlloc
    
    InitialAlloc --> TreatmentAssign
    TreatmentAssign --> InterimAnalysis
    
    InterimAnalysis -- "Adaptation Needed" --> AdaptiveDecision
    AdaptiveDecision --> TreatmentAssign
    
    InterimAnalysis -- "No Adaptation" --> ContinueTrial
    ContinueTrial -- Yes --> TreatmentAssign
    ContinueTrial -- No --> FinalAnalysis
    
    FinalAnalysis --> TrialResults
    
    %% Define subprocess details
    subgraph AdaptationTypes[Adaptation Types]
        RAR[Response-Adaptive\nRandomization]
        ArmDrop[Arm Dropping]
        SampleSize[Sample Size\nRe-estimation]
        Enrichment[Population\nEnrichment]
    end
    
    AdaptiveDecision --> AdaptationTypes
    AdaptationTypes --> AdaptiveDecision
    
    %% Define styles
    classDef input fill:#ffcccc,stroke:#ff6666,stroke-width:2px,color:#000000;
    classDef process fill:#ccccff,stroke:#6666ff,stroke-width:2px,color:#000000;
    classDef decision fill:#ffffcc,stroke:#ffff66,stroke-width:2px,color:#000000;
    classDef output fill:#ccffcc,stroke:#66ff66,stroke-width:2px,color:#000000;
    classDef subproc fill:#f8f8f8,stroke:#cccccc,stroke-width:1px,color:#000000;
    
    class Protocol,PatientCohort input;
    class InitialAlloc,TreatmentAssign,AdaptiveDecision,FinalAnalysis process;
    class InterimAnalysis,ContinueTrial decision;
    class TrialResults output;
    class AdaptationTypes,RAR,ArmDrop,SampleSize,Enrichment subproc;
```

## Self-Healing System Flow

```mermaid
flowchart TD
    %% Define monitoring points
    MonitorData[Data Monitoring]
    MonitorProcess[Process Monitoring]
    MonitorResource[Resource Monitoring]
    
    %% Define detection and diagnosis
    AnomalyDetection[Anomaly Detection]
    ErrorDiagnosis[Error Diagnosis]
    
    %% Define recovery actions
    RecoveryStrategy[Recovery Strategy Selection]
    DataReconstruction[Data Reconstruction]
    AlternativePathway[Alternative Pathway]
    GracefulDegradation[Graceful Degradation]
    Restart[Component Restart]
    
    %% Define verification and reporting
    RecoveryVerification[Recovery Verification]
    ReportGeneration[Report Generation]
    
    %% Define flows
    MonitorData --> AnomalyDetection
    MonitorProcess --> AnomalyDetection
    MonitorResource --> AnomalyDetection
    
    AnomalyDetection -- "Anomaly Detected" --> ErrorDiagnosis
    ErrorDiagnosis --> RecoveryStrategy
    
    RecoveryStrategy -- "Data Error" --> DataReconstruction
    RecoveryStrategy -- "Process Error" --> AlternativePathway
    RecoveryStrategy -- "Resource Error" --> GracefulDegradation
    RecoveryStrategy -- "Fatal Error" --> Restart
    
    DataReconstruction --> RecoveryVerification
    AlternativePathway --> RecoveryVerification
    GracefulDegradation --> RecoveryVerification
    Restart --> RecoveryVerification
    
    RecoveryVerification -- "Success" --> ReportGeneration
    RecoveryVerification -- "Failure" --> ErrorDiagnosis
    
    ReportGeneration --> MonitorData
    ReportGeneration --> MonitorProcess
    ReportGeneration --> MonitorResource
    
    %% Define styles
    classDef monitor fill:#ffe6cc,stroke:#ff9933,stroke-width:2px,color:#000000;
    classDef detection fill:#ccccff,stroke:#6666ff,stroke-width:2px,color:#000000;
    classDef recovery fill:#d8f8e1,stroke:#48a868,stroke-width:2px,color:#000000;
    classDef verify fill:#f9d3e3,stroke:#db7093,stroke-width:2px,color:#000000;
    
    class MonitorData,MonitorProcess,MonitorResource monitor;
    class AnomalyDetection,ErrorDiagnosis detection;
    class RecoveryStrategy,DataReconstruction,AlternativePathway,GracefulDegradation,Restart recovery;
    class RecoveryVerification,ReportGeneration verify;
```

## Visualization Pipeline Flow

```mermaid
flowchart TD
    %% Define inputs
    TrialResults[Trial Results]
    PatientData[Patient Data]
    TreatmentPlan[Treatment Plan]
    
    %% Define visualization processes
    DataPrep[Data Preparation]
    VisualizationGeneration[Visualization Generation]
    DashboardAssembly[Dashboard Assembly]
    ReportGeneration[Report Generation]
    
    %% Define visualizations
    ResponseByArm[Response By Arm]
    ResponseDist[Response Distribution]
    BiomarkerCorr[Biomarker Correlation]
    AdaptationTimeline[Adaptation Timeline]
    AdverseEvents[Adverse Events]
    TreatmentPlanViz[Treatment Plan]
    
    %% Define outputs
    HTMLReport[HTML Report]
    PNGImages[PNG Images]
    JSONData[JSON Data]
    
    %% Define flows
    TrialResults --> DataPrep
    PatientData --> DataPrep
    TreatmentPlan --> DataPrep
    
    DataPrep --> VisualizationGeneration
    
    VisualizationGeneration --> ResponseByArm
    VisualizationGeneration --> ResponseDist
    VisualizationGeneration --> BiomarkerCorr
    VisualizationGeneration --> AdaptationTimeline
    VisualizationGeneration --> AdverseEvents
    VisualizationGeneration --> TreatmentPlanViz
    
    ResponseByArm --> DashboardAssembly
    ResponseDist --> DashboardAssembly
    BiomarkerCorr --> DashboardAssembly
    AdaptationTimeline --> DashboardAssembly
    AdverseEvents --> DashboardAssembly
    TreatmentPlanViz --> DashboardAssembly
    
    DashboardAssembly --> ReportGeneration
    
    ReportGeneration --> HTMLReport
    ReportGeneration --> PNGImages
    ReportGeneration --> JSONData
    
    %% Define styles
    classDef input fill:#ffcccc,stroke:#ff6666,stroke-width:2px,color:#000000;
    classDef process fill:#ccccff,stroke:#6666ff,stroke-width:2px,color:#000000;
    classDef viz fill:#d8f8e1,stroke:#48a868,stroke-width:2px,color:#000000;
    classDef output fill:#ffe6cc,stroke:#ff9933,stroke-width:2px,color:#000000;
    
    class TrialResults,PatientData,TreatmentPlan input;
    class DataPrep,VisualizationGeneration,DashboardAssembly,ReportGeneration process;
    class ResponseByArm,ResponseDist,BiomarkerCorr,AdaptationTimeline,AdverseEvents,TreatmentPlanViz viz;
    class HTMLReport,PNGImages,JSONData output;
```

## Key Data Structures

### Patient Profile

```json
{
  "patient_id": "string",
  "demographics": {
    "age": "integer",
    "sex": "string",
    "ethnicity": "string",
    "weight": "float",
    "height": "float"
  },
  "clinical_data": {
    "crohns_type": "string (ileal|colonic|ileocolonic|perianal)",
    "diagnosis_date": "date",
    "disease_activity": {
      "CDAI": "float",
      "SES-CD": "float",
      "fecal_calprotectin": "float"
    }
  },
  "biomarkers": {
    "genetic_markers": [
      {
        "gene": "string",
        "variant": "string",
        "zygosity": "string"
      }
    ],
    "microbiome_profile": {
      "diversity_index": "float",
      "key_species": [
        {
          "name": "string",
          "abundance": "float"
        }
      ]
    },
    "serum_markers": {
      "CRP": "float",
      "ESR": "float"
    }
  },
  "treatment_history": [
    {
      "medication": "string",
      "response": "string",
      "start_date": "date",
      "end_date": "date",
      "adverse_events": ["string"]
    }
  ]
}
```

### Treatment Plan

```json
{
  "treatment_plan": [
    {
      "medication": "string",
      "dosage": "float",
      "unit": "string",
      "frequency": "string",
      "duration": "integer"
    }
  ],
  "fitness": "float",
  "confidence": "float",
  "explanations": ["string"],
  "biomarker_influences": {
    "biomarker_name": "float"
  },
  "alternatives": [
    {
      "treatment_plan": [],
      "fitness": "float"
    }
  ]
}
```

### Trial Protocol

```json
{
  "trial_id": "string",
  "title": "string",
  "phase": "integer",
  "arms": [
    {
      "armId": "string",
      "name": "string",
      "treatment": {
        "medication": "string",
        "dosage": "string",
        "unit": "string",
        "frequency": "string"
      },
      "biomarkerStratification": [
        {
          "biomarker": "string",
          "criteria": "string"
        }
      ]
    }
  ],
  "adaptiveRules": [
    {
      "triggerCondition": "string",
      "action": "string",
      "parameters": {}
    }
  ],
  "primaryEndpoints": [
    {
      "name": "string",
      "metric": "string",
      "timepoint": "string"
    }
  ],
  "secondaryEndpoints": []
}
```

### Trial Results

```json
{
  "trial_id": "string",
  "status": "string",
  "patient_outcomes": [
    {
      "patient_id": "string",
      "arm": "string",
      "response": "float",
      "adverse_events": ["string"]
    }
  ],
  "adaptations": [
    {
      "type": "string",
      "triggerCondition": "string",
      "timestamp": "datetime",
      "parameters": {}
    }
  ]
}
```

## Data Transformation Logic

### From EHR to Patient Profile

```javascript
function transformEhrToPatientProfile(ehrData) {
  return {
    patient_id: ehrData.patient.id,
    demographics: {
      age: calculateAge(ehrData.patient.birthDate),
      sex: ehrData.patient.gender,
      ethnicity: ehrData.patient.ethnicity,
      weight: extractLatestWeight(ehrData.vitals),
      height: extractLatestHeight(ehrData.vitals)
    },
    clinical_data: {
      crohns_type: extractCrohnsType(ehrData.conditions),
      diagnosis_date: extractDiagnosisDate(ehrData.conditions),
      disease_activity: extractDiseaseActivity(ehrData.labs, ehrData.procedures)
    },
    biomarkers: extractBiomarkers(ehrData.labs, ehrData.genetics),
    treatment_history: extractTreatmentHistory(ehrData.medications)
  };
}
```

### From Profile to Genetic Engine Format

```javascript
function transformProfileForGeneticEngine(patientProfile) {
  return {
    patient_id: patientProfile.patient_id,
    age: patientProfile.demographics.age,
    weight: patientProfile.demographics.weight,
    crohns_type: patientProfile.clinical_data.crohns_type,
    severity: determineSeverity(patientProfile.clinical_data),
    genetic_markers: extractGeneticMarkers(patientProfile.biomarkers),
    biomarker_values: normalizeBiomarkers(patientProfile.biomarkers),
    previous_treatments: transformTreatmentHistory(patientProfile.treatment_history)
  };
}
```

### From Trial Results to Visualization

```javascript
function transformResultsForVisualization(trialResults) {
  return {
    trial_id: trialResults.trial_id,
    status: trialResults.status,
    response_by_arm: calculateResponseByArm(trialResults.patient_outcomes),
    response_distribution: calculateResponseDistribution(trialResults.patient_outcomes),
    adverse_events: calculateAdverseEvents(trialResults.patient_outcomes),
    adaptations: transformAdaptations(trialResults.adaptations)
  };
}
```