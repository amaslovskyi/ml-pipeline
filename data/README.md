# Data Directory Structure

This directory contains the data files for the MLOps pipeline.

## Directory Structure

```
data/
├── raw/          # Raw data files (original, unprocessed)
├── processed/    # Processed data files (cleaned, transformed)
└── interim/      # Intermediate data files (temporary processing)
```

## Usage

- **raw/**: Store original data files as they come from the source
- **processed/**: Store cleaned and transformed data ready for modeling
- **interim/**: Store temporary files during data processing

## DVC Tracking

All data directories are tracked by DVC for version control and remote storage.

## Data Versioning

Use DVC to track data changes:
```bash
dvc add data/raw/
dvc add data/processed/
dvc push  # Push to S3 remote
dvc pull  # Pull from S3 remote
``` 