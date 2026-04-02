# AccessLens v2 (Access Risk Model v1)

AccessLens v2 is a deterministic, rule-based model designed to compute a **normalized Access Risk Score** representing the relative access friction that an individual might face when applying for government welfare schemes. 

This score is calculated based on a **(scheme, persona)** pair, providing insights into structural hurdles without using machine learning, real-world outcome data, or personal information.

## Overview

The purpose of this project is to model non-financial access barriers across different stages of a beneficiary's journey:
1. **Discovery**: Becoming aware of a scheme and understanding eligibility.
2. **Application**: Gathering documents and interacting with digital/physical portals.
3. **Verification**: Undergoing checks, approvals, and final confirmation.

The model computes an **Access Risk Score from 0.0 to 1.0**:
- **0.0** = Minimal access friction
- **0.5** = Moderate friction
- **1.0** = Very high access friction

## Modeled Barriers

The taxonomy defines four broad categories of recurring access friction:
- **Awareness**: Lack of scheme awareness or clarity on eligibility.
- **Documentation**: Missing or difficult-to-obtain documents.
- **Digital**: Lack of device access, internet connectivity, or digital literacy.
- **Institutional**: Dependence on intermediaries, processing delays, or process inconsistency.

*Note: The model does not use real enrollment or rejection data. All default severity values and barrier mappings are structured assumptions intended for simulation and counterfactual analysis.*

## Project Phases & Recent Advancements

### Phase 2: Access Risk Model Extensions
The core Access Risk Model has been expanded with advanced simulation capabilities:
- **Batch Simulation (`batch_simulation_v1.py`)**: Runs the risk model across thousands of persona-scheme combinations to generate aggregate analytics and population-level insights.
- **Counterfactual Simulation (`counterfactual_simulation_v1.py`)**: A "what-if" engine testing hypothetical interventions (e.g., waiving documents, adding offline agent assistance) and showing delta changes in risk scores.
- **Visualizations (`plots_v1.py`)**: Generates detailed `matplotlib/seaborn` charts for batch simulation results.

### Phase 3: Interface Layer
The Interface Layer bridges raw user demographic data and the Access Risk Model through a unified, end-to-end pipeline:
- **Persona Mapping Function (`persona_mapping_v1.py`)**: Translates unstructured user demographic inputs (e.g., age, income, caste, literacy) into standardized model Persona IDs.
- **Eligibility Discovery Module (`eligibility_engine_v1.py`)**: Implements strict deterministic routing and dynamic weighted scoring to rank government schemes based on user eligibility profiles.
- **Integration Pipeline (`pipeline_v1.py`)**: Orchestrates the entire user journey—parsing inputs, mapping personas, evaluating eligibility, computing access risk blockages, and returning actionable JSON insights.

## Requirements

- Python 3.10+
- `pandas` library

Install dependencies using:
```bash
pip install pandas
```

## Running the Models & Pipeline

The project is divided into distinct phases. You can run individual components from their respective directories.

### Running Phase 3 Integration Pipeline (Latest Workflow)
1. Navigate to the Phase 3 folder:
   ```bash
   cd "phase 3 - Interface Layer"
   ```
2. Run the pipeline script to orchestrate demographic mapping, eligibility, and risk scoring:
   ```bash
   python pipeline_v1.py
   ```

### Running Phase 2 Risk Models
1. Navigate to the Phase 2 folder:
   ```bash
   cd "phase 2 - Access Risk Model v1"
   ```
2. Run the core model, counterfactual, or batch simulations:
   ```bash
   python access_risk_model_v1.py
   # Or try counterfactual simulations:
   # python counterfactual_simulation_v1.py
   ```

### Configuration

You can change the target simulation directly at the bottom of the `access_risk_model_v1.py` file:
```python
TARGET_SCHEME_ID  = "pmmvy"
TARGET_PERSONA_ID = "p05"
```
You can substitute these with any valid Scheme ID (e.g., `pmjay`, `jsy`, `kasp`) or Persona ID (from `p01` to `p12`) to see how access friction varies for different individuals and schemes.

## Outputs

The script will output:
1. A **Results Table** showing the severity, activation multiplier, and amplification factor for each individual barrier.
2. The final **Raw Risk Score** and **Normalized Access Risk** (0.0 to 1.0).
3. A **Checker Section** to validate activated/skipped barriers and summarize the dominant barrier types.

## Documentation

For more detailed information, please see the files in the `docs/` folder:
- `MODEL_SPEC.md`: Complete mathematical and logical specification of the risk algorithm.
- `USAGE.md`: Full guide on running the script, including all available scheme and persona IDs.
- `BARRIERS_JUSTIFICATION.txt`: Detailed breakdown of the barrier taxonomy.
- `ASSUMPTIONS.txt`: Key data gaps, limitations, and modelling assumptions.
