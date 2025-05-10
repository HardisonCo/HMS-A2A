"""
Accounting Tools

This module provides MCP-compliant tools for accounting professionals.
"""

from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

from specialized_agents.tools_base import (
    StandardsCompliantTool,
    ContentPart,
    ToolMetadata,
    create_tool_input_model
)
from specialized_agents.standards_validation import StandardsValidator

#
# Accounting Software Tool
#

# Create the Accounting Software Input Schema
AccountingSoftwareInputSchema = create_tool_input_model(
    "AccountingSoftwareInput",
    {
        # General parameters
        "company_name": (str, Field(description="Company name for the accounting records")),
        "start_date": (str, Field(description="Start date for the accounting period (YYYY-MM-DD)")),
        "end_date": (str, Field(description="End date for the accounting period (YYYY-MM-DD)")),

        # Operation-specific parameters
        "operation": (str, Field(description="The specific accounting operation to perform")),

        # Business type and requirements (from original)
        "business_type": (str, Field(description="Type of business (e.g., small business, enterprise, nonprofit)")),
        "industry": (str, Field(description="Industry sector the business operates in")),
        "features_needed": (List[str], Field(description="List of required accounting features")),
        "budget_range": (str, Field(description="Budget range for accounting software")),
        "user_count": (int, Field(description="Number of users who need access to the software")),
        "integration_requirements": (Optional[List[str]], Field(None, description="Systems that need to integrate with the accounting software")),
        "compliance_requirements": (Optional[List[str]], Field(None, description="Specific compliance standards required (e.g., GAAP, IFRS, SOX)")),
        
        # Financial data (optional)
        "financial_data": (Optional[Dict[str, Any]], Field(None, description="Financial data for processing"))
    },
    """Input schema for accounting software tools."""
)


class SoftwareRecommendation(BaseModel):
    """Software recommendation details."""
    name: str
    description: str
    pricing_tier: str
    key_features: List[str]
    pros: List[str]
    cons: List[str]
    compliance_support: List[str]
    suitable_for: List[str]


class AccountingSoftwareResult(BaseModel):
    """Accounting software result."""
    status: str = "success"  # success, partial_success, error
    message: str
    
    # Operation details
    operation_details: Dict[str, Any]
    
    # Optional result fields based on operation type
    financial_statements: Optional[Dict[str, Any]] = None
    transaction_results: Optional[Dict[str, Any]] = None
    reconciliation_results: Optional[Dict[str, Any]] = None
    expense_results: Optional[Dict[str, Any]] = None
    invoice_results: Optional[Dict[str, Any]] = None
    payroll_results: Optional[Dict[str, Any]] = None
    
    # Software evaluation results (original functionality)
    top_recommendations: Optional[List[SoftwareRecommendation]] = None
    alternative_options: Optional[List[SoftwareRecommendation]] = None
    implementation_considerations: Optional[List[str]] = None
    cost_comparison: Optional[Dict[str, Any]] = None
    
    # Generated files
    generated_files: Optional[List[Dict[str, Any]]] = None
    
    # Audit trail
    audit_trail: Optional[Dict[str, Any]] = None
    
    # Standard disclaimer
    disclaimer: str


