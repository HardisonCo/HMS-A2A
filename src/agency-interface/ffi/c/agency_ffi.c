/**
 * @file agency_ffi.c
 * @brief C implementation of the agency FFI interface.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <json-c/json.h>
#include "../agency_ffi.h"

// Configuration file path
#define CONFIG_FILE "../config/agency_data.json"
#define TEMPLATES_DIR "../templates"
#define ISSUE_FINDER_DIR "../agency_issue_finder/agencies"
#define CONNECTOR_DIR "../agencies"

// Global configuration cache
static json_object* g_config = NULL;

/**
 * @brief Load the configuration file.
 *
 * @return A pointer to the configuration object, or NULL if an error occurs.
 */
static json_object* load_config(void) {
    if (g_config != NULL) {
        return g_config;
    }

    json_object* config = json_object_from_file(CONFIG_FILE);
    if (config == NULL) {
        fprintf(stderr, "Error loading configuration file: %s\n", CONFIG_FILE);
        return NULL;
    }

    g_config = config;
    return config;
}

/**
 * @brief Find an agency in the configuration.
 *
 * @param agency The agency acronym.
 * @return A pointer to the agency object, or NULL if not found.
 */
static json_object* find_agency(const char* agency) {
    json_object* config = load_config();
    if (config == NULL) {
        return NULL;
    }

    json_object* agencies;
    if (!json_object_object_get_ex(config, "agencies", &agencies)) {
        fprintf(stderr, "Error: 'agencies' key not found in configuration\n");
        return NULL;
    }

    int num_agencies = json_object_array_length(agencies);
    for (int i = 0; i < num_agencies; i++) {
        json_object* agency_obj = json_object_array_get_idx(agencies, i);
        json_object* acronym;
        if (json_object_object_get_ex(agency_obj, "acronym", &acronym)) {
            const char* acronym_str = json_object_get_string(acronym);
            if (strcmp(acronym_str, agency) == 0) {
                return agency_obj;
            }
        }
    }

    return NULL;
}

/**
 * @brief Read a file into a string.
 *
 * @param file_path The path to the file.
 * @return A pointer to a null-terminated string containing the file contents,
 *         or NULL if an error occurs. The caller is responsible for freeing
 *         the returned string.
 */
static char* read_file(const char* file_path) {
    FILE* file = fopen(file_path, "r");
    if (file == NULL) {
        fprintf(stderr, "Error opening file: %s\n", file_path);
        return NULL;
    }

    // Get the file size
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    // Allocate memory for the file contents
    char* buffer = (char*)malloc(file_size + 1);
    if (buffer == NULL) {
        fprintf(stderr, "Error allocating memory for file contents\n");
        fclose(file);
        return NULL;
    }

    // Read the file
    size_t bytes_read = fread(buffer, 1, file_size, file);
    if (bytes_read != (size_t)file_size) {
        fprintf(stderr, "Error reading file: %s\n", file_path);
        free(buffer);
        fclose(file);
        return NULL;
    }

    // Null-terminate the string
    buffer[file_size] = '\0';

    fclose(file);
    return buffer;
}

char* agency_get_context(const char* agency) {
    json_object* agency_obj = find_agency(agency);
    if (agency_obj == NULL) {
        return NULL;
    }

    // Create a string from the agency object
    const char* json_str = json_object_to_json_string_ext(agency_obj, JSON_C_TO_STRING_PRETTY);
    if (json_str == NULL) {
        return NULL;
    }

    // Copy the string to a new buffer
    char* context = strdup(json_str);
    return context;
}

char* agency_get_issue_finder(const char* agency) {
    // Convert agency to lowercase
    size_t len = strlen(agency);
    char* agency_lower = (char*)malloc(len + 1);
    if (agency_lower == NULL) {
        return NULL;
    }

    for (size_t i = 0; i < len; i++) {
        agency_lower[i] = tolower(agency[i]);
    }
    agency_lower[len] = '\0';

    // Build the issue finder file path
    char file_path[512];
    snprintf(file_path, sizeof(file_path), "%s/%s_finder.py", ISSUE_FINDER_DIR, agency_lower);

    // Free the lowercase agency string
    free(agency_lower);

    // Read the issue finder file
    return read_file(file_path);
}

char* agency_get_research_connector(const char* agency) {
    // Convert agency to lowercase
    size_t len = strlen(agency);
    char* agency_lower = (char*)malloc(len + 1);
    if (agency_lower == NULL) {
        return NULL;
    }

    for (size_t i = 0; i < len; i++) {
        agency_lower[i] = tolower(agency[i]);
    }
    agency_lower[len] = '\0';

    // Build the research connector file path
    char file_path[512];
    snprintf(file_path, sizeof(file_path), "%s/%s_connector.py", CONNECTOR_DIR, agency_lower);

    // Free the lowercase agency string
    free(agency_lower);

    // Read the research connector file
    return read_file(file_path);
}

char* agency_get_ascii_art(const char* agency) {
    // Convert agency to lowercase
    size_t len = strlen(agency);
    char* agency_lower = (char*)malloc(len + 1);
    if (agency_lower == NULL) {
        return NULL;
    }

    for (size_t i = 0; i < len; i++) {
        agency_lower[i] = tolower(agency[i]);
    }
    agency_lower[len] = '\0';

    // Build the ASCII art file path
    char file_path[512];
    snprintf(file_path, sizeof(file_path), "%s/%s_ascii.txt", TEMPLATES_DIR, agency_lower);

    // Free the lowercase agency string
    free(agency_lower);

    // Read the ASCII art file
    return read_file(file_path);
}

