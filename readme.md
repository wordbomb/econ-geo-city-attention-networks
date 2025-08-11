# Economy and Geography Shape the Collective Attention of Cities

This repository contains the code, data processing scripts, and visualization tools used in the paper **"Economy and Geography Shape the Collective Attention of Cities"**.  
The study investigates how economic and geographical factors influence the collective attention patterns among cities, using community detection, topic modeling, and regression analysis.

---

##  Project Structure
```
econ-geo-city-attention-networks/
│
├── 1_Ranking_Calculation.py               # Step 1: Ranking calculation of city mentions
├── 2_Regression_Analysis.py               # Step 2: Regression analysis (OLS / Poisson)
├── 3_Community_Detection.py                # Step 3: Community detection algorithms (Louvain, CPM, etc.)
├── 4_Community_Features.py                 # Step 4: Compute community-level features
├── 5_CPM.py                                # Step 5: Clique Percolation Method implementation
├── 6_LDA.py                                # Step 6: LDA topic modeling per community
├── 7_Economic_Indicators_Calculation.py    # Step 7: Economic indicator calculations
├── Appendix.py                             # Additional analysis and appendix scripts
├── main.py                                 # Main entry point for pipeline execution
├── util.py                                 # Utility functions shared across scripts
├── stopwords.txt                           # Custom stopwords for LDA
├── config.json                             # Configuration file for file paths & parameters
├── readme.md                               # Project README
│
├── cn/                                     # China dataset and analysis results
│   ├── data/                               # Processed data files
│   ├── input_data/                         # Input datasets (transportation, economy, attractions)
│   ├── results/                            # Output results (Excel, PDF, regression outputs)
│
├── us/                                     # US dataset and analysis results
│   ├── data_collection/                    # Data crawling and preprocessing scripts
│   ├── input_data/                         # Input datasets (geojson, csv, xlsx)
│   ├── results/                            # Output results (Excel, PDF, regression outputs)
```
---

##  Installation

**Clone the repository**
```bash
git clone https://github.com/wordbomb/econ-geo-city-attention-networks
cd econ-geo-city-attention-networks
```

##  Usage
You can run the full analysis pipeline with:
```bash
python main.py cn  # Execute code for China
python main.py us  # Execute code for the United States
```