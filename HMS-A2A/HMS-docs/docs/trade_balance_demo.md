# Trade Balance System Demo

This document demonstrates the capabilities of the USTDA/USITC Agency Trade Balance System integrated with the Market Network architecture. This demo shows how to implement Warren Buffett's Import Certificate approach within the Moneyball economic framework for balanced trade.

## 1. Overview of the Demo

This demonstration showcases:

1. Registration of USTDA and USITC agency agents 
2. Creation and application of import certificate policies
3. Certificate issuance and validation
4. Creation of policy-based trade deals
5. Economic impact assessment
6. Win-win status calculation
7. Policy optimization based on WAR score

## 2. Setup and Configuration

### 2.1 Prerequisites

Before running the demo, ensure you have:

- Python 3.10 or higher
- Required packages: numpy, pandas, asyncio
- HMS-A2A repository cloned
- Environment configured

### 2.2 Installation

```bash
# Clone the repository if you haven't already
git clone https://github.com/example/hms-a2a.git
cd hms-a2a

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config.example.yaml config.yaml
```

Edit `config.yaml` to configure the system:

```yaml
system:
  log_level: INFO
  demo_mode: true

agencies:
  ustda:
    enabled: true
  usitc:
    enabled: true

network:
  certificate_required: true
  market_mechanism: continuous_double_auction
```

## 3. Running the Demo

### 3.1 Starting the System

```bash
# Start the system in demo mode
python -m hms_a2a.start --demo
```

This will:
1. Initialize the MAC architecture
2. Register agency agents
3. Set up the market network
4. Prepare the demo environment

### 3.2 Agency Registration

The demo automatically registers the USTDA and USITC agents with the market network:

```python
# The demo runs this code automatically
async def register_agencies():
    # Create economist agent
    economist = create_economist(config_path=None)
    
    # Create market network integrator
    integrator = await integrate_economic_components(economist)
    
    # Create agency extension
    extension = await setup_agency_integration(integrator)
    
    # USTDA agent is registered with these capabilities and value dimensions
    ustda_registration = await extension.register_agency(
        agency_id="USTDA-001",
        agency_type="trade_development",
        capabilities=["policy_development", "trade_facilitation", "project_financing"],
        value_dimensions={
            "economic": 0.4,
            "diplomatic": 0.3,
            "technological": 0.2,
            "environmental": 0.1
        }
    )
    
    # USITC agent is registered with these capabilities and value dimensions
    usitc_registration = await extension.register_agency(
        agency_id="USITC-001",
        agency_type="trade_commission",
        capabilities=["economic_analysis", "trade_impact_assessment", "regulatory_compliance"],
        value_dimensions={
            "economic": 0.5,
            "legal": 0.3,
            "competitive": 0.1,
            "social": 0.1
        }
    )
    
    return extension
```

### 3.3 Policy Creation

The demo creates an import certificate policy:

```python
# The demo runs this code automatically
async def create_policies(extension):
    # Create an import certificate policy
    policy = extension.ustda_agent.policies[next(iter(extension.ustda_agent.policies.keys()))]
    
    # Update policy parameters
    policy.add_parameter("certificate_duration", 180)  # 6 months validity
    policy.add_parameter("initial_allocation", 100.0)  # Initial certificate amount
    policy.add_parameter("transfer_fee", 0.005)  # 0.5% transfer fee
    
    # Activate the policy
    policy.update_status("active", "Activated for demo")
    
    return policy
```

## 4. Demo Scenarios

The demo includes several scenarios to demonstrate different aspects of the system.

### 4.1 Basic Trade Deal

This scenario demonstrates creating a basic trade deal with import certificates:

