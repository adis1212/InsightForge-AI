"""Generate a synthetic wholesale dataset for demonstration."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def generate_synthetic_dataset(output_path: str = "data/samples/synthetic_wholesale.csv"):
    """Generate a reproducible synthetic wholesale dataset."""
    np.random.seed(42)

    n_records = 5000
    n_customers = 200
    n_products = 150

    # Date range: 2023-01-01 to 2023-12-31
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(n_records)]

    # Customers
    customer_ids = [f"C{np.random.randint(10000, 99999)}" for _ in range(n_customers)]

    # Products with realistic wholesale items
    product_names = [
        "Industrial Lubricant 5L", "Steel Bolts M10 (100pc)", "Safety Goggles Pro",
        "Welding Rods 2.5mm", "PVC Pipe 50mm 3m", "Electrical Cable 2.5mm 100m",
        "Cement Portland 50kg", "Paint Primer 20L", "Sandpaper P120 (50pc)",
        "LED Floodlight 100W", "Hydraulic Hose 1/2in", "Bearing 6205-2RS",
        "Air Filter Element", "Conveyor Belt 500mm", "Stainless Sheet 1.2mm",
        "Diesel Generator 5kW", "Forklift Tire 7.00-12", "Chain Link 10mm",
        "Transformer Oil 20L", "Circuit Breaker 63A",
    ]

    stock_codes = [f"WH{i:04d}" for i in range(n_products)]
    countries = ["United Kingdom", "Germany", "France", "Netherlands", "Spain",
                 "Italy", "Belgium", "Sweden", "Australia", "United States",
                 "Ireland", "Portugal", "Norway", "Denmark", "Finland"]
    country_weights = [0.35, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.03,
                       0.02, 0.01, 0.01, 0.01, 0.02]

    records = []
    invoice_counter = 500000
    cancellation_rate = 0.05

    i = 0
    while i < n_records:
        # Generate an invoice with 1-8 line items
        n_items = np.random.randint(1, 9)
        is_cancellation = np.random.random() < cancellation_rate
        invoice_no = f"{'C' if is_cancellation else ''}{invoice_counter}"
        invoice_counter += 1

        cust = np.random.choice(customer_ids)
        country = np.random.choice(countries, p=country_weights)
        inv_date = dates[min(i, len(dates) - 1)]

        for j in range(n_items):
            if i >= n_records:
                break
            prod_idx = np.random.randint(0, n_products)
            qty = np.random.randint(1, 200)
            if is_cancellation:
                qty = -qty
            price = round(np.random.uniform(0.5, 500.0), 2)

            records.append({
                "InvoiceNo": invoice_no,
                "StockCode": stock_codes[prod_idx],
                "Description": np.random.choice(product_names),
                "Quantity": qty,
                "InvoiceDate": inv_date.strftime("%Y-%m-%d %H:%M:%S"),
                "UnitPrice": price,
                "CustomerID": cust,
                "Country": country,
            })
            i += 1

    df = pd.DataFrame(records)

    # Inject some data quality issues for realism
    # Add some missing values
    missing_indices = np.random.choice(len(df), size=50, replace=False)
    df.loc[missing_indices[:20], "CustomerID"] = np.nan
    df.loc[missing_indices[20:35], "Description"] = np.nan
    df.loc[missing_indices[35:45], "UnitPrice"] = np.nan

    # Add a few duplicate rows
    dup_indices = np.random.choice(len(df), size=15, replace=False)
    duplicates = df.iloc[dup_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    # Add a couple of zero-price rows
    df.loc[np.random.choice(len(df), size=5, replace=False), "UnitPrice"] = 0.0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} records -> {output_path}")
    return df


if __name__ == "__main__":
    generate_synthetic_dataset()
