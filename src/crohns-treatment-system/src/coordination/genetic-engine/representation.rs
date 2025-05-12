//! Representation of treatment plans and patient context
//!
//! This module defines the chromosome and gene representations for
//! Crohn's disease treatment plans, as well as the patient context
//! used for fitness evaluation.

use std::collections::HashMap;
use serde::{Serialize, Deserialize};

/// Enumeration of medication types for Crohn's disease
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum MedicationType {
    /// Janus Kinase (JAK) inhibitors
    JakInhibitor,
    /// Interleukin-23 inhibitors
    Il23Inhibitor,
    /// Tumor Necrosis Factor (TNF) inhibitors
    TnfInhibitor,
    /// Immunomodulators
    Immunomodulator,
    /// Corticosteroids
    Corticosteroid,
    /// Aminosalicylates
    Aminosalicylate,
    /// Antibiotics
    Antibiotic,
    /// Probiotics and microbiome modulators
    Probiotic,
}

/// Enumeration of specific medications
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Medication {
    // JAK inhibitors
    Upadacitinib,
    Tofacitinib,
    
    // IL-23 inhibitors
    Risankizumab,
    Mirikizumab,
    Guselkumab,
    
    // TNF inhibitors
    Adalimumab,
    Infliximab,
    Certolizumab,
    Golimumab,
    
    // Immunomodulators
    Azathioprine,
    Mercaptopurine,
    Methotrexate,
    
    // Corticosteroids
    Prednisone,
    Budesonide,
    
    // Aminosalicylates
    Mesalamine,
    Sulfasalazine,
    
    // Antibiotics
    Ciprofloxacin,
    Metronidazole,
    
    // Probiotics and microbiome modulators
    CustomProbiotic,
    FecalMicrobiota,
}

impl Medication {
    /// Get the medication type
    pub fn medication_type(&self) -> MedicationType {
        match self {
            Medication::Upadacitinib | Medication::Tofacitinib => MedicationType::JakInhibitor,
            Medication::Risankizumab | Medication::Mirikizumab | Medication::Guselkumab => MedicationType::Il23Inhibitor,
            Medication::Adalimumab | Medication::Infliximab | Medication::Certolizumab | Medication::Golimumab => MedicationType::TnfInhibitor,
            Medication::Azathioprine | Medication::Mercaptopurine | Medication::Methotrexate => MedicationType::Immunomodulator,
            Medication::Prednisone | Medication::Budesonide => MedicationType::Corticosteroid,
            Medication::Mesalamine | Medication::Sulfasalazine => MedicationType::Aminosalicylate,
            Medication::Ciprofloxacin | Medication::Metronidazole => MedicationType::Antibiotic,
            Medication::CustomProbiotic | Medication::FecalMicrobiota => MedicationType::Probiotic,
        }
    }
}

/// Dosage unit
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum DosageUnit {
    Mg,
    Ml,
    Mcg,
    Cfu,
}

/// Frequency of medication administration
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Frequency {
    Daily,
    BID,
    TID,
    QID,
    Weekly,
    BiWeekly,
    Monthly,
    AsNeeded,
}

/// A gene representing a single medication in a treatment plan
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TreatmentGene {
    /// The medication
    pub medication: Medication,
    /// The dosage amount
    pub dosage: f64,
    /// The dosage unit
    pub unit: DosageUnit,
    /// The frequency of administration
    pub frequency: Frequency,
    /// Duration in days
    pub duration: u32,
}

impl TreatmentGene {
    /// Create a new treatment gene
    pub fn new(medication: Medication, dosage: f64, unit: DosageUnit, frequency: Frequency, duration: u32) -> Self {
        Self {
            medication,
            dosage,
            unit,
            frequency,
            duration,
        }
    }
}

/// A chromosome representing a complete treatment plan
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TreatmentChromosome {
    /// The genes in the chromosome
    pub genes: Vec<TreatmentGene>,
    /// Additional treatment attributes
    pub attributes: HashMap<String, String>,
}

impl TreatmentChromosome {
    /// Create a new treatment chromosome
    pub fn new(genes: Vec<TreatmentGene>) -> Self {
        Self {
            genes,
            attributes: HashMap::new(),
        }
    }
    
    /// Add an attribute to the treatment plan
    pub fn with_attribute(mut self, key: &str, value: &str) -> Self {
        self.attributes.insert(key.to_string(), value.to_string());
        self
    }
    
    /// Get medications by type
    pub fn medications_by_type(&self, medication_type: MedicationType) -> Vec<&TreatmentGene> {
        self.genes.iter()
            .filter(|gene| gene.medication.medication_type() == medication_type)
            .collect()
    }
}

/// Crohn's disease type
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum CrohnsType {
    Ileal,
    Colonic,
    Ileocolonic,
    Perianal,
}