```python
async def demo_basic_trade_deal(extension, policy):
    # Step 1: Create a basic trade deal
    deal_result = await extension.create_policy_based_deal(
        agency_id="USTDA-001",
        problem_statement="Establish electronics manufacturing trade partnership between US and Vietnam",
        stakeholder_ids=["us_manufacturer", "vietnam_supplier", "shipping_company"],
        policy_id=policy.policy_id
    )
    
    # Step 2: Issue certificates to stakeholders
    certificate_us = extension.ustda_agent.issue_import_certificate(
        owner="us_manufacturer",
        value=500000.0
    )
    
    # Step 3: Evaluate economic impact
    model_id = next(iter(extension.usitc_agent.models.keys()))
    impact = await extension.evaluate_deal_economic_impact(
        deal_id=deal_result["deal_id"],
        model_id=model_id
    )
    
    # Step 4: Calculate win-win status
    win_win = await extension.calculate_win_win_status(
        deal_id=deal_result["deal_id"],
        apply_adjustments=True
    )
    
    return {
        "deal": deal_result,
        "certificate": certificate_us,
        "impact": impact,
        "win_win": win_win
    }
```

### 4.2 Trade Balance Optimization

This scenario demonstrates optimizing trade balance using the Import Certificate system:

```python
async def demo_trade_balance_optimization(extension, countries_data):
    # Step 1: Create policy with optimization goal
    policy_id = "POL-" + uuid.uuid4().hex[:8]
    balance_policy = GovernancePolicy(
        policy_id=policy_id,
        title="Trade Balance Optimization Policy",
        description="Policy for optimizing trade balance using import certificates",
        policy_type="import_certificate",
        status="active"
    )
    
    # Add to extension
    extension.policies[policy_id] = balance_policy
    
    # Step 2: Calculate initial balance for each country pair
    balances = {}
    for pair in countries_data["country_pairs"]:
        country_a = pair["country_a"]
        country_b = pair["country_b"]
        
        imports_ab = pair["imports_ab"]
        exports_ab = pair["exports_ab"]
        
        balance = exports_ab - imports_ab
        balance_pct = balance / (imports_ab + exports_ab)
        
        balances[(country_a, country_b)] = {
            "balance": balance,
            "balance_pct": balance_pct,
            "trade_volume": imports_ab + exports_ab
        }
    
    # Step 3: Simulate certificate allocation for balanced trade
    certificate_allocations = {}
    for pair, data in balances.items():
        country_a, country_b = pair
        
        if data["balance"] < 0:
            # Country A has deficit with Country B
            # Allocate certificates equal to exports
            certificate_allocations[country_a] = {
                "amount": data["trade_volume"] / 2,
                "deficit_reduction": abs(data["balance"]),
                "certificate_cost": abs(data["balance"]) * 0.03  # 3% cost
            }
    
    # Step 4: Calculate new trade balance after certificate implementation
    new_balances = {}
    for pair, data in balances.items():
        country_a, country_b = pair
        
        # With certificates, imports cannot exceed exports
        new_balance = 0  # Balanced trade
        new_balance_pct = 0
        
        new_balances[pair] = {
            "balance": new_balance,
            "balance_pct": new_balance_pct,
            "trade_volume": data["trade_volume"] * 0.97  # Slight reduction due to friction
        }
    
    # Step 5: Calculate WAR score improvement
    war_scores = {}
    for pair, data in balances.items():
        country_a, country_b = pair
        
        # Original WAR score - lower due to imbalance
        original_war = 2.5 + (1 - abs(data["balance_pct"])) * 2.5
        
        # New WAR score - higher due to balance
        new_war = 2.5 + (1 - abs(new_balances[pair]["balance_pct"])) * 2.5
        
        war_scores[pair] = {
            "original": original_war,
            "new": new_war,
            "improvement": new_war - original_war
        }
    
    return {
        "original_balances": balances,
        "certificate_allocations": certificate_allocations,
        "new_balances": new_balances,
        "war_scores": war_scores
    }
```

### 4.3 Moneyball Opportunity Identification

This scenario demonstrates using Moneyball principles to identify undervalued trade opportunities:

