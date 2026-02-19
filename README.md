# Confluent Cloud Cost Analysis Tool

This tool analyzes Kafka (LKC) consumption in Confluent Cloud over a specified period and generates a CSV report with network transfer data.

## Quick Start

**Run the tool (recommended):**
```bash
./confluent_cost_analysis.sh
```

The script will:
1. Check and install Python dependencies automatically
2. Prompt you for all required information
3. Generate a CSV file with the analysis results

## What the Tool Prompts For

- **Confluent Cloud API Key**: Your org-level API key
- **Confluent Cloud API Secret**: Your org-level API secret  
- **Cluster ID**: The LKC cluster ID to analyze
- **Reference Date**: Optional date (YYYY-MM-DD), defaults to today
- **Number of Months**: How many months to analyze backwards, defaults to 1

## How It Works

- **Analysis Period**: Analyzes the specified number of months **before** the reference date
- **Default Behavior**: If no reference date is provided, analyzes the last month from today
- **Output**: Generates a CSV with monthly network transfer data

## Output CSV Columns

- `Month`: Month in YYYY-MM format
- `GB_Write`: Gigabytes written
- `GB_Read`: Gigabytes read
- `TB_Write`: Terabytes written
- `TB_Read`: Terabytes read
- `TB_Total`: Total terabytes transferred

## Usage Examples

### Example 1: Analyze Last Month (Default)
```bash
./confluent_cost_analysis.sh
```
Prompts:
- API Key: [your key]
- API Secret: [your secret]
- Cluster ID: lkc-abc123
- Reference Date: [press Enter]
- Number of Months: [press Enter]

Result: `confluent_cost_analysis_lkc-abc123.csv`

### Example 2: Analyze 6 Months Before Specific Date
```bash
./confluent_cost_analysis.sh
```
Prompts:
- API Key: [your key]
- API Secret: [your secret]
- Cluster ID: lkc-abc123
- Reference Date: 2024-01-15
- Number of Months: 6

Result: `confluent_cost_analysis_lkc-abc123.csv`
(Analyzes July 2023 - January 2024)

## Files

- `confluent_cost_analysis.sh`: Main executable script (run this)
- `confluent_cost_analysis.py`: Python analysis engine
- `requirements.txt`: Python dependencies
- `README.md`: This documentation

## Requirements

- Python 3.x
- pip3 (Python package manager)
- Internet connection (for API calls)

**Note**: The shell script automatically checks for these requirements and installs Python dependencies.

## Security

- API credentials are entered interactively and are **not stored**
- No environment variables or configuration files are created
- Credentials are only used for the current analysis session

## Troubleshooting

### "Python 3 is not installed"
Install Python 3 from https://python.org or your system package manager

### "pip3 is not installed"  
Install pip3 using your system package manager

### API authentication errors
- Ensure you're using org-level API credentials
- Verify your API key and secret are correct
- Check that your Confluent Cloud account has billing access

## Advanced Usage

If you need to run the Python script directly (not recommended):
```bash
python3 confluent_cost_analysis.py > output.csv
```

However, using the shell script is recommended as it handles dependency installation and provides a better user experience.

