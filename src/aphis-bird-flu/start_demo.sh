#!/bin/bash
# APHIS Bird Flu Tracking System Demo Launcher

# Set script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "==================================================="
echo "  APHIS Bird Flu Tracking System Demo Launcher"
echo "==================================================="
echo ""
echo "This script will run the APHIS Bird Flu Tracking System demonstration."
echo ""
echo "Options:"
echo "  1. Run complete demonstration"
echo "  2. Run adaptive sampling demo only"
echo "  3. Run outbreak detection demo only"
echo "  4. Run predictive modeling demo only"
echo "  5. Run notification system demo only"
echo "  6. Run visualization services demo only"
echo "  7. Run genetic analysis demo only"
echo "  q. Quit"
echo ""

read -p "Enter your choice (1-7, or q to quit): " choice

case $choice in
    1)
        echo "Running complete demonstration..."
        python3 "$SCRIPT_DIR/demo/demo_script.py" --all
        ;;
    2)
        echo "Running adaptive sampling demonstration..."
        python3 "$SCRIPT_DIR/demo/demo_script.py" --sampling
        ;;
    3)
        echo "Running outbreak detection demonstration..."
        python3 "$SCRIPT_DIR/demo/demo_script.py" --detection
        ;;
    4)
        echo "Running predictive modeling demonstration..."
        python3 "$SCRIPT_DIR/demo/demo_script.py" --prediction
        ;;
    5)
        echo "Running notification system demonstration..."
        python3 "$SCRIPT_DIR/demo/demo_script.py" --notification
        ;;
    6)
        echo "Running visualization services demonstration..."
        python3 "$SCRIPT_DIR/demo/demo_script.py" --visualization
        ;;
    7)
        echo "Running genetic analysis demonstration..."
        python3 "$SCRIPT_DIR/demo/demo_script.py" --genetic
        ;;
    q|Q)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac

echo ""
echo "Demonstration completed. Check the output directory for results:"
echo "$SCRIPT_DIR/demo/output"
echo ""
echo "Thank you for using the APHIS Bird Flu Tracking System demo!"