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


def upload_individual_dataset(api, repo_id: str, subfolder_name: str, token: str = None):
    """Uploads a single raw subfolder directly to the corresponding path in the HF dataset repo."""
    local_subfolder = RAW_DIR / subfolder_name
    if not local_subfolder.exists():
        print(f" [SKIP] Local folder {local_subfolder} does not exist.")
        return False

    print(f"\n>>> Uploading dataset: '{subfolder_name}' -> HF repo '{repo_id}/{subfolder_name}'...")
    try:
        # Check if subfolder has many files (like stargate_pdfs)
        file_count = len(list(local_subfolder.glob("**/*")))
        if file_count > 500 and hasattr(api, "upload_large_folder"):
            print(f" -> Large folder detected ({file_count} files). Using upload_large_folder with batching...")
            api.upload_large_folder(
                repo_id=repo_id,
                folder_path=str(local_subfolder),
                repo_type="dataset",
                path_in_repo=subfolder_name,
                ignore_patterns=[".gitkeep"],
                num_workers=4,
            )
        else:
            api.upload_folder(
                folder_path=str(local_subfolder),
                path_in_repo=subfolder_name,
                repo_id=repo_id,
                repo_type="dataset",
                token=token,
                ignore_patterns=[".gitkeep"],
            )
        print(f" -> [SUCCESS] Uploaded '{subfolder_name}' successfully!")
        return True
    except Exception as e:
        print(f" -> [ERROR] Failed uploading '{subfolder_name}': {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Upload SecureFlow AI Datasets to Hugging Face Hub")
    parser.add_argument(
        "--repo-id",
        type=str,
        required=True,
        help="Your Hugging Face repository ID (e.g., 'your-username/secureflow-ai-datasets')",
    )
    parser.add_argument(
        "--dataset",
        choices=["all", "disc", "medical_phi", "roberta_pii_synth", "um_dlp_benchmark", "contextual_sensitive", "enron_emails", "stargate_pdfs"],
        default="all",
        help="Upload all datasets or a specific dataset subfolder (default: all)",
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
    print(f"Mode                     : Dataset '{args.dataset}'")
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
        print(f" -> [INFO] Repository status: {e}")

    # 2. Upload datasets modularly
    dataset_list = [
        "disc",
        "medical_phi",
        "roberta_pii_synth",
        "um_dlp_benchmark",
        "contextual_sensitive",
        "enron_emails",
        "stargate_pdfs",
    ]

    if args.dataset != "all":
        dataset_list = [args.dataset]

    results = {}
    for dname in dataset_list:
        results[dname] = upload_individual_dataset(api, args.repo_id, dname, token=args.token)

    print("\n" + "=" * 80)
    print(" UPLOAD SUMMARY")
    print("=" * 80)
    for dname, ok in results.items():
        status = "[DONE] Successfully Uploaded" if ok else "[FAILED / SKIPPED]"
        print(f" - {dname.ljust(25)} : {status}")

    print("=" * 80)
    print(f" Repository URL: https://huggingface.co/datasets/{args.repo_id}")
    print("=" * 80)
    print(f"\nTo download on any machine in the future, run:")
    print(f"  python download_raw_datasets.py --hf-repo {args.repo_id}")


if __name__ == "__main__":
    main()
