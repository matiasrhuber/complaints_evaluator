# 8D Report Preprocessing Pipeline (Azure Edition)

This repository contains a specialized preprocessing pipeline designed to convert **8D (Eight Disciplines)** Problem Solving reports from PDF format into structured, LLM-ready JSON data.

## 📂 Project Structure
When you unzip this folder, you will find:
- `preprocess.py`: The core logic for PDF parsing and section extraction.
- `requirements.txt`: Python dependency list for environment setup.
- `local.settings.json`: Configuration for local environment variables.
- `data/`: Local directory for testing input PDFs.
- `processed_data/`: Local directory where JSON outputs are saved.

---

## 🛠️ Local Setup
To run this script on your local machine before deploying to Azure, follow these steps:

1. **Open a terminal** in the project folder.
2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
3. **Activate the environment:**
    Windows: .venv\Scripts\activate
    Mac/Linux: source .venv/bin/activate
4. **Install dependencies:**
    pip install -r requirements.txt
5. **Run the script:**
   Place your 8D PDFs in the `/data` folder and run:
   ```bash
   python preprocess.py

## Azure Deployment Instructions
To automate this pipeline in Azure, it is recommended to use **Azure Functions** with **Blob Storage Trigger**.

1. **Azure Resource Setup**
    Create an **Azure Storage Account**
    Create two containers: **8d-reports-input** (for PDFs) and **8d-json-output** (for processed files).
2. **Configure Environment Variables**
    In the Azure Portal, navigate to your Function App > **Configuration** > **Application Settings** and add:
        PDF_STORAGE_CONNECTION: Your Storage Account connection string.
        INPUT_CONTAINER: 8d-reports-input
        OUTPUT_CONTAINER: 8d-reports-output
3. **Deploy Code**
    If using VS Code, ensure you have the **Azure Funcrions Extension** installed:
        1. Click the Azure icon in the sidebar.
        2. Select "Deploy to Function App."
        3. Choose your app name.
        4. Azure will automatically use the requirements.txt to install pdfplumber and numpy in the cloud environment.