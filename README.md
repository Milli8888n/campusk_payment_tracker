# CampusK Payment Tracker

A comprehensive payment tracking and management system for campus-related services and contracts.

## Features

- **Contract Management**: Create and manage various types of contracts
- **Payment Tracking**: Monitor payment requests and status
- **Database Management**: Tools for database optimization and schema management
- **Sample Data Generation**: Utilities for creating mock data for testing
- **Vietnamese Language Support**: Number to words conversion in Vietnamese

## Project Structure

```
campusk_payment_tracker/
├── src/                    # Source code
├── templates_jinja/        # Jinja2 templates
├── generated_contracts/    # Generated contract files
├── instance/              # Instance-specific files
├── logs/                  # Log files
├── requirements.txt       # Python dependencies
└── *.py                  # Utility scripts
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Milli8888n/campusk_payment_tracker.git
cd campusk_payment_tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The project includes several utility scripts for different purposes:

- `check_database.py` - Database verification and health checks
- `check_flow.py` - Workflow validation
- `create_sample_data.py` - Generate sample data for testing
- `create_contracts.py` - Contract creation utilities
- `optimize_database.py` - Database optimization tools

## Requirements

See `requirements.txt` for the complete list of Python dependencies.

## License

This project is open source and available under the MIT License. 