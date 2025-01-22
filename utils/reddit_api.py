# type: ignore
import requests
from utils.config import USER_AGENT
from typing import List, Dict, Any
from enum import Enum


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
        auth = requests.auth.HTTPBasicAuth(client_id, secret_key)
        data = {"grant_type": "client_credentials"}
        headers = {"User-Agent": USER_AGENT}

        response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
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
    if not subreddit or not isinstance(subreddit, str):
        raise ValueError("Subreddit name must be a non-empty string")

    if not isinstance(limit, int) or limit < 1 or limit > 100:
        raise ValueError("Limit must be an integer between 1 and 100")

    try:
        headers = {
            "Authorization": f"bearer {token}",
            "User-Agent": USER_AGENT,
        }

        url = f"https://oauth.reddit.com/r/{subreddit}/{timeline.value}"
        params = {"limit": limit}

        response = requests.get(
            url=url, headers=headers, params=params, timeout=30
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
                posts.append(post["data"])

        return posts

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to fetch posts from r/{subreddit}: {str(e)}"
        )
    except (KeyError, ValueError) as e:
        raise ValueError(f"Error processing response data: {str(e)}")


def fetch_comments(post_id: str, token: str):
    """
    Fetches and processes comments for a given Reddit post.

    Args:
        post_id (str): The ID of the Reddit post to fetch comments for.
        token (str): The OAuth token for authenticating the API request.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing processed comment data.

    Raises:
        ValueError: If the post_id is invalid or if there is an error processing the comment data.
        requests.exceptions.RequestException: If there is a network-related error during the API request.
    """
    if not post_id or not isinstance(post_id, str):
        raise ValueError("Post ID must be a non-empty string")

    try:
        headers = {
            "Authorization": f"bearer {token}",
            "User-Agent": USER_AGENT,
        }

        url = f"https://oauth.reddit.com/comments/{post_id}"

        response = requests.get(url=url, headers=headers, timeout=30)

        response.raise_for_status()

        data = response.json()

        # Validate response structure
        if not isinstance(data, list) or len(data) < 2:
            raise KeyError("Invalid API response structure")

        # Process comments data
        def extract_comments(
            comment_data: Dict[str, Any], parent_id: str = None, level: int = 0
        ):
            """
            Extracts structured comment data from a given comment object, including replies (nested comments).

            This function recursively processes comments and their replies from a Reddit API structure.
            It extracts essential details such as the comment ID, post ID, author, body, score, and metadata about
            the comment (e.g., whether it is edited, stickied, etc.). It also processes replies, if present, and
            attaches the parent comment ID to each child comment.

            Args:
                comment_data (Dict[str, Any]): A dictionary containing the comment's data.
                parent_id (str, optional): The ID of the parent comment, used for nested comments. Defaults to None.
                level (int, optional): The level of nesting (starting at 0 for the root comment). Defaults to 0.

            Returns:
                List[Dict[str, Any]]: A list of dictionaries containing structured comment data, including replies if any.
            """
            processed = []

            if not isinstance(comment_data, dict):
                return processed

            # Extract basic comment data
            comment = {
                "comment_id": comment_data.get("id"),
                "post_id": post_id,
                "parent_comment_id": parent_id,
                "author": comment_data.get("author"),
                "body": comment_data.get("body"),
                "score": comment_data.get("score"),
                "created_utc": comment_data.get("created_utc"),
                "edited": comment_data.get("edited", False),
                "is_submitter": comment_data.get("is_submitter", False),
                "stickied": comment_data.get("stickied", False),
                "level": level,
            }

            processed.append(comment)

            # Process replies if they exist
            replies = comment_data.get("replies", "")
            if isinstance(replies, dict):
                children = replies.get("data", {}).get("children", [])
                for child in children:
                    if (
                        child.get("kind") == "t1"
                    ):  # t1 is the prefix for comments
                        child_data = child.get("data", {})
                        processed.extend(
                            extract_comments(
                                child_data,
                                parent_id=comment["comment_id"],
                                level=level + 1,
                            )
                        )

            return processed

        # Process all top-level comments
        all_comments = []
        comment_listing = data[1]["data"]["children"]

        for comment in comment_listing:
            if comment["kind"] == "t1":  # Ensure it's a comment
                all_comments.extend(extract_comments(comment["data"]))

        return all_comments

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to fetch comments for post {post_id}: {str(e)}"
        )
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"Error processing comment data: {str(e)}")