```python
async def demo_moneyball_opportunities(extension):
    # Step 1: Get Moneyball opportunities from USTDA agent
    opportunities = extension.ustda_agent.get_moneyball_opportunities()
    
    # Step 2: Apply Buffett Margin of Safety
    margin_of_safety = 0.25  # 25% safety margin
    
    safe_opportunities = []
    for opp in opportunities:
        # Calculate conservative score with margin of safety
        conservative_score = opp["opportunity_score"] * (1 - margin_of_safety)
        conservative_growth = opp["growth_potential"] * (1 - margin_of_safety)
        
        # Only include opportunities that remain positive after MoS
        if conservative_score > 1.0 and conservative_growth > 1.0:
            opp["conservative_score"] = conservative_score
            opp["conservative_growth"] = conservative_growth
            safe_opportunities.append(opp)
    
    # Step 3: Calculate WAR scores for each opportunity
    war_scores = []
    for opp in safe_opportunities:
        # WAR components:
        # 1. Value vs. Current Market (40%)
        # 2. Growth Potential (30%)
        # 3. Development Impact (20%)
        # 4. Strategic Alignment (10%)
        
        value_component = (opp["conservative_score"] - 1.0) / 1.5  # Normalized to 0-1
        growth_component = (opp["conservative_growth"] - 1.0) / 1.5  # Normalized to 0-1
        development_component = opp["development_potential"] / 2.0  # Normalized to 0-1
        strategic_component = 0.5  # Default midpoint
        
        war_score = (
            0.4 * value_component +
            0.3 * growth_component +
            0.2 * development_component +
            0.1 * strategic_component
        ) * 5.0  # Scale to 0-5
        
        war_scores.append({
            "sector": opp["sector"],
            "war_score": war_score,
            "components": {
                "value": value_component * 5.0,
                "growth": growth_component * 5.0,
                "development": development_component * 5.0,
                "strategic": strategic_component * 5.0
            }
        })
    
    # Sort by WAR score
    war_scores.sort(key=lambda x: x["war_score"], reverse=True)
    
    return {
        "all_opportunities": opportunities,
        "safe_opportunities": safe_opportunities,
        "war_scores": war_scores
    }
```

### 4.4 Win-Win Deal Optimization

This scenario demonstrates calculating and optimizing a deal to ensure all stakeholders win:

```python
async def demo_win_win_optimization(extension):
    # Step 1: Create entity profiles
    from win_win_calculation_framework import create_entity_profile, create_value_component
    
    entity_profiles = {
        'ustda': create_entity_profile(
            entity_id='ustda',
            entity_name='US Trade & Development Agency',
            entity_type='government',
            time_preference=0.05,
            risk_preference=0.3
        ),
        'usitc': create_entity_profile(
            entity_id='usitc',
            entity_name='US International Trade Commission',
            entity_type='government',
            time_preference=0.05,
            risk_preference=0.3
        ),
        'us_company': create_entity_profile(
            entity_id='us_company',
            entity_name='US Manufacturing Corp',
            entity_type='corporate',
            time_preference=0.1,
            risk_preference=0.4
        ),
        'foreign_supplier': create_entity_profile(
            entity_id='foreign_supplier',
            entity_name='Foreign Supplier Ltd',
            entity_type='corporate',
            time_preference=0.12,
            risk_preference=0.5
        )
    }
    
    # Step 2: Initial value distribution - not win-win
    initial_value_components = {
        'ustda': {
            'comp_1': create_value_component(
                dimension='economic',
                amount=80.0,
                timeline=[(0, 20.0), (1, 30.0), (2, 30.0)],
                probability=0.9
            ),
            'comp_2': create_value_component(
                dimension='diplomatic',
                amount=40.0,
                timeline=[(1, 20.0), (2, 20.0)],
                probability=0.8
            )
        },
        'usitc': {
            'comp_3': create_value_component(
                dimension='economic',
                amount=60.0,
                timeline=[(0, 20.0), (1, 40.0)],
                probability=0.85
            )
        },
        'us_company': {
            'comp_4': create_value_component(
                dimension='economic',
                amount=120.0,
                timeline=[(0, 40.0), (1, 40.0), (2, 40.0)],
                probability=0.8
            ),
            'comp_5': create_value_component(
                dimension='technological',
                amount=-30.0,  # Negative component - technology transfer cost
                timeline=[(0, -10.0), (1, -10.0), (2, -10.0)],
                probability=0.9
            )
        },
        'foreign_supplier': {
            'comp_6': create_value_component(
                dimension='economic',
                amount=50.0,
                timeline=[(0, 10.0), (1, 20.0), (2, 20.0)],
                probability=0.7
            ),
            'comp_7': create_value_component(
                dimension='technological',
                amount=20.0,
                timeline=[(1, 10.0), (2, 10.0)],
                probability=0.8
            )
        }
    }
    
    # Step 3: Analyze initial distribution
    from win_win_calculation_framework import analyze_win_win_deal
    
    initial_analysis = analyze_win_win_deal(entity_profiles, initial_value_components)
    
    # Step 4: Optimize for win-win
    from win_win_calculation_framework import optimize_value_distribution
    
    optimization_constraints = {
        'min_positive_value': 10.0,
        'min_positive_margin': 2.0
    }
    
    optimized_components = optimize_value_distribution(
        entity_profiles, 
        initial_value_components,
        optimization_constraints
    )
    
    # Step 5: Analyze optimized distribution
    optimized_analysis = analyze_win_win_deal(entity_profiles, optimized_components)
    
    return {
        "initial_analysis": initial_analysis,
        "optimized_components": optimized_components,
        "optimized_analysis": optimized_analysis
    }
```

