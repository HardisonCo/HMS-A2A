// genetic_sequence_analyzer.rs
//
// Genetic sequence analysis for Crohn's Disease-related genes and markers.
//
// This module provides tools for analyzing genetic sequences related to Crohn's Disease,
// identifying mutations, tracking variants, and assessing risk.

use std::collections::HashMap;
use std::fmt;
use std::sync::Arc;

/// Types of genetic biomarkers related to Crohn's disease
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum CrohnsBiomarker {
    /// NOD2 gene variant (key risk factor)
    NOD2,
    /// ATG16L1 gene variant
    ATG16L1,
    /// IL23R gene variant
    IL23R,
    /// IRGM gene variant
    IRGM,
    /// PTPN2 gene variant
    PTPN2,
    /// JAK2 gene variant (relevant for JAK inhibitor treatment)
    JAK2,
    /// STAT3 gene variant
    STAT3,
    /// TNF gene variant
    TNF,
    /// IL12B gene variant
    IL12B,
    /// IL10 gene variant
    IL10,
    /// Other biomarker (with string identifier)
    Other(String),
}

impl fmt::Display for CrohnsBiomarker {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            CrohnsBiomarker::NOD2 => write!(f, "NOD2"),
            CrohnsBiomarker::ATG16L1 => write!(f, "ATG16L1"),
            CrohnsBiomarker::IL23R => write!(f, "IL23R"),
            CrohnsBiomarker::IRGM => write!(f, "IRGM"),
            CrohnsBiomarker::PTPN2 => write!(f, "PTPN2"),
            CrohnsBiomarker::JAK2 => write!(f, "JAK2"),
            CrohnsBiomarker::STAT3 => write!(f, "STAT3"),
            CrohnsBiomarker::TNF => write!(f, "TNF"),
            CrohnsBiomarker::IL12B => write!(f, "IL12B"),
            CrohnsBiomarker::IL10 => write!(f, "IL10"),
            CrohnsBiomarker::Other(name) => write!(f, "{}", name),
        }
    }
}

/// Specific genetic variant 
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct GeneticVariant {
    /// Gene or biomarker affected
    pub biomarker: CrohnsBiomarker,
    /// Specific variant identifier (e.g., rs2066844)
    pub variant_id: String,
    /// Nucleotide change (e.g., "C>T")
    pub nucleotide_change: Option<String>,
    /// Amino acid change (e.g., "R702W")
    pub amino_acid_change: Option<String>,
    /// Risk allele
    pub risk_allele: Option<String>,
    /// Zygosity (homozygous or heterozygous)
    pub zygosity: Option<String>,
}

impl GeneticVariant {
    /// Create a new genetic variant
    pub fn new(
        biomarker: CrohnsBiomarker, 
        variant_id: &str,
        nucleotide_change: Option<&str>,
        amino_acid_change: Option<&str>,
        risk_allele: Option<&str>,
        zygosity: Option<&str>,
    ) -> Self {
        Self {
            biomarker,
            variant_id: variant_id.to_string(),
            nucleotide_change: nucleotide_change.map(|s| s.to_string()),
            amino_acid_change: amino_acid_change.map(|s| s.to_string()),
            risk_allele: risk_allele.map(|s| s.to_string()),
            zygosity: zygosity.map(|s| s.to_string()),
        }
    }

    /// Format the variant as a string
    pub fn to_string(&self) -> String {
        let mut parts = vec![format!("{} {}", self.biomarker, self.variant_id)];
        
        if let Some(aa) = &self.amino_acid_change {
            parts.push(aa.clone());
        }
        
        if let Some(zyg) = &self.zygosity {
            parts.push(format!("({})", zyg));
        }
        
        parts.join(" ")
    }
}

