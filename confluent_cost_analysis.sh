#!/bin/bash

# Confluent Cloud Cost Analysis Tool
# This script installs dependencies and runs the cost analysis tool
# Users should run this script instead of the Python file directly

echo "Confluent Cloud Cost Analysis Tool"
echo "================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Install requirements if needed
echo "Checking and installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --upgrade
else
    echo "Installing requests library..."
    pip3 install requests --upgrade
fi

echo ""
echo "Starting cost analysis..."
echo "========================"
echo ""

# Run the Python script with proper terminal handling
# Python script now handles CSV file creation directly
python3 -u confluent_cost_analysis.py

echo ""
echo "Analysis complete!"
echo "=================="
echo "Results saved to: confluent_cost_analysis_${CLUSTER_ID:-output}.csv"
echo "You can now open this CSV file in Excel or any spreadsheet application."
echo ""
echo "Note: Your API credentials were entered interactively and are not stored."
