import pandas as pd
import numpy as np
import statsmodels.api as sm
import os
from sklearn.preprocessing import MinMaxScaler

# Earth radius in kilometers
R = 6371.0


def significance_marker(p):
    """Return significance stars based on p-value"""
    if p < 0.01:
        return '***'
    elif p < 0.05:
        return '**'
    elif p < 0.1:
        return '*'
    return ''

def run_model(Y, X):

    model = sm.GLM(Y, X, family=sm.families.Poisson()).fit()
    r2 = None

    results_df = pd.DataFrame({
        'VARIABLES': model.params.index,
        'Coefficients': model.params.values,
        'Std Errors': model.bse.values,
        't-values': model.tvalues.values,
        'p-values': model.pvalues.values
    })

    # Add significance stars to coefficients
    results_df['Significance'] = results_df['p-values'].apply(significance_marker)
    results_df['Coefficients'] = results_df.apply(lambda row: f"{row['Coefficients']:.3f}{row['Significance']}", axis=1)
    results_df['Standard Errors'] = results_df['Std Errors'].apply(lambda x: f"({x:.3f})")
    
    # Move 'const' to the first row
    results_df = results_df.sort_values(by='VARIABLES', key=lambda x: x != 'const', ascending=False)
    summary_table = results_df[['VARIABLES', 'Coefficients', 'Standard Errors']]

    if r2 is not None:
        r2_row = pd.DataFrame({'VARIABLES': ['R2'], 'Coefficients': [f"{r2:.3f}"], 'Standard Errors': ['']})
        summary_table = pd.concat([summary_table, r2_row], ignore_index=True)

    return summary_table

def run(country_path, config):
    nodes_file = os.path.join(country_path, 'results', 'city_table_count.xlsx')
    df = pd.read_excel(nodes_file)


    airport_weight = config['airport_weight']

    df['transportation_score'] = airport_weight * df['Has Airport'] + (1 - airport_weight) * df['Has Train Station']
    df['pop_ratio'] = df['Population'] / df['Population'].mean()
    EPS = 1e-6
    df = df[
    (df['tourism_attraction_scores'] > 0) &
    (df['tourism_quality'] > 0) &
    (df['transportation_score'] > 0) &
    (df['GDP'] > 0) &
    (df['mention_count'] > 0)].copy()
    df['new_tc'] = np.log((df['tourism_attraction_scores'] + EPS) * (df['pop_ratio'] + EPS))

    Y = df['mention_count']

    # Independent variables
    X_raw = pd.DataFrame({
    'new_tc': df['new_tc'],                              # ln(tourism × pop_ratio)
    'ln_gdp': np.log(df['GDP'] + EPS),                   # ln(GDP) — direct log, no MinMax
    'transportation': np.log(df['transportation_score'] + EPS),  # ln(transport score)
    'scenic_quality': np.log(df['tourism_quality'] + EPS)       # ln(scenic quality)
    })


    scaler = MinMaxScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X_raw), columns=X_raw.columns)
    X_scaled.index = df.index

    X = sm.add_constant(X_scaled)

    output_dir = os.path.join(country_path, 'results')
    os.makedirs(output_dir, exist_ok=True)

    try:
        summary = run_model(Y, X)
        filename = f"{country_path}_Poisson.xlsx"
        filepath = os.path.join(output_dir, filename)
        summary.to_excel(filepath, index=False)
        print(f"Saved: {filename}")
    except Exception as e:
        print(f"Error running : {e}")
    print("✅ All regression results have been generated.")