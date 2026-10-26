"""
Project: Automated E-Commerce Sales Cleaning & Analytics Pipeline
Author: Rifas
Description: 
    An automated ETL & analytics pipeline using DuckDB and Matplotlib.
    Simulates raw transaction ingestion, handles dirty/anomaly data cleaning via SQL,
    and produces aggregated executive-ready visualizations.
"""

import duckdb
import matplotlib.pyplot as plt
import os

def create_raw_dataset(con):
    """Simulates ingestion of dirty raw transactional data."""
    con.sql("""
        CREATE TABLE raw_transactions (
            transaction_id INT,
            city VARCHAR,
            category VARCHAR,
            amount INT
        );

        INSERT INTO raw_transactions VALUES
            (1, 'Jakarta', 'Elektronik', 500000),
            (2, 'Jakrta', 'Elektronik', 300000),    -- Typo in city name
            (3, 'JKT', 'Elektronik', 450000),        -- Non-standard abbreviation
            (4, 'Bandung', 'Fashion', 150000),
            (5, 'Bandung', 'Fashion', -50000),       -- Anomaly: Negative price
            (6, 'Surabaya', NULL, 200000),           -- Data corruption: NULL category
            (7, 'Surabaya', 'Makanan', 75000),
            (8, 'Medan', 'Otomotif', 800000),
            (9, 'Medan', 'Otomotif', 0),             -- Anomaly: Zero price
            (10, 'Jakarta', 'Fashion', 250000);
    """)

def clean_data(con):
    """Performs data cleaning: standardizing categories, removing nulls and anomalies."""
    con.sql("""
        CREATE TABLE clean_transactions AS
        SELECT 
            transaction_id,
            CASE 
                WHEN city IN ('Jakrta', 'JKT', 'Jakarta') THEN 'Jakarta'
                ELSE city 
            END AS city,
            category,
            amount
        FROM raw_transactions
        WHERE amount > 0 
          AND category IS NOT NULL;
    """)

def generate_analytics_chart(con, output_path="grafik_penjualan.png"):
    """Aggregates sales by city and exports a high-resolution visualization."""
    df = con.sql("""
        SELECT 
            city,
            SUM(amount) AS total_revenue
        FROM clean_transactions
        GROUP BY city
        ORDER BY total_revenue DESC;
    """).df()

    plt.figure(figsize=(9, 5.5))
    colors = ['#1f77b4', '#388bfd', '#58a6ff', '#79c0ff']
    bars = plt.bar(df['city'], df['total_revenue'], color=colors, width=0.6)

    plt.title('Total Revenue by City (Post-Cleaning Pipeline)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('City', fontsize=11, fontweight='bold')
    plt.ylabel('Total Revenue (IDR)', fontsize=11, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    # Format data labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2, 
            height + 25000, 
            f"Rp {height:,.0f}", 
            ha='center', 
            va='bottom', 
            fontweight='bold', 
            fontsize=10
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"[SUCCESS] Report saved successfully to: {output_path}")

def main():
    print("[INFO] Initializing DuckDB in-memory analytical database...")
    con = duckdb.connect()

    print("[INFO] Ingesting raw transactional data...")
    create_raw_dataset(con)

    print("[INFO] Executing SQL Data Cleaning pipeline...")
    clean_data(con)

    print("[INFO] Aggregating metrics and generating executive report...")
    generate_analytics_chart(con)

    print("[INFO] Pipeline executed successfully.")

if __name__ == "__main__":
    main()
