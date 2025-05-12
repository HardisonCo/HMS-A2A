#!/bin/bash
# Crohn's Disease Treatment System Demo Script
# This script runs the demonstration of the integrated Crohn's treatment system

# Set up colored output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "============================================================"
echo "    Crohn's Disease Treatment System - Interactive Demo     "
echo "============================================================"
echo -e "${NC}"

# Create demo data directory if it doesn't exist
if [ ! -d "demo_data" ]; then
    echo -e "${YELLOW}Creating demo data directory...${NC}"
    mkdir -p demo_data
fi

# Check prerequisites
echo -e "${GREEN}Checking system prerequisites...${NC}"

# Check Python
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version)
    echo -e "✅ $PY_VERSION found"
else
    echo -e "${RED}❌ Python 3 not found! This is required for the demo.${NC}"
    exit 1
fi

# Check Rust
if command -v rustc &>/dev/null; then
    RUST_VERSION=$(rustc --version)
    echo -e "✅ $RUST_VERSION found"
else
    echo -e "${YELLOW}⚠️ Rust not found. The demo will run in mock mode without actual Rust components.${NC}"
fi

# Check required Python packages
echo -e "${GREEN}Checking required Python packages...${NC}"
REQUIRED_PACKAGES=("numpy" "pandas" "matplotlib" "seaborn")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" &>/dev/null; then
        echo -e "✅ $package found"
    else
        echo -e "${YELLOW}⚠️ $package not found${NC}"
        MISSING_PACKAGES+=("$package")
    fi
done

# If there are missing packages, ask if the user wants to install them
if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    echo -e "${YELLOW}Some required packages are missing. Do you want to install them? (y/n)${NC}"
    read -r answer
    
    if [[ $answer =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Installing missing packages...${NC}"
        python3 -m pip install "${MISSING_PACKAGES[@]}"
    else
        echo -e "${YELLOW}Continuing without installing missing packages. The demo may not work correctly.${NC}"
    fi
fi

# Create sample patient data for the demo
echo -e "${GREEN}Creating sample patient data...${NC}"

cat > demo_data/patients.csv << EOF
patient_id,age,sex,ethnicity,weight,height,crohns_type,diagnosis_date,CDAI,SES_CD,fecal_calprotectin,CRP,ESR,NOD2,NOD2_zygosity,ATG16L1,IL23R,IL23R_zygosity,microbiome_diversity,F_prausnitzii,E_coli,treatment_history,extraintestinal_manifestations,comorbidities
P001,42,female,Caucasian,65.5,170.0,ileocolonic,2019-03-15,220,12,280,12.5,22,variant,heterozygous,normal,variant,heterozygous,0.65,0.15,0.4,"[{""medication"": ""Infliximab"", ""response"": ""partial"", ""start_date"": ""2019-05-01"", ""end_date"": ""2020-02-15"", ""adverse_events"": [""infusion reaction""]}]",arthritis,asthma
P002,38,male,Caucasian,78.3,178.0,colonic,2018-11-22,190,10,210,8.4,18,normal,NA,variant,normal,NA,0.72,0.23,0.35,"[{""medication"": ""Adalimumab"", ""response"": ""complete"", ""start_date"": ""2019-01-10"", ""end_date"": """", ""adverse_events"": []}]",erythema nodosum,"hypertension, anxiety"
P003,55,female,African,62.1,162.0,ileal,2017-06-08,250,15,340,18.2,32,variant,homozygous,variant,normal,NA,0.58,0.12,0.52,"[{""medication"": ""Infliximab"", ""response"": ""none"", ""start_date"": ""2017-08-15"", ""end_date"": ""2018-03-20"", ""adverse_events"": []}, {""medication"": ""Ustekinumab"", ""response"": ""partial"", ""start_date"": ""2018-05-10"", ""end_date"": """", ""adverse_events"": [""headache""]}]",arthritis;uveitis,diabetes
P004,29,male,Asian,70.2,175.0,ileocolonic,2020-02-17,180,8,180,5.2,15,normal,NA,normal,variant,heterozygous,0.78,0.28,0.3,"[{""medication"": ""Adalimumab"", ""response"": ""partial"", ""start_date"": ""2020-04-05"", ""end_date"": """", ""adverse_events"": [""injection site reaction""]}]","",allergic rhinitis
P005,48,female,Hispanic,58.7,158.0,perianal,2016-09-30,230,14,320,15.8,28,variant,heterozygous,normal,variant,heterozygous,0.62,0.18,0.45,"[{""medication"": ""Vedolizumab"", ""response"": ""none"", ""start_date"": ""2017-01-15"", ""end_date"": ""2017-12-22"", ""adverse_events"": []}, {""medication"": ""Ustekinumab"", ""response"": ""partial"", ""start_date"": ""2018-02-10"", ""end_date"": ""2019-11-05"", ""adverse_events"": []}, {""medication"": ""Infliximab"", ""response"": ""partial"", ""start_date"": ""2020-01-20"", ""end_date"": """", ""adverse_events"": [""infusion reaction"", ""headache""]}]",pyoderma gangrenosum,"depression, osteoporosis"
EOF

echo -e "✅ Created sample patient data at demo_data/patients.csv"

# Create output directory if it doesn't exist
mkdir -p demo_output

# Ask which demo to run
echo -e "${GREEN}Please select a demo to run:${NC}"
echo "1. Full Demo (all components)"
echo "2. Treatment Optimization Demo only"
echo "3. Adaptive Trial Demo only"
echo "4. Self-Healing Demo only"
echo "5. System Health Monitoring Demo only"
echo "0. Exit"

read -r choice

case $choice in
    1)
        echo -e "${GREEN}Running Full Demo...${NC}"
        python3 demo/run_demo.py
        ;;
    2)
        echo -e "${GREEN}Running Treatment Optimization Demo...${NC}"
        python3 demo/run_demo.py --treatment-only
        ;;
    3)
        echo -e "${GREEN}Running Adaptive Trial Demo...${NC}"
        python3 demo/run_demo.py --trial-only
        ;;
    4)
        echo -e "${GREEN}Running Self-Healing Demo...${NC}"
        python3 demo/run_demo.py --healing-only
        ;;
    5)
        echo -e "${GREEN}Running System Health Monitoring Demo...${NC}"
        python3 demo/run_demo.py --health-only
        ;;
    0)
        echo -e "${BLUE}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice! Exiting...${NC}"
        exit 1
        ;;
esac

# If the demo completed successfully, open the HTML reports if available
if [ -f "demo_output/trial/trial_report.html" ]; then
    echo -e "${GREEN}Demo completed successfully! Opening HTML report...${NC}"
    
    # Try to open the HTML report with the default browser
    if command -v xdg-open &>/dev/null; then
        xdg-open demo_output/trial/trial_report.html
    elif command -v open &>/dev/null; then
        open demo_output/trial/trial_report.html
    else
        echo -e "${YELLOW}Could not open HTML report automatically. Please open it manually at:${NC}"
        echo "demo_output/trial/trial_report.html"
    fi
else
    echo -e "${YELLOW}Demo completed, but no HTML report was generated.${NC}"
fi

# Print summary
echo -e "${BLUE}"
echo "============================================================"
echo "               Demo Execution Complete                      "
echo "============================================================"
echo -e "${NC}"
echo -e "${GREEN}Output files have been saved to:${NC}"
echo "demo_output/"
echo ""
echo -e "${BLUE}Thank you for exploring the Crohn's Disease Treatment System!${NC}"