/// Clinical significance of a genetic variant
#[derive(Debug, Clone)]
pub struct VariantSignificance {
    /// Disease risk factor (0.0-1.0)
    pub risk_factor: f32,
    /// Treatment response predictions
    pub treatment_responses: HashMap<String, f32>,
    /// Disease location prediction
    pub disease_location: Option<String>,
    /// Disease behavior prediction
    pub disease_behavior: Option<String>,
    /// Confidence in the assessment (0.0-1.0)
    pub confidence: f32,
    /// Literature references
    pub references: Vec<String>,
}

/// A patient's genetic profile for Crohn's disease
#[derive(Debug, Clone)]
pub struct CrohnsGeneticProfile {
    /// Patient identifier
    pub patient_id: String,
    /// Genetic variants detected
    pub variants: Vec<GeneticVariant>,
    /// Genetic risk score (0.0-1.0)
    pub risk_score: f32,
    /// Treatment response predictions
    pub treatment_predictions: HashMap<String, f32>,
}

impl CrohnsGeneticProfile {
    /// Create a new genetic profile
    pub fn new(patient_id: &str) -> Self {
        Self {
            patient_id: patient_id.to_string(),
            variants: Vec::new(),
            risk_score: 0.0,
            treatment_predictions: HashMap::new(),
        }
    }

    /// Add a genetic variant
    pub fn add_variant(&mut self, variant: GeneticVariant) {
        self.variants.push(variant);
        // Recalculate risk score and treatment predictions when variants change
        self.update_risk_score();
        self.update_treatment_predictions();
    }

    /// Update risk score based on variants
    fn update_risk_score(&mut self) {
        // Simplified risk calculation
        // In a real implementation, this would use a more sophisticated model
        let mut risk = 0.0;
        
        for variant in &self.variants {
            match variant.biomarker {
                CrohnsBiomarker::NOD2 => {
                    if variant.variant_id == "rs2066844" || // R702W
                       variant.variant_id == "rs2066845" || // G908R
                       variant.variant_id == "rs2066847" {  // 1007fs
                        // NOD2 variants are the strongest genetic risk factors
                        risk += 0.15;
                        
                        // Higher risk for homozygous variants
                        if let Some(zyg) = &variant.zygosity {
                            if zyg == "homozygous" {
                                risk += 0.1;
                            }
                        }
                    }
                },
                CrohnsBiomarker::IL23R => {
                    if variant.variant_id == "rs11209026" { // R381Q
                        risk += 0.08;
                    }
                },
                CrohnsBiomarker::ATG16L1 => {
                    if variant.variant_id == "rs2241880" { // T300A
                        risk += 0.05;
                    }
                },
                CrohnsBiomarker::IRGM => {
                    risk += 0.03;
                },
                _ => {
                    risk += 0.01;
                }
            }
        }
        
        // Cap risk at 1.0
        self.risk_score = (risk).min(1.0);
    }

    /// Update treatment predictions based on variants
    fn update_treatment_predictions(&mut self) {
        // Clear existing predictions
        self.treatment_predictions.clear();
        
        // Base response rates (simplified)
        self.treatment_predictions.insert("Anti-TNF".to_string(), 0.6);
        self.treatment_predictions.insert("Anti-IL12/23".to_string(), 0.5);
        self.treatment_predictions.insert("JAK-Inhibitor".to_string(), 0.5);
        self.treatment_predictions.insert("5-ASA".to_string(), 0.4);
        self.treatment_predictions.insert("Steroids".to_string(), 0.7);
        self.treatment_predictions.insert("Immunomodulators".to_string(), 0.5);
        
        // Adjust based on genetic variants
        for variant in &self.variants {
            match variant.biomarker {
                CrohnsBiomarker::NOD2 => {
                    // NOD2 variants predict better response to anti-TNF
                    if let Some(response) = self.treatment_predictions.get_mut("Anti-TNF") {
                        *response += 0.1;
                    }
                    // NOD2 variants predict poorer response to 5-ASA
                    if let Some(response) = self.treatment_predictions.get_mut("5-ASA") {
                        *response -= 0.1;
                    }
                },
                CrohnsBiomarker::IL23R => {
                    // IL23R variants predict better response to IL12/23 inhibitors
                    if let Some(response) = self.treatment_predictions.get_mut("Anti-IL12/23") {
                        *response += 0.15;
                    }
                },
                CrohnsBiomarker::JAK2 | CrohnsBiomarker::STAT3 => {
                    // JAK/STAT pathway variants predict better response to JAK inhibitors
                    if let Some(response) = self.treatment_predictions.get_mut("JAK-Inhibitor") {
                        *response += 0.15;
                    }
                },
                CrohnsBiomarker::TNF => {
                    // TNF variants predict better response to anti-TNF
                    if let Some(response) = self.treatment_predictions.get_mut("Anti-TNF") {
                        *response += 0.1;
                    }
                },
                _ => {}
            }
        }
        
        // Cap all responses at max 0.95
        for response in self.treatment_predictions.values_mut() {
            *response = (*response).min(0.95);
        }
    }
}

