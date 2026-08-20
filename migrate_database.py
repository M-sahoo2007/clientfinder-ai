import os
import pandas as pd

from scoring import calculate_opportunity_score


CSV_FILE = "leads.csv"


VALID_PRIORITIES = {
    "HOT",
    "HIGH",
    "MEDIUM",
    "LOW",
}


SCORING_COLUMNS = [
    "Business Score",
    "Digital Opportunity Score",
    "Opportunity Score",
    "Opportunity Priority",
    "Opportunity Services",
    "Opportunity Reasons",
]


NUMERIC_COLUMNS = [
    "Rating",
    "Reviews",
    "Business Score",
    "Digital Opportunity Score",
    "Opportunity Score",
    "Lead Score",
]


def clean_value(value):
    """Safely convert a CSV value to a clean string."""

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    return str(value).strip()


def normalize_column_name(column):
    """Normalize a column name."""

    name = str(column).strip()

    name = name.replace("_", " ")

    name = " ".join(name.split())

    return name


def normalize_columns(df):
    """
    Normalize old/new scoring column names.

    Examples:
        OpportunityScore
        Opportunity_Score
        Opportunity Score

    become:
        Opportunity Score
    """

    rename_map = {}

    for column in df.columns:

        normalized = normalize_column_name(column)

        compact = (
            normalized
            .lower()
            .replace(" ", "")
        )

        mappings = {
            "opportunityscore": "Opportunity Score",
            "opportunitypriority": "Opportunity Priority",
            "businessscore": "Business Score",
            "digitalopportunityscore": "Digital Opportunity Score",
            "opportunityservices": "Opportunity Services",
            "opportunityreasons": "Opportunity Reasons",
        }

        if compact in mappings:

            rename_map[column] = mappings[compact]

    if rename_map:

        df = df.rename(
            columns=rename_map
        )

    return df


def ensure_columns(df):
    """Ensure required scoring columns exist."""

    for column in SCORING_COLUMNS:

        if column not in df.columns:

            df[column] = ""

    # Lead Score is optional in older databases.
    # Create it so sorting and numeric cleanup are safe.

    if "Lead Score" not in df.columns:

        df["Lead Score"] = ""

    return df


def build_lead_from_row(df, index):
    """Convert one CSV row into a scoring dictionary."""

    lead = {}

    for column in df.columns:

        lead[column] = clean_value(
            df.at[
                index,
                column
            ]
        )

    return lead


def needs_migration(df, index):
    """
    Return True when a record needs opportunity scoring.
    """

    score = clean_value(
        df.at[
            index,
            "Opportunity Score"
        ]
    )

    priority = clean_value(
        df.at[
            index,
            "Opportunity Priority"
        ]
    ).upper()

    if (
        score != ""
        and priority in VALID_PRIORITIES
    ):
        return False

    return True


def clean_numeric_columns(df):
    """Convert numeric database fields safely."""

    for column in NUMERIC_COLUMNS:

        if column not in df.columns:

            continue

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


def clean_text_columns(df):
    """Clean important text columns."""

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

        if column not in df.columns:

            continue

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    return df


def sort_database(df):
    """
    Sort safely even if older CSV files are
    missing optional columns.
    """

    sort_columns = []

    if "Opportunity Score" in df.columns:
        sort_columns.append(
            "Opportunity Score"
        )

    if "Lead Score" in df.columns:
        sort_columns.append(
            "Lead Score"
        )

    if not sort_columns:

        return df.reset_index(
            drop=True
        )

    df = df.sort_values(
        by=sort_columns,
        ascending=[
            False
        ] * len(sort_columns),
        na_position="last",
    )

    return df.reset_index(
        drop=True
    )


