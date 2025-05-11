import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def load_data(csv_file_path):
    """Loads the CSV data into a DataFrame with error handling."""
    try:
        # Try reading with different encodings if needed
        try:
            df = pd.read_csv(csv_file_path)
        except UnicodeDecodeError:
            df = pd.read_csv(csv_file_path, encoding='utf-16')  # Try UTF-16 if UTF-8 fails

        # Print actual column names for debugging
        print("Actual columns in CSV:", df.columns.tolist())

        # Clean column names (remove extra spaces)
        df.columns = df.columns.str.strip()

        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def analyze_level_completion(df):
    """
    Analyzes level completion statistics.

    Parameters:
    df (pd.DataFrame): Game data DataFrame

    Returns:
    dict: Dictionary with analysis results
    """
    if df is None:
        return None

    analysis = {
        'level_counts': df['Level'].value_counts().sort_index(),
        'players_per_level': df.groupby('Level')['Player Name'].nunique(),
        'avg_time_per_level': df.groupby('Level')['Time (s)'].mean(),
        'completion_rate': (df['Level'].value_counts() / len(df['Player Name'].unique()) * 100)
                            }
    return analysis


def plot_correlation_matrix(df, output_dir='data'):
    """
    Creates a correlation matrix plot from the DataFrame using available player data.

    Args:
        df (pd.DataFrame): The DataFrame containing your game data.
        output_dir (str): Directory to save the plot.
    """

    # 1. Select the relevant numerical columns available in the player data
    correlation_data = df[['Time (s)', 'Enemies Defeated', 'HP', 'Distance']].copy()

    # Handle potential missing values
    correlation_data.fillna(0, inplace=True)

    # 2. Calculate the Correlation Matrix
    corr_matrix = correlation_data.corr()

    # 3. Create the Plot
    plt.figure(figsize=(8, 6))  # Adjust figure size for readability
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=.5)
    plt.title('Correlation Matrix of Player Data')

    # 4. Save the Plot
    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, 'correlation_matrix_player_data.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Correlation matrix plot (player data) saved to: {plot_path}")


def save_plots(df, analysis, output_dir='data'):
    """
    Saves all visualization plots to the 'data' directory.
    """
    if df is None or analysis is None:
        print("No data to save plots")
        return

    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create a larger figure with proper spacing
    plt.figure(figsize=(18, 12))
    plt.subplots_adjust(wspace=0.3, hspace=0.4)  # Add more spacing between subplots

    # --- Pie Chart --- (Top-left)
    plt.subplot(2, 2, 1)
    patches, texts, autotexts = plt.pie(
        analysis['level_counts'],
        labels=analysis['level_counts'].index,
        autopct='%1.1f%%',
        startangle=90,
        colors=['#ff9999', '#66b3ff', '#99ff99'],
        textprops={'fontsize': 10}  # Slightly smaller font
    )
    plt.title('Distribution of Levels Completed', pad=15)
    plt.setp(autotexts, size=10, weight="bold")


    # --- Line Graph --- (Bottom-left)
    plt.subplot(2, 2, 3)
    level_styles = {
        1: {'color': 'red', 'marker': 'o', 'label': 'Level 1'},
        2: {'color': 'blue', 'marker': 's', 'label': 'Level 2'},
        3: {'color': 'green', 'marker': 'D', 'label': 'Level 3'},
    }
    for level, style in level_styles.items():
        level_data = df[df['Level'] == level]
        trend = level_data.groupby('Enemies Defeated')['Time (s)'].mean().reset_index()
        plt.plot(
            trend['Enemies Defeated'],
            trend['Time (s)'],
            color=style['color'],
            marker=style['marker'],
            linestyle='-',
            linewidth=2,
            label=style['label'],
            alpha=0.8
        )
    plt.xlabel('Enemies Defeated')
    plt.ylabel('Average Time (seconds)')
    plt.title('Time vs Enemies Defeated (by Level)')
    plt.legend(fontsize='small')  # Smaller legend
    plt.grid(True, linestyle='--', alpha=0.5)

    # --- Completion Rate Bar Chart --- (Bottom-right)
    plt.subplot(2, 2, 2)
    analysis['completion_rate'].plot(kind='bar', color='#ff9999')
    plt.title('Completion Rate (%)')
    plt.xlabel('Level')
    plt.ylabel('Percentage of Players')
    plt.xticks(rotation=0)
    plt.grid(True, linestyle='--', alpha=0.5)

    # Save the figure
    plot_path = os.path.join(output_dir, 'game_analysis_plots.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"All plots saved to: {plot_path}")


def save_visualization(df, analysis, output_dir='data'):
    """
    Saves the analysis results to CSV files in the 'data' directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save raw data
    df.to_csv(os.path.join(output_dir, 'raw_data.csv'), index=False)

    # Save analysis results
    analysis_df = pd.DataFrame({
        'Level': analysis['level_counts'].index,
        'Completions': analysis['level_counts'].values,
        'Unique_Players': analysis['players_per_level'].values,
        'Avg_Time': analysis['avg_time_per_level'].values,
        'Completion_Rate': analysis['completion_rate'].values
    })
    analysis_df.to_csv(os.path.join(output_dir, 'analysis_results.csv'), index=False)


def main():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(script_dir, 'data_record.csv')

    print(f"Looking for data file at: {csv_file_path}")

    # Load and analyze data
    df = load_data(csv_file_path)

    if df is not None:
        analysis = analyze_level_completion(df)
        save_plots(df, analysis)  # This shows the plots interactively
        save_plots(df, analysis)  # This saves the plots to file
        save_visualization(df, analysis)  # This saves the data files

        # Generate and save the correlation matrix plot
        plot_correlation_matrix(df)

        # Print summary statistics
        print("\nSummary Statistics:")
        print(f"Total players: {len(df['Player Name'].unique())}")
        print(f"Total level completions: {len(df)}")


if __name__ == "__main__":
    main()
