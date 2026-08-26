"""
SecureFlow AI — Master End-to-End Dataset Reproduction & Model Training Pipeline.

Orchestrates the complete dataset reproduction lifecycle:
  Step 1: Ingests & validates all raw datasets (DISC, Medical PHI, RoBERTa PII, UM-DLP, Contextual, Enron, STARGATE).
  Step 2: Builds 4-tier document classification splits (70/15/15) and all benchmark suites.
  Step 3: Displays structured validation & schema showcase tables.
  Step 4: (Optional) Trains baseline 4-Tier Document Sensitivity Classifier.

Usage:
  python reproduce_all.py --all
  python reproduce_all.py --download-only
  python reproduce_all.py --process-only
  python reproduce_all.py --validate-only
  python reproduce_all.py --train-baseline
"""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PYTHON_EXE = sys.executable


def run_script(script_name: str, *args):
    script_path = SCRIPT_DIR / script_name
    cmd = [PYTHON_EXE, str(script_path)] + list(args)
    print(f"\n>>> Running: {script_name} {' '.join(args)}")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"[ERROR] Script {script_name} failed with exit code {res.returncode}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="SecureFlow AI — Master Dataset Reproduction Pipeline")
    parser.add_argument("--all", action="store_true", help="Run full pipeline: download -> process -> showcase -> train baseline")
    parser.add_argument("--download-only", action="store_true", help="Download and verify raw datasets only")
    parser.add_argument("--process-only", action="store_true", help="Process and convert datasets into splits and benchmarks")
    parser.add_argument("--validate-only", action="store_true", help="Run dataset schema & metadata presentation showcase")
    parser.add_argument("--train-baseline", action="store_true", help="Train baseline 4-tier document sensitivity classifier")
    args = parser.parse_args()

    # Default to full reproduction if no specific mode is given
    if not any([args.all, args.download_only, args.process_only, args.validate_only, args.train_baseline]):
        args.all = True

    print("=" * 90)
    print(" SECUREFLOW AI — COMPLETE DATASET REPRODUCTION PIPELINE".center(90))
    print("=" * 90)

    if args.download_only:
        run_script("download_raw_datasets.py", "--dataset", "all")
        return

    if args.process_only:
        run_script("organize_datasets.py", "--target", "all")
        return

    if args.validate_only:
        run_script("present_datasets.py")
        return

    if args.all or (not args.download_only and not args.process_only and not args.validate_only and not args.train_baseline):
        # Step 1: Download / Verify Raw Datasets
        print("\n[PHASE 1/4] Downloading & Verifying Raw Datasets...")
        run_script("download_raw_datasets.py", "--dataset", "all")

        # Step 2: Organize & Build Splits & Benchmarks
        print("\n[PHASE 2/4] Organizing Datasets & Building Splits...")
        run_script("organize_datasets.py", "--target", "all")

        # Step 3: Present Datasets & Validation Tables
        print("\n[PHASE 3/4] Generating Tabular Showcase & Validation Report...")
        run_script("present_datasets.py")

        # Step 4: Train Baseline Model
        print("\n[PHASE 4/4] Training Baseline Document Sensitivity Classifier...")
        run_script("train_classifier.py")

        print("\n" + "=" * 90)
        print(" [COMPLETE] ALL DATASETS REPRODUCED AND BASELINE CLASSIFIER TRAINED SUCCESSFULLY".center(90))
        print("=" * 90)
    elif args.train_baseline:
        run_script("train_classifier.py")


if __name__ == "__main__":
    main()
