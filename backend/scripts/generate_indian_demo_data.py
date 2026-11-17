"""
BharatTrade Distributors — Indian FMCG & Wholesale Demo Dataset Generator.

Simulates a regional Indian commercial FMCG distribution business:
- Headquarters: Pune, Maharashtra
- Regional Hubs: Mumbai, Nagpur, Bengaluru, Hyderabad, Delhi, Ahmedabad, Chennai, Jaipur
- Currencies: Indian Rupee (INR / ₹)
- 24 Months of Historical Transactions (2023-01-01 to 2024-12-31)
- Explicit COGS, Unit Prices, GST Rates, and Verified Anomaly Injections
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd


def generate_bharattrade_dataset(
    output_path: str = "data/samples/bharattrade_fmcg_transactions.csv",
    seed: int = 42,
    target_records: int = 6000,
) -> pd.DataFrame:
    """Generate deterministic, high-fidelity Indian FMCG wholesale transactions."""
    np.random.seed(seed)

    # Geographic Distribution Hubs
    cities_data = [
        {"city": "Pune", "state": "Maharashtra", "weight": 0.28},
        {"city": "Mumbai", "state": "Maharashtra", "weight": 0.22},
        {"city": "Nagpur", "state": "Maharashtra", "weight": 0.10},
        {"city": "Bengaluru", "state": "Karnataka", "weight": 0.12},
        {"city": "Hyderabad", "state": "Telangana", "weight": 0.08},
        {"city": "Delhi NCR", "state": "Delhi", "weight": 0.08},
        {"city": "Ahmedabad", "state": "Gujarat", "weight": 0.05},
        {"city": "Chennai", "state": "Tamil Nadu", "weight": 0.04},
        {"city": "Jaipur", "state": "Rajasthan", "weight": 0.03},
    ]
    city_weights = [c["weight"] for c in cities_data]

    # FMCG Product Catalog with realistic wholesale Indian pricing (INR) and GST
    catalog = [
        # Packaged Foods (5% - 12% GST)
        {"code": "FMCG-PF-001", "name": "Sharbati Whole Wheat Atta 10kg", "cat": "Packaged Foods", "price": 420.0, "cost": 345.0, "gst": 5},
        {"code": "FMCG-PF-002", "name": "Royal Daawat Basmati Rice 5kg", "cat": "Packaged Foods", "price": 680.0, "cost": 540.0, "gst": 5},
        {"code": "FMCG-PF-003", "name": "Organic Toor Dal Unpolished 1kg", "cat": "Packaged Foods", "price": 165.0, "cost": 132.0, "gst": 5},
        {"code": "FMCG-PF-004", "name": "Fortune Sunlite Refined Oil 1L", "cat": "Packaged Foods", "price": 140.0, "cost": 118.0, "gst": 5},
        {"code": "FMCG-PF-005", "name": "Jumbo Cashew Nuts W240 500g", "cat": "Packaged Foods", "price": 490.0, "cost": 395.0, "gst": 12},
        {"code": "FMCG-PF-006", "name": "Indori Thick Poha 1kg Pack", "cat": "Packaged Foods", "price": 62.0, "cost": 46.0, "gst": 5},
        {"code": "FMCG-PF-007", "name": "Kachi Ghani Mustard Oil 1L", "cat": "Packaged Foods", "price": 155.0, "cost": 128.0, "gst": 5},

        # Beverages (12% GST)
        {"code": "FMCG-BV-001", "name": "Wagh Bakri Premium CTC Tea 1kg", "cat": "Beverages", "price": 480.0, "cost": 380.0, "gst": 12},
        {"code": "FMCG-BV-002", "name": "Narasu's Filter Coffee Blend 500g", "cat": "Beverages", "price": 310.0, "cost": 242.0, "gst": 12},
        {"code": "FMCG-BV-003", "name": "Ratnagiri Alphonso Mango Pulp 850g", "cat": "Beverages", "price": 240.0, "cost": 182.0, "gst": 12},
        {"code": "FMCG-BV-004", "name": "Girnar Masala Chai Premix 30pk", "cat": "Beverages", "price": 360.0, "cost": 275.0, "gst": 12},
        {"code": "FMCG-BV-005", "name": "Natural Tender Coconut Water 200ml", "cat": "Beverages", "price": 48.0, "cost": 34.0, "gst": 12},

        # Personal Care (18% GST)
        {"code": "FMCG-PC-001", "name": "Mysore Sandal Classic Soap 125g (Pack of 3)", "cat": "Personal Care", "price": 270.0, "cost": 210.0, "gst": 18},
        {"code": "FMCG-PC-002", "name": "Kesh King Ayurvedic Shampoo 340ml", "cat": "Personal Care", "price": 285.0, "cost": 215.0, "gst": 18},
        {"code": "FMCG-PC-003", "name": "Vicco Vajradanti Herbal Paste 200g", "cat": "Personal Care", "price": 135.0, "cost": 102.0, "gst": 18},
        {"code": "FMCG-PC-004", "name": "Bajaj Almond Drops Hair Oil 300ml", "cat": "Personal Care", "price": 195.0, "cost": 150.0, "gst": 18},
        {"code": "FMCG-PC-005", "name": "Medimix Ayurvedic 18-Herb Soap 125g", "cat": "Personal Care", "price": 55.0, "cost": 41.0, "gst": 18},

        # Household Essentials (18% GST)
        {"code": "FMCG-HE-001", "name": "Surf Excel Matic Front Load 2kg", "cat": "Household Essentials", "price": 490.0, "cost": 395.0, "gst": 18},
        {"code": "FMCG-HE-002", "name": "Lizol Disinfectant Floor Cleaner 1L", "cat": "Household Essentials", "price": 185.0, "cost": 142.0, "gst": 18},
        {"code": "FMCG-HE-003", "name": "Vim Dishwash Bar 155g (Pack of 4)", "cat": "Household Essentials", "price": 60.0, "cost": 46.0, "gst": 18},
        {"code": "FMCG-HE-004", "name": "Gala Spin Mop Refill Head (Pack of 2)", "cat": "Household Essentials", "price": 220.0, "cost": 165.0, "gst": 18},
        {"code": "FMCG-HE-005", "name": "Hit Cockroach Spray Lemon 400ml", "cat": "Household Essentials", "price": 235.0, "cost": 178.0, "gst": 18},

        # Grocery & Spices (5% - 12% GST)
        {"code": "FMCG-GR-001", "name": "Madhur Pure Sulphurless Sugar 5kg", "cat": "Grocery", "price": 260.0, "cost": 215.0, "gst": 5},
        {"code": "FMCG-GR-002", "name": "Tata Iodized Rock Salt 1kg", "cat": "Grocery", "price": 32.0, "cost": 24.0, "gst": 5},
        {"code": "FMCG-GR-003", "name": "Organic Kolhapur Jaggery Block 1kg", "cat": "Grocery", "price": 85.0, "cost": 64.0, "gst": 5},
        {"code": "FMCG-GR-004", "name": "Everest Kashmiri Mirch Powder 200g", "cat": "Grocery", "price": 140.0, "cost": 105.0, "gst": 5},
        {"code": "FMCG-GR-005", "name": "Catch Turmeric Powder Salem 500g", "cat": "Grocery", "price": 125.0, "cost": 94.0, "gst": 5},

        # Commercial Stationery (18% GST)
        {"code": "FMCG-ST-001", "name": "Bilt Copy Power A4 Paper 75GSM 500s", "cat": "Stationery", "price": 310.0, "cost": 245.0, "gst": 18},
        {"code": "FMCG-ST-002", "name": "Camlin Whiteboard Marker Box (10 pcs)", "cat": "Stationery", "price": 190.0, "cost": 142.0, "gst": 18},
        {"code": "FMCG-ST-003", "name": "Orpat 12-Digit Commercial Calculator", "cat": "Stationery", "price": 380.0, "cost": 285.0, "gst": 18},
        {"code": "FMCG-ST-004", "name": "Triplicate GST Tax Invoice Book (100 sets)", "cat": "Stationery", "price": 150.0, "cost": 108.0, "gst": 18},
    ]

    # Generate 180 realistic wholesale B2B retail buyers (Kirana stores, Supermarts, Canteens)
    customers = [
        f"CUST-{cities_data[np.random.choice(len(cities_data), p=city_weights)]['city'][:3].upper()}-{1000 + i}"
        for i in range(180)
    ]

    # 24 Months Timeline: Jan 1, 2023 to Dec 31, 2024
    start_date = datetime(2023, 1, 1, 9, 30)
    total_days = 730

    records = []
    invoice_num = 100001
    cancellation_rate = 0.045  # ~4.5% returns / cancellations

    current_records = 0
    while current_records < target_records:
        day_offset = np.random.randint(0, total_days)
        invoice_date = start_date + timedelta(
            days=day_offset,
            hours=int(np.random.normal(4, 2)) % 10,
            minutes=int(np.random.randint(0, 59)),
        )

        month = invoice_date.month

        # Seasonal volume multipliers:
        # - Festive peak in Oct/Nov (Diwali/Navratri): 1.65x
        # - Summer peak in April/May (Beverages): 1.45x
        # - Financial year end in March: 1.30x
        seasonal_mult = 1.0
        if month in [10, 11]:
            seasonal_mult = 1.65
        elif month in [4, 5]:
            seasonal_mult = 1.45
        elif month == 3:
            seasonal_mult = 1.30

        city_choice = cities_data[np.random.choice(len(cities_data), p=city_weights)]
        city = city_choice["city"]
        state = city_choice["state"]
        cust_id = np.random.choice(customers)

        is_cancellation = np.random.random() < cancellation_rate
        prefix = "C" if is_cancellation else ""
        inv_id = f"{prefix}INV-{invoice_num}"
        invoice_num += 1

        # 1 to 6 items per invoice
        n_items = np.random.randint(1, 7)

        for _ in range(n_items):
            if current_records >= target_records:
                break

            product = np.random.choice(catalog)
            category = product["cat"]

            # Category-specific seasonal boost
            cat_mult = seasonal_mult
            if category == "Beverages" and month in [4, 5, 6]:
                cat_mult *= 1.4
            elif category in ["Packaged Foods", "Grocery"] and month in [10, 11]:
                cat_mult *= 1.3

            # Normal wholesale quantities: 10 to 120 units
            base_qty = int(np.random.gamma(shape=3.5, scale=8.0) * cat_mult)
            base_qty = max(5, min(base_qty, 250))

            qty = -base_qty if is_cancellation else base_qty
            unit_price = float(product["price"])
            unit_cost = float(product["cost"])
            gst_rate = product["gst"]

            # Minor volume discount for large orders (2% to 6%)
            if base_qty >= 80:
                unit_price = round(unit_price * 0.95, 2)

            line_total = round(qty * unit_price, 2)
            cogs_total = round(qty * unit_cost, 2)
            gst_amount = round(line_total * (gst_rate / 100.0), 2)
            total_with_gst = round(line_total + gst_amount, 2)

            if is_cancellation:
                order_status = "Cancelled"
                payment_status = "Refunded"
            else:
                order_status = "Delivered"
                p_rand = np.random.random()
                if p_rand < 0.85:
                    payment_status = "Paid"
                elif p_rand < 0.96:
                    payment_status = "Pending_Net30"
                else:
                    payment_status = "Overdue"

            records.append({
                "InvoiceNo": inv_id,
                "StockCode": product["code"],
                "Description": product["name"],
                "Category": category,
                "Quantity": qty,
                "InvoiceDate": invoice_date.strftime("%Y-%m-%d %H:%M:%S"),
                "UnitPrice": unit_price,
                "UnitCost": unit_cost,
                "GSTRate": gst_rate,
                "LineTotalExclGST": line_total,
                "GSTAmount": gst_amount,
                "LineTotalInclGST": total_with_gst,
                "CustomerID": cust_id,
                "City": city,
                "State": state,
                "OrderStatus": order_status,
                "PaymentStatus": payment_status,
            })
            current_records += 1

    df = pd.DataFrame(records)

    # Inject 4 specific, documented synthetic anomalies for Isolation Forest validation:
    # 1. 100x Unit Price Entry Typo
    df.loc[120, "UnitPrice"] = df.loc[120, "UnitPrice"] * 100.0
    df.loc[120, "LineTotalExclGST"] = df.loc[120, "Quantity"] * df.loc[120, "UnitPrice"]

    # 2. Extreme Bulk Order (500x volume order from an institutional canteen)
    df.loc[450, "Quantity"] = 2500
    df.loc[450, "LineTotalExclGST"] = 2500 * df.loc[450, "UnitPrice"]

    # 3. 3:30 AM Off-Hours System Transaction
    df.loc[880, "InvoiceDate"] = "2024-03-14 03:32:15"

    # 4. Severe Unit Price Anomaly (Negative/Free Promotional Entry Error)
    df.loc[1520, "UnitPrice"] = 0.50
    df.loc[1520, "LineTotalExclGST"] = df.loc[1520, "Quantity"] * 0.50

    # Ensure output directory exists
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False)
    print(f"Successfully generated BharatTrade Indian FMCG dataset with {len(df)} records at {out_file.resolve()}")
    return df


if __name__ == "__main__":
    generate_bharattrade_dataset()
