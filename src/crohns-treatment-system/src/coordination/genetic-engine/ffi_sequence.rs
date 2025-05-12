// ffi_sequence.rs
//
// FFI interface for genetic sequence analysis in the Crohn's disease treatment system.
//
// This module exposes genetic analysis capabilities to Python and other languages.

use std::collections::HashMap;
use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_double, c_int};
use std::sync::{Arc, Mutex};

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

use crate::genetic_sequence_analyzer::{
    GeneticSequenceAnalyzer, CrohnsGeneticProfile, GeneticVariant, CrohnsBiomarker
};

// Global analyzer instance
lazy_static! {
    static ref GENETIC_ANALYZER: Mutex<Option<GeneticSequenceAnalyzer>> = Mutex::new(None);
}

/// Initialize the genetic sequence analyzer
#[no_mangle]
pub extern "C" fn initialize_sequence_analyzer() -> *mut c_void {
    let mut analyzer_lock = GENETIC_ANALYZER.lock().unwrap();
    
    // Initialize with default data
    *analyzer_lock = Some(GeneticSequenceAnalyzer::with_defaults());
    
    // Return a non-null pointer on success
    Box::into_raw(Box::new(1)) as *mut c_void
}

/// Clean up resources
#[no_mangle]
pub extern "C" fn shutdown_sequence_analyzer() {
    let mut analyzer_lock = GENETIC_ANALYZER.lock().unwrap();
    *analyzer_lock = None;
}

/// C-compatible genetic analysis result
#[repr(C)]
pub struct GeneticAnalysisResult {
    /// Analysis result as JSON string
    result: *mut c_char,
    /// Error message if analysis failed
    error: *mut c_char,
}

/// Free a genetic analysis result
#[no_mangle]
pub extern "C" fn free_genetic_analysis_result(result: *mut GeneticAnalysisResult) {
    if !result.is_null() {
        unsafe {
            let result_ref = &mut *result;
            
            // Free the result string if not null
            if !result_ref.result.is_null() {
                drop(CString::from_raw(result_ref.result));
                result_ref.result = std::ptr::null_mut();
            }
            
            // Free the error string if not null
            if !result_ref.error.is_null() {
                drop(CString::from_raw(result_ref.error));
                result_ref.error = std::ptr::null_mut();
            }
            
            // Free the result itself
            drop(Box::from_raw(result));
        }
    }
}

/// Analyze genetic sequence data
///
/// Takes a JSON string containing patient data including genetic sequences
/// Returns a JSON string with the analysis results
#[no_mangle]
pub extern "C" fn analyze_genetic_sequences(data_json: *const c_char) -> *mut GeneticAnalysisResult {
    let result_box = Box::new(GeneticAnalysisResult {
        result: std::ptr::null_mut(),
        error: std::ptr::null_mut(),
    });
    let result = Box::into_raw(result_box);
    
    // Get the analyzer
    let analyzer_lock = GENETIC_ANALYZER.lock().unwrap();
    let analyzer = match &*analyzer_lock {
        Some(analyzer) => analyzer,
        None => {
            unsafe {
                (*result).error = CString::new("Sequence analyzer not initialized").unwrap().into_raw();
            }
            return result;
        }
    };
    
    // Parse the input JSON
    let data_str = unsafe {
        match CStr::from_ptr(data_json).to_str() {
            Ok(s) => s,
            Err(_) => {
                (*result).error = CString::new("Invalid UTF-8 in input JSON").unwrap().into_raw();
                return result;
            }
        }
    };
    
    #[derive(Deserialize)]
    struct PatientData {
        patient_id: String,
        sequences: HashMap<String, String>,
        #[serde(default)]
        variants: Option<Vec<VariantInput>>,
    }
    
    #[derive(Deserialize)]
    struct VariantInput {
        gene: String,
        variant_id: String,
        zygosity: Option<String>,
    }
    
    let patient_data: PatientData = match serde_json::from_str(data_str) {
        Ok(data) => data,
        Err(e) => {
            unsafe {
                (*result).error = CString::new(format!("Failed to parse JSON: {}", e)).unwrap().into_raw();
            }
            return result;
        }
    };
    
    // Analyze sequences
    let mut profile = CrohnsGeneticProfile::new(&patient_data.patient_id);
    
    // Process sequences
    if !patient_data.sequences.is_empty() {
        profile = analyzer.create_genetic_profile(&patient_data.patient_id, &patient_data.sequences);
    }
    
    // Add explicitly provided variants
    if let Some(variants) = patient_data.variants {
        for v in variants {
            let biomarker = match v.gene.as_str() {
                "NOD2" => CrohnsBiomarker::NOD2,
                "IL23R" => CrohnsBiomarker::IL23R,
                "ATG16L1" => CrohnsBiomarker::ATG16L1,
                "IRGM" => CrohnsBiomarker::IRGM,
                "PTPN2" => CrohnsBiomarker::PTPN2,
                "JAK2" => CrohnsBiomarker::JAK2,
                "STAT3" => CrohnsBiomarker::STAT3,
                "TNF" => CrohnsBiomarker::TNF,
                "IL12B" => CrohnsBiomarker::IL12B,
                "IL10" => CrohnsBiomarker::IL10,
                other => CrohnsBiomarker::Other(other.to_string()),
            };
            
            let variant = GeneticVariant::new(
                biomarker,
                &v.variant_id,
                None,
                None,
                None,
                v.zygosity.as_deref(),
            );
            
            profile.add_variant(variant);
        }
    }
    
    // Create result JSON
    let result_json = create_profile_json(&profile);
    
    // Set the result
    unsafe {
        (*result).result = CString::new(result_json.to_string()).unwrap().into_raw();
    }
    
    result
}

