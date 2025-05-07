# HMS-A2A Specialized Agents

This package provides a comprehensive framework for specialized agent collaboration, including MCP (Model Context Protocol) tools, deal-based collaboration, and standards validation.

## Components

### Deal Framework

The Deal Framework enables structured collaboration between specialized agents by organizing tasks into Problems, Solutions, Players, and Transactions.

```python
from src.agents.specialized.collaboration.deals import Deal, Problem, Solution, Player, Transaction

# Create a new deal
deal = Deal(
    name="Healthcare Data Analysis Project",
    description="Collaborative analysis of patient data to improve outcomes",
    domains=["healthcare", "data_analysis"]
)

# Add players to the deal
deal.add_player(Player(name="Data Scientist", role="analyst", capabilities=["data_analysis", "ml_modeling"]))
deal.add_player(Player(name="Healthcare Specialist", role="domain_expert", capabilities=["medical_knowledge"]))

# Add a problem to solve
problem = Problem(
    name="Identify factors affecting readmission rates",
    description="Determine key factors that influence hospital readmission rates",
    constraints=["Must maintain patient privacy", "Must use validated statistical methods"],
    success_criteria=["Identifies at least 3 significant factors", "Provides actionable recommendations"]
)
deal.add_problem(problem)

# Propose a solution
solution = Solution(
    name="Machine Learning Analysis",
    description="Use ML to identify patterns in anonymized patient data",
    approach="Apply gradient boosting to identify key features affecting readmission",
    resources_needed=["Anonymized patient data", "Compute resources for model training"]
)
deal.add_solution(solution, problem.id, "Data Scientist")
```

### Standards Validation

The standards validation framework ensures that collaboration components and content comply with domain-specific standards.

```python
from src.agents.specialized.standards_validation import StandardsRegistry, StandardsValidator

# Get the standards registry
registry = StandardsRegistry.get_instance()

# Get a standard
healthcare_standard = registry.get_standard("STD-HEALTHCARE_DOCUMENTATION")

# Create a validator
validator = StandardsValidator()

# Validate content against a standard
result = validator.validate_content(
    patient_report, 
    standard_id="STD-HEALTHCARE_DOCUMENTATION"
)

if not result.is_valid:
    print("Validation failed with the following issues:")
    for violation in result.violations:
        print(f"- {violation.message} (Severity: {violation.severity})")
```

### MCP Tool Registry

The MCP Tool Registry manages tools that can be used by specialized agents, with permissions and discovery mechanisms.

```python
from src.agents.specialized.tools.mcp_registry import register_tool, get_tools_for_domain

# Register a tool
@register_tool(
    name="analyze_patient_data",
    description="Analyze patient data to identify patterns",
    domains=["healthcare", "data_analysis"],
    standards=["HEALTHCARE_ANALYTICS"],
    tags=["analysis", "healthcare", "patient"]
)
def analyze_patient_data(data, metrics, context=None):
    # Tool implementation
    return {
        "results": compute_metrics(data, metrics),
        "insights": extract_insights(data)
    }

# Get tools for a domain
healthcare_tools = get_tools_for_domain("healthcare")
```

### Collaboration Tools

The collaboration tools enable structured interaction between specialized agents.

```python
from src.agents.specialized.tools.collaboration_tools import (
    create_collaboration_session,
    send_message,
    update_shared_context
)

# Create a session
session = create_collaboration_session(
    name="Healthcare Data Analysis",
    description="Collaborative analysis of patient data",
    participants=["healthcare_agent", "data_science_agent"],
    domains=["healthcare", "data_analysis"]
)

# Send a message
send_message(
    session_id=session["session_id"],
    sender="healthcare_agent",
    content="I've identified key clinical factors we should analyze",
    message_type="text"
)

# Update shared context
update_shared_context(
    session_id=session["session_id"],
    updater="healthcare_agent",
    context_key="clinical_factors",
    context_value=["age", "comorbidities", "medication_adherence"]
)
```

## Deal Visualization

The visualization tools provide different ways to visualize a deal and its relationships.

