ClaimCopilot – LLM-Powered Insurance Claim Intake
CS 678 Project Documentation
1. Project Overview
ClaimCopilot is a small agentic AI system that automates parts of the insurance claim intake process.
Given a free-text claim description, the system:
- Extracts key structured fields (claimant name, claim type, amount, date, etc.).
- Validates and normalizes the extracted data.
- Assigns a triage priority (e.g., High / Medium / Low) and routing suggestion.
- Generates a concise, human-readable summary of the claim.
The project includes:
- A toy dataset of synthetic claims (in data/claims.jsonl).
- A multi-agent orchestration pipeline implemented in src/.
- Step-by-step Jupyter/Colab notebooks for setup, agents, CLI, evaluation, and dataset expansion.
- A command-line interface (app.py) and an evaluation script (eval.py).
The goal is to demonstrate how Large Language Models (LLMs) can be combined into a simple, modular, and explainable workflow for insurance claim processing.

2. Repository Structure
After cloning the repository, the directory structure is:
- 01_setup_and_data.ipynb  
  Notebook to set up the environment, folders, and toy dataset. Originally written for Google Colab.
- 02_core_and_agents.ipynb  
  Notebook that demonstrates the the multi-agent pipeline and runs example claims.
- 03_cli_app_and_meta.ipynb  
  Notebook that shows how the CLI app is wired to the agents and how meta-prompts / system prompts are used.
- 04_evaluation.ipynb  
  Notebook that runs evaluation over the dataset and reports metrics.
- 05_expand_dataset.ipynb  
  Notebook that expands the dataset with synthetic claims and case studies.
- app.py  
  Command-line entry point to run the claim pipeline on input text.
- eval.py  
  Evaluation script that processes all claims from the dataset and writes results.
- requirements.txt  
  List of Python package dependencies.
- README.md  
  Short technical README for the repository.
- data/  
  Contains claims.jsonl, the toy dataset of synthetic claims. Each line is one JSON record.
- outputs/  
  Contains pipeline outputs such as:
  - outputs/case_studies.jsonl
  - outputs/claim_result.json
  - outputs/eval_results.json
- src/  
  Project source code:
  - __init__.py – Makes src a Python package.
  - generate_dataset.py – Utilities for generating additional synthetic claims.
  - llm_client.py – LLM wrapper that calls the model using an API key.
  - orchestrator.py – Orchestrates the multi-agent pipeline.
  - state.py – Shared state object passed between agents.
  - agents/ – Folder with agent implementations:
    - base.py – Base agent class (common behavior / interface).
    - extraction.py – Extraction agent for structured fields.
    - validation.py – Validation agent for consistency and sanity checks.
    - triage.py – Triage agent for priority and routing labels.
    - summarization.py – Summarization agent for natural-language summaries.

3. Requirements
3.1 Python and Packages
- Python 3.10 or higher.
- All required packages are listed in requirements.txt.
To install them (on a local machine):
1. Open a terminal in the repository root folder (Claim_CoPilot).
2. Run:
   pip install -r requirements.txt
3.2 LLM / API Key
The project relies on an external LLM API (for example, OpenAI). You must provide an API key via an environment variable:
- Environment variable name: OPENAI_API_KEY
Example (Linux / macOS):
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxx"
Example (in a Python notebook):
import os
os.environ["OPENAI_API_KEY"] = "sk-xxxxxxxxxxxxxxxx"
The file src/llm_client.py reads this environment variable and uses it to send requests to the model. Without this key, the agent pipeline will not be able to generate outputs.

4. Quick Start (Local Machine – Recommended for Grading)
This section describes how to run the application from the command line, starting from a fresh clone.
4.1 Clone the Repository and Install Dependencies
1. Clone the GitHub repository:
   git clone https://github.com/AnuragInampudi/Claim_CoPilot.git
2. Move into the project directory:
   cd Claim_CoPilot
3. Install dependencies:
   pip install -r requirements.txt
4. Set your LLM API key as an environment variable:
   export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxx"
4.2 Running the CLI Application
From the project root (Claim_CoPilot):
Run:
   python app.py
The script will either:
- Prompt you to provide a free-text claim description, or
- Use a sample text and print out:
  - Extracted fields (name, claim type, amount, date, etc.).
  - Triage decision (e.g., High/Medium/Low priority).
  - A concise summary of the claim.
You can usually see available CLI options by running:
   python app.py --help
4.3 Running the Evaluation Script
To run the multi-agent pipeline over the entire dataset in data/claims.jsonl and compute metrics:
1. Make sure the environment is activated and OPENAI_API_KEY is set.
2. In the project root, run:
   python eval.py
The script reads each claim from data/claims.jsonl, processes it, computes evaluation metrics, and writes results to outputs/eval_results.json.

