import time
import requests


def check_website(url, timeout=10):
    """
    Check whether a business website is reachable.

    Returns a dictionary containing:
        - status
        - http_status
        - https
        - response_time
        - final_url
        - error
    """

    if not url or url == "NO WEBSITE LISTED":
        return {
            "Website Status": "NOT_CHECKED",
            "HTTP Status": "",
            "HTTPS": "",
            "Response Time": "",
            "Final URL": "",
            "Website Error": "",
        }

    try:
        start_time = time.perf_counter()

        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/149.0 Safari/537.36"
                )
            },
        )

        end_time = time.perf_counter()

        response_time = round(
            end_time - start_time,
            2
        )

        final_url = response.url

        https = final_url.lower().startswith(
            "https://"
        )

        if 200 <= response.status_code < 400:
            status = "WORKING"

        elif 400 <= response.status_code < 500:
            status = "CLIENT_ERROR"

        elif 500 <= response.status_code < 600:
            status = "SERVER_ERROR"

        else:
            status = "UNKNOWN"

        return {
            "Website Status": status,
            "HTTP Status": response.status_code,
            "HTTPS": "YES" if https else "NO",
            "Response Time": response_time,
            "Final URL": final_url,
            "Website Error": "",
        }

    except requests.exceptions.Timeout:

        return {
            "Website Status": "TIMEOUT",
            "HTTP Status": "",
            "HTTPS": "",
            "Response Time": "",
            "Final URL": "",
            "Website Error": "Request timed out",
        }

    except requests.exceptions.ConnectionError:

        return {
            "Website Status": "CONNECTION_ERROR",
            "HTTP Status": "",
            "HTTPS": "",
            "Response Time": "",
            "Final URL": "",
            "Website Error": "Could not connect to website",
        }

    except requests.exceptions.RequestException as error:

        return {
            "Website Status": "ERROR",
            "HTTP Status": "",
            "HTTPS": "",
            "Response Time": "",
            "Final URL": "",
            "Website Error": str(error),
        }

    except Exception as error:

        return {
            "Website Status": "ERROR",
            "HTTP Status": "",
            "HTTPS": "",
            "Response Time": "",
            "Final URL": "",
            "Website Error": str(error),
        }