import os
from datetime import datetime

import pandas as pd


# ==========================================
# DATABASE FILES
# ==========================================

CSV_FILE = "leads.csv"
ACTIVITY_FILE = "crm_activities.csv"


# ==========================================
# VALID CRM STATUSES
# ==========================================

VALID_STATUSES = {
    "NEW",
    "CONTACTED",
    "INTERESTED",
    "FOLLOW_UP",
    "WON",
    "LOST",
}


# ==========================================
# ACTIVITY DATABASE COLUMNS
# ==========================================

ACTIVITY_COLUMNS = [
    "Activity ID",
    "Place ID",
    "Business Name",
    "Activity Date",
    "Activity Type",
    "Details",
    "Status",
    "Follow-up Date",
]


# ==========================================
# CRM DATABASE COLUMNS
# ==========================================

CRM_COLUMNS = [
    "Place ID",
    "Business Name",
    "Phone",
    "Email",
    "Contact Person",
    "Contacted",
    "Contact Date",
    "Follow-up Date",
    "Contact Method",
    "Lead Status",
    "Deal Value",
    "Notes",
    "Created Date",
    "Last Updated",
]


# ==========================================
# CURRENT DATE / TIME
# ==========================================

def now_string():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ==========================================
# CLEAN VALUE
# ==========================================

def clean(value):
    """
    Convert None / NaN / pandas missing
    values into an empty string.
    """

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (
        TypeError,
        ValueError,
    ):
        pass

    return str(value).strip()


# ==========================================
# NORMALIZE UPDATE VALUE
# ==========================================

def normalize_update_value(
    key,
    value
):
    """
    Normalize values before writing them
    into the CSV-backed DataFrame.

    The CSV database is intentionally kept
    as string data, so numeric CRM values
    such as Deal Value are converted to strings.
    """

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (
        TypeError,
        ValueError,
    ):
        pass

    # --------------------------------------
    # Deal Value
    # --------------------------------------

    if key == "Deal Value":

        try:

            numeric_value = float(
                str(value)
                .replace(",", "")
                .strip()
            )

            if numeric_value < 0:
                return ""

            # Store clean integer when possible
            if numeric_value.is_integer():
                return str(
                    int(numeric_value)
                )

            return str(
                numeric_value
            )

        except (
            ValueError,
            TypeError,
        ):

            return clean(value)

    # --------------------------------------
    # Contacted
    # --------------------------------------

    if key == "Contacted":

        contacted = clean(
            value
        ).upper()

        if contacted in {
            "YES",
            "NO",
        }:
            return contacted

        return clean(value)

    # --------------------------------------
    # Lead Status
    # --------------------------------------

    if key == "Lead Status":

        return clean(
            value
        ).upper()

    # --------------------------------------
    # Everything else
    # --------------------------------------

    return clean(value)


# ==========================================
# LOAD LEADS DATABASE
# ==========================================

def load_leads(
    filename=CSV_FILE
):

    if not os.path.exists(filename):

        return pd.DataFrame()

    try:

        df = pd.read_csv(
            filename,
            dtype=str,
            keep_default_na=False,
        )

    except Exception as error:

        print(
            f"Could not load database: {error}"
        )

        return pd.DataFrame()

    # --------------------------------------
    # Make sure CRM columns exist
    # --------------------------------------

    required_columns = [

        "Place ID",
        "Business Name",

        "Phone",
        "Email",

        "Opportunity Score",
        "Opportunity Priority",

        "Lead Status",
        "Contacted",
        "Contact Person",

        "Contact Date",
        "Follow-up Date",
        "Contact Method",

        "Notes",
        "Deal Value",

        "Created Date",
        "Last Updated",
    ]

    for column in required_columns:

        if column not in df.columns:

            df[column] = ""

    # --------------------------------------
    # Clean missing values
    # --------------------------------------

    for column in df.columns:

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .replace(
                {
                    "nan": "",
                    "NaN": "",
                    "None": "",
                }
            )
            .str.strip()
        )

    return df


# ==========================================
# SAVE LEADS DATABASE
# ==========================================