/// Genetic sequence analyzer for Crohn's disease
pub struct GeneticSequenceAnalyzer {
    /// Reference sequences for key genes
    reference_sequences: HashMap<String, String>,
    /// Database of known variants
    variant_database: HashMap<String, VariantSignificance>,
}

impl GeneticSequenceAnalyzer {
    /// Create a new genetic sequence analyzer
    pub fn new() -> Self {
        Self {
            reference_sequences: HashMap::new(),
            variant_database: HashMap::new(),
        }
    }
    
    /// Load reference sequences
    pub fn load_references(&mut self, references: HashMap<String, String>) {
        self.reference_sequences = references;
    }
    
    /// Load variant database
    pub fn load_variant_database(&mut self, database: HashMap<String, VariantSignificance>) {
        self.variant_database = database;
    }
    
    /// Analyze a gene sequence
    pub fn analyze_sequence(&self, gene: &str, sequence: &str) -> Result<Vec<GeneticVariant>, String> {
        if let Some(reference) = self.reference_sequences.get(gene) {
            // In a real implementation, this would use proper sequence alignment
            // and variant calling algorithms. This is a simplified example.
            
            // Dummy implementation for demonstration
            let mut variants = Vec::new();
            
            if gene == "NOD2" {
                // Check for common NOD2 variants
                if sequence.len() > 2104 && sequence.chars().nth(2104) == Some('T') {
                    variants.push(GeneticVariant::new(
                        CrohnsBiomarker::NOD2,
                        "rs2066844",
                        Some("C>T"),
                        Some("R702W"),
                        Some("T"),
                        Some("heterozygous"),
                    ));
                }
                
                if sequence.len() > 2722 && sequence.chars().nth(2722) == Some('C') {
                    variants.push(GeneticVariant::new(
                        CrohnsBiomarker::NOD2,
                        "rs2066845",
                        Some("G>C"),
                        Some("G908R"),
                        Some("C"),
                        Some("heterozygous"),
                    ));
                }
            } else if gene == "IL23R" {
                // Check for IL23R variants
                if sequence.len() > 1142 && sequence.chars().nth(1142) == Some('A') {
                    variants.push(GeneticVariant::new(
                        CrohnsBiomarker::IL23R,
                        "rs11209026",
                        Some("G>A"),
                        Some("R381Q"),
                        Some("A"),
                        Some("heterozygous"),
                    ));
                }
            }
            
            Ok(variants)
        } else {
            Err(format!("No reference sequence available for gene {}", gene))
        }
    }
    
    /// Get significance of a variant
    pub fn get_variant_significance(&self, variant: &GeneticVariant) -> Option<&VariantSignificance> {
        self.variant_database.get(&variant.variant_id)
    }
    
