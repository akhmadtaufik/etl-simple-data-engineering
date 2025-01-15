import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

# Konfigurasi dasar untuk API Reddit
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
SECRET_KEY = os.getenv("REDDIT_SECRET_KEY")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")


class RedditTimeline(Enum):
    """Available Reddit post timeline options."""

    HOT = "hot"
    NEW = "new"
    TOP = "top"
    RISING = "rising"


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


def fetch_posts(
    subreddit: str,
    limit: int,
    token: str,
    timeline: RedditTimeline = RedditTimeline.HOT,
) -> List[Dict[str, Any]]:
    """
    Fetch posts from a specified subreddit with given timeline option.

    Args:
        subreddit (str): Name of the subreddit to fetch posts from
        timeline (RedditTimeline, optional): Timeline to fetch posts from.
                                           Defaults to HOT.
                                           Options: HOT, NEW, TOP, RISING
        limit (int): Number of posts to fetch. Maximum allowed by Reddit API is 100.

    Returns:
        List[Dict[str, Any]]: List of post data dictionaries containing post information

    Raises:
        ValueError: If subreddit is empty or limit is invalid
        requests.exceptions.RequestException: If API request fails
        KeyError: If API response structure is invalid
    """
    if not subreddit or not isinstance(subreddit, str):  # type: ignore
        raise ValueError("Subreddit name must be a non-empty string")

    if not isinstance(limit, int) or limit < 1 or limit > 100:  # type: ignore
        raise ValueError("Limit must be an integer between 1 and 100")

    try:
        headers = {  # type: ignore
            "Authorization": f"bearer {token}",
            "User-Agent": USER_AGENT,
        }

        url = f"https://oauth.reddit.com/r/{subreddit}/{timeline.value}"
        params = {"limit": limit}

        response = requests.get(
            url=url, headers=headers, params=params, timeout=30  # type: ignore
        )
        response.raise_for_status()

        data = response.json()

        # Validate response structure
        if "data" not in data or "children" not in data["data"]:
            raise KeyError("Invalid API response structure")

        # Extract post data and filter relevant information
        posts = []
        for post in data["data"]["children"]:
            if "data" in post:
                posts.append(post["data"])  # type: ignore

        return posts  # type: ignore

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to fetch posts from r/{subreddit}: {str(e)}"
        )
    except (KeyError, ValueError) as e:
        raise ValueError(f"Error processing response data: {str(e)}")
