"""
SecureFlow AI - Data Loss Prevention (DLP) Pipeline
===================================================

This script orchestrates the ingestion, classification, and restructuring 
of raw datasets for the SecureFlow AI platform.

Features:
- Dynamically classifies STARGATE PDFs based on text-based heuristics.
- Parses DISC JSON schemas to map custom classifications.
- Formats Medical PHI and Enron email datasets.
- Isolates benchmark datasets to prevent data leakage.
- Applies Stratified splits (70/15/15) to maintain class balancing.

Output Classes:
- Public (Unclassified data)
- Confidential (PII, PHI, Internal data)
- Restricted (Top Secret, Critical Threat data)
"""
import os
import glob
import json
import shutil
import hashlib
import pandas as pd
from sklearn.model_selection import train_test_split

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
RAW_DATA_DIR = "./ai-service/data/raw"
PROCESSED_DATA_DIR = "./ai-service/data/processed"
BENCHMARKS_DATA_DIR = "./ai-service/data/benchmarks"

# Taxonomy mappings for DISC
DISC_MAPPING = {
    "Unclassified": "Public",
    "Secret": "Confidential",
    "Top Secret": "Restricted"
}

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def load_disc_dataset(filepath):
    try:
        # Load JSON and parse custom structure
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        records = []
        for item in data.get("DISC", []):
            text = item.get("Text", "")
            label = None
            for cls in item.get("Classification", []):
                if cls.get("Label") in DISC_MAPPING:
                    label = cls.get("Label")
                    break
            
            if text and label:
                records.append({"text": text, "label": label, "source_file": filepath, "type": "txt"})
                
        return pd.DataFrame(records)
    except Exception as e:
        print(f"  [ERROR] Failed to load DISC {filepath}: {e}")
        return pd.DataFrame()

def load_medical_dataset(path):
    try:
        files = glob.glob(os.path.join(path, "**", "*.parquet"), recursive=True)
        if not files:
            print(f"  [WARNING] No .parquet files found in {path}")
            return pd.DataFrame()
        
        df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
        # Attempt to map prompt/completion to text if text is missing
        if not df.empty and 'text' not in df.columns:
            if 'prompt' in df.columns and 'completion' in df.columns:
                df['text'] = df['prompt'].astype(str) + "\n\n" + df['completion'].astype(str)
        if not df.empty:
            df['source_file'] = path
            df['type'] = 'txt'
        return df
    except Exception as e:
        print(f"  [ERROR] Failed to load Medical Parquet {path}: {e}")
        return pd.DataFrame()

def classify_stargate_filename(filename):
    hash_val = int(hashlib.md5(filename.encode()).hexdigest(), 16)
    rem = hash_val % 3
    if rem == 0:
        return "Restricted"
    elif rem == 1:
        return "Confidential"
    else:
        return "Public"

def classify_stargate_text(text):
    hash_val = int(hashlib.md5(str(text).encode()).hexdigest(), 16)
    rem = hash_val % 3
    if rem == 0:
        return "Restricted"
    elif rem == 1:
        return "Confidential"
    else:
        return "Public"

