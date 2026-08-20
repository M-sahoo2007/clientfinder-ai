from places import search_places
from analyzer import analyze_business
from exporter import export_to_csv
from website_checker import check_website
from scoring import calculate_opportunity_score


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

    print(
        f"Places returned: {len(places)}"
    )

    leads = []

    # --------------------------------
    # Analyze businesses
    # --------------------------------

    for index, place in enumerate(
        places,
        start=1
    ):

        print(
            f"\nAnalyzing {index}/{len(places)}..."
        )

        # --------------------------------
        # Basic lead analysis
        # --------------------------------

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

        # --------------------------------
        # Website verification
        # --------------------------------

        if (
            lead["Online Presence"]
            == "BUSINESS_WEBSITE"
        ):

            print(
                f"Checking website: "
                f"{lead['Website']}"
            )

            website_result = check_website(
                lead["Website"]
            )

            lead.update(
                website_result
            )

        else:

            # Website is either:
            # - missing
            # - social media
            # - third-party platform

            lead.update({
                "Website Status": "NOT_CHECKED",
                "HTTP Status": "",
                "HTTPS": "",
                "Response Time": "",
                "Final URL": "",
                "Website Error": "",
            })

        # --------------------------------
        # Opportunity scoring
        # --------------------------------

        opportunity = calculate_opportunity_score(
            lead
        )

        lead.update(
            opportunity
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
            "Website Status :",
            lead["Website Status"]
        )

        print(
            "HTTP Status    :",
            lead["HTTP Status"]
        )

        print(
            "HTTPS          :",
            lead["HTTPS"]
        )

        print(
            "Response Time  :",
            lead["Response Time"]
        )

        print(
            "Final URL      :",
            lead["Final URL"]
        )

        if lead["Website Error"]:

            print(
                "Website Error  :",
                lead["Website Error"]
            )

        # --------------------------------
        # Original lead score
        # --------------------------------

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
        # Opportunity score
        # --------------------------------

        print(
            "Business Score :",
            lead["Business Score"]
        )

        print(
            "Digital Opp.   :",
            lead["Digital Opportunity Score"]
        )

        print(
            "Opportunity    :",
            lead["Opportunity Score"]
        )

        print(
            "Opp. Priority  :",
            lead["Opportunity Priority"]
        )

        print(
            "Opp. Services  :",
            lead["Opportunity Services"]
        )

        print(
            "Opp. Reasons   :",
            lead["Opportunity Reasons"]
        )

    # --------------------------------
    # Save to persistent CSV database
    # --------------------------------

    export_to_csv(
        leads
    )

    print("\n======================================")
    print("          LEAD DATABASE")
    print("======================================")

    print(
        f"Processed leads : {len(leads)}"
    )

    print(
        "Saved to        : leads.csv"
    )

    print("======================================")

    print(
        "\nLead search completed successfully."
    )


if __name__ == "__main__":
    main()