    /// Create a genetic profile from sequence data
    pub fn create_genetic_profile(&self, patient_id: &str, sequences: &HashMap<String, String>) -> CrohnsGeneticProfile {
        let mut profile = CrohnsGeneticProfile::new(patient_id);
        
        // Analyze each sequence
        for (gene, sequence) in sequences {
            if let Ok(variants) = self.analyze_sequence(gene, sequence) {
                for variant in variants {
                    profile.add_variant(variant);
                }
            }
        }
        
        profile
    }
    
    /// Initialize with default data
    pub fn with_defaults() -> Self {
        let mut analyzer = Self::new();
        
        // Load reference sequences (simplified)
        let mut references = HashMap::new();
        references.insert("NOD2".to_string(), "ATGGGCCTTGGGACTTAGGC...".to_string());
        references.insert("IL23R".to_string(), "ATGGCGTCTGCTGAGAGTTC...".to_string());
        references.insert("ATG16L1".to_string(), "ATGGCAGACTCAGCTTCAGC...".to_string());
        analyzer.load_references(references);
        
        // Load variant database (simplified)
        let mut database = HashMap::new();
        
        // NOD2 variant
        let nod2_r702w = VariantSignificance {
            risk_factor: 0.25,
            treatment_responses: {
                let mut map = HashMap::new();
                map.insert("Anti-TNF".to_string(), 0.7);
                map.insert("Anti-IL12/23".to_string(), 0.5);
                map.insert("JAK-Inhibitor".to_string(), 0.5);
                map
            },
            disease_location: Some("Ileal".to_string()),
            disease_behavior: Some("Stricturing".to_string()),
            confidence: 0.9,
            references: vec!["PMID:12567161".to_string()],
        };
        database.insert("rs2066844".to_string(), nod2_r702w);
        
        // IL23R variant
        let il23r_r381q = VariantSignificance {
            risk_factor: 0.15,
            treatment_responses: {
                let mut map = HashMap::new();
                map.insert("Anti-IL12/23".to_string(), 0.8);
                map.insert("Anti-TNF".to_string(), 0.6);
                map.insert("JAK-Inhibitor".to_string(), 0.6);
                map
            },
            disease_location: Some("Colonic".to_string()),
            disease_behavior: Some("Inflammatory".to_string()),
            confidence: 0.85,
            references: vec!["PMID:17033580".to_string()],
        };
        database.insert("rs11209026".to_string(), il23r_r381q);
        
        analyzer.load_variant_database(database);
        
        analyzer
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_genetic_variant_creation() {
        let variant = GeneticVariant::new(
            CrohnsBiomarker::NOD2,
            "rs2066844",
            Some("C>T"),
            Some("R702W"),
            Some("T"),
            Some("heterozygous"),
        );
        
        assert_eq!(variant.biomarker, CrohnsBiomarker::NOD2);
        assert_eq!(variant.variant_id, "rs2066844");
        assert_eq!(variant.nucleotide_change, Some("C>T".to_string()));
        assert_eq!(variant.amino_acid_change, Some("R702W".to_string()));
        assert_eq!(variant.risk_allele, Some("T".to_string()));
        assert_eq!(variant.zygosity, Some("heterozygous".to_string()));
    }
    
    #[test]
    fn test_crohns_genetic_profile() {
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
        
        assert_eq!(profile.patient_id, "P12345");
        assert_eq!(profile.variants.len(), 1);
        assert!(profile.risk_score > 0.0);
        assert!(profile.treatment_predictions.contains_key("Anti-TNF"));
    }
    
    #[test]
    fn test_analyzer_with_defaults() {
        let analyzer = GeneticSequenceAnalyzer::with_defaults();
        
        // Check that reference sequences were loaded
        assert!(analyzer.reference_sequences.contains_key("NOD2"));
        assert!(analyzer.reference_sequences.contains_key("IL23R"));
        
        // Check that variant database was loaded
        assert!(analyzer.variant_database.contains_key("rs2066844"));
        assert!(analyzer.variant_database.contains_key("rs11209026"));
    }
}