```python
from src.agents.specialized.tools.visualization_tools import (
    visualize_deal_graph,
    highlight_deal_path,
    calculate_deal_graph_metrics
)

# Visualize a deal
visualization = visualize_deal_graph(
    deal_dict=deal.to_dict(),
    format="dot",
    include_metadata=True
)

# Highlight a path between nodes
path_viz = highlight_deal_path(
    deal_dict=deal.to_dict(),
    start_node=player_id,
    end_node=solution_id,
    format="svg",
    path_color="red"
)

# Calculate graph metrics
metrics = calculate_deal_graph_metrics(
    deal_dict=deal.to_dict(),
    metrics=["centrality", "density", "diameter"]
)
```

## Domain-Specific Tools

HMS-A2A includes specialized tools for various domains:

### Healthcare Tools
- `validate_phi_handling`: Validate Protected Health Information handling against HIPAA requirements
- `check_authorization`: Check if an agent is authorized to access specific healthcare data
- `generate_hipaa_compliant_report`: Generate a HIPAA-compliant healthcare report
- `validate_hipaa_compliance`: Validate a healthcare process or system against HIPAA requirements

### Agriculture Tools
- `validate_organic_certification`: Validate organic certification claims against standards
- `check_contaminant_levels`: Check if contaminant levels in agricultural products meet standards
- `validate_sustainability_practices`: Validate agricultural sustainability practices against standards

### Financial Tools
- `validate_financial_statement`: Validate financial statement structure and calculations against standards
- `analyze_financial_ratios`: Calculate and analyze key financial ratios from financial statements
- `validate_tax_calculation`: Validate tax calculations against tax regulations
- `generate_financial_report`: Generate a standards-compliant financial report

### Legal Tools
- `validate_legal_document`: Validate a legal document against legal standards and formats
- `analyze_legal_risk`: Analyze the legal risks associated with a scenario or decision
- `generate_legal_citation`: Generate properly formatted legal citations for various sources
- `validate_client_confidentiality`: Validate if sharing certain information would violate client confidentiality

## Usage

### Setting Up a Collaboration

1. Create a Deal to structure the collaboration
2. Add Players representing different specialized agents
3. Define Problems that need to be solved
4. Propose Solutions to address the Problems
5. Create Transactions to exchange resources and approvals
6. Validate all components against relevant standards
7. Visualize the Deal to understand relationships

### MCP Tool Usage

1. Find tools relevant to your domain:
   ```python
   tools = get_tools_for_domain("healthcare")
   ```

2. Execute tools with proper permissions:
   ```python
   result = execute_tool(
       "analyze_patient_data",
       {"data": patient_data, "metrics": ["readmission_risk", "los_prediction"]},
       "healthcare_agent"
   )
   ```

3. Use collaboration tools to coordinate with other agents:
   ```python
   session_id = create_collaboration_session(...)["session_id"]
   send_message(session_id, "healthcare_agent", "Let's analyze this patient cohort...")
   ```

## Documentation

For complete documentation, see:
- [Migration Guide](/migration.md): Information about migrating from HMS-SME
- [Migration Completion](/migration_completion.md): Current migration status
- [Examples](/specialized_agents/collaboration/examples): Example implementations
- [Standards Reference](/data/standards/standards.json): Supported standards definitions

## Contributing

When adding new tools or components:

1. Follow the standard interfaces in `specialized_agents.tools.tool_interface`
2. Register tools with the MCP Registry using the `@register_tool` decorator
3. Add appropriate validation against relevant standards
4. Implement comprehensive docstrings and type hints
5. Add tests in the `tests` directory