/// Get significance of a specific variant
#[no_mangle]
pub extern "C" fn get_variant_significance(variant_id: *const c_char) -> *mut GeneticAnalysisResult {
    let result_box = Box::new(GeneticAnalysisResult {
        result: std::ptr::null_mut(),
        error: std::ptr::null_mut(),
    });
    let result = Box::into_raw(result_box);
    
    // Get the analyzer
    let analyzer_lock = GENETIC_ANALYZER.lock().unwrap();
    let analyzer = match &*analyzer_lock {
        Some(analyzer) => analyzer,
        None => {
            unsafe {
                (*result).error = CString::new("Sequence analyzer not initialized").unwrap().into_raw();
            }
            return result;
        }
    };
    
    // Parse the variant ID
    let variant_id_str = unsafe {
        match CStr::from_ptr(variant_id).to_str() {
            Ok(s) => s,
            Err(_) => {
                (*result).error = CString::new("Invalid UTF-8 in variant ID").unwrap().into_raw();
                return result;
            }
        }
    };
    
    // Create a dummy variant to check significance
    let variant = GeneticVariant::new(
        CrohnsBiomarker::Other("".to_string()),
        variant_id_str,
        None,
        None,
        None,
        None,
    );
    
    // Get significance
    if let Some(significance) = analyzer.get_variant_significance(&variant) {
        // Create JSON
        let significance_json = json!({
            "variant_id": variant_id_str,
            "risk_factor": significance.risk_factor,
            "treatment_responses": significance.treatment_responses,
            "disease_location": significance.disease_location,
            "disease_behavior": significance.disease_behavior,
            "confidence": significance.confidence,
            "references": significance.references,
        });
        
        // Set the result
        unsafe {
            (*result).result = CString::new(significance_json.to_string()).unwrap().into_raw();
        }
    } else {
        // Variant not found
        unsafe {
            (*result).error = CString::new(format!("Variant {} not found in database", variant_id_str)).unwrap().into_raw();
        }
    }
    
    result
}

/// Create a JSON representation of a genetic profile
fn create_profile_json(profile: &CrohnsGeneticProfile) -> Value {
    let variants_json: Vec<Value> = profile.variants.iter().map(|v| {
        json!({
            "biomarker": v.biomarker.to_string(),
            "variant_id": v.variant_id,
            "nucleotide_change": v.nucleotide_change,
            "amino_acid_change": v.amino_acid_change,
            "risk_allele": v.risk_allele,
            "zygosity": v.zygosity,
        })
    }).collect();
    
    json!({
        "patient_id": profile.patient_id,
        "variants": variants_json,
        "risk_score": profile.risk_score,
        "treatment_predictions": profile.treatment_predictions,
    })
}

// Used by Rust for storing context
use std::os::raw::c_void;

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_profile_json_creation() {
        let mut profile = CrohnsGeneticProfile::new("P12345");
        
        // Add variants
        profile.add_variant(GeneticVariant::new(
            CrohnsBiomarker::NOD2,
            "rs2066844",
            Some("C>T"),
            Some("R702W"),
            Some("T"),
            Some("heterozygous"),
        ));
        
        let json = create_profile_json(&profile);
        
        assert_eq!(json["patient_id"], "P12345");
        assert!(!json["variants"].as_array().unwrap().is_empty());
        assert!(json.get("risk_score").is_some());
        assert!(json.get("treatment_predictions").is_some());
    }
}