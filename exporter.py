import os
import pandas as pd
from datetime import datetime


CSV_FILE = "leads.csv"


# ============================================================
# DATABASE SCHEMA
# ============================================================

COLUMNS = [

    # --------------------------------------------------------
    # Google Business Information
    # --------------------------------------------------------

    "Place ID",
    "Business Name",
    "Category",
    "Location",
    "Phone",
    "Address",
    "Rating",
    "Reviews",

    # --------------------------------------------------------
    # Online Presence
    # --------------------------------------------------------

    "Online Presence",
    "Website",

    # --------------------------------------------------------
    # Website Verification
    # --------------------------------------------------------

    "Website Status",
    "HTTP Status",
    "HTTPS",
    "Response Time",
    "Final URL",
    "Website Error",

    # --------------------------------------------------------
    # Opportunity Scoring
    # --------------------------------------------------------

    "Business Score",
    "Digital Opportunity Score",
    "Opportunity Score",
    "Opportunity Priority",
    "Opportunity Services",
    "Opportunity Reasons",

    # --------------------------------------------------------
    # Google Maps
    # --------------------------------------------------------

    "Google Maps",

    # --------------------------------------------------------
    # Lead Management / CRM
    # --------------------------------------------------------

    "Lead Status",
    "Contacted",
    "Contact Date",
    "Follow-up Date",
    "Contact Method",
    "Notes",

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    "Last Updated",
]


# ============================================================
# EXPORT FUNCTION
# ============================================================

