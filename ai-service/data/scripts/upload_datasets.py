import os
import argparse
from huggingface_hub import HfApi

def upload_datasets(repo_id, local_dir, commit_message):
    """
    Uploads the raw datasets from the local directory to the HuggingFace Hub.
    """
    print(f"Uploading datasets from {local_dir} to HuggingFace Hub (Repo: {repo_id})...")
    api = HfApi()
    
    try:
        api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)
        api.upload_large_folder(
            folder_path=local_dir,
            repo_id=repo_id,
            repo_type="dataset",
            ignore_patterns=[".cache/**", ".git/**"]
        )
        print(f"\n[SUCCESS] Datasets uploaded successfully to {repo_id}")
    except Exception as e:
        print(f"\n[ERROR] Failed to upload to HuggingFace: {e}")
        print("Please ensure you are logged in using `huggingface-cli login` and have write access.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload DLP Datasets to HuggingFace")
    parser.add_argument(
        "--repo", 
        type=str, 
        default="xorushi/secureflow-ai-datasets", 
        help="HuggingFace dataset repository ID (e.g., 'username/repo_name')"
    )
    parser.add_argument(
        "--in_dir", 
        type=str, 
        default="./ai-service/data", 
        help="Local directory containing the data to upload"
    )
    parser.add_argument(
        "--msg", 
        type=str, 
        default="Update datasets", 
        help="Commit message for the upload"
    )
    
    args = parser.parse_args()
    upload_datasets(args.repo, args.in_dir, args.msg)