## 5. Demo Output

### 5.1 Basic Trade Deal Results

When running the basic trade deal scenario, you should see output similar to:

```json
{
  "deal": {
    "success": true,
    "deal_id": "DEAL-78f21bca",
    "deal_details": {
      "problem_statement": "Establish electronics manufacturing trade partnership between US and Vietnam",
      "stakeholders": ["USTDA-001", "us_manufacturer", "vietnam_supplier", "shipping_company"],
      "value_dimensions": ["economic", "social", "technological", "environmental"]
    },
    "policy_effects": {
      "type": "import_certificate_requirements",
      "certificate_penalty": 0.2
    },
    "is_win_win": true
  },
  "certificate": {
    "id": "IC-7b93e2a5-us_m-00500000",
    "owner": "us_manufacturer",
    "value": 500000.0,
    "issued_date": "2025-05-04T15:42:37.123456",
    "expiry_date": "2025-11-04T15:42:37.123456",
    "issuing_authority": "USTDA",
    "status": "active"
  },
  "impact": {
    "success": true,
    "deal_id": "DEAL-78f21bca",
    "model_id": "MOD-5a7dc43e",
    "economic_impact": {
      "gdp_impact": 28.35,
      "job_creation": 1342,
      "trade_balance_effect": 15.87,
      "multiplier_effect": 1.85
    }
  },
  "win_win": {
    "success": true,
    "is_win_win": true,
    "entity_values": {
      "USTDA-001": {
        "is_win": true,
        "total_value": 72.58,
        "risk_adjusted_value": 65.32,
        "net_value": 55.32
      },
      "us_manufacturer": {
        "is_win": true,
        "total_value": 120.45,
        "risk_adjusted_value": 102.38,
        "net_value": 32.38
      },
      "vietnam_supplier": {
        "is_win": true,
        "total_value": 85.72,
        "risk_adjusted_value": 72.86,
        "net_value": 42.86
      },
      "shipping_company": {
        "is_win": true,
        "total_value": 28.39,
        "risk_adjusted_value": 24.13,
        "net_value": 14.13
      }
    }
  }
}
```

### 5.2 Trade Balance Optimization Results

The trade balance optimization scenario produces results like:

```json
{
  "original_balances": {
    "US-China": {
      "balance": -279100000000,
      "balance_pct": -0.486,
      "trade_volume": 574500000000
    },
    "US-Germany": {
      "balance": -73500000000,
      "balance_pct": -0.312,
      "trade_volume": 235600000000
    }
  },
  "certificate_allocations": {
    "US": {
      "amount": 287250000000,
      "deficit_reduction": 279100000000,
      "certificate_cost": 8373000000
    }
  },
  "new_balances": {
    "US-China": {
      "balance": 0,
      "balance_pct": 0,
      "trade_volume": 557265000000
    },
    "US-Germany": {
      "balance": 0,
      "balance_pct": 0,
      "trade_volume": 228532000000
    }
  },
  "war_scores": {
    "US-China": {
      "original": 2.685,
      "new": 5.0,
      "improvement": 2.315
    },
    "US-Germany": {
      "original": 3.22,
      "new": 5.0,
      "improvement": 1.78
    }
  }
}
```