def export_to_csv(leads, filename=CSV_FILE):
    """
    Save leads to the persistent CSV database.

    Database rules:

    1. Place ID is the unique business identifier.
    2. Existing businesses are updated.
    3. New businesses are added.
    4. Duplicate Place IDs are removed.
    5. Old scoring columns are removed.
    6. Database is sorted by Opportunity Score.
    7. CRM fields are preserved when an existing lead is updated.
    """

    if not leads:

        print("\nNo leads to save.")

        return

    # ========================================================
    # PREPARE NEW SEARCH RESULTS
    # ========================================================

    new_df = pd.DataFrame(leads)

    # Make sure every database column exists

    for column in COLUMNS:

        if column not in new_df.columns:

            new_df[column] = ""

    # Keep only our official schema

    new_df = new_df[COLUMNS]

    # ========================================================
    # DEFAULT CRM VALUES
    # ========================================================

    if "Lead Status" not in new_df.columns:

        new_df["Lead Status"] = "NEW"

    else:

        new_df["Lead Status"] = (
            new_df["Lead Status"]
            .fillna("")
            .replace("", "NEW")
        )

    if "Contacted" not in new_df.columns:

        new_df["Contacted"] = "NO"

    else:

        new_df["Contacted"] = (
            new_df["Contacted"]
            .fillna("")
            .replace("", "NO")
        )

    # ========================================================
    # UPDATE TIMESTAMP
    # ========================================================

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    new_df["Last Updated"] = current_time

    # ========================================================
    # LOAD EXISTING DATABASE
    # ========================================================

    if os.path.exists(filename):

        try:

            old_df = pd.read_csv(
                filename,
                dtype=str
            )

        except Exception as error:

            print(
                "\nWarning: Could not read existing "
                f"database: {error}"
            )

            old_df = pd.DataFrame()

    else:

        old_df = pd.DataFrame()

    # ========================================================
    # NORMALIZE EXISTING DATABASE
    # ========================================================

    if not old_df.empty:

        # ----------------------------------------------------
        # Remove old scoring columns
        # ----------------------------------------------------

        old_columns_to_remove = [
            "Lead Score",
            "Priority",
            "Recommended Service",
            "Reason",
        ]

        for column in old_columns_to_remove:

            if column in old_df.columns:

                old_df = old_df.drop(
                    columns=[column]
                )

        # ----------------------------------------------------
        # Add missing new columns
        # ----------------------------------------------------

        for column in COLUMNS:

            if column not in old_df.columns:

                old_df[column] = ""

        # ----------------------------------------------------
        # Keep only official schema
        # ----------------------------------------------------

        old_df = old_df[COLUMNS]

    # ========================================================
    # MERGE OLD + NEW
    # ========================================================

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

    # ========================================================
    # CLEAN PLACE IDs
    # ========================================================

    combined["Place ID"] = (
        combined["Place ID"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # ========================================================
    # PRESERVE CRM DATA
    # ========================================================
    #
    # If a business already exists and we search again,
    # Google data should update, BUT:
    #
    # Lead Status
    # Contacted
    # Contact Date
    # Follow-up Date
    # Contact Method
    # Notes
    #
    # should NOT be accidentally erased.
    #
    # ========================================================

    crm_columns = [
        "Lead Status",
        "Contacted",
        "Contact Date",
        "Follow-up Date",
        "Contact Method",
        "Notes",
    ]

    # Build a dictionary of existing CRM information

    existing_crm = {}

    if not old_df.empty:

        for _, row in old_df.iterrows():

            place_id = str(
                row.get("Place ID", "")
            ).strip()

            if not place_id:

                continue

            existing_crm[place_id] = {
                column: str(
                    row.get(column, "")
                ).strip()
                for column in crm_columns
            }

    # Apply old CRM information to new results

    for index, row in new_df.iterrows():

        place_id = str(
            row.get("Place ID", "")
        ).strip()

        if place_id in existing_crm:

            for column in crm_columns:

                old_value = existing_crm[
                    place_id
                ].get(column, "")

                if old_value:

                    new_df.at[
                        index,
                        column
                    ] = old_value

    # Rebuild combined dataframe after CRM preservation

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

    # ========================================================
    # REMOVE DUPLICATE BUSINESSES
    # ========================================================
    #
    # Place ID is the unique key.
    #
    # Old record
    #     ↓
    # New record
    #     ↓
    # Keep newest Google/website/scoring data
    #
    # ========================================================

    combined["Place ID"] = (
        combined["Place ID"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

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

    # ========================================================
    # CLEAN NUMERIC COLUMNS
    # ========================================================

    numeric_columns = [
        "Rating",
        "Reviews",
        "Business Score",
        "Digital Opportunity Score",
        "Opportunity Score",
    ]

    for column in numeric_columns:

        combined[column] = pd.to_numeric(
            combined[column],
            errors="coerce"
        )

    # ========================================================
    # CLEAN TEXT COLUMNS
    # ========================================================

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

        "Google Maps",

        "Lead Status",
        "Contacted",
        "Contact Date",
        "Follow-up Date",
        "Contact Method",
        "Notes",

        "Last Updated",
    ]

    for column in text_columns:

        combined[column] = (
            combined[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # ========================================================
    # DEFAULT CRM VALUES FOR OLD RECORDS
    # ========================================================

    combined["Lead Status"] = (
        combined["Lead Status"]
        .replace("", "NEW")
    )

    combined["Contacted"] = (
        combined["Contacted"]
        .replace("", "NO")
    )

    # ========================================================
    # SORT DATABASE
    # ========================================================
    #
    # Highest opportunity first.
    #
    # Primary:
    #     Opportunity Score
    #
    # Secondary:
    #     Business Score
    #
    # ========================================================

    combined = combined.sort_values(
        by=[
            "Opportunity Score",
            "Business Score"
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

    # ========================================================
    # SAVE DATABASE
    # ========================================================

    combined.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # STATISTICS
    # ========================================================

    total_leads = len(combined)

    # ----------------------------------------
    # Opportunity priority
    # ----------------------------------------

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

    unclassified_count = (
        total_leads
        - (
            hot_count
            + high_count
            + medium_count
            + low_count
        )
    )

    # ----------------------------------------
    # Lead status
    # ----------------------------------------

    status_series = (
        combined["Lead Status"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    new_count = (
        status_series == "NEW"
    ).sum()

    contacted_count = (
        status_series == "CONTACTED"
    ).sum()

    interested_count = (
        status_series == "INTERESTED"
    ).sum()

    follow_up_count = (
        status_series == "FOLLOW_UP"
    ).sum()

    won_count = (
        status_series == "WON"
    ).sum()

    lost_count = (
        status_series == "LOST"
    ).sum()

    # ========================================================
    # DISPLAY DATABASE SUMMARY
    # ========================================================

    print("\n======================================")
    print("          LEAD DATABASE")
    print("======================================")

    print(
        f"Total leads       : {total_leads}"
    )

    print("\nOpportunity:")

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

    print("\nLead Status:")

    print(
        f"NEW               : {new_count}"
    )

    print(
        f"CONTACTED         : {contacted_count}"
    )

    print(
        f"INTERESTED        : {interested_count}"
    )

    print(
        f"FOLLOW_UP         : {follow_up_count}"
    )

    print(
        f"WON               : {won_count}"
    )

    print(
        f"LOST              : {lost_count}"
    )

    print(
        f"\nSaved to          : {filename}"
    )

    print("======================================\n")