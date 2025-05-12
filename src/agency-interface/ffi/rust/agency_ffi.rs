//! Rust bindings for the agency FFI interface.
//!
//! This module provides Rust bindings for the agency FFI interface,
//! allowing Rust code to interact with the agency system.

use std::ffi::{c_char, CStr, CString};
use std::os::raw::c_int;
use std::ptr;
use std::slice;
use std::str;

#[link(name = "agency_ffi")]
extern "C" {
    fn agency_get_context(agency: *const c_char) -> *mut c_char;
    fn agency_get_issue_finder(agency: *const c_char) -> *mut c_char;
    fn agency_get_research_connector(agency: *const c_char) -> *mut c_char;
    fn agency_get_ascii_art(agency: *const c_char) -> *mut c_char;
    fn agency_free_context(context: *mut c_char);
    fn agency_get_all_agencies() -> *mut c_char;
    fn agency_get_agencies_by_tier(tier: c_int) -> *mut c_char;
    fn agency_get_agencies_by_domain(domain: *const c_char) -> *mut c_char;
    fn agency_verify_issue(agency: *const c_char, issue_json: *const c_char) -> c_int;
}

/// Error type for agency operations.
#[derive(Debug)]
pub enum AgencyError {
    /// The specified agency was not found.
    AgencyNotFound,
    /// An error occurred while performing an operation.
    OperationError,
    /// An invalid argument was provided.
    InvalidArgument,
    /// A conversion error occurred.
    ConversionError,
}

/// Helper function to convert a C string to a Rust string.
fn c_string_to_string(c_str: *mut c_char) -> Result<String, AgencyError> {
    if c_str.is_null() {
        return Err(AgencyError::OperationError);
    }

    let string = unsafe {
        let cstr = CStr::from_ptr(c_str);
        let result = cstr.to_str().map_err(|_| AgencyError::ConversionError)?.to_owned();
        agency_free_context(c_str);
        result
    };

    Ok(string)
}

/// Get the context information for an agency.
///
/// Returns JSON-formatted context information for the specified agency.
///
/// # Arguments
///
/// * `agency` - The agency acronym (e.g., "HHS", "DOD").
///
/// # Returns
///
/// A Result containing the context information as a string, or an error.
pub fn get_context(agency: &str) -> Result<String, AgencyError> {
    let agency_cstr = CString::new(agency).map_err(|_| AgencyError::InvalidArgument)?;
    let context_ptr = unsafe { agency_get_context(agency_cstr.as_ptr()) };
    c_string_to_string(context_ptr)
}

/// Get the issue finder data for an agency.
///
/// Returns issue finder data for the specified agency.
///
/// # Arguments
///
/// * `agency` - The agency acronym (e.g., "HHS", "DOD").
///
/// # Returns
///
/// A Result containing the issue finder data as a string, or an error.
pub fn get_issue_finder(agency: &str) -> Result<String, AgencyError> {
    let agency_cstr = CString::new(agency).map_err(|_| AgencyError::InvalidArgument)?;
    let finder_ptr = unsafe { agency_get_issue_finder(agency_cstr.as_ptr()) };
    c_string_to_string(finder_ptr)
}

/// Get the research connector data for an agency.
///
/// Returns research connector data for the specified agency.
///
/// # Arguments
///
/// * `agency` - The agency acronym (e.g., "HHS", "DOD").
///
/// # Returns
///
/// A Result containing the research connector data as a string, or an error.
pub fn get_research_connector(agency: &str) -> Result<String, AgencyError> {
    let agency_cstr = CString::new(agency).map_err(|_| AgencyError::InvalidArgument)?;
    let connector_ptr = unsafe { agency_get_research_connector(agency_cstr.as_ptr()) };
    c_string_to_string(connector_ptr)
}

/// Get the ASCII art for an agency.
///
/// Returns the ASCII art for the specified agency.
///
/// # Arguments
///
/// * `agency` - The agency acronym (e.g., "HHS", "DOD").
///
/// # Returns
///
/// A Result containing the ASCII art as a string, or an error.
pub fn get_ascii_art(agency: &str) -> Result<String, AgencyError> {
    let agency_cstr = CString::new(agency).map_err(|_| AgencyError::InvalidArgument)?;
    let art_ptr = unsafe { agency_get_ascii_art(agency_cstr.as_ptr()) };
    c_string_to_string(art_ptr)
}

