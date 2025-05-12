# agency-interface – Data Model Mapping

## 1. Title & Purpose
Data model for the Agency Interface system that manages agency metadata, contextual information, issue tracking, and Codex CLI integration settings. It provides a structured representation of federal agencies, their domains, and implementation status across tiers.

## 2. Entity Definitions

**Entity: agency**
- Fields:
  - `id` (string) - Agency identifier (e.g., "HHS", "USDA")
  - `name` (string) - Full agency name
  - `short_name` (string) - Abbreviated name
  - `tier` (integer) - Agency tier (1-8)
  - `domain` (string) - Primary domain (e.g., "healthcare", "agriculture")
  - `parent_id` (string, nullable) - Parent agency ID if applicable
  - `website` (string) - Official website URL
  - `description` (string) - Detailed description
  - `implemented` (boolean) - Whether implementation is complete
  - `implementation_status` (float) - Implementation completion percentage
  - `created_at` (timestamp) - Record creation date
  - `updated_at` (timestamp) - Last update date

**Entity: agency_topic**
- Fields:
  - `id` (string) - Topic identifier
  - `agency_id` (string) - Reference to agency.id
  - `name` (string) - Topic name
  - `description` (string) - Topic description
  - `is_active` (boolean) - Whether topic is active
  - `priority` (integer) - Priority level (1-5)
  - `created_at` (timestamp) - Record creation date
  - `updated_at` (timestamp) - Last update date

**Entity: agency_ascii_art**
- Fields:
  - `agency_id` (string) - Reference to agency.id
  - `content` (text) - ASCII art content
  - `width` (integer) - Width in characters
  - `height` (integer) - Height in lines
  - `created_at` (timestamp) - Record creation date
  - `updated_at` (timestamp) - Last update date

**Entity: agency_issue**
- Fields:
  - `id` (string) - Issue identifier
  - `agency_id` (string) - Reference to agency.id
  - `topic_id` (string) - Reference to agency_topic.id
  - `title` (string) - Issue title
  - `description` (text) - Issue description
  - `severity` (integer) - Severity level (1-5)
  - `status` (enum) - Status (open, in_progress, resolved)
  - `created_at` (timestamp) - Record creation date
  - `updated_at` (timestamp) - Last update date
  - `resolved_at` (timestamp, nullable) - Resolution date

**Entity: agency_research**
- Fields:
  - `id` (string) - Research document identifier
  - `agency_id` (string) - Reference to agency.id
  - `topic_id` (string, nullable) - Reference to agency_topic.id
  - `title` (string) - Document title
  - `content` (text) - Document content
  - `file_path` (string, nullable) - Path to external file
  - `metadata` (json) - Additional metadata
  - `created_at` (timestamp) - Record creation date
  - `updated_at` (timestamp) - Last update date

**Entity: agency_context**
- Fields:
  - `agency_id` (string) - Reference to agency.id
  - `topic_id` (string, nullable) - Reference to agency_topic.id
  - `context_type` (enum) - Type (default, issue, research)
  - `context_data` (json) - Context data for Codex CLI
  - `codex_args` (string) - Command line arguments for Codex
  - `created_at` (timestamp) - Record creation date
  - `updated_at` (timestamp) - Last update date

**Entity: agency_implementation_status**
- Fields:
  - `agency_id` (string) - Reference to agency.id
  - `issue_finder` (boolean) - Whether issue finder is implemented
  - `ascii_art` (boolean) - Whether ASCII art is implemented
  - `research_connector` (boolean) - Whether research connector is implemented
  - `codex_integration` (boolean) - Whether Codex integration is implemented
  - `ffi_integration` (boolean) - Whether FFI integration is implemented
  - `implementation_notes` (text) - Implementation notes
  - `created_at` (timestamp) - Record creation date
  - `updated_at` (timestamp) - Last update date

**Entity: agency_launch_history**
- Fields:
  - `id` (string) - Launch record identifier
  - `agency_id` (string) - Reference to agency.id
  - `topic_id` (string, nullable) - Reference to agency_topic.id
  - `user_id` (string) - User who launched
  - `prompt` (text, nullable) - Initial prompt
  - `launch_time` (timestamp) - When launched
  - `duration` (integer, nullable) - Session duration in seconds
  - `metadata` (json) - Additional session data

## 3. Legacy vs. Target Data Model

**Legacy Model (Current Implementation)**
- Simple directory structure with text files
- Agency data stored in JSON and shell scripts
- ASCII art in static text files
- No structured database for issues or research
- Context data hard-coded in shell scripts

**Target Model (In Development)**
- Fully relational database for all entity types
- JSON API interface for programmatic access
- Rich metadata for agencies, topics, and issues
- Cross-referenced resources with proper constraints
- Event-based synchronization for real-time updates
- Support for all agency tiers (1-8)

**Migration Strategy**
- Phase 1: JSON extraction from existing scripts (completed)
- Phase 2: Database schema implementation (in progress)
- Phase 3: Data migration from files to database
- Phase 4: API layer implementation
- Phase 5: Legacy script compatibility layer

## 4. Validation & Constraints

- Agency IDs must be unique and match official abbreviations
- Topic IDs must be unique per agency
- Agency topics must reference valid agencies
- Issues must reference valid agencies and topics
- Research documents must reference valid agencies
- Context data must be valid JSON
- Agency tiers must be between 1 and 8
- Implementation status must be between 0 and 100
- Severity levels must be between 1 and 5
- Status enums must be one of: open, in_progress, resolved
- Context types must be one of: default, issue, research

## 5. Migration Strategy

- Extract data from existing bash scripts using Python parser
- Migrate static ASCII art to database records
- Transform issue finder logic into structured issue records
- Convert hard-coded context settings to dynamic context records
- Implement database migrations using a migration framework
- Provide backward compatibility layer for existing scripts
- Gradual transition of implementation scripts to use the new API
- Parallel operation during transition with feature flags

## 6. Observability & Auditing

- All agency data modifications are logged with timestamps and user IDs
- Agency launch history tracked for usage analytics
- Implementation progress tracked with detailed metrics
- Automated health checks for all agency components
- Performance monitoring for API endpoints
- Usage statistics by agency and topic
- Error tracking for failed launches or context switches
- Integration with centralized logging system
- Regular database integrity validation
- Real-time implementation status dashboard