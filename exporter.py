import os
import pandas as pd
from datetime import datetime


CSV_FILE = "leads.csv"


# ============================================================
# DATABASE SCHEMA
# ============================================================

COLUMNS = [

    # Google Business Information
    "Place ID",
    "Business Name",
    "Category",
    "Location",
    "Phone",
    "Address",
    "Rating",
    "Reviews",

    # Online Presence
    "Online Presence",
    "Website",

    # Website Verification
    "Website Status",
    "HTTP Status",
    "HTTPS",
    "Response Time",
    "Final URL",
    "Website Error",

    # Opportunity Scoring
    "Business Score",
    "Digital Opportunity Score",
    "Opportunity Score",
    "Opportunity Priority",
    "Opportunity Services",
    "Opportunity Reasons",

    # Google Maps
    "Google Maps",

    # CRM
    "Lead Status",
    "Contacted",
    "Contact Date",
    "Follow-up Date",
    "Contact Method",
    "Notes",

    # Database
    "Last Updated",
]


CRM_COLUMNS = [
    "Lead Status",
    "Contacted",
    "Contact Date",
    "Follow-up Date",
    "Contact Method",
    "Notes",
]


NUMERIC_COLUMNS = [
    "Rating",
    "Reviews",
    "Business Score",
    "Digital Opportunity Score",
    "Opportunity Score",
]


TEXT_COLUMNS = [
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


# ============================================================
# HELPERS
# ============================================================

def normalize_dataframe(df):
    """
    Make sure a dataframe follows the official database schema.
    """

    if df is None or df.empty:
        return pd.DataFrame(columns=COLUMNS)

    df = df.copy()

    # Add missing columns
    for column in COLUMNS:
        if column not in df.columns:
            df[column] = ""

    # Remove columns outside the official schema
    df = df[COLUMNS]

    return df


def clean_dataframe(df):
    """
    Clean numeric and text fields.
    """

    df = df.copy()

    # Numeric fields
    for column in NUMERIC_COLUMNS:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Text fields
    for column in TEXT_COLUMNS:

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Default CRM values
    df["Lead Status"] = (
        df["Lead Status"]
        .replace("", "NEW")
    )

    df["Contacted"] = (
        df["Contacted"]
        .replace("", "NO")
    )

    return df


def load_existing_database(filename):
    """
    Load the existing leads database.

    Returns an empty dataframe if the database
    does not exist or cannot be read.
    """

    if not os.path.exists(filename):
        return pd.DataFrame(columns=COLUMNS)

    try:

        df = pd.read_csv(
            filename,
            dtype=str
        )

        return normalize_dataframe(df)

    except Exception as error:

        print(
            "\nWarning: Could not read existing "
            f"database: {error}"
        )

        return pd.DataFrame(columns=COLUMNS)


def get_existing_crm_data(old_df):
    """
    Build a Place ID -> CRM information dictionary.

    This allows us to update Google/website data
    without destroying manually entered CRM data.
    """

    crm_data = {}

    if old_df.empty:
        return crm_data

    for _, row in old_df.iterrows():

        place_id = str(
            row.get("Place ID", "")
        ).strip()

        if not place_id:
            continue

        crm_data[place_id] = {
            column: str(
                row.get(column, "")
            ).strip()
            for column in CRM_COLUMNS
        }

    return crm_data


def preserve_crm_data(new_df, existing_crm):
    """
    Restore existing CRM information onto refreshed leads.
    """

    new_df = new_df.copy()

    for index, row in new_df.iterrows():

        place_id = str(
            row.get("Place ID", "")
        ).strip()

        if not place_id:
            continue

        if place_id not in existing_crm:
            continue

        old_crm = existing_crm[place_id]

        for column in CRM_COLUMNS:

            old_value = old_crm.get(
                column,
                ""
            )

            if old_value:
                new_df.at[
                    index,
                    column
                ] = old_value

    return new_df


def remove_duplicates(df):
    """
    Remove duplicate businesses using Place ID.

    The newest record wins.
    """

    df = df.copy()

    df["Place ID"] = (
        df["Place ID"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    has_place_id = (
        df["Place ID"] != ""
    )

    with_place_id = df[
        has_place_id
    ].drop_duplicates(
        subset=["Place ID"],
        keep="last"
    )

    without_place_id = df[
        ~has_place_id
    ]

    return pd.concat(
        [
            with_place_id,
            without_place_id
        ],
        ignore_index=True
    )


def sort_database(df):
    """
    Sort highest-value opportunities first.
    """

    return df.sort_values(
        by=[
            "Opportunity Score",
            "Business Score",
        ],
        ascending=[
            False,
            False,
        ],
        na_position="last"
    ).reset_index(drop=True)


# ============================================================
# EXPORT DATABASE
# ============================================================

def export_to_csv(
    leads,
    filename=CSV_FILE
):
    """
    Save leads to the persistent CSV database.

    Rules:

    1. Place ID is the unique business identifier.
    2. Existing businesses are updated.
    3. New businesses are appended.
    4. Duplicate Place IDs are removed.
    5. Existing CRM information is preserved.
    6. Latest Google/website/scoring data replaces old data.
    7. Database is sorted by Opportunity Score.
    """

    if not leads:

        print(
            "\nNo leads to save."
        )

        return

    # ========================================================
    # PREPARE NEW LEADS
    # ========================================================

    new_df = pd.DataFrame(leads)

    new_df = normalize_dataframe(
        new_df
    )

    # ========================================================
    # DEFAULT CRM VALUES
    # ========================================================

    new_df["Lead Status"] = (
        new_df["Lead Status"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    new_df.loc[
        new_df["Lead Status"] == "",
        "Lead Status"
    ] = "NEW"

    new_df["Contacted"] = (
        new_df["Contacted"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    new_df.loc[
        new_df["Contacted"] == "",
        "Contacted"
    ] = "NO"

    # ========================================================
    # LOAD OLD DATABASE
    # ========================================================

    old_df = load_existing_database(
        filename
    )

    # ========================================================
    # SAVE EXISTING CRM INFORMATION
    # ========================================================

    existing_crm = get_existing_crm_data(
        old_df
    )

    # Apply old CRM fields to refreshed leads
    new_df = preserve_crm_data(
        new_df,
        existing_crm
    )

    # ========================================================
    # UPDATE TIMESTAMP
    # ========================================================

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    new_df["Last Updated"] = current_time

    # ========================================================
    # MERGE OLD + NEW
    # ========================================================

    if old_df.empty:

        combined = new_df.copy()

    else:

        combined = pd.concat(
            [
                old_df,
                new_df,
            ],
            ignore_index=True
        )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    combined = remove_duplicates(
        combined
    )

    # ========================================================
    # CLEAN DATA
    # ========================================================

    combined = clean_dataframe(
        combined
    )

    # ========================================================
    # SORT DATABASE
    # ========================================================

    combined = sort_database(
        combined
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

    total_leads = len(
        combined
    )

    # --------------------------------------------------------
    # Opportunity statistics
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Lead status statistics
    # --------------------------------------------------------

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

    print(
        "\n======================================"
    )

    print(
        "          LEAD DATABASE"
    )

    print(
        "======================================"
    )

    print(
        f"Total leads       : {total_leads}"
    )

    print(
        "\nOpportunity:"
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
        "\nLead Status:"
    )

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

    print(
        "======================================\n"
    )