def migrate_database():

    print("\n======================================")
    print("       CLIENTFINDER DATABASE")
    print("          MIGRATION TOOL")
    print("======================================\n")

    # ========================================
    # CHECK DATABASE
    # ========================================

    if not os.path.exists(CSV_FILE):

        print(
            f"Database not found: {CSV_FILE}"
        )

        return

    # ========================================
    # LOAD DATABASE
    # ========================================

    try:

        df = pd.read_csv(
            CSV_FILE,
            dtype=str,
            keep_default_na=False,
        )

    except Exception as error:

        print(
            "\nCould not read database:"
        )

        print(error)

        return

    print(
        f"Records loaded: {len(df)}"
    )

    # ========================================
    # CONVERT TO OBJECT DTYPE
    # ========================================

    # This prevents errors such as:
    #
    # Invalid value '25' for dtype 'str'
    #
    # when scoring.py returns numeric values.

    df = df.astype(object)

    # ========================================
    # NORMALIZE COLUMNS
    # ========================================

    df = normalize_columns(df)

    # ========================================
    # ENSURE REQUIRED COLUMNS
    # ========================================

    df = ensure_columns(df)

    # ========================================
    # MIGRATION COUNTERS
    # ========================================

    migrated = 0
    skipped = 0
    failed = 0

    # ========================================
    # PROCESS RECORDS
    # ========================================

    for index in df.index:

        if "Business Name" in df.columns:

            business_name = clean_value(
                df.at[
                    index,
                    "Business Name"
                ]
            )

        else:

            business_name = "Unknown"

        # ------------------------------------
        # Skip already-scored businesses
        # ------------------------------------

        if not needs_migration(
            df,
            index
        ):

            skipped += 1

            continue

        # ------------------------------------
        # Build lead
        # ------------------------------------

        lead = build_lead_from_row(
            df,
            index
        )

        # ------------------------------------
        # Calculate opportunity score
        # ------------------------------------

        try:

            result = calculate_opportunity_score(
                lead
            )

        except Exception as error:

            failed += 1

            print(
                f"\nFAILED: {business_name}"
            )

            print(
                f"Reason: {error}"
            )

            continue

        # ------------------------------------
        # Save calculated scoring
        # ------------------------------------

        for key, value in result.items():

            if key not in df.columns:

                df[key] = ""

            df.at[
                index,
                key
            ] = value

        migrated += 1

        print(
            f"Migrated: {business_name}"
        )

    # ========================================
    # CLEAN DATA
    # ========================================

    df = clean_numeric_columns(df)

    df = clean_text_columns(df)

    # ========================================
    # SORT DATABASE
    # ========================================

    df = sort_database(df)

    # ========================================
    # SAVE DATABASE
    # ========================================

    try:

        df.to_csv(
            CSV_FILE,
            index=False,
            encoding="utf-8-sig",
        )

    except Exception as error:

        print(
            "\nCould not save database:"
        )

        print(error)

        return

    # ========================================
    # VERIFY PRIORITIES
    # ========================================

    priority_series = (
        df["Opportunity Priority"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    unclassified = (
        ~priority_series.isin(
            VALID_PRIORITIES
        )
    ).sum()

    # ========================================
    # PRIORITY COUNTS
    # ========================================

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

    # ========================================
    # DATABASE SUMMARY
    # ========================================

    print("\n======================================")
    print("       MIGRATION COMPLETED")
    print("======================================")

    print(
        f"Total records     : {len(df)}"
    )

    print(
        f"Records migrated  : {migrated}"
    )

    print(
        f"Records skipped    : {skipped}"
    )

    print(
        f"Records failed    : {failed}"
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
        f"Unclassified      : {unclassified}"
    )

    print(
        f"Database saved    : {CSV_FILE}"
    )

    print("======================================\n")

    # ========================================
    # FINAL VALIDATION
    # ========================================

    if (
        unclassified == 0
        and failed == 0
    ):

        print(
            "SUCCESS: Database migration completed."
        )

        print(
            "All leads have valid opportunity scoring."
        )

    elif failed > 0:

        print(
            "WARNING: Some leads failed to migrate."
        )

    else:

        print(
            "WARNING: Some leads are still unclassified."
        )


if __name__ == "__main__":

    migrate_database()