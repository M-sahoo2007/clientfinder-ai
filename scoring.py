def calculate_opportunity_score(lead):
    """
    Calculate a sales opportunity score for a business.

    The score is divided into:

    1. Business Score
       Measures business strength.

    2. Digital Opportunity Score
       Measures how much digital improvement may be useful.

    3. Opportunity Score
       Combined score used for lead priority.
    """

    # --------------------------------
    # Input data
    # --------------------------------

    try:
        rating = float(lead.get("Rating") or 0)
    except (ValueError, TypeError):
        rating = 0

    try:
        reviews = int(lead.get("Reviews") or 0)
    except (ValueError, TypeError):
        reviews = 0

    online_presence = lead.get(
        "Online Presence",
        ""
    )

    website_status = lead.get(
        "Website Status",
        ""
    )

    https = lead.get(
        "HTTPS",
        ""
    )

    response_time = lead.get(
        "Response Time",
        ""
    )

    # --------------------------------
    # BUSINESS SCORE
    # Maximum: 40
    # --------------------------------

    business_score = 0
    business_reasons = []

    # Reviews

    if reviews >= 1000:

        business_score += 20

        business_reasons.append(
            "1000+ Google reviews"
        )

    elif reviews >= 500:

        business_score += 15

        business_reasons.append(
            "500+ Google reviews"
        )

    elif reviews >= 200:

        business_score += 10

        business_reasons.append(
            "200+ Google reviews"
        )

    elif reviews >= 100:

        business_score += 5

        business_reasons.append(
            "100+ Google reviews"
        )

    # Rating

    if rating >= 4.5:

        business_score += 10

        business_reasons.append(
            "4.5+ rating"
        )

    elif rating >= 4.0:

        business_score += 5

        business_reasons.append(
            "4.0+ rating"
        )

    # Additional business strength

    if rating >= 4.5 and reviews >= 500:

        business_score += 10

        business_reasons.append(
            "Strong rating with high review volume"
        )

    # Make sure Business Score never exceeds 40

    business_score = min(
        business_score,
        40
    )

    # --------------------------------
    # DIGITAL OPPORTUNITY SCORE
    # Maximum: 60
    # --------------------------------

    digital_score = 0
    digital_reasons = []
    services = []

    # --------------------------------
    # No website
    # --------------------------------

    if online_presence == "NO_WEBSITE_LISTED":

        digital_score += 40

        digital_reasons.append(
            "No business website listed"
        )

        services.extend([
            "Business Website",
            "Local SEO"
        ])

    # --------------------------------
    # Social media only
    # --------------------------------

    elif online_presence == "SOCIAL_MEDIA_ONLY":

        digital_score += 35

        digital_reasons.append(
            "Only social media presence"
        )

        services.extend([
            "Business Website",
            "Local SEO"
        ])

    # --------------------------------
    # Third-party platform
    # --------------------------------

    elif online_presence == "THIRD_PARTY_PLATFORM":

        digital_score += 30

        digital_reasons.append(
            "Third-party platform instead of own website"
        )

        services.extend([
            "Business Website",
            "Local SEO"
        ])

    # --------------------------------
    # Website problems
    # --------------------------------

    if website_status in {
        "CONNECTION_ERROR",
        "TIMEOUT",
        "ERROR",
        "SERVER_ERROR",
    }:

        digital_score += 35

        digital_reasons.append(
            "Website could not be reliably verified"
        )

        services.append(
            "Website Repair / Rebuild"
        )

    elif website_status == "CLIENT_ERROR":

        digital_score += 25

        digital_reasons.append(
            "Website returned a client error"
        )

        services.append(
            "Website Repair"
        )

    # --------------------------------
    # HTTPS
    # --------------------------------

    if (
        website_status == "WORKING"
        and https == "NO"
    ):

        digital_score += 15

        digital_reasons.append(
            "Website is not using HTTPS"
        )

        services.append(
            "HTTPS / Website Security"
        )

    # --------------------------------
    # Website speed
    # --------------------------------

    try:

        speed = float(
            response_time
        )

        if speed >= 5:

            digital_score += 10

            digital_reasons.append(
                "Very slow website response"
            )

            services.append(
                "Website Performance Optimization"
            )

        elif speed >= 3:

            digital_score += 5

            digital_reasons.append(
                "Slow website response"
            )

            services.append(
                "Website Performance Optimization"
            )

    except (
        ValueError,
        TypeError
    ):

        pass

    # --------------------------------
    # Cap digital score
    # --------------------------------

    digital_score = min(
        digital_score,
        60
    )

    # --------------------------------
    # Combined opportunity score
    # --------------------------------

    opportunity_score = (
        business_score
        + digital_score
    )

    opportunity_score = min(
        opportunity_score,
        100
    )

    # --------------------------------
    # Priority
    # --------------------------------

    if opportunity_score >= 80:

        priority = "HOT"

    elif opportunity_score >= 65:

        priority = "HIGH"

    elif opportunity_score >= 45:

        priority = "MEDIUM"

    else:

        priority = "LOW"

    # --------------------------------
    # Remove duplicate services
    # --------------------------------

    services = list(
        dict.fromkeys(
            services
        )
    )

    # --------------------------------
    # Default service
    # --------------------------------

    if services:

        recommended_service = (
            " + ".join(services)
        )

    else:

        recommended_service = (
            "SEO / Digital Growth"
        )

    # --------------------------------
    # Combine reasons
    # --------------------------------

    all_reasons = (
        business_reasons
        + digital_reasons
    )

    if all_reasons:

        opportunity_reasons = (
            "; ".join(all_reasons)
        )

    else:

        opportunity_reasons = (
            "No major opportunity signals detected"
        )

    # --------------------------------
    # Return
    # --------------------------------

    return {

        "Business Score": business_score,

        "Digital Opportunity Score": digital_score,

        "Opportunity Score": opportunity_score,

        "Opportunity Priority": priority,

        "Opportunity Services": recommended_service,

        "Opportunity Reasons": opportunity_reasons,
    }