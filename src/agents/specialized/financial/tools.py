"""
MCP Tools for Financial Domain.

This module provides MCP-compliant tools for financial services, accounting,
and regulatory compliance such as GAAP and IFRS.
"""
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime, date

from ..tools_base import StandardsCompliantTool
from ..standards_validation import StandardsValidator
from ..mcp_registry import register_tool


class FinancialTools:
    """Collection of MCP-compliant tools for financial domain."""

    @register_tool(
        name="validate_financial_statement",
        description="Validate financial statement structure and calculations against accounting standards",
        domains=["financial", "accounting"],
        standard="GAAP"
    )
    def validate_financial_statement(
        statement_type: str,
        statement_data: Dict[str, Any],
        accounting_standard: str = "GAAP",
        fiscal_period: str = None
    ) -> Dict[str, Any]:
        """
        Validate a financial statement against accounting standards.

        Args:
            statement_type: Type of statement ("income_statement", "balance_sheet", "cash_flow")
            statement_data: The financial statement data to validate
            accounting_standard: The accounting standard to validate against (GAAP, IFRS)
            fiscal_period: The fiscal period for the statement (optional)

        Returns:
            Dictionary with validation results and compliance issues
        """
        validator = StandardsValidator()
        
        # Define required elements for different statement types
        required_elements = {
            "income_statement": [
                "revenue", "expenses", "net_income"
            ],
            "balance_sheet": [
                "assets", "liabilities", "equity"
            ],
            "cash_flow": [
                "operating_activities", "investing_activities", "financing_activities"
            ]
        }
        
        # Define calculation rules
        calculation_rules = {
            "income_statement": {
                "net_income": lambda data: data.get("revenue", 0) - data.get("expenses", 0)
            },
            "balance_sheet": {
                "assets": lambda data: sum(data.get("assets", {}).values()),
                "equity": lambda data: data.get("assets", 0) - data.get("liabilities", 0)
            }
        }
        
        # Check if statement type is valid
        if statement_type not in required_elements:
            validator.add_violation(
                standard=accounting_standard,
                rule="statement_structure",
                message=f"Invalid statement type: {statement_type}",
                severity="high"
            )
            return {
                "valid": False,
                "violations": validator.get_violations(),
                "recommendations": [f"Use one of: {', '.join(required_elements.keys())}"]
            }
        
        # Check for required elements
        for element in required_elements[statement_type]:
            if element not in statement_data:
                validator.add_violation(
                    standard=accounting_standard,
                    rule="statement_structure",
                    message=f"Missing required element: {element}",
                    severity="high"
                )
        
        # Validate calculations if we have all required elements
        if statement_type in calculation_rules and all(elem in statement_data for elem in required_elements[statement_type]):
            for result_field, calculation in calculation_rules[statement_type].items():
                expected_value = calculation(statement_data)
                actual_value = statement_data.get(result_field, 0)
                
                # Allow for minor rounding differences
                if abs(expected_value - actual_value) > 0.01:
                    validator.add_violation(
                        standard=accounting_standard,
                        rule="calculation_accuracy",
                        message=f"Calculation error in {result_field}: expected {expected_value}, got {actual_value}",
                        severity="high"
                    )
        
        # Additional GAAP/IFRS specific validation
        if accounting_standard == "GAAP":
            # Check for revenue recognition
            if statement_type == "income_statement" and "revenue" in statement_data:
                if "revenue_recognition_policy" not in statement_data:
                    validator.add_violation(
                        standard="GAAP",
                        rule="revenue_recognition",
                        message="Revenue recognition policy must be disclosed",
                        severity="medium"
                    )
        elif accounting_standard == "IFRS":
            # Check for fair value measurements
            if statement_type == "balance_sheet" and "assets" in statement_data:
                if "fair_value_measurements" not in statement_data:
                    validator.add_violation(
                        standard="IFRS",
                        rule="fair_value_measurement",
                        message="Fair value measurement information must be provided for assets",
                        severity="medium"
                    )
        
        # Return validation results
        violations = validator.get_violations()
        
        return {
            "valid": len(violations) == 0,
            "statement_type": statement_type,
            "accounting_standard": accounting_standard,
            "fiscal_period": fiscal_period,
            "violations": violations,
            "recommendations": [
                "Ensure all required elements are included",
                "Verify calculation accuracy",
                f"Include all {accounting_standard}-required disclosures"
            ] if violations else []
        }

    @register_tool(
        name="analyze_financial_ratios",
        description="Calculate and analyze key financial ratios from financial statements",
        domains=["financial", "accounting", "investment"],
        standard="GAAP"
    )
    def analyze_financial_ratios(
        balance_sheet: Dict[str, Any],
        income_statement: Dict[str, Any],
        cash_flow_statement: Optional[Dict[str, Any]] = None,
        company_sector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate and analyze key financial ratios from financial statements.

        Args:
            balance_sheet: Balance sheet data
            income_statement: Income statement data
            cash_flow_statement: Optional cash flow statement data
            company_sector: Optional industry sector for benchmark comparison

        Returns:
            Dictionary with calculated ratios and analysis
        """
        ratios = {}
        
        # Liquidity ratios
        try:
            # Current ratio
            current_assets = balance_sheet.get("current_assets", 0)
            current_liabilities = balance_sheet.get("current_liabilities", 0)
            ratios["current_ratio"] = current_assets / current_liabilities if current_liabilities else None
            
            # Quick ratio (Acid-test ratio)
            inventory = balance_sheet.get("inventory", 0)
            quick_assets = current_assets - inventory
            ratios["quick_ratio"] = quick_assets / current_liabilities if current_liabilities else None
        except (KeyError, TypeError, ZeroDivisionError):
            pass
        
        # Profitability ratios
        try:
            # Gross profit margin
            revenue = income_statement.get("revenue", 0)
            gross_profit = income_statement.get("gross_profit", 0)
            ratios["gross_profit_margin"] = (gross_profit / revenue) * 100 if revenue else None
            
            # Net profit margin
            net_income = income_statement.get("net_income", 0)
            ratios["net_profit_margin"] = (net_income / revenue) * 100 if revenue else None
            
            # Return on assets (ROA)
            total_assets = balance_sheet.get("total_assets", 0)
            ratios["return_on_assets"] = (net_income / total_assets) * 100 if total_assets else None
            
            # Return on equity (ROE)
            shareholders_equity = balance_sheet.get("shareholders_equity", 0)
            ratios["return_on_equity"] = (net_income / shareholders_equity) * 100 if shareholders_equity else None
        except (KeyError, TypeError, ZeroDivisionError):
            pass
        
        # Leverage ratios
        try:
            # Debt to equity
            total_debt = balance_sheet.get("total_debt", 0)
            ratios["debt_to_equity"] = total_debt / shareholders_equity if shareholders_equity else None
            
            # Debt ratio
            ratios["debt_ratio"] = total_debt / total_assets if total_assets else None
            
            # Interest coverage
            ebit = income_statement.get("operating_income", 0)
            interest_expense = income_statement.get("interest_expense", 0)
            ratios["interest_coverage"] = ebit / interest_expense if interest_expense else None
        except (KeyError, TypeError, ZeroDivisionError):
            pass
        
        # Efficiency ratios
        try:
            # Asset turnover
            ratios["asset_turnover"] = revenue / total_assets if total_assets else None
            
            # Inventory turnover
            cost_of_goods_sold = income_statement.get("cost_of_goods_sold", 0)
            average_inventory = inventory  # Simplified; should be average of beginning and ending
            ratios["inventory_turnover"] = cost_of_goods_sold / average_inventory if average_inventory else None
            
            # Receivables turnover
            accounts_receivable = balance_sheet.get("accounts_receivable", 0)
            ratios["receivables_turnover"] = revenue / accounts_receivable if accounts_receivable else None
        except (KeyError, TypeError, ZeroDivisionError):
            pass
        
        # Get benchmark data if sector is provided
        benchmarks = {}
        if company_sector:
            # In a real implementation, this would fetch industry benchmarks from a database
            sector_benchmarks = {
                "technology": {
                    "current_ratio": 1.5,
                    "quick_ratio": 1.2,
                    "gross_profit_margin": 50.0,
                    "net_profit_margin": 15.0
                },
                "retail": {
                    "current_ratio": 1.2,
                    "quick_ratio": 0.7,
                    "gross_profit_margin": 25.0,
                    "net_profit_margin": 5.0
                },
                "manufacturing": {
                    "current_ratio": 1.3,
                    "quick_ratio": 0.9,
                    "gross_profit_margin": 30.0,
                    "net_profit_margin": 7.0
                },
                "financial": {
                    "current_ratio": 1.1,
                    "quick_ratio": 1.0,
                    "return_on_equity": 15.0,
                    "debt_to_equity": 2.5
                }
            }
            benchmarks = sector_benchmarks.get(company_sector.lower(), {})
        
        # Generate analysis for each ratio
        analysis = {}
        for ratio_name, ratio_value in ratios.items():
            if ratio_value is None:
                analysis[ratio_name] = "Cannot be calculated due to missing or zero value data"
                continue
                
            benchmark = benchmarks.get(ratio_name)
            if benchmark:
                if ratio_name in ["current_ratio", "quick_ratio"]:
                    if ratio_value >= benchmark:
                        analysis[ratio_name] = f"Good - above industry average of {benchmark}"
                    else:
                        analysis[ratio_name] = f"Concern - below industry average of {benchmark}"
                elif ratio_name in ["gross_profit_margin", "net_profit_margin", "return_on_assets", "return_on_equity"]:
                    if ratio_value >= benchmark:
                        analysis[ratio_name] = f"Good - above industry average of {benchmark}%"
                    else:
                        analysis[ratio_name] = f"Below industry average of {benchmark}%"
                elif ratio_name == "debt_to_equity":
                    if ratio_value <= benchmark:
                        analysis[ratio_name] = f"Good - at or below industry average of {benchmark}"
                    else:
                        analysis[ratio_name] = f"Concern - above industry average of {benchmark}"
            else:
                # Provide general analysis based on common thresholds
                if ratio_name == "current_ratio":
                    if ratio_value >= 2:
                        analysis[ratio_name] = "Strong liquidity position"
                    elif ratio_value >= 1:
                        analysis[ratio_name] = "Adequate liquidity position"
                    else:
                        analysis[ratio_name] = "Potential liquidity issue"
                elif ratio_name == "quick_ratio":
                    if ratio_value >= 1:
                        analysis[ratio_name] = "Strong short-term liquidity"
                    else:
                        analysis[ratio_name] = "May face challenges meeting short-term obligations"
                elif ratio_name == "net_profit_margin":
                    if ratio_value >= 20:
                        analysis[ratio_name] = "Excellent profitability"
                    elif ratio_value >= 10:
                        analysis[ratio_name] = "Good profitability"
                    elif ratio_value >= 5:
                        analysis[ratio_name] = "Average profitability"
                    else:
                        analysis[ratio_name] = "Below average profitability"
                elif ratio_name == "debt_to_equity":
                    if ratio_value >= 2:
                        analysis[ratio_name] = "High leverage - increased financial risk"
                    elif ratio_value >= 1:
                        analysis[ratio_name] = "Moderate leverage"
                    else:
                        analysis[ratio_name] = "Conservative financing"
                else:
                    analysis[ratio_name] = "Calculated successfully"
        
        # Provide overall financial health assessment
        overall_health = "Unable to determine due to insufficient data"
        
        try:
            # Simple algorithm for overall health assessment
            score = 0
            points = 0
            
            if ratios.get("current_ratio", 0) >= 1.5:
                score += 2
                points += 2
            elif ratios.get("current_ratio", 0) >= 1:
                score += 1
                points += 2
                
            if ratios.get("net_profit_margin", 0) >= 10:
                score += 2
                points += 2
            elif ratios.get("net_profit_margin", 0) >= 5:
                score += 1
                points += 2
                
            if ratios.get("debt_to_equity", float('inf')) <= 1:
                score += 2
                points += 2
            elif ratios.get("debt_to_equity", float('inf')) <= 2:
                score += 1
                points += 2
                
            if points > 0:
                health_percent = (score / points) * 100
                
                if health_percent >= 80:
                    overall_health = "Strong financial health"
                elif health_percent >= 60:
                    overall_health = "Good financial health"
                elif health_percent >= 40:
                    overall_health = "Fair financial health"
                else:
                    overall_health = "Concerns about financial health"
        except:
            pass
        
        return {
            "ratios": ratios,
            "analysis": analysis,
            "benchmarks": benchmarks,
            "overall_health": overall_health,
            "improvement_opportunities": [
                key for key, value in analysis.items() 
                if "concern" in value.lower() or "below" in value.lower() or "issue" in value.lower()
            ]
        }

    @register_tool(
        name="validate_tax_calculation",
        description="Validate tax calculations against tax regulations",
        domains=["financial", "tax", "accounting"],
        standard="GAAP"
    )
    def validate_tax_calculation(
        tax_type: str,
        tax_data: Dict[str, Any],
        tax_year: int,
        jurisdiction: str
    ) -> Dict[str, Any]:
        """
        Validate tax calculations against tax regulations.

        Args:
            tax_type: Type of tax ("income", "sales", "property", "payroll")
            tax_data: The tax calculation data to validate
            tax_year: The tax year for the calculation
            jurisdiction: The tax jurisdiction (country, state, or local)

        Returns:
            Dictionary with validation results and compliance issues
        """
        validator = StandardsValidator()
        
        # Check if tax type is valid
        valid_tax_types = ["income", "sales", "property", "payroll", "capital_gains"]
        if tax_type not in valid_tax_types:
            validator.add_violation(
                standard="tax_compliance",
                rule="tax_type",
                message=f"Invalid tax type: {tax_type}",
                severity="high"
            )
            return {
                "valid": False,
                "violations": validator.get_violations(),
                "recommendations": [f"Use one of: {', '.join(valid_tax_types)}"]
            }
        
        # Check required fields for each tax type
        required_fields = {
            "income": ["taxable_income", "deductions", "tax_rate", "tax_amount"],
            "sales": ["taxable_sales", "tax_rate", "tax_amount"],
            "property": ["assessed_value", "tax_rate", "tax_amount"],
            "payroll": ["gross_wages", "tax_rate", "tax_amount"],
            "capital_gains": ["gain_amount", "holding_period", "tax_rate", "tax_amount"]
        }
        
        for field in required_fields[tax_type]:
            if field not in tax_data:
                validator.add_violation(
                    standard="tax_compliance",
                    rule="required_fields",
                    message=f"Missing required field for {tax_type} tax: {field}",
                    severity="high"
                )
        
        # Validate calculations
        if all(field in tax_data for field in required_fields[tax_type]):
            if tax_type == "income":
                taxable_income = tax_data.get("taxable_income", 0)
                tax_rate = tax_data.get("tax_rate", 0)
                reported_tax = tax_data.get("tax_amount", 0)
                
                # Basic validation for flat tax rate
                expected_tax = taxable_income * (tax_rate / 100)
                
                # Allow for minor rounding differences
                if abs(expected_tax - reported_tax) > 1.0:
                    validator.add_violation(
                        standard="tax_compliance",
                        rule="calculation_accuracy",
                        message=f"Income tax calculation error: expected {expected_tax}, got {reported_tax}",
                        severity="high"
                    )
            
            elif tax_type == "sales":
                taxable_sales = tax_data.get("taxable_sales", 0)
                tax_rate = tax_data.get("tax_rate", 0)
                reported_tax = tax_data.get("tax_amount", 0)
                
                expected_tax = taxable_sales * (tax_rate / 100)
                
                if abs(expected_tax - reported_tax) > 1.0:
                    validator.add_violation(
                        standard="tax_compliance",
                        rule="calculation_accuracy",
                        message=f"Sales tax calculation error: expected {expected_tax}, got {reported_tax}",
                        severity="high"
                    )
            
            elif tax_type == "property":
                assessed_value = tax_data.get("assessed_value", 0)
                tax_rate = tax_data.get("tax_rate", 0)
                reported_tax = tax_data.get("tax_amount", 0)
                
                expected_tax = assessed_value * (tax_rate / 100)
                
                if abs(expected_tax - reported_tax) > 1.0:
                    validator.add_violation(
                        standard="tax_compliance",
                        rule="calculation_accuracy",
                        message=f"Property tax calculation error: expected {expected_tax}, got {reported_tax}",
                        severity="high"
                    )
        
        # Jurisdiction-specific validation
        if jurisdiction.lower() == "us":
            current_year = datetime.now().year
            
            # Check if tax year is valid
            if tax_year > current_year:
                validator.add_violation(
                    standard="tax_compliance",
                    rule="tax_year",
                    message=f"Invalid tax year: {tax_year} is in the future",
                    severity="medium"
                )
            
            # Check for specific US tax rules
            if tax_type == "income":
                if "fica_taxes" not in tax_data and "employment_income" in tax_data:
                    validator.add_violation(
                        standard="tax_compliance",
                        rule="us_specific",
                        message="FICA taxes must be calculated for employment income",
                        severity="medium"
                    )
        
        # Return validation results
        violations = validator.get_violations()
        
        return {
            "valid": len(violations) == 0,
            "tax_type": tax_type,
            "tax_year": tax_year,
            "jurisdiction": jurisdiction,
            "violations": violations,
            "recommendations": [
                "Ensure all required fields are included",
                "Verify calculation accuracy",
                "Include all jurisdiction-specific requirements",
                "Consider consulting a tax professional for complex calculations"
            ] if violations else []
        }

    @register_tool(
        name="generate_financial_report",
        description="Generate a standards-compliant financial report",
        domains=["financial", "accounting", "reporting"],
        standard="GAAP"
    )
    def generate_financial_report(
        report_type: str,
        financial_data: Dict[str, Any],
        company_info: Dict[str, Any],
        reporting_period: Dict[str, Any],
        accounting_standard: str = "GAAP"
    ) -> Dict[str, Any]:
        """
        Generate a standards-compliant financial report.

        Args:
            report_type: Type of report ("annual", "quarterly", "audit", "tax")
            financial_data: Financial data for the report
            company_info: Information about the company
            reporting_period: Start and end dates for the reporting period
            accounting_standard: The accounting standard to use

        Returns:
            Dictionary with the generated report
        """
        validator = StandardsValidator()
        
        # Check if report type is valid
        valid_report_types = ["annual", "quarterly", "audit", "tax", "management"]
        if report_type not in valid_report_types:
            validator.add_violation(
                standard=accounting_standard,
                rule="report_type",
                message=f"Invalid report type: {report_type}",
                severity="high"
            )
            return {
                "error": f"Invalid report type: {report_type}",
                "valid_types": valid_report_types
            }
        
        # Check required fields for company info
        required_company_fields = ["name", "address", "identification_number"]
        for field in required_company_fields:
            if field not in company_info:
                validator.add_violation(
                    standard=accounting_standard,
                    rule="company_information",
                    message=f"Missing required company information: {field}",
                    severity="medium"
                )
        
        # Check required fields for reporting period
        required_period_fields = ["start_date", "end_date"]
        for field in required_period_fields:
            if field not in reporting_period:
                validator.add_violation(
                    standard=accounting_standard,
                    rule="reporting_period",
                    message=f"Missing required reporting period information: {field}",
                    severity="medium"
                )
        
        # Check required financial statements based on report type
        required_statements = {
            "annual": ["income_statement", "balance_sheet", "cash_flow_statement", "equity_statement"],
            "quarterly": ["income_statement", "balance_sheet"],
            "audit": ["income_statement", "balance_sheet", "cash_flow_statement"],
            "tax": ["income_statement", "tax_reconciliation"],
            "management": ["income_statement", "key_metrics"]
        }
        
        for statement in required_statements.get(report_type, []):
            if statement not in financial_data:
                validator.add_violation(
                    standard=accounting_standard,
                    rule="report_content",
                    message=f"Missing required financial statement: {statement}",
                    severity="high"
                )
        
        # Generate the report
        report = {
            "metadata": {
                "report_type": report_type,
                "company": company_info.get("name", "Unknown Company"),
                "accounting_standard": accounting_standard,
                "period": f"{reporting_period.get('start_date', 'Unknown')} to {reporting_period.get('end_date', 'Unknown')}",
                "generation_date": datetime.now().strftime("%Y-%m-%d"),
                "compliant": len(validator.get_violations()) == 0
            },
            "company_information": company_info,
            "reporting_period": reporting_period,
            "financial_statements": {}
        }
        
        # Include financial statements that are provided
        for statement_name, statement_data in financial_data.items():
            report["financial_statements"][statement_name] = statement_data
        
        # Add standard-specific report elements
        if accounting_standard == "GAAP":
            report["required_disclosures"] = {
                "accounting_policies": financial_data.get("accounting_policies", "Not provided"),
                "revenue_recognition": financial_data.get("revenue_recognition", "Not provided"),
                "subsequent_events": financial_data.get("subsequent_events", "None reported")
            }
        elif accounting_standard == "IFRS":
            report["required_disclosures"] = {
                "accounting_policies": financial_data.get("accounting_policies", "Not provided"),
                "fair_value_measurements": financial_data.get("fair_value_measurements", "Not provided"),
                "operating_segments": financial_data.get("operating_segments", "Not provided")
            }
        
        # Include compliance information
        violations = validator.get_violations()
        if violations:
            report["compliance_issues"] = violations
            
            report["recommendations"] = [
                "Include all required financial statements",
                "Provide complete company information",
                "Specify accurate reporting period",
                f"Ensure all {accounting_standard} required disclosures are included"
            ]
        
        return report


def register_financial_tools() -> List[str]:
    """Register all financial tools and return their names.
    
    Returns:
        List of registered tool names
    """
    # In a real implementation, this would register tools with a central registry
    tools = [
        FinancialTools.validate_financial_statement,
        FinancialTools.analyze_financial_ratios,
        FinancialTools.validate_tax_calculation,
        FinancialTools.generate_financial_report
    ]
    
    return [tool.__name__ for tool in tools]