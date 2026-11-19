from pathlib import Path

import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns

from config import ENTITY_NAMES, OUTPUT_FOLDER
from data import entities
from metrics.metrics import load_metrics_df

ENTITIES_NAMES = ENTITY_NAMES


def _ensure_charts_dir() -> None:
    Path(f'{OUTPUT_FOLDER}/charts').mkdir(parents=True, exist_ok=True)


def token_frequency_per_report_mean():
    _ensure_charts_dir()
    metrics_df = load_metrics_df()
    mean = metrics_df['report_tokens_count'].mean()
    std = metrics_df['report_tokens_count'].std()

    low, high = stats.t.interval(0.95, df=len(metrics_df)-1, loc=mean, scale=std)
    filtered_df = metrics_df[(metrics_df['report_tokens_count'] >= low) & (metrics_df['report_tokens_count'] <= high)]

    plt.figure(figsize=(10, 6))
    sns.histplot(filtered_df['report_tokens_count'], bins=15, kde=True)
    plt.axvline(mean, color='red', linestyle='--', label=f'Mean: {mean:.2f}')
    plt.title('Distribution in Mean Interval of Tokens Counts per Report')
    plt.xlabel('Token Count')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/charts/token_frequency_per_report_mean.png')
    plt.close()


def token_frequency_per_report():
    _ensure_charts_dir()
    metrics_df = load_metrics_df()
    mean = metrics_df['report_tokens_count'].mean()
    std = metrics_df['report_tokens_count'].std()

    low, high = stats.t.interval(0.95, df=len(metrics_df)-1, loc=mean, scale=std)

    plt.figure(figsize=(10, 6))
    sns.histplot(metrics_df['report_tokens_count'], bins=30, kde=True)
    plt.axvline(mean, color='red', linestyle='--', label=f'Mean: {mean:.2f}')
    plt.axvspan(low, high, color='red', alpha=0.3, label=f'IC 95%')
    plt.title('Distribution of Token Counts per Report')
    plt.xlabel('Token Count')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/charts/token_frequency_per_report.png')
    plt.close()


def token_frequency_per_entity_mean():
    _ensure_charts_dir()
    metrics_df = load_metrics_df()

    for entity_name in entities.get_configured_entities():
        mean = metrics_df[f'{entity_name}_tokens_count'].mean()
        std = metrics_df[f'{entity_name}_tokens_count'].std()

        low, high = stats.t.interval(0.95, df=len(metrics_df)-1, loc=mean, scale=std)
        filtered_df = metrics_df[(metrics_df[f'{entity_name}_tokens_count'] >= low) & (metrics_df[f'{entity_name}_tokens_count'] <= high)]

        plt.figure(figsize=(10, 6))
        sns.histplot(filtered_df[f'{entity_name}_tokens_count'], bins=15, kde=True)
        plt.axvline(mean, color='red', linestyle='--', label=f'Mean: {mean:.2f}')
        plt.title(f'Distribution in Mean Interval of Tokens Counts per {entity_name}')
        plt.xlabel('Token Count')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_FOLDER}/charts/token_frequency_per_{entity_name}_mean.png')
        plt.close()

def token_frequency_per_entity():
    _ensure_charts_dir()
    metrics_df = load_metrics_df()

    for entity_name in entities.get_configured_entities():
        mean = metrics_df[f'{entity_name}_tokens_count'].mean()
        std = metrics_df[f'{entity_name}_tokens_count'].std()

        low, high = stats.t.interval(0.95, df=len(metrics_df)-1, loc=mean, scale=std)

        plt.figure(figsize=(10, 6))
        sns.histplot(metrics_df[f'{entity_name}_tokens_count'], bins=30, kde=True)
        plt.axvline(mean, color='red', linestyle='--', label=f'Mean: {mean:.2f}')
        plt.axvspan(low, high, color='red', alpha=0.3, label=f'IC 95%')
        plt.title(f'Distribution of Token Counts per {entity_name}')
        plt.xlabel('Token Count')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_FOLDER}/charts/token_frequency_per_{entity_name}.png')
        plt.close()