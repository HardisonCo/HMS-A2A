package agency

// #cgo LDFLAGS: -L${SRCDIR}/../c -lagency_ffi
// #include <stdlib.h>
// #include "../agency_ffi.h"
import "C"
import (
	"encoding/json"
	"errors"
	"unsafe"
)

// AgencyError represents an error from the agency FFI interface.
type AgencyError struct {
	Message string
}

// Error implements the error interface for AgencyError.
func (e AgencyError) Error() string {
	return e.Message
}

// Agency represents a federal agency.
type Agency struct {
	Acronym     string   `json:"acronym"`
	Name        string   `json:"name"`
	Domain      string   `json:"domain"`
	Description string   `json:"description"`
	Tier        int      `json:"tier"`
	SubAgencies []Agency `json:"sub_agencies,omitempty"`
}

// GetContext returns the context information for an agency.
func GetContext(agency string) (map[string]interface{}, error) {
	cAgency := C.CString(agency)
	defer C.free(unsafe.Pointer(cAgency))

	contextPtr := C.agency_get_context(cAgency)
	if contextPtr == nil {
		return nil, AgencyError{"Failed to get context for agency"}
	}
	defer C.agency_free_context(contextPtr)

	contextStr := C.GoString(contextPtr)
	var context map[string]interface{}
	err := json.Unmarshal([]byte(contextStr), &context)
	if err != nil {
		return nil, errors.New("failed to parse context JSON: " + err.Error())
	}

	return context, nil
}

// GetIssueFinder returns the issue finder data for an agency.
func GetIssueFinder(agency string) (string, error) {
	cAgency := C.CString(agency)
	defer C.free(unsafe.Pointer(cAgency))

	finderPtr := C.agency_get_issue_finder(cAgency)
	if finderPtr == nil {
		return "", AgencyError{"Failed to get issue finder for agency"}
	}
	defer C.agency_free_context(finderPtr)

	return C.GoString(finderPtr), nil
}

// GetResearchConnector returns the research connector data for an agency.
func GetResearchConnector(agency string) (string, error) {
	cAgency := C.CString(agency)
	defer C.free(unsafe.Pointer(cAgency))

	connectorPtr := C.agency_get_research_connector(cAgency)
	if connectorPtr == nil {
		return "", AgencyError{"Failed to get research connector for agency"}
	}
	defer C.agency_free_context(connectorPtr)

	return C.GoString(connectorPtr), nil
}

// GetAsciiArt returns the ASCII art for an agency.
func GetAsciiArt(agency string) (string, error) {
	cAgency := C.CString(agency)
	defer C.free(unsafe.Pointer(cAgency))

	artPtr := C.agency_get_ascii_art(cAgency)
	if artPtr == nil {
		return "", AgencyError{"Failed to get ASCII art for agency"}
	}
	defer C.agency_free_context(artPtr)

	return C.GoString(artPtr), nil
}

// GetAllAgencies returns a list of all available agencies.
func GetAllAgencies() ([]string, error) {
	agenciesPtr := C.agency_get_all_agencies()
	if agenciesPtr == nil {
		return nil, AgencyError{"Failed to get agencies"}
	}
	defer C.agency_free_context(agenciesPtr)

	agenciesStr := C.GoString(agenciesPtr)
	var agencies []string
	err := json.Unmarshal([]byte(agenciesStr), &agencies)
	if err != nil {
		return nil, errors.New("failed to parse agencies JSON: " + err.Error())
	}

	return agencies, nil
}

// GetAgenciesByTier returns a list of agencies in a specific tier.
func GetAgenciesByTier(tier int) ([]string, error) {
	agenciesPtr := C.agency_get_agencies_by_tier(C.int(tier))
	if agenciesPtr == nil {
		return nil, AgencyError{"Failed to get agencies for tier"}
	}
	defer C.agency_free_context(agenciesPtr)

	agenciesStr := C.GoString(agenciesPtr)
	var agencies []string
	err := json.Unmarshal([]byte(agenciesStr), &agencies)
	if err != nil {
		return nil, errors.New("failed to parse agencies JSON: " + err.Error())
	}

	return agencies, nil
}

// GetAgenciesByDomain returns a list of agencies for a specific domain.
func GetAgenciesByDomain(domain string) ([]string, error) {
	cDomain := C.CString(domain)
	defer C.free(unsafe.Pointer(cDomain))

	agenciesPtr := C.agency_get_agencies_by_domain(cDomain)
	if agenciesPtr == nil {
		return nil, AgencyError{"Failed to get agencies for domain"}
	}
	defer C.agency_free_context(agenciesPtr)

	agenciesStr := C.GoString(agenciesPtr)
	var agencies []string
	err := json.Unmarshal([]byte(agenciesStr), &agencies)
	if err != nil {
		return nil, errors.New("failed to parse agencies JSON: " + err.Error())
	}

	return agencies, nil
}

// VerifyIssue verifies an issue using the agency theorem prover.
func VerifyIssue(agency string, issue map[string]interface{}) (bool, error) {
	cAgency := C.CString(agency)
	defer C.free(unsafe.Pointer(cAgency))

	issueJSON, err := json.Marshal(issue)
	if err != nil {
		return false, errors.New("failed to serialize issue: " + err.Error())
	}

	cIssueJSON := C.CString(string(issueJSON))
	defer C.free(unsafe.Pointer(cIssueJSON))

	result := C.agency_verify_issue(cAgency, cIssueJSON)
	switch result {
	case 1:
		return true, nil
	case 0:
		return false, nil
	default:
		return false, AgencyError{"Error verifying issue"}
	}
}

// GetAgencyInfo returns agency information as a struct.
func GetAgencyInfo(agency string) (*Agency, error) {
	context, err := GetContext(agency)
	if err != nil {
		return nil, err
	}

	// Extract agency information
	agencyInfo := &Agency{
		Acronym:     agency,
		Name:        "",
		Domain:      "general",
		Description: "",
		Tier:        0,
	}

	if name, ok := context["name"].(string); ok {
		agencyInfo.Name = name
	}

	if domain, ok := context["domain"].(string); ok {
		agencyInfo.Domain = domain
	}

	if description, ok := context["description"].(string); ok {
		agencyInfo.Description = description
	}

	if tier, ok := context["tier"].(float64); ok {
		agencyInfo.Tier = int(tier)
	}

	// Extract sub-agencies if present
	if subAgencies, ok := context["sub_agencies"].([]interface{}); ok {
		for _, subAgency := range subAgencies {
			if subAgencyMap, ok := subAgency.(map[string]interface{}); ok {
				subAgencyInfo := Agency{}

				if acronym, ok := subAgencyMap["acronym"].(string); ok {
					subAgencyInfo.Acronym = acronym
				}

				if name, ok := subAgencyMap["name"].(string); ok {
					subAgencyInfo.Name = name
				}

				agencyInfo.SubAgencies = append(agencyInfo.SubAgencies, subAgencyInfo)
			}
		}
	}

	return agencyInfo, nil
}