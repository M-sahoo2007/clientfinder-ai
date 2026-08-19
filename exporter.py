import pandas as pd


def export_to_csv(leads, filename="leads.csv"):

    df = pd.DataFrame(leads)

    if df.empty:
        print("No leads to export.")
        return

    # Highest score first
    df = df.sort_values(
        by="Lead Score",
        ascending=False
    )

    df.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nSaved {len(df)} leads to {filename}")

