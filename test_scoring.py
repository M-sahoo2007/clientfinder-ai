from scoring import calculate_opportunity_score


test_leads = [
    {
        "Business Name": "No Website Example",
        "Rating": 4.5,
        "Reviews": 500,
        "Online Presence": "NO_WEBSITE_LISTED",
        "Website Status": "NOT_CHECKED",
        "HTTPS": "",
        "Response Time": "",
    },
    {
        "Business Name": "Social Media Example",
        "Rating": 4.6,
        "Reviews": 200,
        "Online Presence": "SOCIAL_MEDIA_ONLY",
        "Website Status": "NOT_CHECKED",
        "HTTPS": "",
        "Response Time": "",
    },
    {
        "Business Name": "Third Party Example",
        "Rating": 4.2,
        "Reviews": 300,
        "Online Presence": "THIRD_PARTY_PLATFORM",
        "Website Status": "NOT_CHECKED",
        "HTTPS": "",
        "Response Time": "",
    },
    {
        "Business Name": "HTTP Website Example",
        "Rating": 4.0,
        "Reviews": 500,
        "Online Presence": "BUSINESS_WEBSITE",
        "Website Status": "WORKING",
        "HTTPS": "NO",
        "Response Time": 2.0,
    },
    {
        "Business Name": "Broken Website Example",
        "Rating": 4.5,
        "Reviews": 1000,
        "Online Presence": "BUSINESS_WEBSITE",
        "Website Status": "CONNECTION_ERROR",
        "HTTPS": "",
        "Response Time": "",
    },
    {
        "Business Name": "Slow Website Example",
        "Rating": 4.2,
        "Reviews": 200,
        "Online Presence": "BUSINESS_WEBSITE",
        "Website Status": "WORKING",
        "HTTPS": "YES",
        "Response Time": 5.5,
    },
]


def main():

    print("\n======================================")
    print("       CLIENTFINDER SCORING TEST")
    print("======================================\n")

    for lead in test_leads:

        result = calculate_opportunity_score(
            lead
        )

        print("-" * 60)

        print(
            "Business:",
            lead["Business Name"]
        )

        print(
            "Score:",
            result["Opportunity Score"]
        )

        print(
            "Priority:",
            result["Opportunity Priority"]
        )

        print(
            "Services:",
            result["Opportunity Services"]
        )

        print(
            "Reasons:",
            result["Opportunity Reasons"]
        )


if __name__ == "__main__":
    main()