# SecureFlow AI — Pre-Training & Data Preparation Guide

This guide outlines the mandatory **data preparation, sanitization, tokenization, and alignment steps** required for each dataset before feeding it into SecureFlow AI's training and evaluation pipelines.

---

## 🎯 Dataset-by-Dataset Pre-Training Requirements

```
                                 PRE-TRAINING PIPELINE MAP
                                 
   [DISC JSON]        ──► Watermark Stripping ──► OCR Denoising ──► Text Chunking (512) ──► 4-Tier Classifier
   [Medical PHI]      ──► Q&A Merge ──────────► PHI Normalization ──────────────────────► 4-Tier Classifier
   [Enron Emails]     ──► Header/Sig Cleaning ─► Subject+Body Merge ─────────────────────► 4-Tier Classifier
   
   [RoBERTa PII]      ──► Span Validation ───► Fast Tokenizer Alignment ──► BIO Tagging ──► Transformer NER
   
   [UM-DLP Benchmark] ──► Case Preservation ─► Adversarial Denoising Skip ───────────────► Robustness Eval
   [Contextual Data]  ──► ChatML Template ───► Prompt Loss Masking (-100) ──────────────► LLM Sensitivity
   [STARGATE PDFs]    ──► 300 DPI Raster ────► Deskewing & Otsu Binarization ────────────► OCR Engine
```

---

### 1. DISC (Security Clearance Classification)
*Target Model: 4-Tier Document Sensitivity Classifier (DeBERTa-v3 / RoBERTa / TF-IDF)*

#### Mandatory Steps Before Training:
1. **Header Watermark & Stamp Stripping (De-biasing)**:
   - **Problem**: Raw government cables begin with explicit markings like `TOP SECRET`, `SECRET PESHAWAR 1084`, `UNCLASSIFIED`. If left intact, the model memorizes the first 10 characters instead of understanding document semantics.
   - **Action**: Apply regex sanitization to remove leading classification tags, message transmission IDs (`ZNY SSSSS`, `RITSZYUW`, `EZ1:`), and routing headers:
     ```python
     import re

     def sanitize_disc_text(text: str) -> str:
         # Strip leading classification lines
         text = re.sub(r"(?im)^\s*(strictly\s+)?(top\s*secret|secret|confidential|unclassified|restricted|fouo)[\s:\-]+", "", text)
         # Strip telegram header artifacts
         text = re.sub(r"(?i)\b(c1\s*db-1b2|msgno|zczc|eml\s*dtg|ritszyuw|znr\s*uuuuu|ez1:|ez2:|ez3:)\b[^\n]*", "", text)
         # Remove repetitive noise symbols (e.g., 'ee eee e e @ eo')
         text = re.sub(r"[\b\s]([e\.\@\*\-]{3,})[\b\s]", " ", text)
         return text.strip()
     ```
2. **Text Chunking & Sliding Windows**:
   - Documents exceed 3,000 words. Split documents into 512-token chunks with 64-token overlap:
     ```python
     def chunk_document(text: str, max_words: int = 350, overlap: int = 50):
         words = text.split()
         chunks = []
         for i in range(0, len(words), max_words - overlap):
             chunks.append(" ".join(words[i:i + max_words]))
         return chunks
     ```
3. **Class Weight Adjustment**:
   - `Highly Confidential` has 145 samples vs 3,300+ in `Confidential`. Apply class weighting in the loss function (`compute_class_weight="balanced"` or Focal Loss) to avoid majority class bias.

---

### 2. Medical PHI (Healthcare Protected Health Information)
*Target Model: 4-Tier Document Sensitivity Classifier & Medical PHI Scanner*

