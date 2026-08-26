"""
SecureFlow AI — Upload Local Raw Datasets to Your Personal Hugging Face Repository.

Uploads your entire local raw dataset directory (`ai-service/data/raw/`) or individual datasets
to your Hugging Face account.

Prerequisites:
  1. Install huggingface_hub: `pip install huggingface_hub`
  2. Log in with your Hugging Face token (with WRITE permissions):
     `huggingface-cli login`
     or pass `--token YOUR_HF_WRITE_TOKEN`

Usage:
  python upload_to_huggingface.py --repo-id <YOUR_USERNAME>/secureflow-ai-datasets
  python upload_to_huggingface.py --repo-id <YOUR_USERNAME>/secureflow-ai-datasets --private
"""

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent
RAW_DIR = DATA_DIR / "raw"


def main():
    parser = argparse.ArgumentParser(description="Upload SecureFlow AI Datasets to Hugging Face Hub")
    parser.add_argument(
        "--repo-id",
        type=str,
        required=True,
        help="Your Hugging Face repository ID (e.g., 'your-username/secureflow-ai-datasets')",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Hugging Face Write API Token (optional if already logged in via huggingface-cli login)",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create the Hugging Face repository as private (recommended if containing proprietary data)",
    )
    args = parser.parse_args()

    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        print("[ERROR] huggingface_hub is not installed. Please run: pip install huggingface_hub")
        sys.exit(1)

    api = HfApi(token=args.token)

    print("=" * 80)
    print(" SECUREFLOW AI — UPLOADING DATASETS TO HUGGING FACE")
    print("=" * 80)
    print(f"Target Hugging Face Repo : {args.repo_id}")
    print(f"Local Source Directory   : {RAW_DIR}")
    print(f"Visibility               : {'Private' if args.private else 'Public'}")
    print("-" * 80)

    # 1. Create or verify repo
    try:
        create_repo(
            repo_id=args.repo_id,
            repo_type="dataset",
            private=args.private,
            exist_ok=True,
            token=args.token,
        )
        print(f" -> [SUCCESS] Repository '{args.repo_id}' ready on Hugging Face.")
    except Exception as e:
        print(f" -> [INFO] Checking repository: {e}")

    # 2. Upload the raw folder
    print(f"\n -> Starting upload of all raw datasets to '{args.repo_id}'...")
    print("    (This will upload PDFs, JSONs, Parquets, and Arrow files with multi-threading)")
    
    try:
        future = api.upload_folder(
            folder_path=str(RAW_DIR),
            repo_id=args.repo_id,
            repo_type="dataset",
            token=args.token,
            ignore_patterns=[".gitkeep"],
        )
        print("\n" + "=" * 80)
        print(" [COMPLETE] ALL DATASETS UPLOADED SUCCESSFULLY TO HUGGING FACE!")
        print(f" Repository URL: https://huggingface.co/datasets/{args.repo_id}")
        print("=" * 80)
        print(f"\nTo download this dataset on any machine in the future, run:")
        print(f"  python download_raw_datasets.py --hf-repo {args.repo_id}")
    except Exception as e:
        print(f"\n[ERROR] Failed to upload datasets: {e}")
        print("\nTip: Make sure you have logged in with a token that has WRITE permissions:")
        print("     huggingface-cli login")


if __name__ == "__main__":
    main()