class AccountingSoftwareTool(StandardsCompliantTool[AccountingSoftwareInputSchema, AccountingSoftwareResult]):
    """A standards-compliant tool for evaluating accounting software."""
    
    def __init__(self):
        """Initialize the accounting software evaluation tool."""
        super().__init__(
            name="accounting_software_evaluation",
            description="Evaluates and recommends accounting software based on business requirements, size, industry, and compliance needs",
            input_schema=AccountingSoftwareInputSchema,
            supported_standards=[
                "GAAP",
                "IFRS",
                "SOX",
                "AICPA_CODE_OF_ETHICS"
            ],
            domain="Accounting",
            metadata=ToolMetadata(
                title="Accounting Software Evaluation Tool",
                read_only=True,
                destructive=False,
                idempotent=True,
                open_world=False,
                description="Standards-compliant accounting software evaluation"
            )
        )
    
    async def execute(self, args: AccountingSoftwareInputSchema, session_context: Optional[Dict[str, Any]] = None) -> AccountingSoftwareResult:
        """Execute the accounting software operation.
        
        Args:
            args: Validated input arguments
            session_context: Optional session context
            
        Returns:
            Accounting software operation result
        """
        # Get current time for timestamps
        timestamp = datetime.now().isoformat()
        
        # Standard disclaimer for financial information
        disclaimer = (
            "This information is for informational purposes only and is not financial or accounting advice. "
            "Financial data provided may not reflect all accounting complexities or regulatory requirements. "
            "Always consult with a qualified accounting professional before making financial decisions or "
            "implementing accounting processes. Ensure all accounting practices comply with relevant standards "
            "including GAAP, IFRS, or other applicable frameworks for your jurisdiction."
        )
        
        # Initialize audit trail
        audit_trail = {
            "userId": "system",
            "timestamp": timestamp,
            "ipAddress": "127.0.0.1",
            "actionType": f"ACCOUNTING_{args.operation.upper() if hasattr(args, 'operation') else 'OPERATION'}",
            "details": f"Performed accounting operation for {args.company_name if hasattr(args, 'company_name') else 'company'}"
        }
        
        # Determine which operation to perform
        if not hasattr(args, 'operation') or args.operation == "evaluate_software":
            # Original software evaluation functionality
            return await self._execute_software_evaluation(args, timestamp, disclaimer, audit_trail)
        elif args.operation == "generate_financial_statements":
            return self._generate_financial_statements(args, timestamp, disclaimer, audit_trail)
        elif args.operation == "record_transaction":
            return self._record_transactions(args, timestamp, disclaimer, audit_trail)
        elif args.operation == "reconcile_accounts":
            return self._reconcile_accounts(args, timestamp, disclaimer, audit_trail)
        elif args.operation == "track_expenses":
            return self._track_expenses(args, timestamp, disclaimer, audit_trail)
        elif args.operation == "manage_invoices":
            return self._manage_invoices(args, timestamp, disclaimer, audit_trail)
        elif args.operation == "run_payroll":
            return self._run_payroll(args, timestamp, disclaimer, audit_trail)
        else:
            raise ValueError(f"Unsupported operation: {args.operation}")
            
    async def _execute_software_evaluation(
        self, 
        args: AccountingSoftwareInputSchema, 
        timestamp: str,
        disclaimer: str,
        audit_trail: Dict[str, Any]
    ) -> AccountingSoftwareResult:
        """Execute the original accounting software evaluation functionality.
        
        Args:
            args: Validated input arguments
            timestamp: Operation timestamp
            disclaimer: Standard disclaimer
            audit_trail: Audit trail information
            
        Returns:
            Accounting software evaluation result
        """
        print(f"Evaluating accounting software for {args.business_type} in the {args.industry} industry")
        
        # Generate recommendations based on business type and requirements
        top_recommendations = self._generate_recommendations(
            args.business_type, 
            args.industry, 
            args.features_needed, 
            args.budget_range,
            args.user_count,
            args.compliance_requirements
        )
        
        # Generate alternative options
        alternative_options = self._generate_alternative_options(
            args.business_type,
            args.industry,
            args.features_needed,
            args.budget_range
        )
        
        # Generate implementation considerations
        implementation_considerations = self._generate_implementation_considerations(
            args.business_type,
            args.integration_requirements
        )
        
        # Generate cost comparison
        cost_comparison = self._generate_cost_comparison(
            [rec.name for rec in top_recommendations + alternative_options],
            args.user_count
        )
        
        # Updated evaluation disclaimer
        evaluation_disclaimer = (
            "This evaluation is for informational purposes only and is not an endorsement of any specific product. "
            "Software capabilities and pricing may change over time. Organizations should conduct their own due diligence "
            "before selecting accounting software, including requesting demos, consulting with IT professionals, and "
            "reviewing contracts carefully. Proper implementation is critical for accounting system effectiveness and compliance."
        )
        
        # Prepare operation details
        operation_details = {
            "operationType": "Software Evaluation",
            "timeProcessed": timestamp,
            "affectedRecords": len(top_recommendations) + len(alternative_options)
        }
        
        # Prepare result
        result = AccountingSoftwareResult(
            status="success",
            message=f"Successfully evaluated accounting software options for {args.business_type} businesses in the {args.industry} industry",
            operation_details=operation_details,
            top_recommendations=top_recommendations,
            alternative_options=alternative_options,
            implementation_considerations=implementation_considerations,
            cost_comparison=cost_comparison,
            audit_trail=audit_trail,
            disclaimer=evaluation_disclaimer
        )
        
        return result
        
    def _generate_financial_statements(
        self, 
        args: AccountingSoftwareInputSchema,
        timestamp: str,
        disclaimer: str,
        audit_trail: Dict[str, Any]
    ) -> AccountingSoftwareResult:
        """Generate financial statements.
        
        Args:
            args: Validated input arguments
            timestamp: Operation timestamp
            disclaimer: Standard disclaimer
            audit_trail: Audit trail information
            
        Returns:
            Accounting software result
        """
        # Validate required data is present
        if not args.financial_data:
            raise ValueError("Financial data is required for generating financial statements")
            
        # In a real implementation, this would connect to accounting software
        # and generate actual financial statements
            
        # For this example, we'll calculate simple financial statements
        
        # Extract transactions from financial data (if available)
        transactions = args.financial_data.get("transactions", [])
        accounts = args.financial_data.get("accounts", [])
        
        # Calculate income statement (simplified)
        income_statement = self._calculate_income_statement(transactions)
        
        # Calculate balance sheet (simplified)
        balance_sheet = self._calculate_balance_sheet(accounts)
        
        # Calculate cash flow statement (simplified)
        cash_flow_statement = self._calculate_cash_flow_statement(transactions)
        
        # Generate file info
        file_timestamp = timestamp.replace(":", "-").split(".")[0]
        file_name = f"financial_statements_{args.company_name}_{file_timestamp}.pdf"
        
        # Prepare financial statements
        financial_statements = {
            "incomeStatement": income_statement,
            "balanceSheet": balance_sheet,
            "cashFlowStatement": cash_flow_statement
        }
        
        # Prepare operation details
        operation_details = {
            "operationType": "Financial Statement Generation",
            "timeProcessed": timestamp,
            "affectedRecords": len(transactions) if transactions else 0
        }
        
        # Prepare generated files
        generated_files = [
            {
                "fileName": file_name,
                "fileType": "application/pdf",
                "fileUrl": f"https://example.com/reports/{args.company_name}/financial_statements_{file_timestamp}.pdf",
                "fileSize": 1240000,  # Example size in bytes
                "generatedAt": timestamp
            }
        ]
        
        # Update audit trail
        audit_trail["details"] = f"Generated financial statements for {args.company_name} ({args.start_date} to {args.end_date})"
        
        return AccountingSoftwareResult(
            status="success",
            message="Financial statements generated successfully",
            operation_details=operation_details,
            financial_statements=financial_statements,
            generated_files=generated_files,
            audit_trail=audit_trail,
            disclaimer=disclaimer
        )
    
    def format_result(self, result: AccountingSoftwareResult) -> List[ContentPart]:
        """Format the result for display.
        
        Args:
            result: Accounting software result
            
        Returns:
            List of content parts
        """
        # Create a data part with the full result
        data_part = ContentPart(
            type=ContentPart.ContentType.DATA,
            content=result.model_dump()
        )
        
        # Format basic info
        text_output = f"# {result.operation_details.get('operationType', 'Operation')} Results\n\n"
        text_output += f"**Status:** {result.status}\n"
        text_output += f"**Message:** {result.message}\n"
        text_output += f"**Processed at:** {result.operation_details.get('timeProcessed', '')}\n\n"
        
        # Add operation-specific details
        if result.financial_statements:
            text_output += self._format_financial_statements(result.financial_statements)
        
        if result.transaction_results:
            text_output += self._format_transaction_results(result.transaction_results)
        
        if result.reconciliation_results:
            text_output += self._format_reconciliation_results(result.reconciliation_results)
        
        if result.expense_results:
            text_output += self._format_expense_results(result.expense_results)
        
        if result.invoice_results:
            text_output += self._format_invoice_results(result.invoice_results)
        
        if result.payroll_results:
            text_output += self._format_payroll_results(result.payroll_results)
        
        # Format software evaluation results if present
        if result.top_recommendations:
            top_recs_text = "\n\n".join([
                f"### {rec.name}\n"
                f"{rec.description}\n"
                f"**Pricing tier:** {rec.pricing_tier}\n"
                f"**Key features:** {', '.join(rec.key_features)}\n"
                f"**Pros:** {', '.join(rec.pros)}\n"
                f"**Cons:** {', '.join(rec.cons)}\n"
                f"**Compliance support:** {', '.join(rec.compliance_support)}"
                for rec in result.top_recommendations
            ])
            
            text_output += f"""
## Software Recommendations

### Top Recommendations
{top_recs_text}

"""
            
            if result.implementation_considerations:
                text_output += f"""
### Implementation Considerations
{chr(10).join([f"- {consideration}" for consideration in result.implementation_considerations])}

"""

            if result.cost_comparison:
                text_output += f"""
### Cost Comparison
- Small tier: ${result.cost_comparison.get("small_tier", 0)}/user/month (average)
- Medium tier: ${result.cost_comparison.get("medium_tier", 0)}/user/month (average)
- Enterprise tier: ${result.cost_comparison.get("enterprise_tier", 0)}/user/month (average)

"""
        
        # Add generated files if any
        if result.generated_files and len(result.generated_files) > 0:
            text_output += '## Generated Files\n\n'
            for file in result.generated_files:
                text_output += f"- **{file.get('fileName', 'File')}** ({file.get('fileType', 'Document')}): Generated at {file.get('generatedAt', '')}\n"
                if file.get('fileUrl'):
                    text_output += f"  [Access File]({file.get('fileUrl')})\n"
            text_output += '\n'
        
        # Add disclaimer
        text_output += f"### Disclaimer\n{result.disclaimer}\n"
        
        text_part = ContentPart(
            type=ContentPart.ContentType.TEXT,
            content=text_output.strip()
        )
        
        return [data_part, text_part]
        
    def _format_financial_statements(self, statements: Dict[str, Any]) -> str:
        """Format financial statements for display."""
        output = '## Financial Statement Summary\n\n'
        
        if "incomeStatement" in statements:
            income = statements["incomeStatement"]
            output += '### Income Statement\n'
            total_revenue = income.get("totalRevenue", 0)
            total_expenses = income.get("totalExpenses", 0)
            net_income = income.get("netIncome", 0)
            
            output += f"Total Revenue: {total_revenue:,.2f}\n"
            output += f"Total Expenses: {total_expenses:,.2f}\n"
            output += f"Net Income: {net_income:,.2f}\n\n"
            
            if "breakdownByCategory" in income:
                output += "#### Revenue/Expense Breakdown\n"
                for category, amount in income["breakdownByCategory"].items():
                    output += f"- {category}: {amount:,.2f}\n"
                output += "\n"
        
        if "balanceSheet" in statements:
            balance = statements["balanceSheet"]
            output += '### Balance Sheet\n'
            output += f"Total Assets: {balance.get('totalAssets', 0):,.2f}\n"
            output += f"Total Liabilities: {balance.get('totalLiabilities', 0):,.2f}\n"
            output += f"Total Equity: {balance.get('totalEquity', 0):,.2f}\n"
            
            if "currentRatio" in balance:
                output += f"Current Ratio: {balance['currentRatio']:.2f}\n"
            
            output += '\n'
        
        if "cashFlowStatement" in statements:
            cashflow = statements["cashFlowStatement"]
            output += '### Cash Flow Statement\n'
            output += f"Operating Cash Flow: {cashflow.get('operatingCashFlow', 0):,.2f}\n"
            output += f"Investing Cash Flow: {cashflow.get('investingCashFlow', 0):,.2f}\n"
            output += f"Financing Cash Flow: {cashflow.get('financingCashFlow', 0):,.2f}\n"
            output += f"Net Cash Change: {cashflow.get('netCashChange', 0):,.2f}\n\n"
        
        return output
    
    def _format_transaction_results(self, results: Dict[str, Any]) -> str:
        """Format transaction results for display."""
        output = '## Transaction Results\n\n'
        output += f"Transactions Processed: {results.get('transactionsProcessed', 0)}\n"
        
        if "batchId" in results:
            output += f"Batch ID: {results['batchId']}\n\n"
        
        if "summary" in results and results["summary"]:
            output += '### Transaction Summary by Category\n'
            for category, amount in results["summary"].items():
                output += f"- {category}: {amount:,.2f}\n"
            output += '\n'
        
        return output
    
    def _format_reconciliation_results(self, results: Dict[str, Any]) -> str:
        """Format reconciliation results for display."""
        output = '## Reconciliation Results\n\n'
        output += f"Accounts Reconciled: {results.get('accountsReconciled', 0)}\n"
        output += f"Matched Transactions: {results.get('matchedTransactions', 0)}\n"
        output += f"Unmatched Transactions: {results.get('unmatchedTransactions', 0)}\n\n"
        
        if "adjustments" in results and results["adjustments"]:
            output += '### Adjustments Required\n'
            for adjustment in results["adjustments"]:
                output += f"- {adjustment.get('account', '')}: {adjustment.get('amount', 0):,.2f} ({adjustment.get('reason', '')})\n"
            output += '\n'
        
        return output
    
    def _format_expense_results(self, results: Dict[str, Any]) -> str:
        """Format expense results for display."""
        output = '## Expense Tracking Results\n\n'
        output += f"Expenses Tracked: {results.get('trackedExpenses', 0)}\n"
        output += f"Total Amount: {results.get('totalAmount', 0):,.2f}\n"
        
        if "reimbursableTotal" in results:
            output += f"Reimbursable Total: {results['reimbursableTotal']:,.2f}\n"
        
        if "categorySummary" in results and results["categorySummary"]:
            output += '\n### Expense Summary by Category\n'
            for category, amount in results["categorySummary"].items():
                output += f"- {category}: {amount:,.2f}\n"
        
        output += '\n'
        return output
    
    def _format_invoice_results(self, results: Dict[str, Any]) -> str:
        """Format invoice results for display."""
        output = '## Invoice Management Results\n\n'
        output += f"Invoices Processed: {results.get('processedInvoices', 0)}\n"
        output += f"Total Value: {results.get('totalValue', 0):,.2f}\n\n"
        
        if "statusSummary" in results:
            output += '### Invoice Status Summary\n'
            statuses = results["statusSummary"]
            for status, count in statuses.items():
                if count:
                    output += f"- {status.title()}: {count}\n"
            output += '\n'
        
        if "newInvoiceIds" in results and results["newInvoiceIds"]:
            output += '### New Invoices Created\n'
            for invoice_id in results["newInvoiceIds"]:
                output += f"- {invoice_id}\n"
            output += '\n'
        
        return output
    
    def _format_payroll_results(self, results: Dict[str, Any]) -> str:
        """Format payroll results for display."""
        output = '## Payroll Processing Results\n\n'
        output += f"Employees Paid: {results.get('employeesPaid', 0)}\n"
        output += f"Total Gross Pay: {results.get('totalGrossPay', 0):,.2f}\n"
        output += f"Total Net Pay: {results.get('totalNetPay', 0):,.2f}\n"
        output += f"Total Taxes: {results.get('totalTaxes', 0):,.2f}\n"
        output += f"Total Deductions: {results.get('totalDeductions', 0):,.2f}\n\n"
        
        if "payrollRunId" in results:
            output += f"Payroll Run ID: {results['payrollRunId']}\n"
        
        if "payrollSummaryUrl" in results:
            output += f"[View Detailed Payroll Report]({results['payrollSummaryUrl']})\n"
        
        output += '\n'
        return output
    
    def _generate_recommendations(
        self, 
        business_type: str, 
        industry: str, 
        features_needed: List[str],
        budget_range: str,
        user_count: int,
        compliance_requirements: Optional[List[str]]
    ) -> List[SoftwareRecommendation]:
        """Generate software recommendations based on requirements.
        
        Args:
            business_type: Type of business
            industry: Industry sector
            features_needed: Required features
            budget_range: Budget range
            user_count: Number of users
            compliance_requirements: Compliance requirements
            
        Returns:
            List of software recommendations
        """
        # This would connect to a database or API in a real implementation
        # For demonstration, we'll return static recommendations based on inputs
        
        recommendations = []
        
        # Map business types to appropriate software
        small_business_options = ["QuickBooks Online", "Xero", "Wave", "FreshBooks"]
        enterprise_options = ["SAP", "Oracle NetSuite", "Microsoft Dynamics 365", "Sage Intacct"]
        nonprofit_options = ["QuickBooks Nonprofit", "Aplos", "Fund E-Z", "Blackbaud Financial Edge"]
        
        # Select appropriate options based on business type
        if "small" in business_type.lower():
            target_options = small_business_options
            pricing_tier = "Small Business"
        elif "enterprise" in business_type.lower() or "large" in business_type.lower():
            target_options = enterprise_options
            pricing_tier = "Enterprise"
        elif "nonprofit" in business_type.lower() or "ngo" in business_type.lower():
            target_options = nonprofit_options
            pricing_tier = "Nonprofit"
        else:
            # Default to small business options
            target_options = small_business_options
            pricing_tier = "Small Business"
        
        # Add QuickBooks Online recommendation for small business
        if "small" in business_type.lower() and "QuickBooks Online" in target_options:
            qbo_compliance = ["Basic GAAP compliance"]
            if compliance_requirements:
                if any("sox" in req.lower() for req in compliance_requirements):
                    qbo_compliance.append("Limited SOX support")
                if any("ifrs" in req.lower() for req in compliance_requirements):
                    qbo_compliance.append("Limited IFRS support")
            
            recommendations.append(SoftwareRecommendation(
                name="QuickBooks Online",
                description="Cloud-based accounting software suitable for small to medium-sized businesses",
                pricing_tier=pricing_tier,
                key_features=[
                    "Invoicing",
                    "Expense tracking",
                    "Bank reconciliation",
                    "Financial reporting",
                    "Tax preparation support"
                ],
                pros=[
                    "User-friendly interface",
                    "Wide adoption with accountant support",
                    "Extensive third-party integrations",
                    "Scalable with different tiers"
                ],
                cons=[
                    "Limited customization options",
                    "Advanced features require higher-tier plans",
                    "May not meet all specialized industry needs"
                ],
                compliance_support=qbo_compliance,
                suitable_for=[
                    "Small businesses",
                    "Service-based businesses",
                    "Retail",
                    "Contractors"
                ]
            ))
        
        # Add Xero recommendation for small business
        if "small" in business_type.lower() and "Xero" in target_options:
            xero_compliance = ["Basic GAAP compliance"]
            if compliance_requirements:
                if any("ifrs" in req.lower() for req in compliance_requirements):
                    xero_compliance.append("Good IFRS support")
            
            recommendations.append(SoftwareRecommendation(
                name="Xero",
                description="Cloud-based accounting platform with strong international capabilities",
                pricing_tier=pricing_tier,
                key_features=[
                    "Invoicing and billing",
                    "Bank reconciliation",
                    "Expense claims",
                    "Inventory management",
                    "Multi-currency support"
                ],
                pros=[
                    "Strong international support",
                    "Unlimited users on all plans",
                    "Modern user interface",
                    "Good mobile app"
                ],
                cons=[
                    "Limited reporting compared to some competitors",
                    "U.S. payroll requires add-on",
                    "Customer support can be slow"
                ],
                compliance_support=xero_compliance,
                suitable_for=[
                    "Small to medium businesses",
                    "International businesses",
                    "E-commerce",
                    "Service-based businesses"
                ]
            ))
        
        # Add SAP recommendation for enterprise
        if "enterprise" in business_type.lower() and "SAP" in target_options:
            sap_compliance = ["Full GAAP compliance", "Full IFRS compliance", "SOX compliance support"]
            
            recommendations.append(SoftwareRecommendation(
                name="SAP S/4HANA Finance",
                description="Enterprise-grade financial management system with comprehensive capabilities",
                pricing_tier="Enterprise",
                key_features=[
                    "General ledger accounting",
                    "Accounts payable and receivable",
                    "Asset accounting",
                    "Advanced financial closing",
                    "Financial planning and analysis",
                    "Treasury and risk management",
                    "Consolidated financial statements"
                ],
                pros=[
                    "Comprehensive enterprise solution",
                    "Strong compliance features",
                    "In-memory database for real-time analytics",
                    "Global deployment capabilities",
                    "Industry-specific solutions"
                ],
                cons=[
                    "High implementation cost and complexity",
                    "Lengthy implementation timeline",
                    "Requires specialized expertise",
                    "May be overly complex for smaller organizations"
                ],
                compliance_support=sap_compliance,
                suitable_for=[
                    "Large enterprises",
                    "Multinational corporations",
                    "Companies with complex compliance requirements",
                    "Organizations requiring integrated ERP solution"
                ]
            ))
        
        # Add Aplos recommendation for nonprofit
        if "nonprofit" in business_type.lower() and "Aplos" in target_options:
            aplos_compliance = ["Nonprofit GAAP compliance"]
            
            recommendations.append(SoftwareRecommendation(
                name="Aplos",
                description="Fund accounting software designed specifically for nonprofits and churches",
                pricing_tier="Nonprofit",
                key_features=[
                    "Fund accounting",
                    "Donor management",
                    "Contribution tracking",
                    "Budget management",
                    "Form 990 preparation",
                    "Board reporting"
                ],
                pros=[
                    "Purpose-built for nonprofits",
                    "Simple user interface",
                    "Integrated donation processing",
                    "Good customer support"
                ],
                cons=[
                    "Limited advanced accounting features",
                    "Fewer integrations than general accounting software",
                    "Limited customization options"
                ],
                compliance_support=aplos_compliance,
                suitable_for=[
                    "Small to medium nonprofits",
                    "Churches and faith-based organizations",
                    "Organizations with basic accounting needs",
                    "Organizations with limited accounting staff"
                ]
            ))
        
        # Ensure we have at least one recommendation
        if not recommendations:
            recommendations.append(SoftwareRecommendation(
                name="QuickBooks Online",
                description="Cloud-based accounting software suitable for small to medium-sized businesses",
                pricing_tier="Small Business",
                key_features=[
                    "Invoicing",
                    "Expense tracking",
                    "Bank reconciliation",
                    "Financial reporting",
                    "Tax preparation support"
                ],
                pros=[
                    "User-friendly interface",
                    "Wide adoption with accountant support",
                    "Extensive third-party integrations",
                    "Scalable with different tiers"
                ],
                cons=[
                    "Limited customization options",
                    "Advanced features require higher-tier plans",
                    "May not meet all specialized industry needs"
                ],
                compliance_support=["Basic GAAP compliance"],
                suitable_for=[
                    "Small businesses",
                    "Service-based businesses",
                    "Retail",
                    "Contractors"
                ]
            ))
        
        # Limit to top 2 recommendations
        return recommendations[:2]
    
    def _generate_alternative_options(
        self,
        business_type: str,
        industry: str,
        features_needed: List[str],
        budget_range: str
    ) -> List[SoftwareRecommendation]:
        """Generate alternative software options.
        
        Args:
            business_type: Type of business
            industry: Industry sector
            features_needed: Required features
            budget_range: Budget range
            
        Returns:
            List of alternative software recommendations
        """
        # For demonstration, return one alternative option
        if "small" in business_type.lower():
            return [SoftwareRecommendation(
                name="Wave Accounting",
                description="Free accounting software for small businesses and freelancers",
                pricing_tier="Free (with paid add-ons)",
                key_features=[
                    "Invoicing",
                    "Accounting",
                    "Receipt scanning",
                    "Basic financial reporting"
                ],
                pros=[
                    "Free core accounting features",
                    "User-friendly interface",
                    "Unlimited invoicing",
                    "No monthly fees"
                ],
                cons=[
                    "Limited customer support",
                    "Fewer features than paid alternatives",
                    "Payments and payroll are paid add-ons",
                    "Limited reporting capabilities"
                ],
                compliance_support=["Basic bookkeeping standards"],
                suitable_for=[
                    "Freelancers",
                    "Startups",
                    "Very small businesses",
                    "Businesses with basic accounting needs"
                ]
            )]
        elif "enterprise" in business_type.lower():
            return [SoftwareRecommendation(
                name="Oracle NetSuite",
                description="Cloud-based ERP with comprehensive financial management capabilities",
                pricing_tier="Enterprise",
                key_features=[
                    "Financial management",
                    "Revenue recognition",
                    "Billing",
                    "Global accounting and consolidation",
                    "Reporting and analytics"
                ],
                pros=[
                    "All-in-one cloud solution",
                    "Highly customizable",
                    "Strong multi-subsidiary support",
                    "Built-in business intelligence"
                ],
                cons=[
                    "Complex implementation",
                    "High cost",
                    "Steep learning curve",
                    "May require ongoing consulting support"
                ],
                compliance_support=["GAAP compliance", "IFRS compliance", "SOX compliance"],
                suitable_for=[
                    "Mid-sized to large enterprises",
                    "Fast-growing companies",
                    "Companies with international operations",
                    "Organizations with complex accounting needs"
                ]
            )]
        else:
            return [SoftwareRecommendation(
                name="Sage 50cloud",
                description="Desktop accounting software with cloud capabilities",
                pricing_tier="Small to Medium Business",
                key_features=[
                    "General ledger",
                    "Accounts payable",
                    "Accounts receivable",
                    "Inventory management",
                    "Microsoft 365 integration"
                ],
                pros=[
                    "Strong accounting features",
                    "Industry-specific versions",
                    "Hybrid cloud-desktop approach",
                    "Good audit trails"
                ],
                cons=[
                    "Less modern interface",
                    "Desktop software with cloud add-ons",
                    "More expensive than some cloud-only options",
                    "Can be complex for new users"
                ],
                compliance_support=["GAAP compliance"],
                suitable_for=[
                    "Small to medium businesses",
                    "Businesses transitioning from desktop to cloud",
                    "Organizations with more complex accounting needs",
                    "Manufacturing and distribution businesses"
                ]
            )]
    
    def _generate_implementation_considerations(
        self,
        business_type: str,
        integration_requirements: Optional[List[str]]
    ) -> List[str]:
        """Generate implementation considerations.
        
        Args:
            business_type: Type of business
            integration_requirements: Integration requirements
            
        Returns:
            List of implementation considerations
        """
        considerations = [
            "Develop a clear implementation timeline with defined milestones",
            "Ensure proper staff training before going live with the new system",
            "Run parallel systems during the transition period to validate data accuracy",
            "Establish proper user permissions and access controls from the beginning",
            "Document all configuration decisions and customizations"
        ]
        
        # Add business-type specific considerations
        if "enterprise" in business_type.lower():
            considerations.extend([
                "Consider a phased implementation approach across departments or subsidiaries",
                "Allocate resources for potential integration challenges with legacy systems",
                "Establish a formal change management process to address stakeholder concerns",
                "Develop a data migration strategy for historical financial records"
            ])
        
        # Add integration-specific considerations
        if integration_requirements:
            considerations.append("Test all system integrations thoroughly before going live")
            considerations.append("Document API and integration points for future reference")
            
            if any("crm" in req.lower() for req in integration_requirements):
                considerations.append("Ensure customer data syncs properly between CRM and accounting systems")
            
            if any("ecommerce" in req.lower() for req in integration_requirements):
                considerations.append("Verify that sales tax calculations are consistent across e-commerce and accounting platforms")
            
            if any("payroll" in req.lower() for req in integration_requirements):
                considerations.append("Validate that payroll expense classifications match your chart of accounts")
        
        return considerations
    
    def _generate_cost_comparison(
        self,
        software_names: List[str],
        user_count: int
    ) -> Dict[str, Any]:
        """Generate cost comparison information.
        
        Args:
            software_names: Names of software to compare
            user_count: Number of users
            
        Returns:
            Cost comparison dictionary
        """
        # This would use current pricing in a real implementation
        # For demonstration, we'll return estimated ranges
        
        # Base pricing (simplified)
        pricing = {
            "QuickBooks Online": {"small_tier": 25, "medium_tier": 40, "enterprise_tier": 75},
            "Xero": {"small_tier": 20, "medium_tier": 35, "enterprise_tier": 65},
            "Wave": {"small_tier": 0, "medium_tier": 20, "enterprise_tier": None},
            "FreshBooks": {"small_tier": 15, "medium_tier": 25, "enterprise_tier": 50},
            "SAP S/4HANA Finance": {"small_tier": None, "medium_tier": None, "enterprise_tier": 350},
            "Oracle NetSuite": {"small_tier": None, "medium_tier": 120, "enterprise_tier": 250},
            "Microsoft Dynamics 365": {"small_tier": None, "medium_tier": 100, "enterprise_tier": 200},
            "Sage Intacct": {"small_tier": None, "medium_tier": 150, "enterprise_tier": 275},
            "QuickBooks Nonprofit": {"small_tier": 20, "medium_tier": 35, "enterprise_tier": None},
            "Aplos": {"small_tier": 30, "medium_tier": 45, "enterprise_tier": None},
            "Fund E-Z": {"small_tier": 40, "medium_tier": 65, "enterprise_tier": None},
            "Blackbaud Financial Edge": {"small_tier": None, "medium_tier": 120, "enterprise_tier": 250},
            "Sage 50cloud": {"small_tier": 35, "medium_tier": 65, "enterprise_tier": 125}
        }
        
        # Calculate average prices for the requested software
        small_prices = [pricing.get(name, {}).get("small_tier", 0) for name in software_names]
        small_prices = [p for p in small_prices if p is not None]
        
        medium_prices = [pricing.get(name, {}).get("medium_tier", 0) for name in software_names]
        medium_prices = [p for p in medium_prices if p is not None]
        
        enterprise_prices = [pricing.get(name, {}).get("enterprise_tier", 0) for name in software_names]
        enterprise_prices = [p for p in enterprise_prices if p is not None]
        
        # Calculate averages, handling empty lists
        avg_small = sum(small_prices) / len(small_prices) if small_prices else 0
        avg_medium = sum(medium_prices) / len(medium_prices) if medium_prices else 0
        avg_enterprise = sum(enterprise_prices) / len(enterprise_prices) if enterprise_prices else 0
        
        # Return the cost comparison
        return {
            "small_tier": round(avg_small),
            "medium_tier": round(avg_medium),
            "enterprise_tier": round(avg_enterprise),
            "estimated_annual_cost": {
                "small_tier": round(avg_small * 12 * user_count),
                "medium_tier": round(avg_medium * 12 * user_count),
                "enterprise_tier": round(avg_enterprise * 12 * user_count)
            },
            "notes": [
                "Prices are estimates and may vary based on current promotions",
                "Additional costs may apply for implementation, training, and add-ons",
                "Enterprise solutions typically require custom pricing quotes",
                "Consider the total cost of ownership, including implementation and training"
            ]
        }


