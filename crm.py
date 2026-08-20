from datetime import datetime

import pandas as pd

from crm_database import (
    VALID_STATUSES,
    load_leads,
    find_leads,
    get_lead,
    update_lead,
    append_activity,
    get_activity_history,
    status_counts,
    priority_counts,
    pipeline_value,
    due_followups,
)


# ==========================================
# UI HELPERS
# ==========================================

def print_header(title):
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)


def pause():
    input("\nPress Enter to continue...")


def clean_display_value(value):
    """
    Convert pandas NaN/None values into blank strings.
    """
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    return str(value).strip()


def input_required(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("This field is required.")


# ==========================================
# SELECT LEAD
# ==========================================

def select_lead():
    query = input_required(
        "Search business / phone / Place ID: "
    )

    matches = find_leads(query)

    if matches.empty:
        print("\nNo matching leads found.")
        return None

    print("\nMatching leads:\n")

    for number, (_, row) in enumerate(
        matches.iterrows(),
        start=1
    ):
        business_name = clean_display_value(
            row.get("Business Name")
        )

        phone = clean_display_value(
            row.get("Phone")
        )

        status = clean_display_value(
            row.get("Lead Status")
        ) or "NEW"

        score = clean_display_value(
            row.get("Opportunity Score")
        )

        print(
            f"{number}. "
            f"{business_name} | "
            f"{phone} | "
            f"Status: {status} | "
            f"Score: {score}"
        )

    choice = input(
        "\nSelect lead number: "
    ).strip()

    try:
        selected_index = int(choice) - 1

        if selected_index < 0:
            raise IndexError

        selected = matches.iloc[
            selected_index
        ]

    except (ValueError, IndexError):
        print("Invalid selection.")
        return None

    return clean_display_value(
        selected.get("Place ID")
    )


# ==========================================
# SHOW LEAD
# ==========================================

def show_lead(place_id):
    index, df = get_lead(place_id)

    if index is None:
        print("Lead not found.")
        return

    row = df.loc[index]

    print_header("LEAD DETAILS")

    fields = [
        "Business Name",
        "Place ID",
        "Category",
        "Location",
        "Phone",
        "Email",
        "Contact Person",
        "Website",
        "Google Maps",
        "Rating",
        "Reviews",
        "Opportunity Score",
        "Opportunity Priority",
        "Opportunity Services",
        "Lead Status",
        "Contacted",
        "Contact Date",
        "Follow-up Date",
        "Contact Method",
        "Deal Value",
        "Notes",
        "Created Date",
        "Last Updated",
    ]

    for field in fields:
        value = clean_display_value(
            row.get(field, "")
        )

        print(
            f"{field:<24}: {value}"
        )


# ==========================================
# DASHBOARD
# ==========================================

def dashboard():
    df = load_leads()

    print_header(
        "CLIENTFINDER AI CRM DASHBOARD"
    )

    if df.empty:
        print("No leads in database.")
        return

    statuses = status_counts(df)
    priorities = priority_counts(df)

    print(
        f"Total leads          : {len(df)}"
    )

    # --------------------------------------
    # Pipeline
    # --------------------------------------

    print("\nPIPELINE")

    for status in [
        "NEW",
        "CONTACTED",
        "INTERESTED",
        "FOLLOW_UP",
        "WON",
        "LOST",
    ]:
        print(
            f"{status:<20}: "
            f"{statuses.get(status, 0)}"
        )

    # --------------------------------------
    # Opportunity
    # --------------------------------------

    print("\nOPPORTUNITY")

    for priority in [
        "HOT",
        "HIGH",
        "MEDIUM",
        "LOW",
    ]:
        print(
            f"{priority:<20}: "
            f"{priorities.get(priority, 0)}"
        )

    # --------------------------------------
    # Deal value
    # --------------------------------------

    print(
        f"\nPipeline value       : "
        f"₹{pipeline_value(df):,.2f}"
    )

    # --------------------------------------
    # Follow-ups
    # --------------------------------------

    try:
        due = due_followups()
        due_count = len(due)
    except Exception as error:
        print(
            f"Follow-up check error: {error}"
        )
        due_count = 0

    print(
        f"Due follow-ups       : "
        f"{due_count}"
    )


# ==========================================
# LIST LEADS
# ==========================================

def list_leads(
    df,
    title="LEADS"
):
    print_header(title)

    if df.empty:
        print("No leads found.")
        return

    columns = [
        "Business Name",
        "Phone",
        "Opportunity Score",
        "Opportunity Priority",
        "Lead Status",
        "Follow-up Date",
        "Deal Value",
    ]

    view = df.copy()

    for column in columns:
        if column not in view.columns:
            view[column] = ""

    view = view[columns].copy()

    for column in columns:
        view[column] = (
            view[column]
            .apply(clean_display_value)
        )

    print(
        view.to_string(index=False)
    )


# ==========================================
# SEARCH
# ==========================================

def search_menu():
    query = input_required(
        "Search: "
    )

    results = find_leads(query)

    list_leads(
        results,
        "SEARCH RESULTS"
    )


# ==========================================
# FILTER BY PRIORITY
# ==========================================

def priority_menu():
    priority = input_required(
        "Priority (HOT/HIGH/MEDIUM/LOW): "
    ).upper()

    valid = {
        "HOT",
        "HIGH",
        "MEDIUM",
        "LOW",
    }

    if priority not in valid:
        print("Invalid priority.")
        return

    df = load_leads()

    values = (
        df["Opportunity Priority"]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    results = df[
        values == priority
    ]

    list_leads(
        results,
        f"{priority} LEADS"
    )


# ==========================================
# FILTER BY STATUS
# ==========================================

def status_menu():
    status = input_required(
        "Status "
        "(NEW/CONTACTED/INTERESTED/"
        "FOLLOW_UP/WON/LOST): "
    ).upper()

    if status not in VALID_STATUSES:
        print("Invalid status.")
        return

    df = load_leads()

    values = (
        df["Lead Status"]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    results = df[
        values == status
    ]

    list_leads(
        results,
        f"{status} LEADS"
    )


# ==========================================
# UPDATE STATUS
# ==========================================

def update_status():
    place_id = select_lead()

    if not place_id:
        return

    status = input_required(
        "New status "
        "(NEW/CONTACTED/INTERESTED/"
        "FOLLOW_UP/WON/LOST): "
    ).upper()

    if status not in VALID_STATUSES:
        print("Invalid status.")
        return

    success, message = update_lead(
        place_id,
        {
            "Lead Status": status
        }
    )

    if success:
        index, df = get_lead(place_id)

        if index is not None:
            row = df.loc[index]

            append_activity(
                place_id,
                row.get(
                    "Business Name",
                    ""
                ),
                "STATUS_CHANGE",
                f"Status changed to {status}",
                status=status,
            )

    print(message)


# ==========================================
# RECORD CONTACT
# ==========================================

def record_contact():
    place_id = select_lead()

    if not place_id:
        return

    method = input(
        "Contact method "
        "(Call/WhatsApp/Email/Visit/Other): "
    ).strip()

    person = input(
        "Contact person: "
    ).strip()

    email = input(
        "Email: "
    ).strip()

    details = input(
        "Contact outcome/details: "
    ).strip()

    follow_up = input(
        "Next follow-up date "
        "(YYYY-MM-DD, blank if none): "
    ).strip()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    updates = {
        "Lead Status": "CONTACTED",
        "Contacted": "YES",
        "Contact Date": now,
        "Contact Method": method,
        "Contact Person": person,
        "Email": email,
    }

    # --------------------------------------
    # Add contact notes
    # --------------------------------------

    if details:
        index, df = get_lead(
            place_id
        )

        if index is not None:
            old_notes = clean_display_value(
                df.loc[index].get(
                    "Notes",
                    ""
                )
            )

            new_note = (
                f"[{now}] {details}"
            )

            if old_notes:
                updates["Notes"] = (
                    old_notes
                    + "\n"
                    + new_note
                )
            else:
                updates["Notes"] = new_note

    # --------------------------------------
    # Follow-up
    # --------------------------------------

    if follow_up:
        updates[
            "Follow-up Date"
        ] = follow_up

        updates[
            "Lead Status"
        ] = "FOLLOW_UP"

    success, message = update_lead(
        place_id,
        updates
    )

    if success:
        index, df = get_lead(
            place_id
        )

        if index is not None:
            row = df.loc[index]

            append_activity(
                place_id,
                row.get(
                    "Business Name",
                    ""
                ),
                "CONTACT",
                details,
                status=updates[
                    "Lead Status"
                ],
                follow_up_date=follow_up,
            )

    print(message)


# ==========================================
# SCHEDULE FOLLOW-UP
# ==========================================

def schedule_followup():
    place_id = select_lead()

    if not place_id:
        return

    follow_up = input_required(
        "Follow-up date "
        "(YYYY-MM-DD): "
    )

    note = input(
        "Follow-up note: "
    ).strip()

    updates = {
        "Lead Status": "FOLLOW_UP",
        "Follow-up Date": follow_up,
    }

    # --------------------------------------
    # Add note
    # --------------------------------------

    if note:
        index, df = get_lead(
            place_id
        )

        if index is not None:
            old_notes = clean_display_value(
                df.loc[index].get(
                    "Notes",
                    ""
                )
            )

            timestamp = (
                datetime.now()
                .strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            new_note = (
                f"[{timestamp}] "
                f"Follow-up: {note}"
            )

            if old_notes:
                updates["Notes"] = (
                    old_notes
                    + "\n"
                    + new_note
                )
            else:
                updates["Notes"] = new_note

    success, message = update_lead(
        place_id,
        updates
    )

    if success:
        index, df = get_lead(
            place_id
        )

        if index is not None:
            row = df.loc[index]

            append_activity(
                place_id,
                row.get(
                    "Business Name",
                    ""
                ),
                "FOLLOW_UP",
                note,
                status="FOLLOW_UP",
                follow_up_date=follow_up,
            )

    print(message)


# ==========================================
# ADD NOTE
# ==========================================

def add_note():
    place_id = select_lead()

    if not place_id:
        return

    note = input_required(
        "Note: "
    )

    index, df = get_lead(
        place_id
    )

    if index is None:
        print("Lead not found.")
        return

    old_notes = clean_display_value(
        df.loc[index].get(
            "Notes",
            ""
        )
    )

    timestamp = (
        datetime.now()
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    new_note = (
        f"[{timestamp}] {note}"
    )

    if old_notes:
        new_notes = (
            old_notes
            + "\n"
            + new_note
        )
    else:
        new_notes = new_note

    success, message = update_lead(
        place_id,
        {
            "Notes": new_notes
        }
    )

    if success:
        row = df.loc[index]

        append_activity(
            place_id,
            row.get(
                "Business Name",
                ""
            ),
            "NOTE",
            note,
        )

    print(message)


# ==========================================
# DEAL VALUE
# ==========================================

def deal_value():
    place_id = select_lead()

    if not place_id:
        return

    value = input_required(
        "Deal value in INR: "
    )

    try:
        value = float(
            value.replace(",", "")
        )

    except ValueError:
        print("Invalid amount.")
        return

    success, message = update_lead(
        place_id,
        {
            "Deal Value": value
        }
    )

    if success:
        index, df = get_lead(
            place_id
        )

        if index is not None:
            row = df.loc[index]

            append_activity(
                place_id,
                row.get(
                    "Business Name",
                    ""
                ),
                "DEAL_VALUE",
                f"Deal value set to ₹{value:,.2f}",
            )

    print(message)


# ==========================================
# ACTIVITY HISTORY
# ==========================================

def activity_history():
    place_id = select_lead()

    if not place_id:
        return

    history = get_activity_history(
        place_id
    )

    print_header(
        "ACTIVITY HISTORY"
    )

    if history.empty:
        print("No activity recorded.")
        return

    columns = [
        "Activity Date",
        "Activity Type",
        "Details",
        "Status",
        "Follow-up Date",
    ]

    view = history.copy()

    for column in columns:
        if column not in view.columns:
            view[column] = ""

        view[column] = (
            view[column]
            .apply(clean_display_value)
        )

    print(
        view[
            columns
        ].to_string(
            index=False
        )
    )


# ==========================================
# DUE FOLLOW-UPS
# ==========================================

def due_followups_menu():
    df = due_followups()

    list_leads(
        df,
        "DUE / OVERDUE FOLLOW-UPS"
    )


# ==========================================
# SALES REPORT
# ==========================================

def sales_report():
    df = load_leads()

    print_header(
        "SALES REPORT"
    )

    if df.empty:
        print("No leads.")
        return

    status = (
        df["Lead Status"]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    won = df[
        status == "WON"
    ]

    lost = df[
        status == "LOST"
    ]

    print(
        f"Won deals          : {len(won)}"
    )

    print(
        f"Lost deals         : {len(lost)}"
    )

    won_values = pd.to_numeric(
        won["Deal Value"],
        errors="coerce"
    ).fillna(0)

    lost_values = pd.to_numeric(
        lost["Deal Value"],
        errors="coerce"
    ).fillna(0)

    won_value = won_values.sum()
    lost_value = lost_values.sum()

    print(
        f"Won value          : "
        f"₹{won_value:,.2f}"
    )

    print(
        f"Lost value         : "
        f"₹{lost_value:,.2f}"
    )

    # --------------------------------------
    # Conversion rate
    # --------------------------------------

    total_closed = (
        len(won)
        + len(lost)
    )

    if total_closed > 0:

        win_rate = (
            len(won)
            / total_closed
            * 100
        )

        print(
            f"Closed win rate    : "
            f"{win_rate:.1f}%"
        )

    else:

        print(
            "Closed win rate    : 0.0%"
        )


# ==========================================
# CRM MENU
# ==========================================

def crm_menu():

    while True:

        print_header(
            "CLIENTFINDER AI CRM"
        )

        print("1. Dashboard")
        print("2. View all leads")
        print("3. Search lead")
        print("4. Filter by opportunity priority")
        print("5. Filter by lead status")
        print("6. View lead details")
        print("7. Record contact")
        print("8. Update lead status")
        print("9. Schedule follow-up")
        print("10. Add note")
        print("11. Record deal value")
        print("12. Activity history")
        print("13. Due / overdue follow-ups")
        print("14. Sales report")
        print("0. Exit CRM")

        choice = input(
            "\nSelect: "
        ).strip()

        if choice == "1":

            dashboard()

        elif choice == "2":

            list_leads(
                load_leads(),
                "ALL LEADS"
            )

        elif choice == "3":

            search_menu()

        elif choice == "4":

            priority_menu()

        elif choice == "5":

            status_menu()

        elif choice == "6":

            place_id = select_lead()

            if place_id:
                show_lead(place_id)

        elif choice == "7":

            record_contact()

        elif choice == "8":

            update_status()

        elif choice == "9":

            schedule_followup()

        elif choice == "10":

            add_note()

        elif choice == "11":

            deal_value()

        elif choice == "12":

            activity_history()

        elif choice == "13":

            due_followups_menu()

        elif choice == "14":

            sales_report()

        elif choice == "0":

            print(
                "\nLeaving CRM..."
            )

            break

        else:

            print(
                "\nInvalid option."
            )


# ==========================================
# DIRECT RUN
# ==========================================

if __name__ == "__main__":
    crm_menu()