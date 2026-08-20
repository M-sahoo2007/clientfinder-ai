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

    # Online presence
    "Online Presence",
    "Website",

    # Website verification
    "Website Status",
    "HTTP Status",
    "HTTPS",
    "Response Time",
    "Final URL",
    "Website Error",

    # Opportunity scoring
    "Business Score",
    "Digital Opportunity Score",
    "Opportunity Score",
    "Opportunity Priority",
    "Opportunity Services",
    "Opportunity Reasons",

    # Original analysis
    "Lead Score",
    "Priority",
    "Recommended Service",
    "Reason",

    # Google Maps
    "Google Maps",

    # Database
    "Last Updated",
]


def export_to_csv(leads, filename=CSV_FILE):
    """
    Save leads to the persistent CSV database.

    Rules:
    - Place ID is the unique business identifier.
    - Existing businesses are replaced with the newest data.
    - New businesses are appended.
    - Duplicate Place IDs are removed.
    - Database is sorted by Opportunity Score.
    """

    if not leads:
        print("\nNo leads to save.")
        return

    # ========================================
    # PREPARE NEW SEARCH RESULTS
    # ========================================

    new_df = pd.DataFrame(leads)

    for column in COLUMNS:

        if column not in new_df.columns:
            new_df[column] = ""

    new_df = new_df[COLUMNS]

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    new_df["Last Updated"] = current_time

    # ========================================
    # LOAD EXISTING DATABASE
    # ========================================

    if os.path.exists(filename):

        try:

            old_df = pd.read_csv(
                filename,
                dtype=str
            )

        except Exception as error:

            print(
                "\nWarning: Could not read "
                f"existing database: {error}"
            )

            old_df = pd.DataFrame()

    else:

        old_df = pd.DataFrame()

    # ========================================
    # NORMALIZE OLD DATABASE
    # ========================================

    if not old_df.empty:

        for column in COLUMNS:

            if column not in old_df.columns:
                old_df[column] = ""

        old_df = old_df[COLUMNS]

    # ========================================
    # MERGE OLD + NEW
    # ========================================

    if old_df.empty:

        combined = new_df.copy()

    else:

        combined = pd.concat(
            [
                old_df,
                new_df
            ],
            ignore_index=True
        )

    # ========================================
    # CLEAN PLACE IDs
    # ========================================

    combined["Place ID"] = (
        combined["Place ID"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # ========================================
    # REMOVE DUPLICATE BUSINESSES
    # ========================================
    #
    # Place ID is our unique identifier.
    #
    # If the same Place ID appears twice:
    #
    # OLD DATA
    #    ↓
    # NEW DATA
    #    ↓
    # KEEP NEW DATA
    #
    # ========================================

    has_place_id = (
        combined["Place ID"] != ""
    )

    with_place_id = combined[
        has_place_id
    ].drop_duplicates(
        subset=["Place ID"],
        keep="last"
    )

    without_place_id = combined[
        ~has_place_id
    ]

    combined = pd.concat(
        [
            with_place_id,
            without_place_id
        ],
        ignore_index=True
    )

    # ========================================
    # CLEAN NUMERIC COLUMNS
    # ========================================

    numeric_columns = [
        "Rating",
        "Reviews",
        "Business Score",
        "Digital Opportunity Score",
        "Opportunity Score",
        "Lead Score",
    ]

    for column in numeric_columns:

        combined[column] = pd.to_numeric(
            combined[column],
            errors="coerce"
        )

    # ========================================
    # CLEAN TEXT COLUMNS
    # ========================================

    text_columns = [
        "Place ID",
        "Business Name",
        "Category",
        "Location",
        "Phone",
        "Address",
        "Online Presence",
        "Website",
        "Website Status",
        "HTTP Status",
        "HTTPS",
        "Response Time",
        "Final URL",
        "Website Error",
        "Opportunity Priority",
        "Opportunity Services",
        "Opportunity Reasons",
        "Priority",
        "Recommended Service",
        "Reason",
        "Google Maps",
        "Last Updated",
    ]

    for column in text_columns:

        combined[column] = (
            combined[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # ========================================
    # SORT DATABASE
    # ========================================
    #
    # 1. Opportunity Score
    # 2. Lead Score
    #
    # Highest-value opportunities appear first.
    #
    # ========================================

    combined = combined.sort_values(
        by=[
            "Opportunity Score",
            "Lead Score"
        ],
        ascending=[
            False,
            False
        ],
        na_position="last"
    )

    combined = combined.reset_index(
        drop=True
    )

    # ========================================
    # SAVE DATABASE
    # ========================================

    combined.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================
    # DATABASE STATISTICS
    # ========================================

    total_leads = len(combined)

    priority_series = (
        combined["Opportunity Priority"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    hot_count = (
        priority_series == "HOT"
    ).sum()

    high_count = (
        priority_series == "HIGH"
    ).sum()

    medium_count = (
        priority_series == "MEDIUM"
    ).sum()

    low_count = (
        priority_series == "LOW"
    ).sum()

    classified_count = (
        hot_count
        + high_count
        + medium_count
        + low_count
    )

    unclassified_count = (
        total_leads
        - classified_count
    )

    # ========================================
    # DISPLAY DATABASE SUMMARY
    # ========================================

    print("\n======================================")
    print("          LEAD DATABASE")
    print("======================================")

    print(
        f"Total leads       : {total_leads}"
    )

    print(
        f"HOT leads         : {hot_count}"
    )

    print(
        f"HIGH leads        : {high_count}"
    )

    print(
        f"MEDIUM leads      : {medium_count}"
    )

    print(
        f"LOW leads         : {low_count}"
    )

    print(
        f"Unclassified      : {unclassified_count}"
    )

    print(
        f"Saved to          : {filename}"
    )

    print("======================================\n")