## Professional Specialties
The following professional specialties are available:
| Specialty | Specialty | Specialty |
|-----------|-----------|----------|
| [Accountant](./accountant) | [Florist](./florist) | [Political Consultant](./political_consultant) |
| [Accounting](./accounting) | [Food Photographer](./food_photographer) | [Pool Maintenance Specialist](./pool_maintenance_specialist) |
| [Acupuncturist](./acupuncturist) | [Freight Manager](./freight_manager) | [Portrait Photographer](./portrait_photographer) |
| [Ad Designer](./ad_designer) | [Ghostwriter](./ghostwriter) | [Pr Specialist](./pr_specialist) |
| [Agriculture](./agriculture) | [Government](./government) | [Presentation Designer](./presentation_designer) |
| [Android Developer](./android_developer) | [Grant Writer](./grant_writer) | [Pricing Strategist](./pricing_strategist) |
| [Animator](./animator) | [Graphic Designer](./graphic_designer) | [Print Designer](./print_designer) |
| [Architect](./architect) | [Green Cleaning Specialist](./green_cleaning_specialist) | [Professional Organizer](./professional_organizer) |
| [Attorney](./attorney) | [Headshot Photographer](./headshot_photographer) | [Project Coordinator](./project_coordinator) |
| [Audio Engineer](./audio_engineer) | [Health Coach](./health_coach) | [Property Manager](./property_manager) |
| [Bartender](./bartender) | [Healthcare](./healthcare) | [Psychiatrist](./psychiatrist) |
| [Behavioral Therapist](./behavioral_therapist) | [Healthcare Consultant](./healthcare_consultant) | [Psychologist](./psychologist) |
| [Blogger](./blogger) | [Holistic Medicine Practitioner](./holistic_medicine_practitioner) | [Psychotherapist](./psychotherapist) |
| [Bookkeeper](./bookkeeper) | [House Sitter](./house_sitter) | [Public Speaking Coach](./public_speaking_coach) |
| [Brand Consultant](./brand_consultant) | [Hr Consultant](./hr_consultant) | [Qa Engineer](./qa_engineer) |
| [Brand Designer](./brand_designer) | [Hr Manager](./hr_manager) | [Real Estate Agent](./real_estate_agent) |
| [Business Analyst](./business_analyst) | [Illustrator](./illustrator) | [Real Estate Appraiser](./real_estate_appraiser) |
| [Business Consultant](./business_consultant) | [Industrial Designer](./industrial_designer) | [Real Estate Marketer](./real_estate_marketer) |
| [Career Coach](./career_coach) | [Information Security Specialist](./information_security_specialist) | [Real Estate Photographer](./real_estate_photographer) |
| [Carpet Cleaner](./carpet_cleaner) | [Insurance Agent](./insurance_agent) | [Research Specialist](./research_specialist) |
| [Caterer](./caterer) | [Insurance Consultant](./insurance_consultant) | [Resume Writer](./resume_writer) |
| [Change Management Consultant](./change_management_consultant) | [Insurance Underwriter](./insurance_underwriter) | [Retirement Planner](./retirement_planner) |
| [Childcare Provider](./childcare_provider) | [Interior Designer](./interior_designer) | [Ride Service Provider](./ride_service_provider) |
| [Chiropractor](./chiropractor) | [Ios Developer](./ios_developer) | [Saas Developer](./saas_developer) |
| [Cloud Application Developer](./cloud_application_developer) | [It Consultant](./it_consultant) | [Seo Specialist](./seo_specialist) |
| [Cloud Engineer](./cloud_engineer) | [Journalist](./journalist) | [Small Business Tax Advisor](./small_business_tax_advisor) |
| [Commercial Cleaner](./commercial_cleaner) | [Landscape Architect](./landscape_architect) | [Social Media Manager](./social_media_manager) |
| [Commercial Photographer](./commercial_photographer) | [Last Mile Delivery Specialist](./last_mile_delivery_specialist) | [Socialwork](./socialwork) |
| [Content Marketer](./content_marketer) | [Laundry Specialist](./laundry_specialist) | [Software Engineer](./software_engineer) |
| [Content Writer](./content_writer) | [Legal](./legal) | [Sound Designer](./sound_designer) |
| [Copywriter](./copywriter) | [Legal Consultant](./legal_consultant) | [Specialist](./specialist) |
| [Corporate Event Planner](./corporate_event_planner) | [Life Coach](./life_coach) | [Speech Therapist](./speech_therapist) |
| [Corporate Photographer](./corporate_photographer) | [Limousine Service Provider](./limousine_service_provider) | [Sports Photographer](./sports_photographer) |
| [Corporate Trainer](./corporate_trainer) | [Local Mover](./local_mover) | [Stock Photographer](./stock_photographer) |
| [Counselor](./counselor) | [Logistics Consultant](./logistics_consultant) | [Stress Management Coach](./stress_management_coach) |
| [Courier Service Provider](./courier_service_provider) | [Logo Designer](./logo_designer) | [Substance Abuse Counselor](./substance_abuse_counselor) |
| [Cybersecurity Specialist](./cybersecurity_specialist) | [Long Distance Mover](./long_distance_mover) | [Supply Chain Manager](./supply_chain_manager) |
| [Data Entry Specialist](./data_entry_specialist) | [Management Consultant](./management_consultant) | [Tax Preparer](./tax_preparer) |
| [Data Recovery Specialist](./data_recovery_specialist) | [Market Research Analyst](./market_research_analyst) | [Technical Writer](./technical_writer) |
| [Data Scientist](./data_scientist) | [Marketing Consultant](./marketing_consultant) | [Telecommunications Engineer](./telecommunications_engineer) |
| [Database Developer](./database_developer) | [Marriage Family Therapist](./marriage_family_therapist) | [Telehealth Provider](./telehealth_provider) |
| [Dei Specialist](./dei_specialist) | [Meal Planning Specialist](./meal_planning_specialist) | [Telemedicine](./telemedicine) |
| [Dentist](./dentist) | [Mental Health Counselor](./mental_health_counselor) | [Three D Artist](./three_d_artist) |
| [Dietitian](./dietitian) | [Mindfulness Instructor](./mindfulness_instructor) | [Trade Show Coordinator](./trade_show_coordinator) |
| [Digital Marketing Consultant](./digital_marketing_consultant) | [Mobile App Developer](./mobile_app_developer) | [Transcription Specialist](./transcription_specialist) |
| [Dj](./dj) | [Mortgage Broker](./mortgage_broker) | [Translation Specialist](./translation_specialist) |
| [Editor](./editor) | [Move In Out Cleaner](./move_in_out_cleaner) | [Translator](./translator) |
| [Education](./education) | [Nature Photographer](./nature_photographer) | [Transportation Planner](./transportation_planner) |
| [Elder Care Provider](./elder_care_provider) | [Network Engineer](./network_engineer) | [Trucking Service Provider](./trucking_service_provider) |
| [Email Marketing Specialist](./email_marketing_specialist) | [Non Profit Consultant](./non_profit_consultant) | [Ui Ux Designer](./ui_ux_designer) |
| [Engineering Designer](./engineering_designer) | [Notary](./notary) | [Ux Researcher](./ux_researcher) |
| [Enterprise Content Manager](./enterprise_content_manager) | [Nutrition](./nutrition) | [Ux Writer](./ux_writer) |
| [Environmental Consultant](./environmental_consultant) | [Nutrition Consultant](./nutrition_consultant) | [Vehicle Transport Specialist](./vehicle_transport_specialist) |
| [Event Photographer](./event_photographer) | [Occupational Therapist](./occupational_therapist) | [Veterinarian](./veterinarian) |
| [Event Planner](./event_planner) | [Operations Manager](./operations_manager) | [Video Editor](./video_editor) |
| [Event Producer](./event_producer) | [Packaging Designer](./packaging_designer) | [Videographer](./videographer) |
| [Executive Administrator](./executive_administrator) | [Packaging Specialist](./packaging_specialist) | [Virtual Assistant](./virtual_assistant) |
| [Executive Coach](./executive_coach) | [Paralegal](./paralegal) | [Warehouse Manager](./warehouse_manager) |
| [Exercise Physiologist](./exercise_physiologist) | [Payroll Specialist](./payroll_specialist) | [Web Designer](./web_designer) |
| [Financial](./financial) | [Personal Assistant](./personal_assistant) | [Web Developer](./web_developer) |
| [Financial Advisor](./financial_advisor) | [Personal Chef](./personal_chef) | [Wedding Officiant](./wedding_officiant) |
| [Financial Analyst](./financial_analyst) | [Pet Care Provider](./pet_care_provider) | [Wedding Planner](./wedding_planner) |
| [Financial Planner](./financial_planner) | [Pet Groomer](./pet_groomer) | [Wellness Coach](./wellness_coach) |
| [Financial Reporter](./financial_reporter) | [Pet Photographer](./pet_photographer) | [Window Cleaner](./window_cleaner) |
| [Fitness Trainer](./fitness_trainer) | [Pharmacy Consultant](./pharmacy_consultant) | [Wordpress Designer](./wordpress_designer) |
| [Fleet Manager](./fleet_manager) | [Physical Therapist](./physical_therapist) | [Yoga Instructor](./yoga_instructor) |