void agency_free_context(char* context) {
    free(context);
}

char* agency_get_all_agencies() {
    json_object* config = load_config();
    if (config == NULL) {
        return NULL;
    }

    json_object* agencies;
    if (!json_object_object_get_ex(config, "agencies", &agencies)) {
        fprintf(stderr, "Error: 'agencies' key not found in configuration\n");
        return NULL;
    }

    // Create a new JSON array for the agency acronyms
    json_object* agency_list = json_object_new_array();
    if (agency_list == NULL) {
        return NULL;
    }

    int num_agencies = json_object_array_length(agencies);
    for (int i = 0; i < num_agencies; i++) {
        json_object* agency_obj = json_object_array_get_idx(agencies, i);
        json_object* acronym;
        if (json_object_object_get_ex(agency_obj, "acronym", &acronym)) {
            // Add the acronym to the list
            json_object_array_add(agency_list, json_object_get(acronym));
        }
    }

    // Create a string from the agency list
    const char* json_str = json_object_to_json_string_ext(agency_list, JSON_C_TO_STRING_PRETTY);
    if (json_str == NULL) {
        json_object_put(agency_list);
        return NULL;
    }

    // Copy the string to a new buffer
    char* result = strdup(json_str);

    // Free the agency list
    json_object_put(agency_list);

    return result;
}

char* agency_get_agencies_by_tier(int tier) {
    json_object* config = load_config();
    if (config == NULL) {
        return NULL;
    }

    json_object* agencies;
    if (!json_object_object_get_ex(config, "agencies", &agencies)) {
        fprintf(stderr, "Error: 'agencies' key not found in configuration\n");
        return NULL;
    }

    // Create a new JSON array for the agency acronyms
    json_object* agency_list = json_object_new_array();
    if (agency_list == NULL) {
        return NULL;
    }

    int num_agencies = json_object_array_length(agencies);
    for (int i = 0; i < num_agencies; i++) {
        json_object* agency_obj = json_object_array_get_idx(agencies, i);
        
        // Check if the agency is in the specified tier
        json_object* agency_tier;
        if (json_object_object_get_ex(agency_obj, "tier", &agency_tier)) {
            int tier_value = json_object_get_int(agency_tier);
            if (tier_value == tier) {
                // Add the agency acronym to the list
                json_object* acronym;
                if (json_object_object_get_ex(agency_obj, "acronym", &acronym)) {
                    json_object_array_add(agency_list, json_object_get(acronym));
                }
            }
        }
    }

    // Create a string from the agency list
    const char* json_str = json_object_to_json_string_ext(agency_list, JSON_C_TO_STRING_PRETTY);
    if (json_str == NULL) {
        json_object_put(agency_list);
        return NULL;
    }

    // Copy the string to a new buffer
    char* result = strdup(json_str);

    // Free the agency list
    json_object_put(agency_list);

    return result;
}

char* agency_get_agencies_by_domain(const char* domain) {
    json_object* config = load_config();
    if (config == NULL) {
        return NULL;
    }

    json_object* agencies;
    if (!json_object_object_get_ex(config, "agencies", &agencies)) {
        fprintf(stderr, "Error: 'agencies' key not found in configuration\n");
        return NULL;
    }

    // Create a new JSON array for the agency acronyms
    json_object* agency_list = json_object_new_array();
    if (agency_list == NULL) {
        return NULL;
    }

    int num_agencies = json_object_array_length(agencies);
    for (int i = 0; i < num_agencies; i++) {
        json_object* agency_obj = json_object_array_get_idx(agencies, i);
        
        // Check if the agency is in the specified domain
        json_object* agency_domain;
        if (json_object_object_get_ex(agency_obj, "domain", &agency_domain)) {
            const char* domain_value = json_object_get_string(agency_domain);
            if (strcmp(domain_value, domain) == 0) {
                // Add the agency acronym to the list
                json_object* acronym;
                if (json_object_object_get_ex(agency_obj, "acronym", &acronym)) {
                    json_object_array_add(agency_list, json_object_get(acronym));
                }
            }
        }
    }

    // Create a string from the agency list
    const char* json_str = json_object_to_json_string_ext(agency_list, JSON_C_TO_STRING_PRETTY);
    if (json_str == NULL) {
        json_object_put(agency_list);
        return NULL;
    }

    // Copy the string to a new buffer
    char* result = strdup(json_str);

    // Free the agency list
    json_object_put(agency_list);

    return result;
}

int agency_verify_issue(const char* agency, const char* issue_json) {
    // This is a simplified implementation that just checks if the issue JSON is valid
    // A real implementation would use the agency prover integration to verify the issue
    
    json_object* issue = json_tokener_parse(issue_json);
    if (issue == NULL) {
        return -1; // Invalid JSON
    }
    
    // Check if the issue has the required fields
    int valid = 1;
    const char* required_fields[] = {"id", "title", "description", "affected_areas"};
    int num_fields = sizeof(required_fields) / sizeof(required_fields[0]);
    
    for (int i = 0; i < num_fields; i++) {
        json_object* field;
        if (!json_object_object_get_ex(issue, required_fields[i], &field)) {
            valid = 0;
            break;
        }
    }
    
    json_object_put(issue);
    return valid;
}