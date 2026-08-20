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

    # ========================================
    # USER INPUT
    # ========================================

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

    # ========================================
    # GOOGLE PLACES SEARCH
    # ========================================

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

    # ========================================
    # PROCESS EACH BUSINESS
    # ========================================

    for index, place in enumerate(
        places,
        start=1
    ):

        print(
            f"\nAnalyzing {index}/{len(places)}..."
        )

        # ====================================
        # BASIC BUSINESS ANALYSIS
        # ====================================

        try:

            lead = analyze_business(
                place
            )

        except Exception as error:

            print(
                f"Analysis failed: {error}"
            )

            continue

        # ====================================
        # PLACE ID
        # ====================================

        lead["Place ID"] = place.get(
            "id",
            ""
        )

        # ====================================
        # SEARCH INFORMATION
        # ====================================

        lead["Category"] = category

        lead["Location"] = location

        # ====================================
        # CONTACT INFORMATION
        # ====================================

        lead["Phone"] = place.get(
            "nationalPhoneNumber",
            "N/A"
        )

        lead["Address"] = place.get(
            "formattedAddress",
            "N/A"
        )

        # ====================================
        # GOOGLE MAPS
        # ====================================

        lead["Google Maps"] = place.get(
            "googleMapsUri",
            "N/A"
        )

        # ====================================
        # WEBSITE VERIFICATION
        # ====================================

        online_presence = lead.get(
            "Online Presence",
            ""
        )

        website = lead.get(
            "Website",
            ""
        )

        if (
            online_presence
            == "BUSINESS_WEBSITE"
            and website
            and website != "NO WEBSITE LISTED"
        ):

            print(
                f"Checking website: {website}"
            )

            try:

                website_result = check_website(
                    website
                )

                if website_result:

                    lead.update(
                        website_result
                    )

            except Exception as error:

                print(
                    f"Website check failed: {error}"
                )

                lead.update({
                    "Website Status": "CHECK_FAILED",
                    "HTTP Status": "",
                    "HTTPS": "",
                    "Response Time": "",
                    "Final URL": "",
                    "Website Error": str(error),
                })

        else:

            # --------------------------------
            # No own business website
            #
            # Possible cases:
            # NO_WEBSITE_LISTED
            # SOCIAL_MEDIA_ONLY
            # THIRD_PARTY_PLATFORM
            # --------------------------------

            lead.update({
                "Website Status": "NOT_CHECKED",
                "HTTP Status": "",
                "HTTPS": "",
                "Response Time": "",
                "Final URL": "",
                "Website Error": "",
            })

        # ====================================
        # OPPORTUNITY SCORING
        # ====================================

        print(
            "Calculating opportunity score..."
        )

        try:

            opportunity = (
                calculate_opportunity_score(
                    lead
                )
            )

            lead.update(
                opportunity
            )

        except Exception as error:

            print(
                f"Opportunity scoring failed: {error}"
            )

            # Safe fallback
            lead.update({
                "Business Score": 0,
                "Digital Opportunity Score": 0,
                "Opportunity Score": 0,
                "Opportunity Priority": "LOW",
                "Opportunity Services": "Manual Review",
                "Opportunity Reasons": (
                    f"Scoring error: {error}"
                ),
            })

        # ====================================
        # ADD LEAD
        # ====================================

        leads.append(
            lead
        )

    # ========================================
    # CHECK RESULTS
    # ========================================

    if not leads:

        print(
            "\nNo leads could be processed."
        )

        return

    # ========================================
    # DISPLAY RESULTS
    # ========================================

    print("\n======================================")
    print("           QUALIFIED LEADS")
    print("======================================\n")

    for lead in leads:

        print(
            "-" * 60
        )

        print(
            "Business       :",
            lead.get(
                "Business Name",
                "Unknown"
            )
        )

        print(
            "Place ID       :",
            lead.get(
                "Place ID",
                ""
            )
        )

        print(
            "Category       :",
            lead.get(
                "Category",
                ""
            )
        )

        print(
            "Location       :",
            lead.get(
                "Location",
                ""
            )
        )

        print(
            "Phone          :",
            lead.get(
                "Phone",
                "N/A"
            )
        )

        print(
            "Address        :",
            lead.get(
                "Address",
                "N/A"
            )
        )

        print(
            "Rating         :",
            lead.get(
                "Rating",
                ""
            )
        )

        print(
            "Reviews        :",
            lead.get(
                "Reviews",
                ""
            )
        )

        # ====================================
        # ONLINE PRESENCE
        # ====================================

        print(
            "Online Presence:",
            lead.get(
                "Online Presence",
                ""
            )
        )

        print(
            "Website        :",
            lead.get(
                "Website",
                ""
            )
        )

        # ====================================
        # WEBSITE CHECK
        # ====================================

        print(
            "Website Status :",
            lead.get(
                "Website Status",
                ""
            )
        )

        print(
            "HTTP Status    :",
            lead.get(
                "HTTP Status",
                ""
            )
        )

        print(
            "HTTPS          :",
            lead.get(
                "HTTPS",
                ""
            )
        )

        print(
            "Response Time  :",
            lead.get(
                "Response Time",
                ""
            )
        )

        print(
            "Final URL      :",
            lead.get(
                "Final URL",
                ""
            )
        )

        website_error = lead.get(
            "Website Error",
            ""
        )

        if website_error:

            print(
                "Website Error  :",
                website_error
            )

        # ====================================
        # ORIGINAL LEAD SCORE
        # ====================================

        print(
            "Lead Score     :",
            lead.get(
                "Lead Score",
                ""
            )
        )

        print(
            "Priority       :",
            lead.get(
                "Priority",
                ""
            )
        )

        print(
            "Recommended    :",
            lead.get(
                "Recommended Service",
                ""
            )
        )

        print(
            "Reason         :",
            lead.get(
                "Reason",
                ""
            )
        )

        # ====================================
        # OPPORTUNITY SCORE
        # ====================================

        print(
            "Business Score :",
            lead.get(
                "Business Score",
                ""
            )
        )

        print(
            "Digital Opp.   :",
            lead.get(
                "Digital Opportunity Score",
                ""
            )
        )

        print(
            "Opportunity    :",
            lead.get(
                "Opportunity Score",
                ""
            )
        )

        print(
            "Opp. Priority  :",
            lead.get(
                "Opportunity Priority",
                ""
            )
        )

        print(
            "Opp. Services  :",
            lead.get(
                "Opportunity Services",
                ""
            )
        )

        print(
            "Opp. Reasons   :",
            lead.get(
                "Opportunity Reasons",
                ""
            )
        )

        print(
            "Google Maps    :",
            lead.get(
                "Google Maps",
                ""
            )
        )

    # ========================================
    # SAVE DATABASE
    # ========================================

    print(
        "\nSaving leads to database..."
    )

    try:

        export_to_csv(
            leads
        )

    except Exception as error:

        print(
            "\nDatabase export failed:"
        )

        print(error)

        return

    # ========================================
    # SEARCH STATISTICS
    # ========================================

    priorities = [
        lead.get(
            "Opportunity Priority",
            ""
        )
        for lead in leads
    ]

    hot = priorities.count(
        "HOT"
    )

    high = priorities.count(
        "HIGH"
    )

    medium = priorities.count(
        "MEDIUM"
    )

    low = priorities.count(
        "LOW"
    )

    # ========================================
    # FINAL SUMMARY
    # ========================================

    print("\n======================================")
    print("          SEARCH COMPLETED")
    print("======================================")

    print(
        f"Businesses found    : {len(places)}"
    )

    print(
        f"Businesses processed: {len(leads)}"
    )

    print(
        f"HOT opportunities   : {hot}"
    )

    print(
        f"HIGH opportunities  : {high}"
    )

    print(
        f"MEDIUM opportunities: {medium}"
    )

    print(
        f"LOW opportunities   : {low}"
    )

    print(
        "Database updated    : leads.csv"
    )

    print("======================================")

    print(
        "\nLead search completed successfully."
    )


if __name__ == "__main__":
    main()