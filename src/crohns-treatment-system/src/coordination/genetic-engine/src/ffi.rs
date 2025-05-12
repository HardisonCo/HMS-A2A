/*!
FFI bindings for the genetic engine

This module provides Python bindings for the genetic engine using PyO3.
*/

use crate::{
    BiomarkerAnalysis, BiomarkerData, Biomarker, GeneticConfig, GeneticEngine, PatientData,
    TreatmentOutcomeSimulation, TreatmentPlan, TreatmentVerification,
};
use pyo3::exceptions::{PyRuntimeError, PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::HashMap;
use std::sync::Arc;

/// Python wrapper for GeneticConfig
#[pyclass]
#[derive(Clone)]
pub struct PyGeneticConfig {
    #[pyo3(get, set)]
    pub population_size: usize,
    #[pyo3(get, set)]
    pub generations: usize,
    #[pyo3(get, set)]
    pub mutation_rate: f64,
    #[pyo3(get, set)]
    pub crossover_rate: f64,
    #[pyo3(get, set)]
    pub elitism_count: usize,
    #[pyo3(get, set)]
    pub tournament_size: usize,
}

#[pymethods]
impl PyGeneticConfig {
    #[new]
    fn new(
        population_size: Option<usize>,
        generations: Option<usize>,
        mutation_rate: Option<f64>,
        crossover_rate: Option<f64>,
        elitism_count: Option<usize>,
        tournament_size: Option<usize>,
    ) -> Self {
        PyGeneticConfig {
            population_size: population_size.unwrap_or(100),
            generations: generations.unwrap_or(50),
            mutation_rate: mutation_rate.unwrap_or(0.1),
            crossover_rate: crossover_rate.unwrap_or(0.7),
            elitism_count: elitism_count.unwrap_or(5),
            tournament_size: tournament_size.unwrap_or(3),
        }
    }
}

impl From<PyGeneticConfig> for GeneticConfig {
    fn from(config: PyGeneticConfig) -> Self {
        GeneticConfig {
            population_size: config.population_size,
            generations: config.generations,
            mutation_rate: config.mutation_rate,
            crossover_rate: config.crossover_rate,
            elitism_count: config.elitism_count,
            tournament_size: config.tournament_size,
        }
    }
}

/// Python wrapper for GeneticEngine
#[pyclass]
pub struct PyGeneticEngine {
    engine: Arc<GeneticEngine>,
}

#[pymethods]
impl PyGeneticEngine {
    #[new]
    fn new(config: Option<PyGeneticConfig>) -> Self {
        let engine = match config {
            Some(cfg) => GeneticEngine::new(cfg.into()),
            None => GeneticEngine::default(),
        };
        PyGeneticEngine {
            engine: Arc::new(engine),
        }
    }

    /// Optimize treatment for a patient
    #[pyo3(signature = (patient_data))]
    fn optimize_treatment(&self, py: Python, patient_data: PyObject) -> PyResult<PyObject> {
        // Convert Python patient data to Rust
        let patient = convert_patient_data(py, patient_data)?;

        // Optimize treatment
        let treatment_plan = self.engine.optimize_treatment(patient);

        // Convert treatment plan to Python dict
        convert_treatment_plan_to_py(py, treatment_plan)
    }

    /// Verify a treatment plan
    #[pyo3(signature = (treatment_plan))]
    fn verify_treatment(&self, py: Python, treatment_plan: PyObject) -> PyResult<PyObject> {
        // Convert Python treatment plan to Rust
        let treatment = convert_treatment_plan(py, treatment_plan)?;

        // Verify treatment
        let verification = self.engine.verify_treatment(treatment);

        // Convert verification result to Python dict
        convert_verification_to_py(py, verification)
    }

    /// Evaluate biomarkers
    #[pyo3(signature = (biomarker_data))]
    fn evaluate_biomarkers(&self, py: Python, biomarker_data: PyObject) -> PyResult<PyObject> {
        // Convert Python biomarker data to Rust
        let biomarkers = convert_biomarker_data(py, biomarker_data)?;

        // Evaluate biomarkers
        let analysis = self.engine.evaluate_biomarkers(biomarkers);

        // Convert analysis to Python dict
        convert_biomarker_analysis_to_py(py, analysis)
    }

    /// Simulate treatment outcome
    #[pyo3(signature = (patient_data, treatment_plan))]
    fn simulate_treatment_outcome(
        &self,
        py: Python,
        patient_data: PyObject,
        treatment_plan: PyObject,
    ) -> PyResult<PyObject> {
        // Convert Python patient data and treatment plan to Rust
        let patient = convert_patient_data(py, patient_data)?;
        let treatment = convert_treatment_plan(py, treatment_plan)?;

        // Simulate treatment outcome
        let outcome = self.engine.simulate_treatment_outcome(patient, treatment);

        // Convert outcome to Python dict
        convert_outcome_simulation_to_py(py, outcome)
    }

    /// Get alternative treatment plans
    #[pyo3(signature = (treatment_plan))]
    fn get_treatment_alternatives(&self, py: Python, treatment_plan: PyObject) -> PyResult<PyObject> {
        // Convert Python treatment plan to Rust
        let treatment = convert_treatment_plan(py, treatment_plan)?;

        // Get alternatives
        let alternatives = self.engine.get_treatment_alternatives(treatment);

        // Convert alternatives to Python list
        let py_alternatives = PyList::empty(py);
        for alt in alternatives {
            let py_alt = convert_treatment_plan_to_py(py, alt)?;
            py_alternatives.append(py_alt)?;
        }

        Ok(py_alternatives.into())
    }
}

/// Crohn's Treatment Optimizer
///
/// This class provides an interface to the Rust genetic engine for optimizing
/// Crohn's disease treatments based on patient data and genetic markers.
#[pyclass]
pub struct CrohnsTreatmentOptimizer {
    engine: Arc<GeneticEngine>,
    config: PyGeneticConfig,
}

#[pymethods]
impl CrohnsTreatmentOptimizer {
    #[new]
    fn new(config: Option<PyGeneticConfig>) -> Self {
        let config = config.unwrap_or_else(|| PyGeneticConfig::new(None, None, None, None, None, None));
        let engine = Arc::new(GeneticEngine::new(config.clone().into()));
        CrohnsTreatmentOptimizer { engine, config }
    }

    /// Optimize treatment for a specific patient
    fn optimize_treatment(&self, py: Python, patient_data: PyObject) -> PyResult<PyObject> {
        // Convert Python patient data to Rust
        let patient = convert_patient_data(py, patient_data)?;

        // Run optimization
        let treatment_plan = self.engine.optimize_treatment(patient);

        // Convert result to Python dict
        convert_treatment_plan_to_py(py, treatment_plan)
    }

    /// Evaluate biomarkers for a patient
    fn evaluate_biomarkers(&self, py: Python, biomarker_data: PyObject) -> PyResult<PyObject> {
        // Convert Python biomarker data to Rust
        let biomarkers = convert_biomarker_data(py, biomarker_data)?;

        // Evaluate biomarkers
        let analysis = self.engine.evaluate_biomarkers(biomarkers);

        // Convert analysis to Python dict
        convert_biomarker_analysis_to_py(py, analysis)
    }

    /// Simulate the outcome of a treatment for a patient
    fn simulate_treatment_outcome(
        &self,
        py: Python,
        patient_data: PyObject,
        treatment_plan: PyObject,
    ) -> PyResult<PyObject> {
        // Convert Python data to Rust
        let patient = convert_patient_data(py, patient_data)?;
        let treatment = convert_treatment_plan(py, treatment_plan)?;

        // Simulate outcome
        let outcome = self.engine.simulate_treatment_outcome(patient, treatment);

        // Convert outcome to Python dict
        convert_outcome_simulation_to_py(py, outcome)
    }

    /// Verify if a treatment plan is safe and effective
    fn verify_treatment(&self, py: Python, treatment_plan: PyObject) -> PyResult<PyObject> {
        // Convert Python treatment plan to Rust
        let treatment = convert_treatment_plan(py, treatment_plan)?;

        // Verify treatment
        let verification = self.engine.verify_treatment(treatment);

        // Convert verification to Python dict
        convert_verification_to_py(py, verification)
    }

    /// Get alternative treatment plans
    fn get_treatment_alternatives(&self, py: Python, treatment_plan: PyObject) -> PyResult<PyObject> {
        // Convert Python treatment plan to Rust
        let treatment = convert_treatment_plan(py, treatment_plan)?;

        // Get alternatives
        let alternatives = self.engine.get_treatment_alternatives(treatment);

        // Convert alternatives to Python list
        let py_alternatives = PyList::empty(py);
        for alt in alternatives {
            let py_alt = convert_treatment_plan_to_py(py, alt)?;
            py_alternatives.append(py_alt)?;
        }

        Ok(py_alternatives.into())
    }

    /// Get the current configuration
    fn get_config(&self) -> PyGeneticConfig {
        self.config.clone()
    }

    /// Set a new configuration
    fn set_config(&mut self, config: PyGeneticConfig) {
        self.config = config.clone();
        self.engine = Arc::new(GeneticEngine::new(config.into()));
    }
}

/// Optimize treatment for a patient
#[pyfunction]
fn optimize_treatment(py: Python, patient_data: PyObject, config: Option<PyGeneticConfig>) -> PyResult<PyObject> {
    let optimizer = CrohnsTreatmentOptimizer::new(config);
    optimizer.optimize_treatment(py, patient_data)
}

/// Evaluate biomarkers for a patient
#[pyfunction]
fn evaluate_biomarkers(py: Python, biomarker_data: PyObject, config: Option<PyGeneticConfig>) -> PyResult<PyObject> {
    let optimizer = CrohnsTreatmentOptimizer::new(config);
    optimizer.evaluate_biomarkers(py, biomarker_data)
}

/// Simulate treatment outcome for a patient
#[pyfunction]
fn simulate_treatment_outcome(
    py: Python,
    patient_data: PyObject,
    treatment_plan: PyObject,
    config: Option<PyGeneticConfig>,
) -> PyResult<PyObject> {
    let optimizer = CrohnsTreatmentOptimizer::new(config);
    optimizer.simulate_treatment_outcome(py, patient_data, treatment_plan)
}

/// Verify a treatment plan
#[pyfunction]
fn verify_treatment(py: Python, treatment_plan: PyObject, config: Option<PyGeneticConfig>) -> PyResult<PyObject> {
    let optimizer = CrohnsTreatmentOptimizer::new(config);
    optimizer.verify_treatment(py, treatment_plan)
}

/// Analyze genetic sequences for Crohn's disease variants
#[pyfunction]
fn analyze_genetic_sequences(py: Python, sequence_data: PyObject) -> PyResult<PyObject> {
    // Extract patient and sequence data
    let sequence_dict = sequence_data.extract::<&PyDict>(py)?;

    // Create a result dictionary - in a real implementation, this would analyze sequences
    let result = PyDict::new(py);

    // Get patient ID
    let patient_id = match sequence_dict.get_item("patient_id") {
        Some(id) => id.extract::<String>()?,
        None => return Err(PyValueError::new_err("Missing patient_id in sequence data")),
    };

    result.set_item("analysis_id", format!("GEN-{}-{}", patient_id, "ABC123"))?;
    result.set_item("analysis_timestamp", "2023-05-15T14:30:00Z")?;
    
    // Create variants list
    let variants = PyList::empty(py);
    let variant1 = PyDict::new(py);
    variant1.set_item("gene", "NOD2")?;
    variant1.set_item("variant_id", "R702W")?;
    variant1.set_item("nucleotide_change", "C2104T")?;
    variant1.set_item("protein_change", "Arg702Trp")?;
    variant1.set_item("zygosity", "heterozygous")?;
    variant1.set_item("clinical_significance", "pathogenic")?;
    variant1.set_item("impact_score", 0.85)?;
    variant1.set_item("description", "Common NOD2 variant associated with Crohn's disease, particularly ileal disease.")?;
    variants.append(variant1)?;

    let variant2 = PyDict::new(py);
    variant2.set_item("gene", "IL23R")?;
    variant2.set_item("variant_id", "R381Q")?;
    variant2.set_item("nucleotide_change", "G1142A")?;
    variant2.set_item("protein_change", "Arg381Gln")?;
    variant2.set_item("zygosity", "heterozygous")?;
    variant2.set_item("clinical_significance", "protective")?;
    variant2.set_item("impact_score", 0.72)?;
    variant2.set_item("description", "Protective variant that reduces risk of inflammatory bowel disease.")?;
    variants.append(variant2)?;

    let variant3 = PyDict::new(py);
    variant3.set_item("gene", "ATG16L1")?;
    variant3.set_item("variant_id", "T300A")?;
    variant3.set_item("nucleotide_change", "A898G")?;
    variant3.set_item("protein_change", "Thr300Ala")?;
    variant3.set_item("zygosity", "homozygous")?;
    variant3.set_item("clinical_significance", "risk factor")?;
    variant3.set_item("impact_score", 0.68)?;
    variant3.set_item("description", "Associated with impaired autophagy and increased susceptibility to Crohn's disease.")?;
    variants.append(variant3)?;

    result.set_item("variants", variants)?;

    // Create risk assessment
    let risk_assessment = PyDict::new(py);
    risk_assessment.set_item("overall_risk", "high")?;
    risk_assessment.set_item("risk_score", 0.78)?;

    let contributing_factors = PyList::empty(py);
    let factor1 = PyDict::new(py);
    factor1.set_item("factor", "NOD2 R702W variant")?;
    factor1.set_item("contribution", "major")?;
    factor1.set_item("description", "Associated with 2-4x increased risk of Crohn's disease")?;
    contributing_factors.append(factor1)?;

    let factor2 = PyDict::new(py);
    factor2.set_item("factor", "ATG16L1 T300A homozygosity")?;
    factor2.set_item("contribution", "moderate")?;
    factor2.set_item("description", "Associated with 1.5-2x increased risk")?;
    contributing_factors.append(factor2)?;

    risk_assessment.set_item("contributing_factors", contributing_factors)?;
    risk_assessment.set_item("confidence", 0.92)?;
    result.set_item("risk_assessment", risk_assessment)?;

    // Create treatment recommendations
    let recommendations = PyList::empty(py);
    let rec1 = PyDict::new(py);
    rec1.set_item("treatment", "Ustekinumab")?;
    rec1.set_item("expected_efficacy", 0.82)?;

    let basis1 = PyList::empty(py);
    let basis_item1 = PyDict::new(py);
    basis_item1.set_item("gene", "IL23R")?;
    basis_item1.set_item("variant", "R381Q")?;
    basis_item1.set_item("effect", "Variant suggests good response to IL-12/23 inhibition")?;
    basis1.append(basis_item1)?;
    rec1.set_item("genetic_basis", basis1)?;

    rec1.set_item("confidence", 0.78)?;
    rec1.set_item("contraindications", PyList::empty(py))?;
    recommendations.append(rec1)?;

    let rec2 = PyDict::new(py);
    rec2.set_item("treatment", "Vedolizumab")?;
    rec2.set_item("expected_efficacy", 0.75)?;

    let basis2 = PyList::empty(py);
    let basis_item2 = PyDict::new(py);
    basis_item2.set_item("gene", "NOD2")?;
    basis_item2.set_item("variant", "R702W")?;
    basis_item2.set_item("effect", "Patients with NOD2 variants often respond well to gut-selective therapies")?;
    basis2.append(basis_item2)?;
    rec2.set_item("genetic_basis", basis2)?;

    rec2.set_item("confidence", 0.71)?;
    rec2.set_item("contraindications", PyList::empty(py))?;
    recommendations.append(rec2)?;

    result.set_item("treatment_recommendations", recommendations)?;

    Ok(result.into())
}

/// Get detailed information about a specific Crohn's disease genetic variant
#[pyfunction]
fn get_crohns_variant_info(py: Python, gene: String, variant: String) -> PyResult<PyObject> {
    // In a real implementation, this would query a database or knowledge base
    // For this demo, we'll return a static example for NOD2 R702W
    
    let result = PyDict::new(py);
    
    if gene == "NOD2" && variant == "R702W" {
        result.set_item("gene", "NOD2")?;
        result.set_item("variant", "R702W")?;
        result.set_item("significance", "pathogenic")?;
        result.set_item("description", "Missense variant in the NOD2 gene resulting in an arginine to tryptophan substitution at position 702.")?;
        result.set_item("impact_on_disease", "Associated with 2-4 fold increased risk of Crohn's disease, particularly ileal Crohn's disease.")?;
        
        let frequency = PyDict::new(py);
        frequency.set_item("general_population", 0.04)?;
        frequency.set_item("crohns_patients", 0.15)?;
        frequency.set_item("caucasian", 0.05)?;
        frequency.set_item("asian", 0.01)?;
        frequency.set_item("african", 0.02)?;
        result.set_item("frequency", frequency)?;
        
        let treatment_implications = PyList::empty(py);
        
        let impl1 = PyDict::new(py);
        impl1.set_item("treatment", "Anti-TNF agents")?;
        impl1.set_item("effect", "Reduced efficacy in patients with NOD2 variants")?;
        impl1.set_item("evidence_level", "moderate")?;
        treatment_implications.append(impl1)?;
        
        let impl2 = PyDict::new(py);
        impl2.set_item("treatment", "Vedolizumab")?;
        impl2.set_item("effect", "May have increased efficacy in patients with NOD2 variants")?;
        impl2.set_item("evidence_level", "limited")?;
        treatment_implications.append(impl2)?;
        
        let impl3 = PyDict::new(py);
        impl3.set_item("treatment", "Surgery")?;
        impl3.set_item("effect", "Higher risk of postoperative recurrence")?;
        impl3.set_item("evidence_level", "strong")?;
        treatment_implications.append(impl3)?;
        
        result.set_item("treatment_implications", treatment_implications)?;
        
        let literature = PyList::empty(py);
        
        let lit1 = PyDict::new(py);
        lit1.set_item("title", "A frameshift mutation in NOD2 associated with susceptibility to Crohn's disease")?;
        lit1.set_item("authors", vec!["Ogura Y", "Bonen DK", "Inohara N", "et al."])?;
        lit1.set_item("journal", "Nature")?;
        lit1.set_item("year", 2001)?;
        lit1.set_item("doi", "10.1038/35079114")?;
        lit1.set_item("pubmed_id", "11385577")?;
        lit1.set_item("key_findings", "Identification of NOD2 as a susceptibility gene for Crohn's disease.")?;
        literature.append(lit1)?;
        
        let lit2 = PyDict::new(py);
        lit2.set_item("title", "Association between the R702W mutation in the NOD2/CARD15 gene and Crohn's disease in Hungarian and German cohorts")?;
        lit2.set_item("authors", vec!["Nagy Z", "Karadi O", "Rumi G", "et al."])?;
        lit2.set_item("journal", "World J Gastroenterol")?;
        lit2.set_item("year", 2005)?;
        lit2.set_item("pubmed_id", "16437633")?;
        lit2.set_item("key_findings", "Confirmed the association between R702W mutation and Crohn's disease in European populations.")?;
        literature.append(lit2)?;
        
        result.set_item("literature", literature)?;
    } else {
        // Return a generic template for other variants
        result.set_item("gene", gene)?;
        result.set_item("variant", variant)?;
        result.set_item("significance", "unknown")?;
        result.set_item("description", "Detailed information not available for this variant.")?;
        
        let frequency = PyDict::new(py);
        frequency.set_item("general_population", 0.0)?;
        result.set_item("frequency", frequency)?;
        
        result.set_item("treatment_implications", PyList::empty(py))?;
        result.set_item("literature", PyList::empty(py))?;
    }
    
    Ok(result.into())
}

/// Convert Python patient data to Rust
fn convert_patient_data(py: Python, patient_data: PyObject) -> PyResult<PatientData> {
    let patient_dict = patient_data.extract::<&PyDict>(py)?;

    // Extract patient_id
    let patient_id = match patient_dict.get_item("patient_id") {
        Some(id) => id.extract::<String>()?,
        None => return Err(PyValueError::new_err("Missing patient_id")),
    };

    // Extract demographics
    let demographics = match patient_dict.get_item("demographics") {
        Some(demos) => {
            let demo_dict = demos.extract::<&PyDict>()?;
            crate::models::Demographics {
                age: demo_dict
                    .get_item("age")
                    .map(|v| v.extract::<u32>())
                    .transpose()
                    .unwrap_or(Ok(0))?,
                sex: demo_dict
                    .get_item("sex")
                    .map(|v| v.extract::<String>())
                    .transpose()
                    .unwrap_or(Ok("unknown".to_string()))?,
                ethnicity: demo_dict
                    .get_item("ethnicity")
                    .map(|v| v.extract::<String>())
                    .transpose()
                    .unwrap_or(Ok("unknown".to_string()))?,
                weight: demo_dict
                    .get_item("weight")
                    .map(|v| v.extract::<f64>())
                    .transpose()
                    .unwrap_or(Ok(0.0))?,
                height: demo_dict
                    .get_item("height")
                    .map(|v| v.extract::<f64>())
                    .transpose()
                    .unwrap_or(Ok(0.0))?,
            }
        }
        None => crate::models::Demographics {
            age: 0,
            sex: "unknown".to_string(),
            ethnicity: "unknown".to_string(),
            weight: 0.0,
            height: 0.0,
        },
    };

    // Extract clinical_data
    let clinical_data = match patient_dict.get_item("clinical_data") {
        Some(clinical) => {
            let clinical_dict = clinical.extract::<&PyDict>()?;
            let crohns_type = clinical_dict
                .get_item("crohns_type")
                .map(|v| v.extract::<String>())
                .transpose()
                .unwrap_or(Ok("unknown".to_string()))?;

            // Extract disease_activity
            let disease_activity = match clinical_dict.get_item("disease_activity") {
                Some(activity) => {
                    let activity_dict = activity.extract::<&PyDict>()?;
                    crate::models::DiseaseActivity {
                        cdai: activity_dict
                            .get_item("CDAI")
                            .map(|v| v.extract::<u32>())
                            .transpose()
                            .unwrap_or(Ok(0))?,
                        ses_cd: activity_dict
                            .get_item("SES_CD")
                            .map(|v| v.extract::<u32>())
                            .transpose()
                            .unwrap_or(Ok(0))?,
                        fecal_calprotectin: activity_dict
                            .get_item("fecal_calprotectin")
                            .map(|v| v.extract::<f64>())
                            .transpose()
                            .unwrap_or(Ok(0.0))?,
                        crp: activity_dict
                            .get_item("CRP")
                            .map(|v| v.extract::<f64>())
                            .transpose()
                            .unwrap_or(Ok(0.0))?,
                        esr: activity_dict
                            .get_item("ESR")
                            .map(|v| v.extract::<u32>())
                            .transpose()
                            .unwrap_or(Ok(0))?,
                    }
                }
                None => crate::models::DiseaseActivity {
                    cdai: 0,
                    ses_cd: 0,
                    fecal_calprotectin: 0.0,
                    crp: 0.0,
                    esr: 0,
                },
            };

            crate::models::ClinicalData {
                crohns_type,
                disease_activity,
            }
        }
        None => crate::models::ClinicalData {
            crohns_type: "unknown".to_string(),
            disease_activity: crate::models::DiseaseActivity {
                cdai: 0,
                ses_cd: 0,
                fecal_calprotectin: 0.0,
                crp: 0.0,
                esr: 0,
            },
        },
    };

    // Extract biomarkers
    let biomarkers = match patient_dict.get_item("biomarkers") {
        Some(bio) => {
            let bio_dict = bio.extract::<&PyDict>()?;
            
            // Extract genetic_markers
            let genetic_markers = match bio_dict.get_item("genetic_markers") {
                Some(markers) => {
                    let marker_list = markers.extract::<&PyList>()?;
                    let mut markers_vec = Vec::new();
                    for marker in marker_list {
                        let marker_dict = marker.extract::<&PyDict>()?;
                        markers_vec.push(crate::models::GeneticMarker {
                            gene: marker_dict
                                .get_item("gene")
                                .map(|v| v.extract::<String>())
                                .transpose()
                                .unwrap_or(Ok("unknown".to_string()))?,
                            variant: marker_dict
                                .get_item("variant")
                                .map(|v| v.extract::<String>())
                                .transpose()
                                .unwrap_or(Ok("unknown".to_string()))?,
                            zygosity: marker_dict
                                .get_item("zygosity")
                                .map(|v| v.extract::<String>())
                                .transpose()
                                .unwrap_or(Ok("unknown".to_string()))?,
                        });
                    }
                    markers_vec
                }
                None => Vec::new(),
            };
            
            // Extract microbiome_profile
            let microbiome_profile = match bio_dict.get_item("microbiome_profile") {
                Some(microbiome) => {
                    let microbiome_dict = microbiome.extract::<&PyDict>()?;
                    let diversity_index = microbiome_dict
                        .get_item("diversity_index")
                        .map(|v| v.extract::<f64>())
                        .transpose()
                        .unwrap_or(Ok(0.0))?;
                    
                    // Extract key_species
                    let key_species = match microbiome_dict.get_item("key_species") {
                        Some(species) => {
                            let species_list = species.extract::<&PyList>()?;
                            let mut species_vec = Vec::new();
                            for species_item in species_list {
                                let species_dict = species_item.extract::<&PyDict>()?;
                                species_vec.push(crate::models::MicrobiomeSpecies {
                                    name: species_dict
                                        .get_item("name")
                                        .map(|v| v.extract::<String>())
                                        .transpose()
                                        .unwrap_or(Ok("unknown".to_string()))?,
                                    abundance: species_dict
                                        .get_item("abundance")
                                        .map(|v| v.extract::<f64>())
                                        .transpose()
                                        .unwrap_or(Ok(0.0))?,
                                });
                            }
                            species_vec
                        }
                        None => Vec::new(),
                    };
                    
                    crate::models::MicrobiomeProfile {
                        diversity_index,
                        key_species,
                    }
                }
                None => crate::models::MicrobiomeProfile {
                    diversity_index: 0.0,
                    key_species: Vec::new(),
                },
            };
            
            // Extract serum_markers
            let serum_markers = match bio_dict.get_item("serum_markers") {
                Some(serum) => {
                    let serum_dict = serum.extract::<&PyDict>()?;
                    crate::models::SerumMarkers {
                        crp: serum_dict
                            .get_item("CRP")
                            .map(|v| v.extract::<f64>())
                            .transpose()
                            .unwrap_or(Ok(0.0))?,
                        esr: serum_dict
                            .get_item("ESR")
                            .map(|v| v.extract::<u32>())
                            .transpose()
                            .unwrap_or(Ok(0))?,
                    }
                }
                None => crate::models::SerumMarkers {
                    crp: 0.0,
                    esr: 0,
                },
            };
            
            crate::models::Biomarkers {
                genetic_markers,
                microbiome_profile,
                serum_markers,
            }
        }
        None => crate::models::Biomarkers {
            genetic_markers: Vec::new(),
            microbiome_profile: crate::models::MicrobiomeProfile {
                diversity_index: 0.0,
                key_species: Vec::new(),
            },
            serum_markers: crate::models::SerumMarkers {
                crp: 0.0,
                esr: 0,
            },
        },
    };
    
    // Extract treatment_history
    let treatment_history = match patient_dict.get_item("treatment_history") {
        Some(history) => {
            let history_list = history.extract::<&PyList>()?;
            let mut history_vec = Vec::new();
            for treatment in history_list {
                let treatment_dict = treatment.extract::<&PyDict>()?;
                
                // Extract adverse_events
                let adverse_events = match treatment_dict.get_item("adverse_events") {
                    Some(events) => {
                        let events_list = events.extract::<&PyList>()?;
                        let mut events_vec = Vec::new();
                        for event in events_list {
                            events_vec.push(event.extract::<String>()?);
                        }
                        events_vec
                    }
                    None => Vec::new(),
                };
                
                history_vec.push(crate::models::TreatmentHistory {
                    medication: treatment_dict
                        .get_item("medication")
                        .map(|v| v.extract::<String>())
                        .transpose()
                        .unwrap_or(Ok("unknown".to_string()))?,
                    response: treatment_dict
                        .get_item("response")
                        .map(|v| v.extract::<String>())
                        .transpose()
                        .unwrap_or(Ok("unknown".to_string()))?,
                    adverse_events,
                });
            }
            history_vec
        }
        None => Vec::new(),
    };

    Ok(PatientData {
        patient_id,
        demographics,
        clinical_data,
        biomarkers,
        treatment_history,
    })
}

/// Convert Rust treatment plan to Python dict
fn convert_treatment_plan_to_py(py: Python, treatment_plan: TreatmentPlan) -> PyResult<PyObject> {
    let result = PyDict::new(py);
    
    // Convert treatment_plan
    let treatments = PyList::empty(py);
    for treatment in treatment_plan.treatment_plan {
        let treatment_dict = PyDict::new(py);
        treatment_dict.set_item("medication", treatment.medication)?;
        treatment_dict.set_item("dosage", treatment.dosage)?;
        treatment_dict.set_item("unit", treatment.unit)?;
        treatment_dict.set_item("frequency", treatment.frequency)?;
        treatment_dict.set_item("duration", treatment.duration)?;
        treatments.append(treatment_dict)?;
    }
    result.set_item("treatment_plan", treatments)?;
    
    // Set fitness and confidence
    result.set_item("fitness", treatment_plan.fitness)?;
    result.set_item("confidence", treatment_plan.confidence)?;
    
    // Convert explanations
    let explanations = PyList::empty(py);
    for explanation in treatment_plan.explanations {
        explanations.append(explanation)?;
    }
    result.set_item("explanations", explanations)?;
    
    // Convert biomarker_influences
    let influences = PyDict::new(py);
    for (biomarker, influence) in treatment_plan.biomarker_influences {
        influences.set_item(biomarker, influence)?;
    }
    result.set_item("biomarker_influences", influences)?;
    
    Ok(result.into())
}

/// Convert Python treatment plan to Rust
fn convert_treatment_plan(py: Python, treatment_plan: PyObject) -> PyResult<TreatmentPlan> {
    let plan_dict = treatment_plan.extract::<&PyDict>(py)?;
    
    // Extract treatment_plan
    let treatment_plan_list = match plan_dict.get_item("treatment_plan") {
        Some(treatments) => {
            let treatments_list = treatments.extract::<&PyList>()?;
            let mut treatments_vec = Vec::new();
            for treatment in treatments_list {
                let treatment_dict = treatment.extract::<&PyDict>()?;
                treatments_vec.push(crate::models::Treatment {
                    medication: treatment_dict
                        .get_item("medication")
                        .map(|v| v.extract::<String>())
                        .transpose()
                        .unwrap_or(Ok("unknown".to_string()))?,
                    dosage: treatment_dict
                        .get_item("dosage")
                        .map(|v| v.extract::<f64>())
                        .transpose()
                        .unwrap_or(Ok(0.0))?,
                    unit: treatment_dict
                        .get_item("unit")
                        .map(|v| v.extract::<String>())
                        .transpose()
                        .unwrap_or(Ok("mg".to_string()))?,
                    frequency: treatment_dict
                        .get_item("frequency")
                        .map(|v| v.extract::<String>())
                        .transpose()
                        .unwrap_or(Ok("daily".to_string()))?,
                    duration: treatment_dict
                        .get_item("duration")
                        .map(|v| v.extract::<u32>())
                        .transpose()
                        .unwrap_or(Ok(0))?,
                });
            }
            treatments_vec
        }
        None => Vec::new(),
    };
    
    // Extract fitness and confidence
    let fitness = plan_dict
        .get_item("fitness")
        .map(|v| v.extract::<f64>())
        .transpose()
        .unwrap_or(Ok(0.0))?;
    
    let confidence = plan_dict
        .get_item("confidence")
        .map(|v| v.extract::<f64>())
        .transpose()
        .unwrap_or(Ok(0.0))?;
    
    // Extract explanations
    let explanations = match plan_dict.get_item("explanations") {
        Some(explanations) => {
            let explanations_list = explanations.extract::<&PyList>()?;
            let mut explanations_vec = Vec::new();
            for explanation in explanations_list {
                explanations_vec.push(explanation.extract::<String>()?);
            }
            explanations_vec
        }
        None => Vec::new(),
    };
    
    // Extract biomarker_influences
    let biomarker_influences = match plan_dict.get_item("biomarker_influences") {
        Some(influences) => {
            let influences_dict = influences.extract::<&PyDict>()?;
            let mut influences_map = HashMap::new();
            for (key, value) in influences_dict.iter() {
                influences_map.insert(
                    key.extract::<String>()?,
                    value.extract::<f64>()?,
                );
            }
            influences_map
        }
        None => HashMap::new(),
    };
    
    // Create a dummy patient for the treatment plan
    // In a real implementation, the patient data would be properly extracted
    let patient = crate::models::Patient {
        id: "dummy".to_string(),
    };
    
    Ok(TreatmentPlan {
        patient,
        treatment_plan: treatment_plan_list,
        fitness,
        confidence,
        explanations,
        biomarker_influences,
    })
}

/// Convert Rust treatment verification to Python dict
fn convert_verification_to_py(py: Python, verification: TreatmentVerification) -> PyResult<PyObject> {
    let result = PyDict::new(py);
    
    result.set_item("is_valid", verification.is_valid)?;
    result.set_item("safety_score", verification.safety_score)?;
    result.set_item("efficacy_score", verification.efficacy_score)?;
    
    // Convert warnings
    let warnings = PyList::empty(py);
    for warning in verification.warnings {
        warnings.append(warning)?;
    }
    result.set_item("warnings", warnings)?;
    
    // Convert recommendations
    let recommendations = PyList::empty(py);
    for recommendation in verification.recommendations {
        recommendations.append(recommendation)?;
    }
    result.set_item("recommendations", recommendations)?;
    
    Ok(result.into())
}

/// Convert Python biomarker data to Rust
fn convert_biomarker_data(py: Python, biomarker_data: PyObject) -> PyResult<BiomarkerData> {
    let data_dict = biomarker_data.extract::<&PyDict>(py)?;
    
    // Extract patient_id
    let patient_id = match data_dict.get_item("patient_id") {
        Some(id) => id.extract::<String>()?,
        None => return Err(PyValueError::new_err("Missing patient_id in biomarker data")),
    };
    
    // Extract markers
    let markers = match data_dict.get_item("markers") {
        Some(markers) => {
            let markers_list = markers.extract::<&PyList>()?;
            let mut markers_vec = Vec::new();
            for marker in markers_list {
                let marker_dict = marker.extract::<&PyDict>()?;
                markers_vec.push(Biomarker {
                    name: marker_dict
                        .get_item("name")
                        .map(|v| v.extract::<String>())
                        .transpose()
                        .unwrap_or(Ok("unknown".to_string()))?,
                    value: marker_dict
                        .get_item("value")
                        .map(|v| v.extract::<f64>())
                        .transpose()
                        .unwrap_or(Ok(0.0))?,
                    zygosity: marker_dict
                        .get_item("zygosity")
                        .map(|v| v.extract::<String>())
                        .transpose()
                        .ok(),
                });
            }
            markers_vec
        }
        None => Vec::new(),
    };
    
    Ok(BiomarkerData {
        patient_id,
        markers,
    })
}

/// Convert Rust biomarker analysis to Python dict
fn convert_biomarker_analysis_to_py(py: Python, analysis: BiomarkerAnalysis) -> PyResult<PyObject> {
    let result = PyDict::new(py);
    
    result.set_item("patient_id", analysis.patient_id)?;
    result.set_item("overall_genetic_risk", analysis.overall_genetic_risk)?;
    
    // Convert biomarker_scores
    let scores = PyList::empty(py);
    for score in analysis.biomarker_scores {
        let score_dict = PyDict::new(py);
        score_dict.set_item("biomarker", score.biomarker)?;
        score_dict.set_item("impact_score", score.impact_score)?;
        score_dict.set_item("confidence", score.confidence)?;
        
        let medications = PyList::empty(py);
        for medication in score.relevant_medications {
            medications.append(medication)?;
        }
        score_dict.set_item("relevant_medications", medications)?;
        
        scores.append(score_dict)?;
    }
    result.set_item("biomarker_scores", scores)?;
    
    Ok(result.into())
}

/// Convert Rust treatment outcome simulation to Python dict
fn convert_outcome_simulation_to_py(py: Python, outcome: TreatmentOutcomeSimulation) -> PyResult<PyObject> {
    let result = PyDict::new(py);
    
    result.set_item("patient_id", outcome.patient_id)?;
    result.set_item("response_probability", outcome.response_probability)?;
    result.set_item("remission_probability", outcome.remission_probability)?;
    result.set_item("confidence", outcome.confidence)?;
    
    // Convert treatment_plan
    result.set_item("treatment_plan", convert_treatment_plan_to_py(py, outcome.treatment_plan)?)?;
    
    // Convert predicted_biomarker_changes
    let changes = PyList::empty(py);
    for change in outcome.predicted_biomarker_changes {
        let change_dict = PyDict::new(py);
        change_dict.set_item("biomarker", change.biomarker)?;
        change_dict.set_item("current_value", change.current_value)?;
        change_dict.set_item("predicted_value", change.predicted_value)?;
        change_dict.set_item("unit", change.unit)?;
        changes.append(change_dict)?;
    }
    result.set_item("predicted_biomarker_changes", changes)?;
    
    // Convert adverse_events
    let events = PyList::empty(py);
    for event in outcome.adverse_events {
        let event_dict = PyDict::new(py);
        event_dict.set_item("event_type", event.event_type)?;
        event_dict.set_item("probability", event.probability)?;
        event_dict.set_item("severity", event.severity)?;
        events.append(event_dict)?;
    }
    result.set_item("adverse_events", events)?;
    
    Ok(result.into())
}

/// Generate the Python module
#[pymodule]
pub fn genetic_engine_ffi(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyGeneticConfig>()?;
    m.add_class::<PyGeneticEngine>()?;
    m.add_class::<CrohnsTreatmentOptimizer>()?;
    
    m.add_function(wrap_pyfunction!(optimize_treatment, m)?)?;
    m.add_function(wrap_pyfunction!(evaluate_biomarkers, m)?)?;
    m.add_function(wrap_pyfunction!(simulate_treatment_outcome, m)?)?;
    m.add_function(wrap_pyfunction!(verify_treatment, m)?)?;
    m.add_function(wrap_pyfunction!(analyze_genetic_sequences, m)?)?;
    m.add_function(wrap_pyfunction!(get_crohns_variant_info, m)?)?;
    
    Ok(())
}