### 5.3 Moneyball Opportunities Results

The Moneyball opportunity identification scenario produces:

```json
{
  "war_scores": [
    {
      "sector": "renewable_energy",
      "war_score": 3.85,
      "components": {
        "value": 3.95,
        "growth": 4.23,
        "development": 3.62,
        "strategic": 2.5
      }
    },
    {
      "sector": "technology",
      "war_score": 3.52,
      "components": {
        "value": 3.72,
        "growth": 3.85,
        "development": 2.85,
        "strategic": 2.5
      }
    },
    {
      "sector": "infrastructure",
      "war_score": 3.21,
      "components": {
        "value": 2.83,
        "growth": 3.24,
        "development": 4.15,
        "strategic": 2.5
      }
    },
    {
      "sector": "manufacturing",
      "war_score": 2.95,
      "components": {
        "value": 2.64,
        "growth": 2.92,
        "development": 3.75,
        "strategic": 2.5
      }
    }
  ]
}
```

### 5.4 Win-Win Optimization Results

The Win-Win optimization scenario shows:

```json
{
  "initial_analysis": {
    "is_win_win": false,
    "entity_values": {
      "ustda": {
        "total_value": 114.8,
        "time_adjusted_value": 109.2,
        "risk_adjusted_value": 103.5,
        "is_win": true
      },
      "usitc": {
        "total_value": 56.2,
        "time_adjusted_value": 53.6,
        "risk_adjusted_value": 50.8,
        "is_win": true
      },
      "us_company": {
        "total_value": 83.6,
        "time_adjusted_value": 79.4,
        "risk_adjusted_value": 75.5,
        "is_win": true
      },
      "foreign_supplier": {
        "total_value": -5.8,
        "time_adjusted_value": -5.2,
        "risk_adjusted_value": -4.9,
        "is_win": false
      }
    },
    "negative_entities": ["foreign_supplier"],
    "improvement_opportunities": [
      {
        "entity_id": "foreign_supplier",
        "entity_type": "corporate",
        "negative_value": -5.8,
        "focus_dimension": "economic",
        "required_improvement": 6.8
      }
    ]
  },
  "optimized_analysis": {
    "is_win_win": true,
    "entity_values": {
      "ustda": {
        "total_value": 103.3,
        "time_adjusted_value": 98.3,
        "risk_adjusted_value": 93.2,
        "is_win": true
      },
      "usitc": {
        "total_value": 56.2,
        "time_adjusted_value": 53.6,
        "risk_adjusted_value": 50.8,
        "is_win": true
      },
      "us_company": {
        "total_value": 75.2,
        "time_adjusted_value": 71.5,
        "risk_adjusted_value": 67.9,
        "is_win": true
      },
      "foreign_supplier": {
        "total_value": 10.9,
        "time_adjusted_value": 9.8,
        "risk_adjusted_value": 9.3,
        "is_win": true
      }
    },
    "value_distribution": {
      "ustda": 0.42,
      "usitc": 0.23,
      "us_company": 0.31,
      "foreign_supplier": 0.04
    },
    "value_inequality_gini": 0.32
  }
}
```

## 6. Extending the Demo

### 6.1 Adding Custom Policies

You can extend the demo by adding custom policies:

```python
# Create a tariff policy
tariff_policy = GovernancePolicy(
    policy_id="POL-" + uuid.uuid4().hex[:8],
    title="Targeted Tariff Policy",
    description="Applies tariffs to specific sectors",
    policy_type="tariff",
    status="draft"
)

# Add parameters
tariff_policy.add_parameter("tariff_rate", 0.05)  # 5% tariff
tariff_policy.add_parameter("affected_sectors", ["electronics", "automotive"])
tariff_policy.add_parameter("exemption_threshold", 10000000)  # $10M exemption

# Activate policy
tariff_policy.update_status("active", "Activated for demonstration")

# Register with extension
extension.policies[tariff_policy.policy_id] = tariff_policy
```

### 6.2 Creating Custom Economic Models

You can create custom economic models:

