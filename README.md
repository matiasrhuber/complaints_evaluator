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

## 1. Create the Azure Resources (Portal)
Before deploying code, you need the "house" for it to live in.
1. *Create the Function App:*
    Search for the *Function App* in the top bar
    *Runtime Stack:* Python 3.13
    *Operating System:* Linux   # Windows might be better
    *Plan Type:* Consumption (Serverless) is usually best for background processing like 8D analysis.
2. *Create the Storage Containers:*
    Go to your *Storage Account* linked to the function
    Under *Containers*, create two: 8d-reports-input and 8d-json-output #8d-reports-input directory may need to be adjusted depending on what has been done by the China team
3. *Set Connection Strings:*
    In the *Function App* menu, go to *Settings* > *Configuration*
    Add a *New application setting:*
        Name: AZURE_STORAGE_CONNECTION_STRING
        Value: (Copy your storage account "Access Key" connection string)

## 2. Prepare Your Deployment Package
Azure needs your files in a specific structure to recognize the dependencies in your requirements.txt
*Critical Step for Python:* You cannot just zip the folder. You must install the libraries into the folder so Azure can see them immediately. Run this command in your local terminal:
    pip install -r requirements.txt --target=".python_packages/lib/site-packages"
Your folder should now have a .python_packages directory. **Zip the contents** of your folder (not the parent folder itself)

## 3. Deploy the Zip via Portal/CLI
Since you want to stay within the Portal/Account context, you have two easy options to "push" that zip file:

### Option A: The "Advanced Tools" (Kudu) - No CLI needed
1. In the Portal, go to your **Function App*
2. Search for **Advanced Tools* in the left menu and click **Go**
3. In the new window (Kudu), select **Zip Deploy** from the top menu
4. **Drag and drop** your 8D_Processor.zip file onto the page. Azure will automatically unzip it and start the service.

### Option B: Azure CLI (From Portal Cloud Shell)
If you prefer a single command without installing anything on your PC:
1. Click the **Cloud Shell** icon (>_) at the top right of the Azure Portal
2. Upload your zip file to the Cloud Shell storage
3. Run:
    az functionapp deployment source config-zip -g <ResourceGroupName> -n <FunctionAppName> --src <YourZipFileName>.zip

## 4. Final Validation
Once deployed, go back to the **Azure Portal:*
1. Select your **Function App* > **Functions**
2. You should see your function listeed there.
3. Click **Log Stream**
4. Upload a PDF to your 8d-reports-input container in a seperate tab.
5. Watch the logs; you should see "Processing [file]..." and the successful generation of your JSON in the output container.






<!-- ## Azure Deployment Instructions
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
        4. Azure will automatically use the requirements.txt to install pdfplumber and numpy in the cloud environment. -->