/// Disease severity
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum DiseaseSeverity {
    Mild,
    Moderate,
    Severe,
}

/// Patient context for treatment optimization
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PatientContext {
    /// Patient identifier
    pub patient_id: String,
    /// Age in years
    pub age: u32,
    /// Weight in kg
    pub weight: f64,
    /// Crohn's disease type
    pub crohns_type: CrohnsType,
    /// Disease severity
    pub severity: DiseaseSeverity,
    /// History of previous treatments
    pub treatment_history: Vec<TreatmentPlan>,
    /// Genetic markers
    pub genetic_markers: HashMap<String, String>,
    /// Microbiome profile
    pub microbiome_profile: HashMap<String, f64>,
    /// Inflammatory markers
    pub inflammatory_markers: HashMap<String, f64>,
    /// Comorbidities
    pub comorbidities: Vec<String>,
    /// Medication allergies
    pub allergies: Vec<String>,
}

impl PatientContext {
    /// Create a new patient context
    pub fn new(
        patient_id: String,
        age: u32,
        weight: f64,
        crohns_type: CrohnsType,
        severity: DiseaseSeverity,
    ) -> Self {
        Self {
            patient_id,
            age,
            weight,
            crohns_type,
            severity,
            treatment_history: Vec::new(),
            genetic_markers: HashMap::new(),
            microbiome_profile: HashMap::new(),
            inflammatory_markers: HashMap::new(),
            comorbidities: Vec::new(),
            allergies: Vec::new(),
        }
    }
    
    /// Add a genetic marker
    pub fn with_genetic_marker(mut self, marker: &str, value: &str) -> Self {
        self.genetic_markers.insert(marker.to_string(), value.to_string());
        self
    }
    
    /// Add a microbiome profile entry
    pub fn with_microbiome_entry(mut self, species: &str, abundance: f64) -> Self {
        self.microbiome_profile.insert(species.to_string(), abundance);
        self
    }
    
    /// Add an inflammatory marker
    pub fn with_inflammatory_marker(mut self, marker: &str, value: f64) -> Self {
        self.inflammatory_markers.insert(marker.to_string(), value);
        self
    }
    
    /// Add a comorbidity
    pub fn with_comorbidity(mut self, comorbidity: &str) -> Self {
        self.comorbidities.push(comorbidity.to_string());
        self
    }
    
    /// Add a medication allergy
    pub fn with_allergy(mut self, allergy: &str) -> Self {
        self.allergies.push(allergy.to_string());
        self
    }
    
    /// Add a treatment history entry
    pub fn with_treatment_history(mut self, treatment: TreatmentPlan) -> Self {
        self.treatment_history.push(treatment);
        self
    }
}

/// Treatment response
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum TreatmentResponse {
    Complete,
    Partial,
    None,
    Adverse,
}

/// Treatment plan with outcome information
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TreatmentPlan {
    /// The treatment chromosome
    pub treatment: TreatmentChromosome,
    /// Start date (ISO format)
    pub start_date: String,
    /// End date (ISO format)
    pub end_date: Option<String>,
    /// Treatment response
    pub response: Option<TreatmentResponse>,
    /// Clinical remission achieved
    pub clinical_remission: Option<bool>,
    /// Endoscopic improvement
    pub endoscopic_improvement: Option<bool>,
    /// Side effects encountered
    pub side_effects: Vec<String>,
    /// Reason for discontinuation
    pub discontinuation_reason: Option<String>,
}

impl TreatmentPlan {
    /// Create a new treatment plan
    pub fn new(treatment: TreatmentChromosome, start_date: String) -> Self {
        Self {
            treatment,
            start_date,
            end_date: None,
            response: None,
            clinical_remission: None,
            endoscopic_improvement: None,
            side_effects: Vec::new(),
            discontinuation_reason: None,
        }
    }
    
    /// Set the treatment response
    pub fn with_response(mut self, response: TreatmentResponse) -> Self {
        self.response = Some(response);
        self
    }
    
    /// Set the clinical remission status
    pub fn with_clinical_remission(mut self, remission: bool) -> Self {
        self.clinical_remission = Some(remission);
        self
    }
    
    /// Set the endoscopic improvement status
    pub fn with_endoscopic_improvement(mut self, improvement: bool) -> Self {
        self.endoscopic_improvement = Some(improvement);
        self
    }
    
    /// Add a side effect
    pub fn with_side_effect(mut self, side_effect: &str) -> Self {
        self.side_effects.push(side_effect.to_string());
        self
    }
    
    /// Set the end date
    pub fn with_end_date(mut self, end_date: String) -> Self {
        self.end_date = Some(end_date);
        self
    }
    
    /// Set the discontinuation reason
    pub fn with_discontinuation_reason(mut self, reason: &str) -> Self {
        self.discontinuation_reason = Some(reason.to_string());
        self
    }
}