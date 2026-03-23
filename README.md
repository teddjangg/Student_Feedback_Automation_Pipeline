# Student Feedback Automation Pipeline

## 🔄 Before vs After

**Before**
- Manual feedback writing for each student
- Time-consuming (10+ minutes per student)
- Inconsistent tone and quality

**After**
- Automated feedback generation using LLM
- Scalable to dozens of students in minutes
- Consistent and structured output

---

## 🚨 Motivation
Teachers, TAs! Have you ever felt that writing feedback reports individually takes too much time?

This project was motivated by a real-world inefficiency observed in an academy setting, where instructors manually generated repetitive student feedback reports. I designed an automated pipeline to transform structured performance data into consistent, high-quality reports using LLMs, significantly reducing time and effort.

---

## Overview
This project automates the generation of personalized student feedback reports by integrating Google Sheets data with an LLM-based text generation pipeline.

It reads structured student performance data, applies preprocessing and rule-based filtering, and generates parent-friendly feedback at scale.

---

## Features
- Read student data directly from Google Sheets
- Preprocess and clean missing / invalid values
- Rule-based filtering (e.g., insufficient submissions)
- Generate personalized feedback using LLM
- Export results to Excel

---

## ⚙️ Pipeline Structure

Google Sheets
↓

Data Cleaning (pandas)
↓

Rule-based Filtering
↓

LLM Prompt Generation
↓

Feedback Output (Excel)

---

## Example Input (Google Sheets Format)

### 📥 Input (Google Sheets)
<img width="964" height="669" alt="Screenshot 2026-03-22 at 10 55 56 PM" src="https://github.com/user-attachments/assets/fb460706-9805-477a-88c6-22a7113420df" />

- Student A, B, C (anonymized)
- Homework scores recorded as percentages
- Missing values handled explicitly

### 📤 Generated Report
<img width="1414" height="580" alt="Screenshot 2026-03-22 at 11 03 39 PM" src="https://github.com/user-attachments/assets/39b38f5a-c8ec-496b-919f-a438ad6074d0" />

---

## Tech Stack
- Python (pandas, numpy)
- Google Sheets API (gspread)
- Gemini API (LLM)

---

## How It Works
1. Connect to Google Sheets using service account
2. Extract and structure student performance data
3. Clean and preprocess missing values
4. Apply rule-based filtering
5. Generate feedback using structured prompts
6. Export results as Excel file

---

## Project Highlights
- Designed an end-to-end automation pipeline from data ingestion to LLM-based feedback generation
- Implemented structured prompt engineering (role / instruction / data separation)
- Applied rule-based logic to improve output reliability
- Optimized API usage with rate control

---
## Edge Case Handling

To ensure reliability, feedback is only generated when sufficient data is available:

- Students with no valid participation data are excluded
- Students who submitted less than half of the assignments are skipped

This prevents generating unreliable or misleading feedback.

### Example Logic

```python
if len(valid_hw) == 0:
    # No participation data
    continue

if submitted_count < len(valid_hw) / 2:
    # Insufficient submissions
    continue
```

## 🧠 Prompt Design

The prompt is structured into multiple components to ensure consistency and quality:

- **System Prompt**: Defines the role and tone (teacher, polite and warm)
- **Style Prompt**: Provides an example format to guide output structure
- **Rule Prompt**: Enforces constraints such as tone, length, and required elements
- **Data Prompt**: Injects student-specific performance data
- **Final Instruction**: Specifies the final task

## Setup

### 1. Install dependencies
pip install pandas gspread google-auth

### 2. Add credentials
- Place `service_account.json` in the project root
- Set your API key as environment variable:
export GEMINI_API_KEY="your_api_key"

### 3. Run

```python
from feedback_pipeline import feedbackauto
import os

feedbackauto(
    spreadsheet_name="scoring",
    worksheet_name="AP Cal 오전",
    api_key=os.getenv("GEMINI_API_KEY")
)
```
---

## Note
- Sensitive files such as API keys and service account credentials are excluded.
- Sample data is provided instead of real student data for privacy reasons.

---

## Future Improvements
- Direct write-back to Google Sheets
- Async processing for faster generation
- Web interface (Streamlit)
- Support for flexible input formats (currently optimized for a fixed spreadsheet structure)






