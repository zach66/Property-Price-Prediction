#!/usr/bin/env bash


# Acquire data from S3
python3 run.py acquire --config=config/model.yaml --output=data/model/raw.csv

# Clean
python3 run.py clean --input=data/model/raw.csv --config=config/model.yaml --output=data/model/clean.csv

# Generate features
python3 run.py featurize --input=data/model/clean.csv --config=config/model.yaml --output=data/model/features.csv

# Train model, print metrics and output feature importance file
python3 run.py train --input=data/model/features.csv --config=config/model.yaml --output=data/model/model.pkl --output1=data/model/metric.txt