```python
# Create a sector-specific economic model
model = EconomicModel(
    model_id="MOD-" + uuid.uuid4().hex[:8],
    title="Semiconductor Sector Impact Model",
    description="Specialized model for semiconductor trade impact analysis",
    model_type="sector_specific"
)

# Add parameters
model.add_parameter("supply_elasticity", -1.2)
model.add_parameter("demand_elasticity", -0.8)
model.add_parameter("production_multiplier", 2.3)
model.add_parameter("employment_ratio", 12.5)  # Jobs per $1M output

# Register with extension
extension.economic_models[model.model_id] = model
```

### 6.3 Customizing Win-Win Calculations

You can customize how the win-win calculations work:

```python
# Custom entity profile creation
custom_profile = create_entity_profile(
    entity_id="custom_entity",
    entity_name="Custom Strategic Partner",
    entity_type="corporate",
    dimensions={
        "revenue_impact": 0.3,
        "strategic_alignment": 0.4,
        "technology_transfer": 0.2,
        "regulatory_compliance": 0.1
    },
    time_preference=0.08,  # Lower time preference (more future-oriented)
    risk_preference=0.25,  # Lower risk aversion (more risk tolerant)
    resource_constraints={
        "capital": 5000000.0,
        "personnel": 100.0,
        "time": 365.0
    }
)

# Register with extension
extension.entity_profiles["custom_entity"] = custom_profile
```

## 7. API Examples

### 7.1 JavaScript Client

```javascript
// Example JavaScript API client
const tradeBalanceClient = new TradeBalanceAPI({
  apiKey: 'your_api_key_here',
  baseUrl: 'https://api.example.com/trade-balance'
});

// Register an agency
async function registerAgency() {
  const result = await tradeBalanceClient.registerAgency({
    agency_id: 'USTDA-DEMO',
    agency_type: 'trade_development',
    capabilities: ['policy_development', 'trade_facilitation'],
    value_dimensions: {
      economic: 0.4, 
      diplomatic: 0.3, 
      technological: 0.2, 
      environmental: 0.1
    }
  });
  
  console.log('Agency registered:', result);
}

// Create a policy-based deal
async function createDeal() {
  const result = await tradeBalanceClient.createPolicyBasedDeal({
    agency_id: 'USTDA-DEMO',
    problem_statement: 'Establish semiconductor manufacturing partnership between US and Taiwan',
    stakeholder_ids: ['us_chipmaker', 'taiwan_foundry', 'logistics_provider'],
    policy_id: 'POL-12345'
  });
  
  console.log('Deal created:', result);
  
  // Get win-win status
  const winWin = await tradeBalanceClient.calculateWinWin({
    deal_id: result.deal_id,
    apply_adjustments: true
  });
  
  console.log('Win-Win status:', winWin);
}
```

### 7.2 Python SDK

```python
from hms_a2a.trade_balance import TradeBalanceSDK

# Initialize SDK
sdk = TradeBalanceSDK(api_key="your_api_key_here")

# Issue certificate
certificate = sdk.issue_certificate(
    owner="strategic_partner",
    value=1000000.0,
    duration=180
)

print(f"Certificate issued: {certificate.id}")

# Analyze economic impact
impact = sdk.analyze_economic_impact(
    deal_id="DEAL-12345",
    model_id="MODEL-67890",
    detailed=True
)

print(f"GDP Impact: {impact.gdp_impact}")
print(f"Job Creation: {impact.job_creation}")
print(f"Trade Balance Effect: {impact.trade_balance_effect}")
```

## 8. Conclusion

This demo showcases how to integrate USTDA and USITC agency agents with the Market Network architecture to implement Warren Buffett's Import Certificate system. By combining economic theory, formal verification, and Moneyball-style analysis, the system provides a comprehensive approach to balancing international trade.

Key benefits demonstrated:

1. **Trade Balance**: The Import Certificate system effectively addresses trade imbalances
2. **Economic Impact**: USITC models quantify the effects of trade policies
3. **Win-Win Deals**: Value optimization ensures all stakeholders benefit
4. **Opportunity Identification**: Moneyball approach finds undervalued sectors
5. **Margin of Safety**: Buffett principles ensure conservative projections

To explore further capabilities, you can modify the demo scenarios, add custom policies, or extend the economic models to address specific trade challenges.