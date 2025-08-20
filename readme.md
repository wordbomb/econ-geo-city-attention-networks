# Economy and Geography Shape the Collective Attention of Cities

This repository contains the code, data processing scripts, and visualization tools used in the paper **"Economy and Geography Shape the Collective Attention of Cities"**.  
The study investigates how economic and geographical factors influence the collective attention patterns among cities, using community detection, topic modeling, and regression analysis.

---

##  Project Structure
```
econ-geo-city-attention-networks/
│
├── 1_Ranking_Calculation.py                # Step 1: Ranking calculation of city mentions
├── 2_Regression_Analysis.py                # Step 2: Regression analysis
├── 3_Community_Detection.py                # Step 3: Community detection algorithms (Louvain, LPA, LD, DN.)
├── 4_Community_Features.py                 # Step 4: Compute community-level features
├── 5_CPM.py                                # Step 5: Clique Percolation Method implementation
├── 6_LDA.py                                # Step 6: LDA topic modeling per community
├── 7_Economic_Indicators_Calculation.py    # Step 7: Economic indicator calculations
├── Appendix.py                             # Additional analysis and appendix scripts
├── main.py                                 # Main entry point for pipeline execution
├── util.py                                 # Utility functions shared across scripts
├── stopwords.txt                           # Custom stopwords for LDA
├── config.json                             # Configuration file for parameters
├── readme.md                               # Project README
│
├── cn/                                     # China dataset and analysis results
│   ├── data/                               # Processed data files
│   ├── input_data/                         # Input datasets (transportation, economy, attractions)
│   ├── results/                            # Output results (Excel, PDF, regression outputs)
│
├── us/                                     # US dataset and analysis results
│   ├── data/                               # Processed data files
│   ├── data_collection/                    # Data crawling and preprocessing scripts
│   ├── input_data/                         # Input datasets (geojson, csv, xlsx)
│   ├── results/                            # Output results (Excel, PDF, regression outputs)
```
---

## Data Directories

### `cn/` — China dataset and analysis results  

| File / Folder | Description |
|---------------|-------------|
| `input_data/transportation.xlsx` | Indicates whether each Chinese city has an **airport** and **train station** (boolean/flag fields). |
| `input_data/economy_attractions.xlsx` | City-level economy and tourism dataset with fields: **5A, 4A, 3A scenic spot counts, GDP, Population, Area, Latitude, Longitude**.<br> **5A/4A/3A** are official tourism attraction ratings in China. |
| `data/comment_data.xlsx` | Raw user comments. |
| `data/processed_comments_with_ids.xlsx` | Cleaned user comments with user IDs. |
| `data/community_aggregated_data.xlsx` | Aggregated community-level indicators: **Community, mention_count, GDP**. |
| `results/city_Louvain.xlsx`, `city_LPA.xlsx`, `city_GN.xlsx`, `city_LD.xlsx` | Community detection results from different algorithms. |
| `results/city_CPM_k4.xlsx`, `city_CPM_edges_k4.xlsx` | Clique Percolation Method (CPM) results with k=4. |
| `results/city_table_count.xlsx` | City-level basic information and metrics, including: **mention_count, GDP, Population, Area, Longitude, Latitude, Degree Centrality, Betweenness Centrality, Closeness Centrality, Has Airport, Has Ferry Terminal, Has Train Station, total_attractions, total_reviews, five_score, four_score, three_score, two_score, one_score, tourism_quality, population_attraction_score, tourism_attraction_scores, harris_market_potential**. |
| `results/city_relations.xlsx` | City network edge list with columns **source, target**; an edge exists if two cities are mentioned by the same user. |
| `results/lda_crc.xlsx` | Community-level topic consistency metrics: **Community ID, CRC**. |
| `results/*_analysis.xlsx` | Analytical results such as centrality measures and city comparisons. |
| `results/*_regression.txt/xlsx` | **OLS regression analysis results**. |
| `results/cn_Poisson.xlsx` | **Poisson regression analysis results**. |
| `results/gdp_mentions_effectivesize_regression.txt` | Specialized regression results: <br>GDP vs Mention Count <br>GDP vs Effective Size (structural holes). |

---

### `us/` — US dataset and analysis results  

| File / Folder | Description |
|---------------|-------------|
| `input_data/usa_economy.xlsx` | US city-level **Population** and **GDP**. |
| `input_data/usa_attractions.xlsx` | US city tourism attractions, fields: counts of **Rating 1–5 attractions**.<br>Ratings are from **TripAdvisor user reviews**. |
| `input_data/usa_ferry_terminals.geojson` | Ferry terminal spatial data. |
| `input_data/usa-airports.csv` | Airport data. |
| `input_data/usa_railway_station.geojson` | Railway station data. |
| `input_data/county_boundary.json`, `gadm41_USA_2.json` | Administrative boundary data. |
| `input_data/US_city_county_state*.csv` | Mapping between cities, counties, and states. |
| `data/processed_comments_with_ids.xlsx` | Cleaned user comments. |
| `data/community_aggregated_data.xlsx` | Aggregated community-level indicators: **Community, mention_count, GDP**. |
| `results/city_Louvain.xlsx`, `city_LPA.xlsx`, `city_GN.xlsx`, `city_LD.xlsx` | Community detection results. |
| `results/city_CPM_k8.xlsx`, `city_CPM_edges_k8.xlsx` | Clique Percolation Method (CPM) results with k=8. |
| `results/city_table_count.xlsx` | City-level basic information and metrics (same fields as `cn/`). |
| `results/city_relations.xlsx` | City network edge list (same format as `cn/`). |
| `results/lda_crc.xlsx` | Community-level topic consistency metrics: **Community ID, CRC**. |
| `results/*_analysis.xlsx` | Analytical results such as centrality measures, GDP-mention relations, isolated city comparisons. |
| `results/*_regression.txt/xlsx` | **OLS regression analysis results**. |
| `results/us_Poisson.xlsx` | **Poisson regression analysis results**. |
| `results/gdp_mentions_effectivesize_regression.txt` | Specialized regression results: GDP vs Mention Count and GDP vs Effective Size. |

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

## Citation

If you find this repository useful for your research, please cite the following paper:

```bibtex
@article{shang2025economy,
  title={Economy and Geography Shape the Collective Attention of Cities},
  author={Shang, Ke-ke and Zhu, Jiangli and Yi, Junfan and Zhang, Liwen and Yang, Junjie and Guo, Ge and Jin, Zixuan and Small, Michael},
  journal={arXiv preprint arXiv:2508.08907},
  year={2025}
}