#### Mandatory Steps Before Training:
1. **Dialogue Unification & Formatting**:
   - Merge `prompt` (patient inquiry) and `completion` (doctor's clinical assessment) into a single cohesive clinical record:
     ```python
     def prepare_medical_record(prompt: str, completion: str) -> str:
         return f"Clinical Consultation Record:\nPatient Inquiry: {prompt.strip()}\nPhysician Findings & Diagnosis: {completion.strip()}"
     ```
2. **Specialized Medical Acronym & Tokenizer Vocabulary Check**:
   - Verify that standard tokenizers do not over-fragment critical medical terms (`appendix cancer`, `mg/dL`, `metastasized`, `biopsy`). Use a domain-adapted tokenizer (e.g. `BioLinkBERT` / `ClinicalBERT`) if training deep neural networks.
3. **Deduplication & Length Filtering**:
   - Discard boilerplate introductions (`"Hi and welcome to HCM..."`) and drop any entries shorter than 50 characters.

---

### 3. RoBERTa-PII-Synth (Token NER & Entity Redaction)
*Target Model: Token-Classification Transformer (RoBERTa / DeBERTa / spaCy NER)*

#### Mandatory Steps Before Training:
1. **Fast Tokenizer Span Alignment (Character $\to$ Subword Token)**:
   - **Problem**: Character-level start/end indices in `spans` will not match subword token indices when tokenized by byte-pair encoding (BPE).
   - **Action**: Use Hugging Face `FastTokenizer` with `return_offsets_mapping=True` and map each token to BIO tags:
     ```python
     from transformers import AutoTokenizer

     tokenizer = AutoTokenizer.from_pretrained("roberta-base", add_prefix_space=True)

     def tokenize_and_align_labels(example, label_to_id):
         tokenized_inputs = tokenizer(
             example["text"],
             truncation=True,
             max_length=512,
             return_offsets_mapping=True,
         )
         labels = []
         offsets = tokenized_inputs["offset_mapping"]
         spans = example["spans"]

         for i, (start, end) in enumerate(offsets):
             if start == end:
                 labels.append(-100)  # Special tokens [CLS], [SEP]
                 continue
             
             token_label = "O"
             for span in spans:
                 if span["start"] <= start < span["end"]:
                     prefix = "B-" if start == span["start"] else "I-"
                     token_label = f"{prefix}{span['label']}"
                     break
             
             labels.append(label_to_id.get(token_label, 0))

         tokenized_inputs["labels"] = labels
         return tokenized_inputs
     ```
2. **Span Boundary Integrity Check**:
   - Assert `0 <= span['start'] < span['end'] <= len(text)` on all records before training to prevent indexing exceptions.
3. **Loss Masking**:
   - Ensure subword continuation tokens or special tokens (`<s>`, `</s>`, `<pad>`) have label `-100` so they are ignored by PyTorch CrossEntropyLoss.

---

### 4. UM-DLP Public Benchmarking Dataset
*Target Evaluation: Adversarial Robustness & Evasion Benchmark*

#### Mandatory Steps Before Evaluation:
1. **Do NOT Apply Aggressive Normalization**:
   - **Critical Rule**: UM-DLP explicitly tests obfuscations (`crdit c@rd`, `5 5 5 - 0 1 9 9`, character leaks). Do **NOT** strip special characters, punctuation, or lowercase the input prior to testing, or you will invalidate the adversarial benchmark.
2. **Binary Ground Truth Mapping**:
   - Map ground truth strings to binary targets:
     ```python
     def get_dlp_target(val: str) -> int:
         return 1 if str(val).strip().lower() == "sensitive" else 0
     ```
3. **Slice-Based Performance Reporting**:
   - Evaluate model metrics broken down by attack slice:
     * `Positive Direct`: Base recall on cleartext PII/IP
     * `Positive Obfuscated`: Adversarial evasion resistance
     * `Negative Keyword`: False Positive Rate on benign text containing sensitive words

---

### 5. Contextual Sensitive Data
*Target Model: LLM Sensitivity Instruction Tuner / Fine-Tuner*

#### Mandatory Steps Before Training:
1. **Instruction Template Formatting (ChatML / Alpaca)**:
   - Format the row into an instruction-following prompt:
     ```python
     def format_context_instruction(row) -> str:
         return (
             f"<|im_start|>system\n"
             f"{row['instruction']}<|im_end|>\n"
             f"<|im_start|>user\n"
             f"Column Name: {row['column_name']}\n"
             f"Sample Records: {row['records']}<|im_end|>\n"
             f"<|im_start|>assistant\n"
             f"{row['output']}<|im_end|>"
         )
     ```
2. **Prompt Loss Masking**:
   - When fine-tuning Llama/Mistral/Qwen models, set `labels = -100` for all tokens up to `<|im_start|>assistant` so loss is computed exclusively on the reasoning and classification output.
3. **Safe Evaluation of Record Strings**:
   - Use `ast.literal_eval` instead of `eval()` to parse the stringified list of sample records.

---

### 6. Enron Corporate Email Corpus (AESLC)
*Target Model: 4-Tier Document Sensitivity Classifier & Internal Domain Benchmark*

#### Mandatory Steps Before Training:
1. **Email Header & Signature Block Cleaning**:
   - Remove automated legal disclaimers (`"This email may contain confidential and privileged material..."`), forwarding headers (`"-----Original Message-----"`), and multi-line phone/signature footers:
     ```python
     def clean_enron_email(body: str) -> str:
         # Strip forwarding chains
         body = re.split(r"-----Original Message-----|From:\s+|To:\s+", body, flags=re.IGNORECASE)[0]
         # Strip common confidentiality footers
         body = re.split(r"The information contained in this communication is confidential", body, flags=re.IGNORECASE)[0]
         return body.strip()
     ```
2. **Subject + Body Synthesis**:
   - Format inputs as `"Subject: {subject}\n\n{body}"` to ensure subject lines provide top-level context for the classifier.

---

### 7. STARGATE CIA Scanned PDF Archive
*Target Engine: Tesseract / PaddleOCR / Vision-Language OCR Pipeline*

#### Mandatory Steps Before OCR & Model Inference:
1. **PDF Page Rasterization**:
   - Convert scanned vector/PDF pages to high-resolution uncompressed 300 DPI grayscale images:
     ```python
     from pdf2image import convert_from_path

     def pdf_to_images(pdf_path: str, dpi: int = 300):
         return convert_from_path(pdf_path, dpi=dpi, grayscale=True)
     ```
2. **Image Preprocessing & Binarization (OpenCV Pipeline)**:
   - Apply deskewing, Otsu adaptive thresholding, and morphological opening to eliminate scanning noise:
     ```python
     import cv2
     import numpy as np

     def preprocess_scanned_image(image_np):
         # 1. Grayscale
         gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY) if len(image_np.shape) == 3 else image_np
         # 2. Otsu thresholding
         _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
         # 3. Noise removal
         kernel = np.ones((1, 1), np.uint8)
         opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
         return opening
     ```
3. **OCR Post-Processing & Normalization**:
   - Repair common OCR letter-digit substitutions (`S5N` $\to$ `SSN`, broken hyphenation at line breaks).

---

## ⚡ Summary Checklist Before Launching Training

| Dataset | Pre-Training Checklist | Critical Failure Mode If Skipped |
| :--- | :--- | :--- |
| **DISC** | `[x]` Strip classification headers<br>`[x]` 512-token chunking<br>`[x]` Focal loss / class weighting | Model overfits to header text (`TOP SECRET`) instead of content |
| **Medical PHI** | `[x]` Concatenate prompt + completion<br>`[x]` Filter short queries (<50 chars) | Model misses clinical context in physician diagnosis |
| **RoBERTa PII** | `[x]` FastTokenizer offset alignment<br>`[x]` BIO subword tag mapping<br>`[x]` Loss mask (`-100`) on special tokens | Tokenizer misalignment causes corrupted NER span predictions |
| **UM-DLP** | `[x]` Preserve exact case & special chars<br>`[x]` Map binary labels (1/0) | Aggressive cleaning destroys adversarial evasion test cases |
| **Contextual** | `[x]` Format into ChatML template<br>`[x]` Mask system prompt loss | Model fails to learn reasoning steps |
| **Enron** | `[x]` Strip signature blocks & legal footers<br>`[x]` Prepend subject line | Repetitive legal footers create false-positive sensitive triggers |
| **STARGATE** | `[x]` 300 DPI rasterization<br>`[x]` Otsu binarization & deskewing | Low-quality OCR produces gibberish tokens |