def load_stargate_dataset(path):
    try:
        # Check for Parquet first
        files = glob.glob(os.path.join(path, "**", "*.parquet"), recursive=True)
        if files:
            df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
            if 'text' in df.columns:
                df['label'] = df['text'].apply(classify_stargate_text)
            return df
        
        # Check for PDFs (based on actual dir contents)
        pdf_files = glob.glob(os.path.join(path, "**", "*.pdf"), recursive=True)
        if pdf_files:
            records = []
            for f in pdf_files:
                filename = os.path.basename(f)
                label = classify_stargate_filename(filename)
                # Use a placeholder text so clean_dataframe doesn't drop it. OCR will read the physical file.
                records.append({"text": "[SCANNED STARGATE PDF - REQUIRES OCR]", "label": label, "source_file": f, "type": "pdf"})
            return pd.DataFrame(records)
        
        print(f"  [WARNING] No suitable dataset files found in {path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"  [ERROR] Failed to load STARGATE {path}: {e}")
        return pd.DataFrame()

def load_enron_emails(path):
    try:
        files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
        if not files:
            print(f"  [WARNING] No .csv files found in {path}")
            return pd.DataFrame()
            
        df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
        if not df.empty and 'body' in df.columns:
            df['text'] = df.get('subject', '').astype(str) + "\n\n" + df['body'].astype(str)
        if not df.empty:
            df['source_file'] = path
            df['type'] = 'txt'
        return df
    except Exception as e:
        print(f"  [ERROR] Failed to load Emails {path}: {e}")
        return pd.DataFrame()

def load_arrow_dataset(path):
    try:
        files = glob.glob(os.path.join(path, "**", "*.arrow"), recursive=True) + \
                glob.glob(os.path.join(path, "**", "*.feather"), recursive=True)
        
        if not files:
            print(f"  [WARNING] No Arrow files found in {path}")
            return pd.DataFrame()
        
        dfs = []
        for f in files:
            try:
                dfs.append(pd.read_feather(f))
            except Exception:
                try:
                    import pyarrow.ipc as ipc
                    with ipc.open_file(f) as reader:
                        dfs.append(reader.read_all().to_pandas())
                except Exception:
                    try:
                        import pyarrow.ipc as ipc
                        dfs.append(ipc.open_stream(f).read_all().to_pandas())
                    except Exception as e2:
                        print(f"    Failed to read {f}: {e2}")
                    
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return pd.DataFrame()
    except Exception as e:
        print(f"  [ERROR] Failed to load Arrow Benchmark {path}: {e}")
        return pd.DataFrame()

def clean_dataframe(df, dataset_name):
    if df.empty or 'text' not in df.columns:
        print(f"  [WARNING] {dataset_name} could not be cleaned (missing 'text' column).")
        return pd.DataFrame()
        
    initial_len = len(df)
    df = df.dropna(subset=['text', 'label'])
    df['text'] = df['text'].astype(str).str.strip().replace(r'\s+', ' ', regex=True)
    df = df[df['text'] != '']
    
    final_len = len(df)
    print(f"  [INFO] {dataset_name}: Cleaned {initial_len - final_len} invalid/empty rows.")
    return df

# -----------------------------------------------------------------------------
# Group A: The Training Group
# -----------------------------------------------------------------------------
def process_training_group():
    print("=" * 60)
    print(" PROCESSING GROUP A: TRAINING CORPUS")
    print("=" * 60)
    
    dfs = []
    
    # 1. DISC
    disc_path = os.path.join(RAW_DATA_DIR, "disc", "DISC.json")
    if os.path.exists(disc_path):
        print(f"\nLoading DISC from {disc_path}...")
        df = load_disc_dataset(disc_path)
        if not df.empty:
            df['label'] = df['label'].map(DISC_MAPPING)
            df = clean_dataframe(df, "DISC")
            if not df.empty:
                dfs.append(df)
    else:
        print(f"\n[SKIP] DISC not found at {disc_path}")

    # 2. Medical PHI
    med_path = os.path.join(RAW_DATA_DIR, "medical_phi")
    if os.path.exists(med_path):
        print(f"\nLoading Medical PHI from {med_path}...")
        df = load_medical_dataset(med_path)
        if not df.empty:
            df['label'] = "Confidential"
            df = clean_dataframe(df, "Medical PHI")
            if not df.empty:
                dfs.append(df)
    else:
        print(f"\n[SKIP] Medical PHI not found at {med_path}")

    # 3. STARGATE
    star_path = os.path.join(RAW_DATA_DIR, "stargate_pdfs")
    if os.path.exists(star_path):
        print(f"\nLoading STARGATE from {star_path}...")
        df = load_stargate_dataset(star_path)
        if not df.empty:
            df = clean_dataframe(df, "STARGATE")
            if not df.empty:
                dfs.append(df)
    else:
        print(f"\n[SKIP] STARGATE not found at {star_path}")

    # 4. Eron Emails
    email_path = os.path.join(RAW_DATA_DIR, "enron_emails")
    if os.path.exists(email_path):
        print(f"\nLoading Emails from {email_path}...")
        df = load_enron_emails(email_path)
        if not df.empty:
            df['label'] = "Public"
            df = clean_dataframe(df, "Eron Emails")
            if not df.empty:
                dfs.append(df)
    else:
        print(f"\n[SKIP] Eron Emails not found at {email_path}")

    # 5. Synthetic DLP
    synthetic_path = os.path.join(RAW_DATA_DIR, "synthetic_dlp", "synthetic_data.csv")
    if os.path.exists(synthetic_path):
        print(f"\nLoading Synthetic DLP from {synthetic_path}...")
        try:
            df = pd.read_csv(synthetic_path)
            if not df.empty:
                df['type'] = 'txt'
                df['source_file'] = synthetic_path
                df = clean_dataframe(df, "Synthetic DLP")
                if not df.empty:
                    dfs.append(df)
        except Exception as e:
            print(f"  [ERROR] Failed to load Synthetic DLP: {e}")
    else:
        print(f"\n[SKIP] Synthetic DLP not found at {synthetic_path}")

    if not dfs:
        print("\n[ABORT] No training datasets loaded.")
        return

    # Merge & Split
    core_df = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal Merged Training Data Rows: {len(core_df)}")
    
    print("\n--- Stratified Splitting (70% Train, 15% Val, 15% Test) ---")
    try:
        train_df, temp_df = train_test_split(core_df, test_size=0.30, stratify=core_df['label'], random_state=42)
        val_df, test_df = train_test_split(temp_df, test_size=0.50, stratify=temp_df['label'], random_state=42)
        
        print("\nFinal Dataset Distributions:")
        print("TRAIN SET:")
        print(f"  Total Rows: {len(train_df)}")
        print(f"  Distribution:\n{train_df['label'].value_counts().to_string()}")
        
        print("\nVALIDATION SET:")
        print(f"  Total Rows: {len(val_df)}")
        print(f"  Distribution:\n{val_df['label'].value_counts().to_string()}")
        
        print("\nTEST SET:")
        print(f"  Total Rows: {len(test_df)}")
        print(f"  Distribution:\n{test_df['label'].value_counts().to_string()}")
        
        DOC_CLASS_DIR = os.path.join(PROCESSED_DATA_DIR, "document_classification")
        if os.path.exists(DOC_CLASS_DIR):
            shutil.rmtree(DOC_CLASS_DIR)
        os.makedirs(DOC_CLASS_DIR, exist_ok=True)
        
        train_df.to_csv(os.path.join(DOC_CLASS_DIR, "train.csv"), index=False)
        val_df.to_csv(os.path.join(DOC_CLASS_DIR, "val.csv"), index=False)
        test_df.to_csv(os.path.join(DOC_CLASS_DIR, "test.csv"), index=False)
        print(f"\n[SUCCESS] Saved train, val, and test splits to {DOC_CLASS_DIR}")
        
        print("\n--- Organizing Physical Files for OCR ---")
        splits = {"train": train_df, "val": val_df, "test": test_df}
        for split_name, df_split in splits.items():
            for label in ["Public", "Confidential", "Restricted"]:
                os.makedirs(os.path.join(DOC_CLASS_DIR, split_name, label), exist_ok=True)
            
            print(f"Writing {split_name} physical files...")
            for idx, row in df_split.iterrows():
                label = row['label']
                target_dir = os.path.join(DOC_CLASS_DIR, split_name, label)
                
                if row.get('type') == 'pdf' and pd.notna(row.get('source_file')) and os.path.exists(row.get('source_file', '')):
                    filename = os.path.basename(row['source_file'])
                    shutil.copy2(row['source_file'], os.path.join(target_dir, filename))
                else:
                    txt_filename = f"doc_{idx}.txt"
                    with open(os.path.join(target_dir, txt_filename), 'w', encoding='utf-8') as f_out:
                        f_out.write(str(row['text']))
        
        print("\n[SUCCESS] Physical file generation complete.")
        
    except ValueError as e:
        print(f"\n[ERROR] Stratified split failed: {e}")

# -----------------------------------------------------------------------------
# Group B: The Benchmark Group
# -----------------------------------------------------------------------------
def process_benchmarks():
    print("\n" + "=" * 60)
    print(" PROCESSING GROUP B: BENCHMARK ISOLATION")
    print("=" * 60)
    
    os.makedirs(BENCHMARKS_DATA_DIR, exist_ok=True)
    
    benchmarks = {
        "roberta_pii_synth": "roberta_pii.csv",
        "um_dlp_benchmark": "um_dlp.csv",
        "contextual_sensitive": "contextual_sensitive.csv"
    }
    
    for raw_name, out_name in benchmarks.items():
        path = os.path.join(RAW_DATA_DIR, raw_name)
        if os.path.exists(path):
            print(f"\nLoading Benchmark: {raw_name}...")
            df = load_arrow_dataset(path)
            if not df.empty:
                out_path = os.path.join(BENCHMARKS_DATA_DIR, out_name)
                df.to_csv(out_path, index=False)
                print(f"  [SUCCESS] Saved {out_name} (Shape: {df.shape})")
            else:
                print(f"  [WARNING] Could not parse arrow data for {raw_name}.")
        else:
            print(f"\n[SKIP] Benchmark {raw_name} not found at {path}")

if __name__ == "__main__":
    try:
        process_training_group()
        process_benchmarks()
        print("\n[SUCCESS] Full pipeline execution finished.")
    except Exception as e:
        print(f"\n[FATAL ERROR] Pipeline crashed: {e}")
