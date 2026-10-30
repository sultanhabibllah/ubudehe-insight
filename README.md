# Ubudehe Insight
### Rwanda Poverty Intelligence Platform

**Prepared by:** Habibllah Ayodele and Noella Uwera [Team Matrix] 
**Competition:** NISR Big Data Hackathon 2026  
**Track:** Financial Inclusion & Poverty Reduction  
**Data Source:** NISR EICV7 (2023/24)

---

## 1. Project Overview

Ubudehe Insight is an interactive data analysis and decision-support platform developed for the National Institute of Statistics of Rwanda (NISR) 2026 Big Data Hackathon.

The platform transforms official poverty statistics from Rwanda's Seventh Integrated Household Living Conditions Survey (EICV7, 2023/24) into accessible, interactive visualizations that help users understand regional disparities, compare different dimensions of poverty, and explore intervention-prioritization scenarios.

The project aims to make Rwanda's national poverty statistics more accessible and actionable for researchers, government institutions, development partners, and civil society organizations.

## Watch the Demo

Watch our demonstration of Ubudehe Insight, presented by Habibllah Ayodele and Noella Uwera.

**[▶ Watch the 3-minute application demo](https://drive.google.com/file/d/14S2stbO_r0ODzRglYfBf1-_CC1OrwLQW/view?usp=sharing)**

[Download the demo video from GitHub](demo/Team%20Matrix%20Demo%20Video.mp4)

## 2. Problem Statement

Rwanda produces extensive statistical information through national surveys, including the EICV7 household living conditions survey.

However, understanding geographical poverty disparities often requires navigating multiple datasets, publications, and statistical tables.

Monetary poverty and multidimensional poverty also measure different aspects of deprivation. Looking at either indicator in isolation can provide an incomplete picture of regional conditions.

**Ubudehe Insight addresses this challenge by bringing selected poverty indicators together in one interactive platform.**

The application supports evidence-informed decision-making aligned with Rwanda's national development priorities, including the Second National Strategy for Transformation (NST2) and Vision 2050.

## 3. Project Objectives

Ubudehe Insight aims to:

- Improve access to official poverty statistics through interactive visualizations.
- Highlight geographical disparities across Rwanda's five provinces.
- Enable direct comparison of monetary and multidimensional poverty indicators.
- Demonstrate how changing analytical priorities influences regional rankings.
- Support evidence-informed poverty-reduction planning.
- Improve transparency by making data sources, statistical definitions, and methodology accessible.

## 4. Data Sources

The application uses official data published by the **National Institute of Statistics of Rwanda (NISR)**.

### Dataset 1: EICV7 Poverty Profile

**Original file:** [EICV7_Tables_Rwanda_Poverty_Profile.xlsx](data/EICV7_Tables_Rwanda_Poverty_Profile.xlsx)

**Relevant table:** Table 0.1

Selected indicators:

- Provincial monetary poverty rates
- Published monetary poverty confidence intervals

[Official NISR Poverty Profile](https://statistics.gov.rw/data-sources/surveys/EICV/integrated-household-living-conditions-survey-7-eicv-7/eicv7-poverty-profile-report-202324)

### Dataset 2: EICV7 Multidimensional Poverty

**Original file:** [Tables_and_Figures_EICV7_Multidimensional_Poverty_MPI.xlsx](data/Tables_and_Figures_EICV7_Multidimensional_Poverty_MPI.xlsx)

**Relevant table:** Table B.5

Selected indicators:

- Multidimensional poverty incidence
- Multidimensional poverty intensity
- Multidimensional Poverty Index (MPI)

[Official NISR Multidimensional Poverty Report](https://statistics.gov.rw/data-sources/surveys/EICV/integrated-household-living-conditions-survey-7-eicv-7/eicv7-thematic-report-multidimensional-poverty)

### Geographic Coverage

The application currently covers Rwanda's five provinces:

1. City of Kigali
2. Southern Province
3. Western Province
4. Northern Province
5. Eastern Province

The application uses published provincial aggregates rather than individual household records.

## 5. Data Processing and Preparation

The original NISR Excel workbooks are preserved in the project's `data/` directory.

Data processing is performed using Python and Pandas.

The workflow consists of:

1. Importing the original NISR Excel datasets.
2. Extracting the selected provincial poverty indicators.
3. Standardizing geographical names across the two datasets.
4. Merging the monetary and multidimensional poverty indicators using province names.
5. Creating the cleaned analytical dataset.
6. Validating the resulting records and numerical values.

The resulting dataset is saved as:

`data/poverty_cleaned.csv`

The data extraction process is implemented in `prepare_data.py`, while validation and analytical functions are implemented in `analysis.py`.

## 6. Application Features

### 6.1 Poverty Overview

The overview provides a national snapshot of poverty in Rwanda.

Users can examine national estimates, identify provinces with relatively high or low poverty rates, and explore important regional patterns.

### 6.2 Poverty Explorer

The Poverty Explorer enables users to:

- Select a province.
- Switch between poverty indicators.
- Examine regional statistics.
- Compare provincial estimates with national estimates.
- View automatically generated descriptive insights.
- Download regional evidence briefs.

### 6.3 Regional Comparison

The Regional Comparison module enables users to compare two provinces directly.

It provides:

- Side-by-side visualizations.
- Monetary poverty comparisons.
- Multidimensional poverty comparisons.
- Absolute percentage-point differences.
- Detailed indicator tables.
- Downloadable comparison data.

This helps users understand how different measures of poverty may reveal different geographical patterns.

### 6.4 Intervention Scenario Lab

The Scenario Lab allows users to explore how different analytical priorities influence relative provincial rankings.

Users can assign different weights to:

- Monetary poverty incidence
- Multidimensional poverty incidence

The application recalculates regional priority scores as the weights change.

**The Scenario Lab is an illustrative decision-support tool. It does not predict the impact of particular interventions or determine official government funding priorities.**

### 6.5 Evidence & Data

The Evidence & Data section provides access to:

- The cleaned provincial dataset.
- Published confidence intervals for monetary poverty.
- Data quality indicators.
- Statistical definitions.
- Original data sources.
- Methodological limitations.
- Downloadable data.

## 7. Analytical Methodology

### 7.1 Descriptive Statistical Analysis

The application uses published EICV7 estimates to analyze differences between provinces.

Provincial poverty estimates are compared with national estimates using percentage-point differences.

These comparisons are descriptive and do not automatically establish statistical significance.

### 7.2 Scenario-Based Prioritization

The Scenario Lab uses a transparent weighted scoring methodology.

Two indicators are included:

- Monetary poverty incidence
- Multidimensional poverty incidence

**Step 1: Normalize the indicators**

Each indicator is normalized using min-max normalization:

\[
X_{\text{normalized}} = \frac{X-X_{\min}}{X_{\max}-X_{\min}}
\]

**Step 2: Normalize the weights**

User-selected weights are normalized so that their sum equals 1.

**Step 3: Calculate the priority score**

\[
\text{Priority Score} = 100 \times \sum_{i=1}^{n}(w_i \times X_{i,\text{normalized}})
\]

Where:

- \(w_i\) represents the normalized weight assigned to each indicator.
- \(X_{i,\text{normalized}}\) represents the normalized indicator value.
- \(n\) represents the number of selected indicators.

The resulting scores are used to produce a relative ranking of the five provinces.

### Interpretation

Higher scores indicate higher relative values across the selected poverty indicators under the chosen weighting assumptions.

The rankings are not official NISR rankings and should not be interpreted as estimates of the number of people requiring assistance, government funding requirements, or expected policy impacts.

## 8. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Application framework | Streamlit |
| Data processing | Pandas, NumPy |
| Data visualization | Plotly |
| Excel processing | openpyxl |
| Automated testing | pytest |
| Version control | Git and GitHub |
| Deployment | Streamlit Community Cloud |

## 9. Project Structure

```text
ubudehe-insight/
├── app.py
├── analysis.py
├── prepare_data.py
├── styles.css
├── requirements.txt
├── README.md
├── data/
│   ├── poverty_cleaned.csv
│   ├── EICV7_Tables_Rwanda_Poverty_Profile.xlsx
│   └── Tables_and_Figures_EICV7_Multidimensional_Poverty_MPI.xlsx
├── tests/
│   └── test_analysis.py
└── demo/
    └── demo.webm
```

The `demo/` folder contains the application walkthrough once the recording is added.

## 10. Installation and Local Setup

### Clone the repository

```bash
git clone https://github.com/sultanhabibllah/ubudehe-insight.git
cd ubudehe-insight
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the environment

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Prepare the dataset

The cleaned dataset is included in the repository. To regenerate it from the original Excel workbooks:

```bash
python prepare_data.py
```

### Run the application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal.

## 11. Testing and Validation

Automated tests are included to validate the analytical engine.

The tests cover:

- Expected number of provinces
- Unique province records
- Missing-value checks
- Valid poverty percentages
- Verification of selected published values
- Provincial comparison functions
- Scenario score calculations
- Priority ranking behavior
- Invalid weight handling
- Descriptive insight generation
- Confidence interval consistency
- MPI calculation consistency

Run the test suite using:

```bash
python -m pytest tests/ -v
```

The analytical test suite passed during development. The deployed application's interactive components should also be tested manually, including navigation, filtering, chart rendering, scenario adjustments, and file downloads.

## 12. Project Team

**Prepared by:**

**Habibllah Ayodele**  
**Noella Uwera**

Developed as a two-student entry for the NISR Big Data Hackathon 2026 under the Financial Inclusion & Poverty Reduction track.

Both team members are credited equally for the project submission. Individual responsibilities can be documented separately where relevant.

## 13. Potential Users and Impact

Ubudehe Insight is designed to support evidence-informed discussions among:

- **Government institutions:** Exploring geographical differences and informing policy discussions.
- **Development partners:** Understanding regional deprivation patterns.
- **Civil society organizations:** Identifying areas that may merit further investigation.
- **Researchers:** Comparing official statistical indicators.
- **Students and educators:** Learning about poverty measurement and evidence-based analysis.

The application makes selected official statistics easier to access, understand, compare, and communicate.

## 14. Project Limitations

Ubudehe Insight is a prototype developed using published provincial statistical aggregates.

Its current limitations include:

- No household-level analysis.
- No district-level poverty estimates.
- No prediction of future poverty rates.
- No assessment of causal relationships.
- No estimation of intervention costs or expected returns.
- No adjustment for provincial population sizes in priority rankings.
- No propagation of statistical uncertainty into scenario scores.
- No evaluation of actual intervention effectiveness.

The scenario model is exploratory and should not replace detailed policy analysis or official statistical methodologies.

## 15. Future Development Opportunities

Potential future improvements include:

- District-level analysis where suitable official data is available.
- Integration of additional EICV7 indicators covering living conditions and access to essential services.
- Geographic visualization using administrative boundary data.
- Historical comparisons across survey rounds where methodologies permit.
- Population-adjusted prioritization indicators.
- More advanced statistical uncertainty analysis.
- Additional reporting and data export capabilities.

These are future development possibilities and are not presented as existing features of the submitted prototype.

## 16. AI Assistance Disclosure

Generative AI tools, including OpenAI's ChatGPT, were used to assist with:

- Project planning.
- Debugging and troubleshooting.
- Documentation preparation.

The project team is responsible for reviewing the implementation, validating the data, verifying the methodology, coding, testing the application, and ensuring that submitted materials appropriately acknowledge their sources.

## 17. Data Attribution

**Primary data provider:** National Institute of Statistics of Rwanda (NISR)

**Survey:** Seventh Integrated Household Living Conditions Survey (EICV7), 2023/24

The original NISR datasets remain attributed to their publisher.

Ubudehe Insight is an independently developed hackathon prototype and should not be interpreted as an official NISR statistical product.

---

**Ubudehe Insight**  
*Rwanda Poverty Intelligence*

Prepared by **Habibllah Ayodele and Noella Uwera**

NISR Big Data Hackathon 2026  
Financial Inclusion & Poverty Reduction Track
