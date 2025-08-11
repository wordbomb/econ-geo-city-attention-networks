import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import os

def run(country_path, config):
    if config['country']=='us':
        comment_file = os.path.join(country_path, 'data', 'comment_data_filter.xlsx')
        data= pd.read_excel(comment_file)
        
        end_date = pd.to_datetime(config['end_date'])
        data.set_index('Date Created', inplace=True)
        records_per_week = data.resample('7D').size().reset_index(name='Record Count')
        last_record_date = records_per_week['Date Created'].max()
        days_in_last_period = (end_date - last_record_date).days


        if days_in_last_period < 7:
            records_per_week = records_per_week[:-1]
        data.reset_index(inplace=True)

        plt.figure(figsize=(10, 5.8))
        plt.grid(False)
        plt.plot(records_per_week['Date Created'], records_per_week['Record Count'], color='#8FBBD9', linewidth=5)

        plt.ylabel('Number of mentions', fontsize=26) 

        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.xticks(rotation=45)

        plt.tick_params(axis='both', which='major', labelsize=20)
        plt.tight_layout()
        line_chart_file = os.path.join(country_path, 'results', 'Number of mentions.pdf')
        plt.savefig(line_chart_file)
    
    if config['country']=='cn':
        comment_file = os.path.join(country_path, 'data', 'comment and like.xlsx')

        data = pd.read_excel(comment_file, dtype={'Date': str})

        end_date = pd.to_datetime(config['end_date'])
        year = end_date.year 

        def parse_md(s):
            s = str(s).strip()
            s = s.replace('-', '.').replace('/', '.')
            m, d = s.split('.')
            m, d = int(m), int(d)
            return pd.Timestamp(year=year, month=m, day=d)

        data['Date'] = data['Date'].apply(parse_md)

        data = data.sort_values('Date').set_index('Date')

        data = data.loc[:end_date]

        records_per_week = (
            data['Likes']
            .resample('7D')
            .sum()
            .reset_index(name='Likes')
        )

        plt.figure(figsize=(10, 5.8))
        plt.grid(False)
        plt.plot(records_per_week['Date'], records_per_week['Likes'], color='#8FBBD9', linewidth=5)


        plt.ylabel('Number of likes', fontsize=26) 

        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.xticks(rotation=45)

        plt.tick_params(axis='both', which='major', labelsize=20)
        plt.tight_layout()
        line_chart_file = os.path.join(country_path, 'results', 'Number of likes.pdf')
        plt.savefig(line_chart_file)



    # Load data
    city_table_file = os.path.join(country_path, 'results', 'city_table_count.xlsx')
    city_table_df = pd.read_excel(city_table_file)
    city_table_df['Category'] = city_table_df['Degree'].apply(lambda x: 'Isolated Cities' if x == 0 else 'Network Cities')

    # Separate connected and isolated nodes
    connected_nodes = city_table_df[city_table_df['Degree'] != 0]
    isolated_nodes = city_table_df[city_table_df['Degree'] == 0]

    # Compute counts and averages
    connected_count = len(connected_nodes)
    isolated_count = len(isolated_nodes)
    connected_mean_mentions = connected_nodes['mention_count'].mean()
    isolated_mean_mentions = isolated_nodes['mention_count'].mean()
    connected_std_mentions = connected_nodes['mention_count'].std()
    isolated_std_mentions = isolated_nodes['mention_count'].std()

    # Compute additional statistics for connected and isolated nodes
    connected_median_mentions = connected_nodes['mention_count'].median()
    connected_quartiles = connected_nodes['mention_count'].quantile([0.25, 0.75])
    connected_whisker_low = connected_nodes['mention_count'].quantile(0.25) - 1.5 * (connected_quartiles[0.75] - connected_quartiles[0.25])
    connected_whisker_high = connected_nodes['mention_count'].quantile(0.75) + 1.5 * (connected_quartiles[0.75] - connected_quartiles[0.25])

    isolated_median_mentions = isolated_nodes['mention_count'].median()
    isolated_quartiles = isolated_nodes['mention_count'].quantile([0.25, 0.75])
    isolated_whisker_low = isolated_nodes['mention_count'].quantile(0.25) - 1.5 * (isolated_quartiles[0.75] - isolated_quartiles[0.25])
    isolated_whisker_high = isolated_nodes['mention_count'].quantile(0.75) + 1.5 * (isolated_quartiles[0.75] - isolated_quartiles[0.25])

    # Set up figure layout
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1])

    # Plot 1 - City Counts
    axes[0].bar(['Network Cities', 'Isolated Cities'], [connected_count, isolated_count], color=['#1f77b4', '#ff7f0e'])
    axes[0].set_xticks([0, 1])
    axes[0].set_xticklabels(['Network Cities', 'Isolated Cities'], fontsize=16)
    axes[0].set_ylabel("City Counts", fontsize=22)
    axes[0].tick_params(axis='y', which='major', labelsize=16)
    axes[0].grid(False)
    # axes[0].text(-0.2, 0.95, 'a', fontsize=36, fontweight='bold', transform=axes[0].transAxes)

    # Plot 2 - Average Mentioned Counts with Error Bars
    axes[1].bar(['Network Cities', 'Isolated Cities'], [connected_mean_mentions, isolated_mean_mentions],
                yerr=[connected_std_mentions, isolated_std_mentions], color=['#1f77b4', '#ff7f0e'], capsize=5)
    axes[1].set_xticks([0, 1])
    axes[1].set_xticklabels(['Network Cities', 'Isolated Cities'], fontsize=16)
    axes[1].set_ylabel("Average Mentioned Counts", fontsize=22)
    axes[1].tick_params(axis='y', which='major', labelsize=16)
    axes[1].grid(False)
    # axes[1].text(-0.2, 0.95, 'b', fontsize=36, fontweight='bold', transform=axes[1].transAxes)

    # Plot 3 - Mentioned Counts Boxplots
    axes[2].boxplot(connected_nodes['mention_count'], positions=[1], widths=0.6, patch_artist=True, showfliers=False,
                    boxprops=dict(facecolor='#1f77b4', color='#1f77b4'),
                    medianprops=dict(color='black'))
    axes[2].boxplot(isolated_nodes['mention_count'], positions=[2], widths=0.6, patch_artist=True, showfliers=False,
                    boxprops=dict(facecolor='#ff7f0e', color='#ff7f0e'),
                    medianprops=dict(color='black'))
    axes[2].set_xticks([1, 2])
    axes[2].set_xticklabels(['Network Cities', 'Isolated Cities'], fontsize=16)
    axes[2].set_ylabel("Mentioned Counts Distribution", fontsize=22)
    axes[2].tick_params(axis='y', which='major', labelsize=16)
    axes[2].grid(False)
    # axes[2].text(-0.2, 0.95, 'c', fontsize=36, fontweight='bold', transform=axes[2].transAxes)

    plt.tight_layout()
    comparison_file = os.path.join(country_path, 'results', 'Comparison_of_Network_and_Isolated_Cities.pdf')
    plt.savefig(comparison_file)

    # Prepare data for export to Excel
    connected_stats = {
        'Category': 'Network Cities',
        'Count': connected_count,
        'Mean Mention Count': connected_mean_mentions,
        'Standard Deviation': connected_std_mentions,
        'Median Mention Count': connected_median_mentions,
        '25th Percentile': connected_quartiles[0.25],
        '75th Percentile': connected_quartiles[0.75],
        'Whisker Low': connected_whisker_low,
        'Whisker High': connected_whisker_high
    }

    isolated_stats = {
        'Category': 'Isolated Cities',
        'Count': isolated_count,
        'Mean Mention Count': isolated_mean_mentions,
        'Standard Deviation': isolated_std_mentions,
        'Median Mention Count': isolated_median_mentions,
        '25th Percentile': isolated_quartiles[0.25],
        '75th Percentile': isolated_quartiles[0.75],
        'Whisker Low': isolated_whisker_low,
        'Whisker High': isolated_whisker_high
    }

    # Combine statistics into a DataFrame and export to Excel
    stats_df = pd.DataFrame([connected_stats, isolated_stats])
    statistics_file = os.path.join(country_path, 'results', 'Network_vs_Isolated_Cities_Statistics.xlsx')
    stats_df.to_excel(statistics_file, index=False)