#
# Spreadsheet Tool
#

# Create the Spreadsheet Analysis Input Schema
SpreadsheetAnalysisInputSchema = create_tool_input_model(
    "SpreadsheetAnalysisInput",
    {
        "spreadsheet_type": (str, Field(description="Type of spreadsheet (e.g., financial model, budget, forecast)")),
        "purpose": (str, Field(description="Intended purpose of the spreadsheet")),
        "structure_review": (bool, Field(description="Whether to review spreadsheet structure and organization")),
        "formula_analysis": (bool, Field(description="Whether to analyze formulas for errors and best practices")),
        "data_validation": (bool, Field(description="Whether to check data validation and integrity")),
        "compliance_check": (Optional[List[str]], Field(None, description="Specific compliance standards to check against (e.g., GAAP, IFRS)")),
        "risk_assessment": (bool, Field(description="Whether to assess risks in the financial model"))
    },
    """Input schema for spreadsheet analysis tool."""
)


class SpreadsheetRisk(BaseModel):
    """Identified risk in a spreadsheet."""
    category: str
    severity: str
    description: str
    impact: str
    mitigation: str


class SpreadsheetBestPractice(BaseModel):
    """Best practice recommendation for spreadsheets."""
    category: str
    description: str
    implementation: str
    benefits: List[str]