def save_leads(
    df,
    filename=CSV_FILE
):

    if df is None:
        return False

    try:

        # Ensure missing values are blank
        df = df.copy()

        for column in df.columns:

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .replace(
                    {
                        "nan": "",
                        "NaN": "",
                        "None": "",
                    }
                )
            )

        df.to_csv(
            filename,
            index=False,
            encoding="utf-8-sig",
        )

        return True

    except Exception as error:

        print(
            f"Could not save database: {error}"
        )

        return False


# ==========================================
# FIND LEADS
# ==========================================

def find_leads(
    query,
    filename=CSV_FILE
):

    df = load_leads(
        filename
    )

    if df.empty:

        return df

    query = clean(
        query
    ).lower()

    if not query:

        return df.iloc[0:0]

    # --------------------------------------
    # Business name
    # --------------------------------------

    business_match = (
        df["Business Name"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            query,
            regex=False,
        )
    )

    # --------------------------------------
    # Place ID
    # --------------------------------------

    place_match = (
        df["Place ID"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            query,
            regex=False,
        )
    )

    # --------------------------------------
    # Phone
    # --------------------------------------

    phone_match = (
        df["Phone"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            query,
            regex=False,
        )
    )

    return df[
        business_match
        | place_match
        | phone_match
    ]


# ==========================================
# GET SINGLE LEAD
# ==========================================

def get_lead(
    place_id,
    filename=CSV_FILE
):

    df = load_leads(
        filename
    )

    if df.empty:

        return None, df

    target = clean(
        place_id
    )

    matches = df[
        df["Place ID"]
        .fillna("")
        .astype(str)
        .str.strip()
        == target
    ]

    if matches.empty:

        return None, df

    return (
        matches.index[0],
        df,
    )


# ==========================================
# UPDATE LEAD
# ==========================================

def update_lead(
    place_id,
    updates,
    filename=CSV_FILE
):
    """
    Update a CRM lead using Place ID.

    Important:
    The CSV database is loaded as strings.
    Therefore every update is normalized
    before being assigned to the DataFrame.

    This prevents errors such as:

        Invalid value '25000.0'
        for dtype 'str'
    """

    if not isinstance(
        updates,
        dict
    ):

        return (
            False,
            "Updates must be a dictionary.",
        )

    index, df = get_lead(
        place_id,
        filename,
    )

    if index is None:

        return (
            False,
            "Lead not found.",
        )

    # --------------------------------------
    # Validate Lead Status
    # --------------------------------------

    if "Lead Status" in updates:

        status = clean(
            updates["Lead Status"]
        ).upper()

        if status not in VALID_STATUSES:

            return (
                False,
                f"Invalid lead status: {status}",
            )

        updates = updates.copy()

        updates[
            "Lead Status"
        ] = status

    # --------------------------------------
    # Apply updates safely
    # --------------------------------------

    for key, value in updates.items():

        if key not in df.columns:

            df[key] = ""

        normalized_value = (
            normalize_update_value(
                key,
                value,
            )
        )

        # Convert column to object/string-safe
        # before assigning.
        if df[key].dtype.name.startswith(
            "string"
        ):

            df[key] = (
                df[key]
                .astype(object)
            )

        df.at[
            index,
            key,
        ] = normalized_value

    # --------------------------------------
    # Update timestamp
    # --------------------------------------

    if "Last Updated" not in df.columns:

        df["Last Updated"] = ""

    df.at[
        index,
        "Last Updated",
    ] = now_string()

    # --------------------------------------
    # Save database
    # --------------------------------------

    saved = save_leads(
        df,
        filename,
    )

    if not saved:

        return (
            False,
            "Could not save lead database.",
        )

    return (
        True,
        "Lead updated successfully.",
    )


# ==========================================
# ADD CRM ACTIVITY
# ==========================================

