//! FFI bindings for the genetic engine
//!
//! This module provides Foreign Function Interface bindings to expose
//! the genetic engine functionality to other languages, particularly
//! Python for HMS-A2A integration.

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::wrap_pyfunction;
use pyo3::exceptions::PyValueError;

use serde_json;
use std::collections::HashMap;

use crate::core::{GeneticEngine, GeneticConfig, Population, Individual};
use crate::representation::{TreatmentChromosome, TreatmentGene, PatientContext, Medication, DosageUnit, Frequency};

/// Python class for genetic treatment optimization
#[pyclass]
pub struct TreatmentOptimizer {
    /// The underlying genetic engine
    engine: GeneticEngine,
}

#[pymethods]
impl TreatmentOptimizer {
    /// Create a new treatment optimizer with default configuration
    #[new]
    fn new() -> Self {
        Self {
            engine: GeneticEngine::new(GeneticConfig::default()),
        }
    }
    
    /// Optimize a treatment plan for a patient
    fn optimize_treatment(&mut self, patient_data: PyObject, py: Python) -> PyResult<PyObject> {
        // Convert Python patient data to Rust PatientContext
        let patient_context = self.convert_patient_data(patient_data, py)?;
        
        // Create initial population (simplified for now)
        let initial_population = self.create_initial_population(&patient_context);
        
        // Run the optimization
        let (final_population, stats) = self.engine.optimize(initial_population, &patient_context);
        
        // Convert the best treatment back to Python
        if let Some(best_individual) = final_population.best_individual {
            self.convert_treatment_to_python(best_individual, stats.best_fitness, py)
        } else {
            Err(PyValueError::new_err("Optimization failed to find a valid treatment plan"))
        }
    }
    
    /// Evaluate the fitness of a treatment plan
    fn evaluate_fitness(&self, treatment_plan: PyObject, patient_data: PyObject, py: Python) -> PyResult<f64> {
        // Convert Python patient data to Rust PatientContext
        let patient_context = self.convert_patient_data(patient_data, py)?;
        
        // Convert Python treatment plan to TreatmentChromosome
        let treatment_chromosome = self.convert_python_to_treatment(treatment_plan, py)?;
        
        // Create an individual
        let individual = Individual::new(treatment_chromosome);
        
        // This is a simplified version - the actual implementation would use the fitness function
        // For now, we return a dummy value
        Ok(0.75)
    }
    
    /// Helper method to convert Python patient data to Rust PatientContext
    fn convert_patient_data(&self, patient_data: PyObject, py: Python) -> PyResult<PatientContext> {
        // This is a simplified implementation
        // In a real implementation, we would parse the Python dictionary
        let patient_dict = patient_data.extract::<&PyDict>(py)?;
        
        let patient_id = patient_dict.get_item("patient_id")
            .ok_or_else(|| PyValueError::new_err("Missing patient_id"))?
            .extract::<String>()?;
            
        let age = patient_dict.get_item("age")
            .ok_or_else(|| PyValueError::new_err("Missing age"))?
            .extract::<u32>()?;
            
        let weight = patient_dict.get_item("weight")
            .ok_or_else(|| PyValueError::new_err("Missing weight"))?
            .extract::<f64>()?;
        
        // For simplicity, we use default values for the remaining fields
        // In a real implementation, we would parse all fields
        use crate::representation::{CrohnsType, DiseaseSeverity};
        let patient_context = PatientContext::new(
            patient_id,
            age,
            weight,
            CrohnsType::Ileocolonic, // Default
            DiseaseSeverity::Moderate, // Default
        );
        
        Ok(patient_context)
    }
    
    /// Helper method to create an initial population
    fn create_initial_population(&self, patient_context: &PatientContext) -> Population {
        // This is a simplified implementation
        // In a real implementation, we would generate a diverse initial population
        let mut individuals = Vec::new();
        
        for _ in 0..100 {
            let genes = vec![
                TreatmentGene::new(
                    Medication::Upadacitinib,
                    15.0,
                    DosageUnit::Mg,
                    Frequency::Daily,
                    30
                ),
                TreatmentGene::new(
                    Medication::Azathioprine,
                    50.0,
                    DosageUnit::Mg,
                    Frequency::Daily,
                    30
                ),
            ];
            
            let chromosome = TreatmentChromosome::new(genes);
            individuals.push(Individual::new(chromosome));
        }
        
        Population::new(individuals)
    }
    
    /// Helper method to convert a treatment individual to Python
    fn convert_treatment_to_python(&self, individual: Individual, fitness: f64, py: Python) -> PyResult<PyObject> {
        let treatment_dict = PyDict::new(py);
        
        // Add fitness
        treatment_dict.set_item("fitness", fitness)?;
        
        // Add medications
        let medications = PyList::empty(py);
        for gene in &individual.chromosome.genes {
            let medication_dict = PyDict::new(py);
            medication_dict.set_item("name", format!("{:?}", gene.medication))?;
            medication_dict.set_item("dosage", gene.dosage)?;
            medication_dict.set_item("unit", format!("{:?}", gene.unit))?;
            medication_dict.set_item("frequency", format!("{:?}", gene.frequency))?;
            medication_dict.set_item("duration", gene.duration)?;
            
            medications.append(medication_dict)?;
        }
        treatment_dict.set_item("medications", medications)?;
        
        // Add attributes
        let attributes = PyDict::new(py);
        for (key, value) in &individual.chromosome.attributes {
            attributes.set_item(key, value)?;
        }
        treatment_dict.set_item("attributes", attributes)?;
        
        Ok(treatment_dict.to_object(py))
    }
    
    /// Helper method to convert Python treatment to TreatmentChromosome
    fn convert_python_to_treatment(&self, treatment_plan: PyObject, py: Python) -> PyResult<TreatmentChromosome> {
        // This is a simplified implementation
        // In a real implementation, we would parse the Python dictionary
        
        // For now, we return a dummy chromosome
        let genes = vec![
            TreatmentGene::new(
                Medication::Upadacitinib,
                15.0,
                DosageUnit::Mg,
                Frequency::Daily,
                30
            ),
        ];
        
        Ok(TreatmentChromosome::new(genes))
    }
}

/// Python module definition
#[pymodule]
fn genetic_engine(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<TreatmentOptimizer>()?;
    
    Ok(())
}