class SpreadsheetAnalysisResult(BaseModel):
    """Spreadsheet analysis result."""
    structure_recommendations: List[str]
    formula_recommendations: List[str]
    data_validation_findings: List[str]
    identified_risks: List[SpreadsheetRisk]
    best_practices: List[SpreadsheetBestPractice]
    compliance_notes: Dict[str, List[str]]
    disclaimer: str


class SpreadsheetTool(StandardsCompliantTool[SpreadsheetAnalysisInputSchema, SpreadsheetAnalysisResult]):
    """A standards-compliant tool for analyzing financial spreadsheets."""
    
    def __init__(self):
        """Initialize the spreadsheet analysis tool."""
        super().__init__(
            name="spreadsheet_analysis",
            description="Analyzes financial spreadsheets for formula accuracy, structural integrity, and compliance with accounting standards",
            input_schema=SpreadsheetAnalysisInputSchema,
            supported_standards=[
                "GAAP",
                "IFRS",
                "AICPA_CODE_OF_ETHICS"
            ],
            domain="Accounting",
            metadata=ToolMetadata(
                title="Financial Spreadsheet Analysis Tool",
                read_only=True,
                destructive=False,
                idempotent=True,
                open_world=False,
                description="Standards-compliant financial spreadsheet analysis"
            )
        )
    
    async def execute(self, args: SpreadsheetAnalysisInputSchema, session_context: Optional[Dict[str, Any]] = None) -> SpreadsheetAnalysisResult:
        """Execute the spreadsheet analysis.
        
        Args:
            args: Validated input arguments
            session_context: Optional session context
            
        Returns:
            Spreadsheet analysis result
        """
        print(f"Analyzing {args.spreadsheet_type} spreadsheet for {args.purpose}")
        
        # Structure recommendations
        structure_recommendations = self._generate_structure_recommendations(
            args.spreadsheet_type, 
            args.purpose
        ) if args.structure_review else []
        
        # Formula recommendations
        formula_recommendations = self._generate_formula_recommendations(
            args.spreadsheet_type
        ) if args.formula_analysis else []
        
        # Data validation findings
        data_validation_findings = self._generate_data_validation_findings(
            args.spreadsheet_type,
            args.purpose
        ) if args.data_validation else []
        
        # Identified risks
        identified_risks = self._generate_risk_assessment(
            args.spreadsheet_type,
            args.purpose
        ) if args.risk_assessment else []
        
        # Best practices
        best_practices = self._generate_best_practices(
            args.spreadsheet_type,
            args.purpose
        )
        
        # Compliance notes
        compliance_notes = self._generate_compliance_notes(
            args.compliance_check,
            args.spreadsheet_type
        )
        
        # Generate standard disclaimer
        disclaimer = (
            "This analysis is provided for informational purposes only and should not be considered a comprehensive audit "
            "of your financial spreadsheets. The recommendations are based on general best practices and may not address all "
            "specific requirements of your organization. Professional judgment should be exercised when implementing any changes. "
            "For a complete assessment, consult with a qualified accounting professional who can review your actual spreadsheets."
        )
        
        # Prepare result
        result = SpreadsheetAnalysisResult(
            structure_recommendations=structure_recommendations,
            formula_recommendations=formula_recommendations,
            data_validation_findings=data_validation_findings,
            identified_risks=identified_risks,
            best_practices=best_practices,
            compliance_notes=compliance_notes,
            disclaimer=disclaimer
        )
        
        return result
    
    def format_result(self, result: SpreadsheetAnalysisResult) -> List[ContentPart]:
        """Format the result for display.
        
        Args:
            result: Spreadsheet analysis result
            
        Returns:
            List of content parts
        """
        # Create a data part with the full result
        data_part = ContentPart(
            type=ContentPart.ContentType.DATA,
            content=result.model_dump()
        )
        
        # Format risks for text display
        risks_text = "\n\n".join([
            f"### {risk.category} (Severity: {risk.severity})\n"
            f"**Description:** {risk.description}\n"
            f"**Impact:** {risk.impact}\n"
            f"**Mitigation:** {risk.mitigation}"
            for risk in result.identified_risks
        ]) if result.identified_risks else "No specific risks identified."
        
        # Format compliance notes
        compliance_text = ""
        for standard, notes in result.compliance_notes.items():
            compliance_text += f"### {standard}\n"
            for note in notes:
                compliance_text += f"- {note}\n"
        
        # Create a text summary
        text_summary = f"""
## Financial Spreadsheet Analysis

### Structure Recommendations
{chr(10).join([f"- {rec}" for rec in result.structure_recommendations]) if result.structure_recommendations else "No structure recommendations provided."}

### Formula Recommendations
{chr(10).join([f"- {rec}" for rec in result.formula_recommendations]) if result.formula_recommendations else "No formula recommendations provided."}

### Data Validation Findings
{chr(10).join([f"- {finding}" for finding in result.data_validation_findings]) if result.data_validation_findings else "No data validation review performed."}

### Risk Assessment
{risks_text}

### Compliance Notes
{compliance_text}

### Best Practices
{chr(10).join([f"- {practice.description}" for practice in result.best_practices])}

### Disclaimer
{result.disclaimer}
        """.strip()
        
        text_part = ContentPart(
            type=ContentPart.ContentType.TEXT,
            content=text_summary
        )
        
        return [data_part, text_part]
    
    def _generate_structure_recommendations(self, spreadsheet_type: str, purpose: str) -> List[str]:
        """Generate structure recommendations.
        
        Args:
            spreadsheet_type: Type of spreadsheet
            purpose: Purpose of the spreadsheet
            
        Returns:
            List of structure recommendations
        """
        common_recommendations = [
            "Separate input assumptions from calculations and outputs in distinct sections or worksheets",
            "Use consistent formatting to distinguish inputs, calculations, and outputs (e.g., blue for inputs, black for formulas)",
            "Include a 'cover' or 'dashboard' sheet that summarizes key results and provides navigation",
            "Create a dedicated sheet for documentation that explains the purpose, methodology, and key assumptions",
            "Use named ranges for important variables to improve formula readability and maintenance"
        ]
        
        specific_recommendations = []
        
        if "financial model" in spreadsheet_type.lower():
            specific_recommendations = [
                "Structure the model with a clear time series (columns) and line items (rows) convention",
                "Include separate modules for income statement, balance sheet, and cash flow statement",
                "Ensure proper linkage between financial statements (e.g., net income flowing to retained earnings)",
                "Include a separate sheet for sensitivity analysis and scenarios",
                "Create a dedicated assumptions sheet with clearly documented inputs"
            ]
        elif "budget" in spreadsheet_type.lower():
            specific_recommendations = [
                "Organize by department or cost center to facilitate accountability",
                "Include both monthly and annual views with appropriate subtotals",
                "Add variance columns/sheets to compare actual vs. budget figures",
                "Include prior year comparisons for context",
                "Create a sheet for budget allocation methodologies and rationales"
            ]
        elif "forecast" in spreadsheet_type.lower():
            specific_recommendations = [
                "Include both historical data and forecast periods for context and trend analysis",
                "Clearly indicate which cells contain historical data versus projections",
                "Include multiple scenario sheets (e.g., base case, optimistic, pessimistic)",
                "Create a dedicated assumptions sheet that drives the forecast",
                "Include a variance analysis comparing previous forecasts to actuals"
            ]
        
        # Combine and return recommendations
        return common_recommendations + specific_recommendations
    
    def _generate_formula_recommendations(self, spreadsheet_type: str) -> List[str]:
        """Generate formula recommendations.
        
        Args:
            spreadsheet_type: Type of spreadsheet
            
        Returns:
            List of formula recommendations
        """
        common_recommendations = [
            "Break complex calculations into smaller, more manageable steps",
            "Use named ranges instead of cell references to improve readability",
            "Avoid hardcoded values within formulas; use input cells instead",
            "Use structured references in tables (e.g., Table1[Column1]) for clarity",
            "Implement error handling with IFERROR or IFNA functions where appropriate",
            "Use data validation to prevent invalid entries in input cells",
            "Avoid circular references in formulas unless absolutely necessary",
            "Use absolute references ($A$1) consistently when copying formulas",
            "Document complex formulas with comments explaining the methodology"
        ]
        
        specific_recommendations = []
        
        if "financial model" in spreadsheet_type.lower():
            specific_recommendations = [
                "Ensure balance sheet balances (Assets = Liabilities + Equity) with a check row",
                "Verify that cash flow calculations properly account for all cash movements",
                "Use consistent sign conventions (e.g., expenses as negative or positive)",
                "Implement circular reference handling properly for financial statements with interconnected elements",
                "Use proper time-value-of-money functions (NPV, IRR, XIRR) for investment analyses"
            ]
        elif "budget" in spreadsheet_type.lower():
            specific_recommendations = [
                "Use SUM functions with explicit ranges rather than relying on adjacent cell references",
                "Implement variance calculations with both absolute and percentage differences",
                "Use SUMIFS or SUMPRODUCT for complex budget allocations across departments",
                "Create running totals for year-to-date budget vs. actual comparisons",
                "Use conditional formatting to highlight significant variances"
            ]
        
        # Combine and return recommendations
        return common_recommendations + specific_recommendations
    
    def _generate_data_validation_findings(self, spreadsheet_type: str, purpose: str) -> List[str]:
        """Generate data validation findings.
        
        Args:
            spreadsheet_type: Type of spreadsheet
            purpose: Purpose of the spreadsheet
            
        Returns:
            List of data validation findings
        """
        common_findings = [
            "Implement dropdown lists for categorical inputs to ensure consistency",
            "Add validation rules to prevent negative values where inappropriate (e.g., quantity fields)",
            "Set up date validations to ensure proper date sequencing and formatting",
            "Use validation to enforce consistent units (e.g., thousands, millions) throughout the model",
            "Create checksum formulas to verify that subtotals add up to totals",
            "Add validation rules for percentage inputs to ensure they're within reasonable ranges"
        ]
        
        specific_findings = []
        
        if "financial model" in spreadsheet_type.lower():
            specific_findings = [
                "Implement balance sheet checks to ensure assets equal liabilities plus equity",
                "Add cash flow reconciliation checks to verify beginning + changes = ending cash",
                "Create income statement validation to ensure subtotals are correctly calculated",
                "Verify that depreciation schedules properly account for asset additions and retirements",
                "Add cross-statement validation checks (e.g., net income flows correctly to balance sheet)"
            ]
        elif "budget" in spreadsheet_type.lower():
            specific_findings = [
                "Create validation to ensure budget allocations don't exceed total available budget",
                "Add rules to flag unusually large variances between budget periods",
                "Implement checks to ensure budget categories reconcile to the master budget",
                "Verify that departmental budgets sum to the correct organizational total",
                "Add validation for cost allocation methodologies to ensure they sum to 100%"
            ]
        
        # Combine and return findings
        return common_findings + specific_findings
    
    def _generate_risk_assessment(self, spreadsheet_type: str, purpose: str) -> List[SpreadsheetRisk]:
        """Generate risk assessment.
        
        Args:
            spreadsheet_type: Type of spreadsheet
            purpose: Purpose of the spreadsheet
            
        Returns:
            List of identified risks
        """
        risks = [
            SpreadsheetRisk(
                category="Formula Errors",
                severity="High",
                description="Complex, nested formulas that are difficult to audit and maintain",
                impact="Calculation errors that could lead to incorrect financial decisions",
                mitigation="Break complex formulas into simpler steps with intermediate calculations"
            ),
            SpreadsheetRisk(
                category="Versioning",
                severity="Medium",
                description="Lack of proper version control leading to multiple conflicting versions",
                impact="Using outdated or incorrect data for decision-making",
                mitigation="Implement a formal version control system with clear naming conventions and change logs"
            ),
            SpreadsheetRisk(
                category="Documentation",
                severity="Medium",
                description="Insufficient documentation of assumptions, methodologies, and data sources",
                impact="Inability to understand or validate the model, especially when used by others",
                mitigation="Create a dedicated documentation sheet with comprehensive explanations of all key elements"
            ),
            SpreadsheetRisk(
                category="Hardcoded Values",
                severity="High",
                description="Hardcoded values embedded within formulas",
                impact="Difficult to update and audit; potential for inconsistent assumptions",
                mitigation="Move all assumptions to a dedicated inputs section and reference them in formulas"
            )
        ]
        
        # Add specific risks based on spreadsheet type
        if "financial model" in spreadsheet_type.lower():
            risks.append(SpreadsheetRisk(
                category="Circular References",
                severity="High",
                description="Unintentional circular references in financial statement calculations",
                impact="Excel may not converge on the correct answer, leading to incorrect calculations",
                mitigation="Restructure the model to eliminate unnecessary circular references or properly manage them with iteration settings"
            ))
            
            risks.append(SpreadsheetRisk(
                category="Financial Statement Linkage",
                severity="Critical",
                description="Improper linkage between financial statements",
                impact="Inconsistent financial statements that don't properly flow from one to another",
                mitigation="Implement validation checks to ensure proper flow from income statement to balance sheet to cash flow statement"
            ))
        
        elif "forecast" in spreadsheet_type.lower():
            risks.append(SpreadsheetRisk(
                category="Growth Assumptions",
                severity="High",
                description="Unrealistic or inconsistent growth assumptions",
                impact="Overly optimistic forecasts leading to poor business decisions",
                mitigation="Document rationale for growth assumptions and compare to historical performance and industry benchmarks"
            ))
            
            risks.append(SpreadsheetRisk(
                category="Sensitivity Analysis",
                severity="Medium",
                description="Inadequate sensitivity analysis for key variables",
                impact="Failure to understand how forecast results could change under different scenarios",
                mitigation="Implement robust scenario and sensitivity analysis for all key input variables"
            ))
        
        return risks
    
    def _generate_best_practices(self, spreadsheet_type: str, purpose: str) -> List[SpreadsheetBestPractice]:
        """Generate best practices.
        
        Args:
            spreadsheet_type: Type of spreadsheet
            purpose: Purpose of the spreadsheet
            
        Returns:
            List of best practices
        """
        best_practices = [
            SpreadsheetBestPractice(
                category="Structure",
                description="Use a consistent color scheme for different types of cells",
                implementation="Blue for inputs, black for calculations, green for outputs/links to other sheets",
                benefits=[
                    "Improves visual navigation",
                    "Makes it clear which cells users should modify",
                    "Reduces risk of inadvertently changing formula cells"
                ]
            ),
            SpreadsheetBestPractice(
                category="Documentation",
                description="Include a comprehensive documentation sheet",
                implementation="Create a dedicated sheet explaining purpose, structure, key assumptions, and update history",
                benefits=[
                    "Ensures continuity when spreadsheet changes hands",
                    "Provides context for users and reviewers",
                    "Serves as a reference for future updates"
                ]
            ),
            SpreadsheetBestPractice(
                category="Formulas",
                description="Use named ranges for important variables",
                implementation="Define named ranges for key inputs and use them in formulas instead of cell references",
                benefits=[
                    "Improves formula readability",
                    "Makes formulas more maintainable",
                    "Reduces the risk of incorrect cell references when formulas are copied"
                ]
            ),
            SpreadsheetBestPractice(
                category="Review",
                description="Implement a formal review process",
                implementation="Have a second person review all formulas and structure before finalization",
                benefits=[
                    "Identifies errors that the creator might miss",
                    "Ensures the spreadsheet is understandable by others",
                    "Improves overall quality and reliability"
                ]
            )
        ]
        
        # Add specific best practices based on spreadsheet type
        if "financial model" in spreadsheet_type.lower():
            best_practices.append(SpreadsheetBestPractice(
                category="Modeling",
                description="Create a single source of truth for all assumptions",
                implementation="Dedicate an assumptions sheet where all input variables are defined once and referenced elsewhere",
                benefits=[
                    "Ensures consistency across the model",
                    "Makes scenario analysis easier",
                    "Simplifies updates to assumptions"
                ]
            ))
            
            best_practices.append(SpreadsheetBestPractice(
                category="Validation",
                description="Include cross-statement validation checks",
                implementation="Add formulas that verify mathematical relationships between financial statements",
                benefits=[
                    "Catches errors in statement linkages",
                    "Ensures financial statement integrity",
                    "Builds confidence in model accuracy"
                ]
            ))
        
        return best_practices
    
    def _generate_compliance_notes(self, compliance_check: Optional[List[str]], spreadsheet_type: str) -> Dict[str, List[str]]:
        """Generate compliance notes.
        
        Args:
            compliance_check: List of compliance standards to check against
            spreadsheet_type: Type of spreadsheet
            
        Returns:
            Dictionary of compliance notes by standard
        """
        compliance_notes = {}
        
        if not compliance_check:
            # Return notes for common standards if none specified
            compliance_check = ["GAAP", "IFRS"]
        
        if "GAAP" in compliance_check:
            gaap_notes = [
                "Ensure proper revenue recognition timing based on GAAP principles",
                "Follow accrual accounting principles consistently throughout the spreadsheet",
                "Apply consistent inventory valuation methods (FIFO, LIFO, weighted average)",
                "Properly classify expenses between operating and non-operating items",
                "Ensure depreciation methods are applied consistently and in accordance with policy"
            ]
            
            if "financial model" in spreadsheet_type.lower():
                gaap_notes.append("Verify that financial statement presentation follows GAAP classification requirements")
                gaap_notes.append("Ensure proper handling of deferred tax assets and liabilities")
            
            compliance_notes["GAAP"] = gaap_notes
        
        if "IFRS" in compliance_check:
            ifrs_notes = [
                "Apply appropriate recognition criteria for assets and liabilities under IFRS",
                "Follow IFRS measurement principles for fair value where applicable",
                "Ensure proper treatment of lease calculations per IFRS 16",
                "Apply appropriate revenue recognition steps according to IFRS 15",
                "Consider IFRS requirements for financial instrument classification"
            ]
            
            if "financial model" in spreadsheet_type.lower():
                ifrs_notes.append("Verify statement of financial position format complies with IFRS presentation requirements")
                ifrs_notes.append("Ensure proper handling of provisions and contingent liabilities per IAS 37")
            
            compliance_notes["IFRS"] = ifrs_notes
        
        if "SOX" in compliance_check:
            sox_notes = [
                "Implement appropriate cell protection and access controls for key formulas",
                "Maintain versioning and change management documentation",
                "Include clear audit trails for all significant changes",
                "Establish review and approval workflows for spreadsheet modifications",
                "Implement validation checks for critical calculations"
            ]
            
            compliance_notes["Sarbanes-Oxley (SOX)"] = sox_notes
        
        return compliance_notes


