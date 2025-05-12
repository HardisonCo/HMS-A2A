/**
 * @file agency_ffi.h
 * @brief FFI interface specification for the agency interface.
 *
 * This header defines the C interface for accessing agency context data across 
 * language boundaries. It provides function prototypes for retrieving
 * agency-specific context information that can be used from any language
 * that supports FFI with C.
 */

#ifndef AGENCY_FFI_H
#define AGENCY_FFI_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Get the context information for an agency.
 *
 * Returns JSON-formatted context information for the specified agency.
 * The caller is responsible for freeing the returned string using
 * agency_free_context() when it is no longer needed.
 *
 * @param agency The agency acronym (e.g., "HHS", "DOD").
 * @return A pointer to a null-terminated string containing the context
 *         information, or NULL if the agency is not found or an error occurs.
 */
char* agency_get_context(const char* agency);

/**
 * @brief Get the issue finder data for an agency.
 *
 * Returns JSON-formatted issue finder data for the specified agency.
 * The caller is responsible for freeing the returned string using
 * agency_free_context() when it is no longer needed.
 *
 * @param agency The agency acronym (e.g., "HHS", "DOD").
 * @return A pointer to a null-terminated string containing the issue finder
 *         data, or NULL if the agency is not found or an error occurs.
 */
char* agency_get_issue_finder(const char* agency);

/**
 * @brief Get the research connector data for an agency.
 *
 * Returns JSON-formatted research connector data for the specified agency.
 * The caller is responsible for freeing the returned string using
 * agency_free_context() when it is no longer needed.
 *
 * @param agency The agency acronym (e.g., "HHS", "DOD").
 * @return A pointer to a null-terminated string containing the research
 *         connector data, or NULL if the agency is not found or an error occurs.
 */
char* agency_get_research_connector(const char* agency);

/**
 * @brief Get the ASCII art for an agency.
 *
 * Returns the ASCII art for the specified agency.
 * The caller is responsible for freeing the returned string using
 * agency_free_context() when it is no longer needed.
 *
 * @param agency The agency acronym (e.g., "HHS", "DOD").
 * @return A pointer to a null-terminated string containing the ASCII art,
 *         or NULL if the agency is not found or an error occurs.
 */
char* agency_get_ascii_art(const char* agency);

/**
 * @brief Free a context string returned by any of the agency_get_* functions.
 *
 * @param context The context string to free.
 */
void agency_free_context(char* context);

/**
 * @brief Get the list of all available agencies.
 *
 * Returns a JSON array of agency acronyms.
 * The caller is responsible for freeing the returned string using
 * agency_free_context() when it is no longer needed.
 *
 * @return A pointer to a null-terminated string containing the agency list,
 *         or NULL if an error occurs.
 */
char* agency_get_all_agencies();

/**
 * @brief Get the agencies in a specific tier.
 *
 * Returns a JSON array of agency acronyms for the specified tier.
 * The caller is responsible for freeing the returned string using
 * agency_free_context() when it is no longer needed.
 *
 * @param tier The tier number (1-8).
 * @return A pointer to a null-terminated string containing the agency list,
 *         or NULL if an error occurs.
 */
char* agency_get_agencies_by_tier(int tier);

/**
 * @brief Get the agencies for a specific domain.
 *
 * Returns a JSON array of agency acronyms for the specified domain.
 * The caller is responsible for freeing the returned string using
 * agency_free_context() when it is no longer needed.
 *
 * @param domain The domain name (e.g., "healthcare", "defense").
 * @return A pointer to a null-terminated string containing the agency list,
 *         or NULL if an error occurs.
 */
char* agency_get_agencies_by_domain(const char* domain);

/**
 * @brief Verify an issue using the agency theorem prover.
 *
 * Verifies that an issue is valid according to domain theorems.
 *
 * @param agency The agency acronym (e.g., "HHS", "DOD").
 * @param issue_json JSON-formatted issue data.
 * @return 1 if the issue is valid, 0 if it is invalid, -1 if an error occurs.
 */
int agency_verify_issue(const char* agency, const char* issue_json);

#ifdef __cplusplus
}
#endif

#endif /* AGENCY_FFI_H */