import os
import pandas as pd
from datetime import datetime


CSV_FILE = "leads.csv"


COLUMNS = [
    "Place ID",
    "Business Name",
    "Category",
    "Location",
    "Phone",
    "Address",
    "Rating",
    "Reviews",
    "Online Presence",
    "Website",
    "Lead Score",
    "Priority",
    "Recommended Service",
    "Reason",
    "Google Maps",
    "Last Updated",
]


def export_to_csv(leads, filename=CSV_FILE):

    if not leads:
        print("\nNo leads to save.")
        return

    # ----------------------------------------
    # New search results
    # ----------------------------------------

    new_df = pd.DataFrame(leads)

    # Make sure every expected column exists
    for column in COLUMNS:

        if column not in new_df.columns:
            new_df[column] = ""

    new_df = new_df[COLUMNS]

    # Update timestamp
    new_df["Last Updated"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # ----------------------------------------
    # Load existing database
    # ----------------------------------------

    if os.path.exists(filename):

        try:

            old_df = pd.read_csv(
                filename,
                dtype=str
            )

        except Exception:

            old_df = pd.DataFrame()

    else:

        old_df = pd.DataFrame()

    # ----------------------------------------
    # Make sure old database has correct columns
    # ----------------------------------------

    if not old_df.empty:

        for column in COLUMNS:

            if column not in old_df.columns:
                old_df[column] = ""

        old_df = old_df[COLUMNS]

    # ----------------------------------------
    # Merge old + new
    # ----------------------------------------

    if old_df.empty:

        combined = new_df

    else:

        combined = pd.concat(
            [
                old_df,
                new_df
            ],
            ignore_index=True
        )

        # Remove empty Place IDs from duplicate logic
        combined["Place ID"] = (
            combined["Place ID"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # Keep newest data for existing businesses
        # combined = combined.drop_duplicates(
        #     subset=["Place ID"],
        #     keep="last"
        # )
        
        has_place_id = combined["Place ID"].ne("")

        with_id = combined[has_place_id].drop_duplicates(
            subset=["Place ID"],
           keep="last"
        )

        without_id = combined[~has_place_id]

        combined = pd.concat(
           [
               with_id,
              without_id
          ],
          ignore_index=True
        )
        

    # ----------------------------------------
    # Clean numeric fields
    # ----------------------------------------

    combined["Rating"] = pd.to_numeric(
        combined["Rating"],
        errors="coerce"
    )

    combined["Reviews"] = pd.to_numeric(
        combined["Reviews"],
        errors="coerce"
    )

    combined["Lead Score"] = pd.to_numeric(
        combined["Lead Score"],
        errors="coerce"
    )

    # ----------------------------------------
    # Sort by Lead Score
    # ----------------------------------------

    combined = combined.sort_values(
        by="Lead Score",
        ascending=False,
        na_position="last"
    )

    # ----------------------------------------
    # Save clean CSV
    # ----------------------------------------

    combined.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig"
    )

    # ----------------------------------------
    # Statistics
    # ----------------------------------------

    print("\n======================================")
    print("          LEAD DATABASE")
    print("======================================")

    print(
        f"Total leads : {len(combined)}"
    )

    print(
        f"Saved to    : {filename}"
    )

    print("======================================\n")

