import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi dasar untuk API Reddit
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
SECRET_KEY = os.getenv("REDDIT_SECRET_KEY")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")


def get_access_token(client_id: str, secret_key: str) -> str:
    """
    Get Reddit API access token using client credentials flow.

    Args:
        client_id (str): Reddit API client ID
        secret_key (str): Reddit API secret key

    Returns:
        str: Access token if successful

    Raises:
        requests.exceptions.RequestException: If API request fails
        ValueError: If response is invalid or authentication fails
    """
    try:
        auth = requests.auth.HTTPBasicAuth(client_id, secret_key)  # type: ignore
        data = {"grant_type": "client_credentials"}
        headers = {"User-Agent": USER_AGENT}

        response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,  # type: ignore
            data=data,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()  # Raise exception for bad status codes

        token_data = response.json()
        if "access_token" not in token_data:
            raise ValueError("Access token not found in response")

        return token_data["access_token"]

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to get access token: {str(e)}"
        )
    except (ValueError, KeyError) as e:
        raise ValueError(f"Invalid response from Reddit API: {str(e)}")