/// Get the list of all available agencies.
///
/// Returns a JSON array of agency acronyms.
///
/// # Returns
///
/// A Result containing the agency list as a string, or an error.
pub fn get_all_agencies() -> Result<String, AgencyError> {
    let agencies_ptr = unsafe { agency_get_all_agencies() };
    c_string_to_string(agencies_ptr)
}

/// Get the agencies in a specific tier.
///
/// Returns a JSON array of agency acronyms for the specified tier.
///
/// # Arguments
///
/// * `tier` - The tier number (1-8).
///
/// # Returns
///
/// A Result containing the agency list as a string, or an error.
pub fn get_agencies_by_tier(tier: i32) -> Result<String, AgencyError> {
    let agencies_ptr = unsafe { agency_get_agencies_by_tier(tier) };
    c_string_to_string(agencies_ptr)
}

/// Get the agencies for a specific domain.
///
/// Returns a JSON array of agency acronyms for the specified domain.
///
/// # Arguments
///
/// * `domain` - The domain name (e.g., "healthcare", "defense").
///
/// # Returns
///
/// A Result containing the agency list as a string, or an error.
pub fn get_agencies_by_domain(domain: &str) -> Result<String, AgencyError> {
    let domain_cstr = CString::new(domain).map_err(|_| AgencyError::InvalidArgument)?;
    let agencies_ptr = unsafe { agency_get_agencies_by_domain(domain_cstr.as_ptr()) };
    c_string_to_string(agencies_ptr)
}

/// Verify an issue using the agency theorem prover.
///
/// Verifies that an issue is valid according to domain theorems.
///
/// # Arguments
///
/// * `agency` - The agency acronym (e.g., "HHS", "DOD").
/// * `issue_json` - JSON-formatted issue data.
///
/// # Returns
///
/// A Result containing a boolean indicating whether the issue is valid, or an error.
pub fn verify_issue(agency: &str, issue_json: &str) -> Result<bool, AgencyError> {
    let agency_cstr = CString::new(agency).map_err(|_| AgencyError::InvalidArgument)?;
    let issue_cstr = CString::new(issue_json).map_err(|_| AgencyError::InvalidArgument)?;
    
    let result = unsafe { agency_verify_issue(agency_cstr.as_ptr(), issue_cstr.as_ptr()) };
    
    match result {
        1 => Ok(true),
        0 => Ok(false),
        _ => Err(AgencyError::OperationError),
    }
}

/// A struct representing an agency.
#[derive(Debug, Clone)]
pub struct Agency {
    /// The agency acronym.
    pub acronym: String,
    /// The agency name.
    pub name: String,
    /// The agency domain.
    pub domain: String,
    /// The agency description.
    pub description: String,
    /// The agency tier.
    pub tier: i32,
}

/// Get agency information as a struct.
///
/// # Arguments
///
/// * `agency` - The agency acronym (e.g., "HHS", "DOD").
///
/// # Returns
///
/// A Result containing an Agency struct, or an error.
pub fn get_agency_info(agency: &str) -> Result<Agency, AgencyError> {
    let context = get_context(agency)?;
    
    // Parse the JSON context
    let json: serde_json::Value = serde_json::from_str(&context)
        .map_err(|_| AgencyError::ConversionError)?;
    
    // Extract the agency information
    let acronym = json["acronym"].as_str()
        .ok_or(AgencyError::ConversionError)?
        .to_owned();
    
    let name = json["name"].as_str()
        .ok_or(AgencyError::ConversionError)?
        .to_owned();
    
    let domain = json["domain"].as_str()
        .unwrap_or("general")
        .to_owned();
    
    let description = json["description"].as_str()
        .unwrap_or("")
        .to_owned();
    
    let tier = json["tier"].as_i64()
        .unwrap_or(0) as i32;
    
    Ok(Agency {
        acronym,
        name,
        domain,
        description,
        tier,
    })
}