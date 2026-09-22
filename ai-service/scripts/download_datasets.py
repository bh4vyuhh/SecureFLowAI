import os
import argparse
from huggingface_hub import snapshot_download

def download_datasets(repo_id, local_dir):
    """
    Downloads the entire dataset repository from HuggingFace Hub to the local directory.
    """
    print(f"Downloading datasets from HuggingFace Hub (Repo: {repo_id})...")
    os.makedirs(local_dir, exist_ok=True)
    
    try:
        snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        print(f"\n[SUCCESS] Datasets downloaded successfully to {local_dir}")
    except Exception as e:
        print(f"\n[ERROR] Failed to download from HuggingFace: {e}")
        print("Please ensure you are logged in using `huggingface-cli login` if the repo is private.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download DLP Datasets from HuggingFace")
    parser.add_argument(
        "--repo", 
        type=str, 
        default="xorushi/secureflow-ai-datasets", 
        help="HuggingFace dataset repository ID (e.g., 'username/repo_name')"
    )
    parser.add_argument(
        "--out_dir", 
        type=str, 
        default="./ai-service/data", 
        help="Local directory to download the data to"
    )
    
    args = parser.parse_args()
    download_datasets(args.repo, args.out_dir)
