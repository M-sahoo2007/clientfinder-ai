from urllib.parse import urlparse


SOCIAL_DOMAINS = {
    "facebook.com",
    "www.facebook.com",
    "instagram.com",
    "www.instagram.com",
    "twitter.com",
    "www.twitter.com",
    "x.com",
    "www.x.com",
    "linkedin.com",
    "www.linkedin.com",
    "youtube.com",
    "www.youtube.com",
    "tiktok.com",
    "www.tiktok.com",
}


THIRD_PARTY_DOMAINS = {
    "booking.com",
    "www.booking.com",
    "oyorooms.com",
    "www.oyorooms.com",
    "tripadvisor.com",
    "www.tripadvisor.com",
    "justdial.com",
    "www.justdial.com",
    "zomato.com",
    "www.zomato.com",
    "swiggy.com",
    "www.swiggy.com",
    "makemytrip.com",
    "www.makemytrip.com",
    "goibibo.com",
    "www.goibibo.com",
    "agoda.com",
    "www.agoda.com",
    "expedia.com",
    "www.expedia.com",
}


def classify_online_presence(website_url):
    """
    Classify the URL returned by Google Places.

    Returns:
        NO_WEBSITE_LISTED
        SOCIAL_MEDIA_ONLY
        THIRD_PARTY_PLATFORM
        BUSINESS_WEBSITE
        UNKNOWN
    """

    if not website_url:
        return "NO_WEBSITE_LISTED"

    try:
        parsed = urlparse(
            website_url.lower().strip()
        )

        domain = parsed.netloc

        # Remove port
        domain = domain.split(":")[0]

        # Remove accidental www.
        clean_domain = domain.removeprefix("www.")

        # Social media
        if (
            domain in SOCIAL_DOMAINS
            or clean_domain in {
                d.removeprefix("www.")
                for d in SOCIAL_DOMAINS
            }
        ):
            return "SOCIAL_MEDIA_ONLY"

        # Third-party platforms
        if (
            domain in THIRD_PARTY_DOMAINS
            or clean_domain in {
                d.removeprefix("www.")
                for d in THIRD_PARTY_DOMAINS
            }
        ):
            return "THIRD_PARTY_PLATFORM"

        return "BUSINESS_WEBSITE"

    except Exception:
        return "UNKNOWN"


def analyze_business(place):

    # --------------------------------
    # Basic information
    # --------------------------------

    place_id = place.get("id")

    name = place.get(
        "displayName",
        {}
    ).get(
        "text",
        "Unknown"
    )

    rating = place.get(
        "rating",
        0
    )

    reviews = place.get(
        "userRatingCount",
        0
    )

    website = place.get(
        "websiteUri"
    )

    # --------------------------------
    # Online presence
    # --------------------------------

    online_presence = classify_online_presence(
        website
    )

    score = 0
    reasons = []

    # --------------------------------
    # Online presence scoring
    # --------------------------------

    if online_presence == "NO_WEBSITE_LISTED":

        score += 40

        reasons.append(
            "No website listed on Google"
        )

        recommended_service = (
            "Business Website + Local SEO"
        )

    elif online_presence == "SOCIAL_MEDIA_ONLY":

        score += 30

        reasons.append(
            "Social media listed instead of business website"
        )

        recommended_service = (
            "Business Website + Local SEO"
        )

    elif online_presence == "THIRD_PARTY_PLATFORM":

        score += 25

        reasons.append(
            "Third-party platform listed instead of business website"
        )

        recommended_service = (
            "Business Website + Local SEO"
        )

    elif online_presence == "BUSINESS_WEBSITE":

        reasons.append(
            "Business website listed"
        )

        recommended_service = (
            "Website + SEO Audit"
        )

    else:

        score += 20

        reasons.append(
            "Online presence could not be classified"
        )

        recommended_service = (
            "Website Audit"
        )

    # --------------------------------
    # Review score
    # --------------------------------

    if reviews >= 1000:

        score += 25

        reasons.append(
            "1000+ reviews"
        )

    elif reviews >= 500:

        score += 20

        reasons.append(
            "500+ reviews"
        )

    elif reviews >= 200:

        score += 15

        reasons.append(
            "200+ reviews"
        )

    elif reviews >= 100:

        score += 10

        reasons.append(
            "100+ reviews"
        )

    # --------------------------------
    # Rating score
    # --------------------------------

    if rating >= 4.5:

        score += 15

        reasons.append(
            "Excellent rating"
        )

    elif rating >= 4.0:

        score += 10

        reasons.append(
            "Good rating"
        )

    elif rating >= 3.5:

        score += 5

        reasons.append(
            "Average rating"
        )

    # --------------------------------
    # Priority
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
    # Return lead
    # --------------------------------

    return {
        "Place ID": place_id,
        "Business Name": name,
        "Rating": rating,
        "Reviews": reviews,
        "Online Presence": online_presence,
        "Website": (
            website
            if website
            else "NO WEBSITE LISTED"
        ),
        "Lead Score": score,
        "Priority": priority,
        "Recommended Service": recommended_service,
        "Reason": "; ".join(reasons),
    }