def append_activity(
    place_id,
    business_name,
    activity_type,
    details="",
    status="",
    follow_up_date="",
    filename=ACTIVITY_FILE,
):

    # --------------------------------------
    # Load activity database
    # --------------------------------------

    if os.path.exists(filename):

        try:

            df = pd.read_csv(
                filename,
                dtype=str,
                keep_default_na=False,
            )

        except Exception:

            df = pd.DataFrame(
                columns=ACTIVITY_COLUMNS
            )

    else:

        df = pd.DataFrame(
            columns=ACTIVITY_COLUMNS
        )

    # --------------------------------------
    # Ensure columns exist
    # --------------------------------------

    for column in ACTIVITY_COLUMNS:

        if column not in df.columns:

            df[column] = ""

    # --------------------------------------
    # Generate activity ID
    # --------------------------------------

    activity_id = (
        datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )
        + "-"
        + str(
            len(df) + 1
        )
    )

    # --------------------------------------
    # Create activity
    # --------------------------------------

    new_activity = {

        "Activity ID":
            clean(activity_id),

        "Place ID":
            clean(place_id),

        "Business Name":
            clean(business_name),

        "Activity Date":
            now_string(),

        "Activity Type":
            clean(activity_type),

        "Details":
            clean(details),

        "Status":
            clean(status).upper(),

        "Follow-up Date":
            clean(follow_up_date),
    }

    # --------------------------------------
    # Append activity
    # --------------------------------------

    df = pd.concat(
        [
            df,
            pd.DataFrame(
                [new_activity]
            ),
        ],
        ignore_index=True,
    )

    df = df[
        ACTIVITY_COLUMNS
    ]

    # --------------------------------------
    # Save activity database
    # --------------------------------------

    try:

        df.to_csv(
            filename,
            index=False,
            encoding="utf-8-sig",
        )

    except Exception as error:

        print(
            f"Could not save activity: {error}"
        )


# ==========================================
# GET ACTIVITY HISTORY
# ==========================================

def get_activity_history(
    place_id,
    filename=ACTIVITY_FILE,
):

    if not os.path.exists(filename):

        return pd.DataFrame(
            columns=ACTIVITY_COLUMNS
        )

    try:

        df = pd.read_csv(
            filename,
            dtype=str,
            keep_default_na=False,
        )

    except Exception:

        return pd.DataFrame(
            columns=ACTIVITY_COLUMNS
        )

    for column in ACTIVITY_COLUMNS:

        if column not in df.columns:

            df[column] = ""

    target = clean(
        place_id
    )

    history = df[
        df["Place ID"]
        .fillna("")
        .astype(str)
        .str.strip()
        == target
    ].copy()

    if history.empty:

        return history

    return history.sort_values(
        by="Activity Date",
        ascending=False,
    )


# ==========================================
# STATUS COUNTS
# ==========================================

def status_counts(df):

    result = {
        status: 0
        for status in VALID_STATUSES
    }

    if df.empty:

        return result

    if "Lead Status" not in df.columns:

        return result

    statuses = (
        df["Lead Status"]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    for status in VALID_STATUSES:

        result[status] = int(
            (
                statuses
                == status
            ).sum()
        )

    return result


# ==========================================
# PRIORITY COUNTS
# ==========================================

def priority_counts(df):

    priorities = [
        "HOT",
        "HIGH",
        "MEDIUM",
        "LOW",
    ]

    result = {
        priority: 0
        for priority in priorities
    }

    if df.empty:

        return result

    if "Opportunity Priority" not in df.columns:

        return result

    values = (
        df["Opportunity Priority"]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    for priority in priorities:

        result[priority] = int(
            (
                values
                == priority
            ).sum()
        )

    return result


# ==========================================
# PIPELINE VALUE
# ==========================================

def pipeline_value(df):

    if df.empty:

        return 0.0

    if "Deal Value" not in df.columns:

        return 0.0

    values = pd.to_numeric(
        df["Deal Value"],
        errors="coerce",
    ).fillna(0)

    return float(
        values.sum()
    )


# ==========================================
# DUE / OVERDUE FOLLOW-UPS
# ==========================================

def due_followups(
    filename=CSV_FILE
):

    df = load_leads(
        filename
    )

    if df.empty:

        return pd.DataFrame()

    if "Follow-up Date" not in df.columns:

        return pd.DataFrame()

    # --------------------------------------
    # Convert dates safely
    # --------------------------------------

    dates = pd.to_datetime(
        df["Follow-up Date"],
        errors="coerce",
    ).dt.normalize()

    # --------------------------------------
    # Current day
    # --------------------------------------

    today = (
        pd.Timestamp.today()
        .normalize()
    )

    # --------------------------------------
    # Due / overdue
    # --------------------------------------

    result = df[
        dates.notna()
        & (
            dates <= today
        )
    ].copy()

    return result