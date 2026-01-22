# Copilot Instructions for Amino Acid Sequence Analysis

## Project Overview
This project analyzes amino acid sequences from multiple data sources (CSV, JSON) to compute statistics and visualizations on sequence composition.

## Data Sources & Formats

### Primary Data
- **aa_sequences_varlen.csv**: Tab-separated file with columns `id` and `sequence` (102 sequences)
- **proteins.json**: Nested structure with `proteins[]` containing `name` and `meta.sequence` fields
- Both contain variable-length amino acid sequences

### Data Access Patterns
```python
# CSV loading (see read_csv.py)
df = pd.read_csv('aa_sequences_varlen.csv')

# JSON loading (see read_csv.py)
data = json.load(f)
for protein in data["proteins"]:
    sequence = protein["meta"]["sequence"]
```

## Key Workflows

### 1. Sequence Analysis Notebook (analysis_sequences.ipynb)
The primary analysis workflow:
- Cell 1-2: Setup pandas/matplotlib imports
- Cell 3-4: Load CSV data and display structure
- Cell 5: Compute amino acid counts per sequence (`.str.len()`)
- Cell 6: Generate bar chart visualization

**Dev Note**: The notebook uses 20x8 figsize for charts - adjust proportionally for data changes.

### 2. Batch Sequence Processing (read_csv.py)
Supports three input methods:
- `--csv <file>`: Parse CSV (skips header, takes column[1])
- `--json <file>`: Parse JSON (navigates `proteins[].meta.sequence`)
- `--seq <string>`: Single sequence string

Outputs sequence length for each entry. Pattern: use argparse for flexible input handling.

## Code Patterns & Conventions

### Data Manipulation
- Use pandas `.str.len()` for sequence length calculation (not `len()` on Series)
- Column naming: snake_case with descriptive suffixes (`amino_acids_count`, `id`)
- Statistics use `.mean()`, `.min()`, `.max()` on Series objects

### Visualization
- Libraries: `matplotlib` only (no plotly)
- Standard chart: bar chart with sequence ID on x-axis, count on y-axis
- Formatting: `figsize=(14, 6)`, `color='steelblue'`, `alpha=0.8`, rotated x-labels

### Language & Comments
- **French throughout**: All docstrings, print statements, and comments use French
- Consistent terminology: "acides aminés" (amino acids), "séquence" (sequence), "nombre de caractères" (character count)

## Critical Files
- [analysis_sequences.ipynb](../analysis_sequences.ipynb) - Primary analysis notebook
- [read_csv.py](../read_csv.py) - Multi-format data loader with CLI args
- [aa_sequences_varlen.csv](../aa_sequences_varlen.csv) - Main data source (102 sequences)

## Environment
- Python 3.x with venv at `.venv/`
- Dependencies: pandas, matplotlib (minimal stack)
- No external APIs or databases
