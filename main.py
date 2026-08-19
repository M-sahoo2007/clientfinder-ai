from places import search_places
from analyzer import analyze_business
from exporter import export_to_csv


def main():

    print("\n======================================")
    print("       CLIENTFINDER AI")
    print("       Local Lead Finder")
    print("======================================\n")

    # --------------------------------
    # User input
    # --------------------------------

    location = input(
        "Enter location: "
    ).strip()

    category = input(
        "Enter business category: "
    ).strip()

    if not location or not category:
        print(
            "\nLocation and category are required."
        )
        return

    print("\nSearching businesses...\n")

    # --------------------------------
    # Google Places search
    # --------------------------------

    places = search_places(
        category=category,
        location=location,
        max_results=20
    )

    if not places:
        print(
            "\nNo businesses found."
        )
        return

    leads = []

    # --------------------------------
    # Analyze businesses
    # --------------------------------

    for place in places:

        lead = analyze_business(
            place
        )

        # --------------------------------
        # Search information
        # --------------------------------

        lead["Category"] = category

        lead["Location"] = location

        # --------------------------------
        # Contact information
        # --------------------------------

        lead["Phone"] = place.get(
            "nationalPhoneNumber",
            "N/A"
        )

        lead["Address"] = place.get(
            "formattedAddress",
            "N/A"
        )

        # --------------------------------
        # Google Maps
        # --------------------------------

        lead["Google Maps"] = place.get(
            "googleMapsUri",
            "N/A"
        )

        leads.append(
            lead
        )

    # --------------------------------
    # Display results
    # --------------------------------

    print("\n======================================")
    print("           QUALIFIED LEADS")
    print("======================================\n")

    for lead in leads:

        print(
            "-" * 60
        )

        print(
            "Business       :",
            lead["Business Name"]
        )

        print(
            "Category       :",
            lead["Category"]
        )

        print(
            "Location       :",
            lead["Location"]
        )

        print(
            "Phone          :",
            lead["Phone"]
        )

        print(
            "Rating         :",
            lead["Rating"]
        )

        print(
            "Reviews        :",
            lead["Reviews"]
        )

        print(
            "Online Presence:",
            lead["Online Presence"]
        )

        print(
            "Website        :",
            lead["Website"]
        )

        print(
            "Lead Score     :",
            lead["Lead Score"]
        )

        print(
            "Priority       :",
            lead["Priority"]
        )

        print(
            "Recommended    :",
            lead["Recommended Service"]
        )

        print(
            "Reason         :",
            lead["Reason"]
        )

    # --------------------------------
    # Save to persistent CSV database
    # --------------------------------

    export_to_csv(
        leads
    )


if __name__ == "__main__":
    main()
