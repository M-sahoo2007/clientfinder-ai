from places import search_places
from analyzer import analyze_business
from exporter import export_to_csv


def main():

    print("\n======================================")
    print("       CLIENTFINDER AI")
    print("       Local Lead Finder")
    print("======================================\n")

    location = input("Enter location: ")
    category = input("Enter business category: ")

    print("\nSearching businesses...\n")

    places = search_places(
        category=category,
        location=location,
        max_results=20
    )

    if not places:
        print("No businesses found.")
        return

    leads = []

    for place in places:

        lead = analyze_business(place)

        # Add information useful for contacting the business
        lead["Phone"] = place.get(
            "nationalPhoneNumber",
            "N/A"
        )

        lead["Address"] = place.get(
            "formattedAddress",
            "N/A"
        )

        lead["Google Maps"] = place.get(
            "googleMapsUri",
            "N/A"
        )

        leads.append(lead)

    # --------------------------------
    # Display results
    # --------------------------------

    print("\n======================================")
    print("           QUALIFIED LEADS")
    print("======================================\n")

    for lead in leads:

        print("-" * 60)

        print("Business       :", lead["Business Name"])
        print("Rating         :", lead["Rating"])
        print("Reviews        :", lead["Reviews"])
        print("Website        :", lead["Website"])
        print("Lead Score     :", lead["Lead Score"])
        print("Priority       :", lead["Priority"])
        print("Recommended    :", lead["Recommended Service"])
        print("Reason         :", lead["Reason"])

    # --------------------------------
    # Export
    # --------------------------------

    export_to_csv(leads)


if __name__ == "__main__":
    main()

