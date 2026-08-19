def analyze_business(place):
    """
    Analyze a Google Places result and calculate
    a simple sales lead score.
    """

    name = place.get("displayName", {}).get("text", "Unknown")
    rating = place.get("rating", 0)
    reviews = place.get("userRatingCount", 0)
    website = place.get("websiteUri")

    score = 0
    reasons = []

    # --------------------------------
    # Website
    # --------------------------------

    if not website:
        score += 40
        reasons.append("No website listed on Google")
    else:
        reasons.append("Website listed")

    # --------------------------------
    # Review count
    # --------------------------------

    if reviews >= 1000:
        score += 25
        reasons.append("1000+ reviews")

    elif reviews >= 500:
        score += 20
        reasons.append("500+ reviews")

    elif reviews >= 200:
        score += 15
        reasons.append("200+ reviews")

    elif reviews >= 100:
        score += 10
        reasons.append("100+ reviews")

    # --------------------------------
    # Rating
    # --------------------------------

    if rating >= 4.5:
        score += 15
        reasons.append("Excellent rating")

    elif rating >= 4.0:
        score += 10
        reasons.append("Good rating")

    elif rating >= 3.5:
        score += 5
        reasons.append("Average rating")

    # --------------------------------
    # Lead priority
    # --------------------------------

    if score >= 80:
        priority = "HOT"

    elif score >= 60:
        priority = "HIGH"

    elif score >= 40:
        priority = "MEDIUM"

    else:
        priority = "LOW"

    # --------------------------------
    # Recommended service
    # --------------------------------

    if not website:
        service = "Website + Local SEO"
    else:
        service = "Website/SEO Audit"

    return {
        "Business Name": name,
        "Rating": rating,
        "Reviews": reviews,
        "Website": website if website else "NO WEBSITE LISTED",
        "Lead Score": score,
        "Priority": priority,
        "Recommended Service": service,
        "Reason": "; ".join(reasons)
    }