# Add these helper methods for the AccountingSoftwareTool class
    def _calculate_income_statement(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate income statement from transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Income statement dictionary
        """
        # Initialize totals
        total_revenue = 0
        total_expenses = 0
        breakdown_by_category = {}
        
        # Process each transaction
        for transaction in transactions:
            category = transaction.get("category", "Uncategorized")
            amount = transaction.get("amount", 0)
            transaction_type = transaction.get("type", "expense")
            
            # Initialize category in breakdown if not exists
            if category not in breakdown_by_category:
                breakdown_by_category[category] = 0
            
            # Add to totals based on transaction type
            if transaction_type == "income":
                total_revenue += amount
                breakdown_by_category[category] += amount
            elif transaction_type == "expense":
                total_expenses += amount
                # Store expenses as negative values in breakdown
                breakdown_by_category[category] -= amount
        
        # Calculate net income
        net_income = total_revenue - total_expenses
        
        return {
            "totalRevenue": total_revenue,
            "totalExpenses": total_expenses,
            "netIncome": net_income,
            "breakdownByCategory": breakdown_by_category
        }
    
    def _calculate_balance_sheet(self, accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate balance sheet from accounts.
        
        Args:
            accounts: List of account dictionaries
            
        Returns:
            Balance sheet dictionary
        """
        # Initialize totals
        total_assets = 0
        total_liabilities = 0
        total_equity = 0
        current_assets = 0
        current_liabilities = 0
        
        # Process each account
        for account in accounts:
            account_type = account.get("type", "")
            balance = account.get("balance", 0)
            
            if account_type == "asset":
                total_assets += balance
                if account.get("is_current", True):  # Default to current if not specified
                    current_assets += balance
            elif account_type == "liability":
                total_liabilities += balance
                if account.get("is_current", True):  # Default to current if not specified
                    current_liabilities += balance
            elif account_type == "equity":
                total_equity += balance
        
        # Calculate current ratio (if possible)
        current_ratio = current_assets / current_liabilities if current_liabilities > 0 else None
        
        return {
            "totalAssets": total_assets,
            "totalLiabilities": total_liabilities,
            "totalEquity": total_equity,
            "currentRatio": current_ratio
        }
    
    def _calculate_cash_flow_statement(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate cash flow statement from transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Cash flow statement dictionary
        """
        # Initialize cash flows
        operating_cash_flow = 0
        investing_cash_flow = 0
        financing_cash_flow = 0
        
        # Process each transaction
        for transaction in transactions:
            amount = transaction.get("amount", 0)
            category = transaction.get("category", "").lower()
            transaction_type = transaction.get("type", "expense")
            
            # Categorize cash flows (simplified approach)
            if category in ["revenue", "sales", "income", "expense", "operating"]:
                # Operating cash flows
                if transaction_type == "income":
                    operating_cash_flow += amount
                else:
                    operating_cash_flow -= amount
            elif category in ["asset", "equipment", "property", "investment"]:
                # Investing cash flows
                if transaction_type == "income":  # Sale of asset
                    investing_cash_flow += amount
                else:  # Purchase of asset
                    investing_cash_flow -= amount
            elif category in ["loan", "debt", "financing", "dividend", "capital"]:
                # Financing cash flows
                if transaction_type == "income":  # New loan or capital
                    financing_cash_flow += amount
                else:  # Loan payment or dividend
                    financing_cash_flow -= amount
            else:
                # Default to operating for uncategorized
                if transaction_type == "income":
                    operating_cash_flow += amount
                else:
                    operating_cash_flow -= amount
        
        # Calculate net cash change
        net_cash_change = operating_cash_flow + investing_cash_flow + financing_cash_flow
        
        return {
            "operatingCashFlow": operating_cash_flow,
            "investingCashFlow": investing_cash_flow,
            "financingCashFlow": financing_cash_flow,
            "netCashChange": net_cash_change
        }
    
    def _record_transactions(
        self, 
        args: AccountingSoftwareInputSchema,
        timestamp: str,
        disclaimer: str,
        audit_trail: Dict[str, Any]
    ) -> AccountingSoftwareResult:
        """Record transactions.
        
        Args:
            args: Validated input arguments
            timestamp: Operation timestamp
            disclaimer: Standard disclaimer
            audit_trail: Audit trail information
            
        Returns:
            Accounting software result
        """
        # Validate required data is present
        if not args.financial_data or not args.financial_data.get("transactions"):
            raise ValueError("Transaction data is required for recording transactions")
            
        transactions = args.financial_data.get("transactions", [])
        
        # Generate transaction IDs (in a real system, this would be done by the DB)
        transaction_ids = [f"TXN-{hash(timestamp)}-{i}" for i in range(len(transactions))]
        
        # Calculate summary by category
        category_summary = {}
        for transaction in transactions:
            category = transaction.get("category", "Uncategorized")
            amount = transaction.get("amount", 0)
            transaction_type = transaction.get("type", "expense")
            
            if category not in category_summary:
                category_summary[category] = 0
                
            if transaction_type == "income":
                category_summary[category] += amount
            else:  # expense or transfer
                category_summary[category] -= amount
        
        # Prepare operation details
        operation_details = {
            "operationType": "Transaction Recording",
            "timeProcessed": timestamp,
            "affectedRecords": len(transactions)
        }
        
        # Prepare transaction results
        transaction_results = {
            "transactionsProcessed": len(transactions),
            "transactionIds": transaction_ids,
            "batchId": f"BATCH-{hash(timestamp)}",
            "summary": category_summary
        }
        
        # Update audit trail
        audit_trail["details"] = f"Recorded {len(transactions)} transactions for {args.company_name}"
        
        return AccountingSoftwareResult(
            status="success",
            message=f"Successfully recorded {len(transactions)} transactions",
            operation_details=operation_details,
            transaction_results=transaction_results,
            audit_trail=audit_trail,
            disclaimer=disclaimer
        )
    
    def _reconcile_accounts(
        self, 
        args: AccountingSoftwareInputSchema,
        timestamp: str,
        disclaimer: str,
        audit_trail: Dict[str, Any]
    ) -> AccountingSoftwareResult:
        """Reconcile accounts.
        
        Args:
            args: Validated input arguments
            timestamp: Operation timestamp
            disclaimer: Standard disclaimer
            audit_trail: Audit trail information
            
        Returns:
            Accounting software result
        """
        # Validate required data is present
        if not args.financial_data or not args.financial_data.get("accounts"):
            raise ValueError("Account data is required for account reconciliation")
            
        accounts = args.financial_data.get("accounts", [])
        transactions = args.financial_data.get("transactions", [])
        
        # In a real system, this would match bank statements with recorded transactions
        # For this example, simulate a 95% match rate
        total_transactions = len(transactions)
        matched_transactions = int(total_transactions * 0.95)
        unmatched_transactions = total_transactions - matched_transactions
        
        # Generate adjustments if there are unmatched transactions
        adjustments = []
        if unmatched_transactions > 0 and len(accounts) > 0:
            # Example adjustments
            adjustments = [
                {
                    "account": accounts[0].get("name", "Unknown"),
                    "amount": 142.50,
                    "reason": "Missing transaction fee"
                }
            ]
            
            # Add a second adjustment if multiple accounts
            if len(accounts) > 1:
                adjustments.append({
                    "account": accounts[1].get("name", "Unknown"),
                    "amount": -56.75,
                    "reason": "Duplicate payment recorded"
                })
        
        # Prepare operation details
        operation_details = {
            "operationType": "Account Reconciliation",
            "timeProcessed": timestamp,
            "affectedRecords": len(accounts)
        }
        
        # Prepare reconciliation results
        reconciliation_results = {
            "accountsReconciled": len(accounts),
            "matchedTransactions": matched_transactions,
            "unmatchedTransactions": unmatched_transactions,
            "adjustments": adjustments
        }
        
        # Prepare generated files if there are adjustments
        generated_files = None
        if adjustments:
            file_timestamp = timestamp.replace(":", "-").split(".")[0]
            generated_files = [
                {
                    "fileName": f"reconciliation_report_{args.company_name}_{file_timestamp}.pdf",
                    "fileType": "application/pdf",
                    "fileUrl": f"https://example.com/reports/{args.company_name}/reconciliation_{file_timestamp}.pdf",
                    "generatedAt": timestamp
                }
            ]
        
        # Update audit trail
        audit_trail["details"] = f"Reconciled {len(accounts)} accounts for {args.company_name}"
        
        # Determine status based on unmatched transactions
        status = "success" if unmatched_transactions == 0 else "partial_success"
        message = "All accounts reconciled successfully" if unmatched_transactions == 0 else \
                 f"Reconciliation completed with {unmatched_transactions} unmatched transactions"
        
        return AccountingSoftwareResult(
            status=status,
            message=message,
            operation_details=operation_details,
            reconciliation_results=reconciliation_results,
            generated_files=generated_files,
            audit_trail=audit_trail,
            disclaimer=disclaimer
        )

    def requires_human_review(self, args: AccountingSoftwareInputSchema, result: AccountingSoftwareResult) -> bool:
        """Determine if human review is required for this operation.
        
        Args:
            args: The validated arguments
            result: The tool result
            
        Returns:
            Boolean indicating if human review is required
        """
        # Operations that always require review
        if hasattr(args, 'operation') and args.operation == "generate_financial_statements":
            # Official financial statements should be reviewed
            return True
            
        if result.status == "partial_success":
            # Any partially successful operations should be reviewed
            return True
            
        # Check for unmatched transactions in reconciliation
        if result.reconciliation_results and result.reconciliation_results.get("unmatchedTransactions", 0) > 0:
            return True
            
        # Check for large payroll processing
        if result.payroll_results and result.payroll_results.get("totalGrossPay", 0) > 50000:
            return True
            
        # Check for sensitive operations per standards validation
        from specialized_agents.standards_validation import StandardsValidator
        validator = StandardsValidator("accounting", ["GAAP", "IFRS", "SOX"])
        
        # Convert arguments to string representation for validation
        args_str = str(args.dict() if hasattr(args, "dict") else args)
        
        # Validate the operation against accounting standards
        validation_result = validator.validate_content(args_str)
        
        # If validation failed, require human review
        if not validation_result.valid:
            return True
            
        return False

def register_accounting_tools() -> List[str]:
    """Register all accounting tools and return their names.
    
    Returns:
        List of registered tool names
    """
    # In a production environment, this would register the tools with a tool registry
    tools = [
        AccountingSoftwareTool(),
        SpreadsheetTool()
    ]
    
    return [tool.name for tool in tools]