5. Running via Jupyter / Google Colab Notebooks
If you prefer an interactive, step-by-step view of the system (ideal for demonstration and grading), you can run the notebooks in order. They are designed so that each notebook can be run top-to-bottom.
For a local Jupyter setup:
- Open the notebooks (.ipynb files) using Jupyter Notebook or JupyterLab.
- For each notebook, run all cells from top to bottom.
For Google Colab:
- Upload or open the notebooks in Colab.
- Some cells are written explicitly for Colab (e.g., Google Drive mounting and /content/ paths).
Brief description of each notebook:
5.1 Notebook 01 – Setup and Data (01_setup_and_data.ipynb)
- Initializes folders (src, data, outputs, notebooks).
- Ensures src/ is importable.
- Creates or verifies data/claims.jsonl.
- Prints sample lines from the dataset.
5.2 Notebook 02 – Core Pipeline and Agents (02_core_and_agents.ipynb)
- Imports all core components from src/.
- Demonstrates a single claim passing through:
  Extraction → Validation → Triage → Summarization.
- Prints intermediate and final results.
5.3 Notebook 03 – CLI App and Meta-Prompts (03_cli_app_and_meta.ipynb)
- Shows how the CLI (app.py) wraps the orchestrator.
- Introduces system prompts / meta-prompts for each agent.
- Demonstrates sample CLI-like runs from the notebook.
5.4 Notebook 04 – Evaluation (04_evaluation.ipynb)
- Loads data/claims.jsonl.
- Runs the full pipeline on each claim.
- Computes simple evaluation metrics (e.g., for summaries and extracted fields).
- Saves metrics to outputs/eval_results.json.
5.5 Notebook 05 – Dataset Expansion (05_expand_dataset.ipynb)
- Uses the LLM to generate additional synthetic claims.
- Saves them to outputs/case_studies.jsonl.

6. Data Format
The main dataset is stored in data/claims.jsonl.
- File type: JSON Lines (JSONL). Each line is a valid JSON object representing one claim.
Example fields in each record:
- id: Unique identifier (e.g., "c1").
- text: Free-text description of the claim.
- claimant_name: Name of the claimant.
- policy_type: Type of policy (Health, Auto, Property, etc.).
- claim_amount: Numeric claim amount.
- incident_date: Date of incident in ISO format (YYYY-MM-DD).
- priority: Reference priority label (Low, Medium, High).
- gold_summary: Reference summary used for evaluation.
This format allows:
- Extraction agent to recover structured fields from text.
- Evaluation code to compare extracted fields against ground truth.
- Summarization agent output to be compared with gold_summary.

7. Outputs
The outputs/ directory contains files created by the pipeline and notebooks.
Key files:
1. outputs/claim_result.json
   - An example of the pipeline applied to a single claim.
   - Includes extracted fields, validation info, triage decision, and final summary.
2. outputs/eval_results.json
   - Evaluation results over all claims in data/claims.jsonl.
   - May include accuracy or similarity scores for extraction and summarization.
3. outputs/case_studies.jsonl
   - Additional synthetic claims generated for experimentation and analysis.

8. Notes for Instructor / Grader
If the goal is simply to verify correctness and see the system in action, there are two straightforward options.
Option A – Minimal Command-Line Check
1. Clone repository and install dependencies:
   git clone https://github.com/AnuragInampudi/Claim_CoPilot.git
   cd Claim_CoPilot
   pip install -r requirements.txt
2. Set API key:
   export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxx"
3. Run:
   python app.py
   python eval.py
Option B – Full Notebook Walkthrough
Run the notebooks in sequence:
1. 01_setup_and_data.ipynb
2. 02_core_and_agents.ipynb
3. 03_cli_app_and_meta.ipynb
4. 04_evaluation.ipynb
5. 05_expand_dataset.ipynb
Notes on Paths:
- Some original cells reference Google Colab paths like /content/drive/MyDrive/Claim_CoPilot.
- When running locally, these can be ignored or replaced with a local base path (e.g., current directory).
- The committed repository already contains the necessary code and dataset, so it can run entirely from the cloned folder without Google Drive.

9. Conceptual Summary
ClaimCopilot illustrates a small but complete agentic AI workflow:
- Input: Free-text insurance claim description.
- Processing: Extraction → Validation → Triage → Summarization.
- Output: Structured data, a concise summary, and a priority signal.
This project ties together:
- Prompt engineering and LLM usage.
- Modular software engineering (agents, orchestrator, CLI).
- Basic evaluation of LLM-based systems.
- Synthetic data generation for experimentation.
This document is intended to provide a clear, self-contained description so that someone unfamiliar with the original setup (such as a course instructor) can understand, install, run, and inspect the project and its outputs.

