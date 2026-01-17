"""Activities for finding condo contact emails using Brave Search."""

import json
import os
import re
from datetime import timedelta
from pathlib import Path
from typing import Any

import httpx

from src.worker.lib.decorators import configured_activity


@configured_activity(
    name="brave_search_condo",
    start_to_close_timeout=timedelta(seconds=30),
)
async def brave_search_condo(
    condo_name: str, condo_address: str = "", location: str = "Singapore"
) -> list[dict[str, str]]:
    """
    Search for condo contact information using Brave Search API.

    Args:
        condo_name: Name of the condo
        condo_address: Full address/description of the condo
        location: Location (default: Singapore)

    Returns:
        List of search results with title, url, and description
    """
    api_key = os.getenv("BRAVE_SEARCH_API")
    if not api_key:
        raise ValueError("BRAVE_SEARCH_API environment variable not set")

    # Search for contact information - Use full address if available
    search_term = condo_address if condo_address else condo_name
    query = f"{search_term} {location} email or contact"

    async with httpx.AsyncClient() as client:
        # 1. Web Search
        web_response = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": api_key,
            },
            params={
                "q": query,
                "count": 10,
            },
            timeout=30.0,
        )
        web_response.raise_for_status()
        web_data = web_response.json()

        # 2. Local POI Search
        local_response = await client.get(
            "https://api.search.brave.com/res/v1/local/search",
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": api_key,
            },
            params={
                "q": search_term,
            },
            timeout=30.0,
        )
        local_data = {}
        if local_response.status_code == 200:
            local_data = local_response.json()

    # Extract web results
    results = []
    web_results_count = 0
    for result in web_data.get("web", {}).get("results", []):
        results.append(
            {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "description": result.get("description", ""),
                "source": "web",
            }
        )
        web_results_count += 1

    # Extract local results
    local_results_count = 0
    contact_info_found = 0
    for result in local_data.get("results", []):
        # Local results have different structure (POI)
        # We extract website and contact info (email, phone)
        website = result.get("website", "")
        contact = result.get("contact", {})
        email = contact.get("email", "")
        phone = contact.get("phone", "")

        if email or phone:
            contact_info_found += 1

        # Build a rich description that includes contact details
        desc_parts = []
        if email:
            desc_parts.append(f"Email: {email}")
        if phone:
            desc_parts.append(f"Phone: {phone}")
        addr = result.get("address", {}).get("formatted_address", "")
        if addr:
            desc_parts.append(f"Address: {addr}")

        description = " | ".join(desc_parts)

        # Include if we have either a website to scrape or direct contact info
        if website or email or phone:
            results.append(
                {
                    "title": result.get("name", ""),
                    "url": website or "",
                    "description": description,
                    "source": "local",
                }
            )
            local_results_count += 1

    from temporalio import activity

    activity.logger.info(
        f"Brave Search Results: {web_results_count} web, {local_results_count} local "
        f"({contact_info_found} with direct contact info)"
    )

    return results


@configured_activity(
    name="extract_emails_from_results",
    start_to_close_timeout=timedelta(seconds=10),
)
async def extract_emails_from_results(
    search_results: list[dict[str, str]],
) -> list[str]:
    """
    Extract email addresses from search results using regex.

    Args:
        search_results: List of search results from Brave

    Returns:
        List of extracted email addresses
    """
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    emails = set()

    for result in search_results:
        # Extract from title
        emails.update(re.findall(email_pattern, result.get("title", "")))
        # Extract from description
        emails.update(re.findall(email_pattern, result.get("description", "")))
        # Extract from URL (sometimes emails are in URLs)
        emails.update(re.findall(email_pattern, result.get("url", "")))

    # Filter out common spam/invalid patterns
    filtered_emails = []
    spam_domains = ["example.com", "test.com", "localhost"]

    for email in emails:
        domain = email.split("@")[1].lower()
        if domain not in spam_domains:
            filtered_emails.append(email)

    return sorted(filtered_emails)


@configured_activity(
    name="save_condo_emails",
    start_to_close_timeout=timedelta(seconds=10),
)
async def save_condo_emails(
    condo_name: str,
    emails: list[str],
    output_dir: str = "data/condo/emails",
) -> str:
    """
    Save extracted emails to a text file.

    Args:
        condo_name: Name of the condo
        emails: List of email addresses
        output_dir: Directory to save the file in

    Returns:
        Path to the saved file
    """
    # Normalize condo name for filename
    normalized_name = condo_name.lower()
    normalized_name = re.sub(r"['\"]", "", normalized_name)
    normalized_name = re.sub(r"[.\s-]+", "_", normalized_name)
    normalized_name = re.sub(r"_+", "_", normalized_name)
    normalized_name = normalized_name.strip("_")

    output_path = Path(output_dir) / f"condo.{normalized_name}.email.txt"

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save emails
    with open(output_path, "w", encoding="utf-8") as f:
        for email in sorted(emails):
            f.write(f"{email}\n")

    return str(output_path)


@configured_activity(
    name="load_condo_data",
    start_to_close_timeout=timedelta(seconds=10),
)
async def load_condo_data(condo_name: str, data_dir: str = "data") -> dict[str, Any]:
    """
    Load condo data from JSON file.

    Args:
        condo_name: Name of the condo
        data_dir: Directory containing the data files

    Returns:
        Condo data from JSON file
    """
    # Normalize condo name for filename
    normalized_name = condo_name.lower()
    normalized_name = re.sub(r"['\"]", "", normalized_name)
    normalized_name = re.sub(r"[.\s-]+", "_", normalized_name)
    normalized_name = re.sub(r"_+", "_", normalized_name)
    normalized_name = normalized_name.strip("_")

    file_path = Path(data_dir) / f"condo.{normalized_name}.json"

    if not file_path.exists():
        raise FileNotFoundError(f"Condo data file not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


@configured_activity(
    name="list_condo_names",
    start_to_close_timeout=timedelta(minutes=5),
)
async def list_condo_names(data_dir: str = "data/condos") -> list[dict[str, str]]:
    """
    List all condo names and addresses from JSON files in the directory that match specific types.

    Args:
        data_dir: Directory containing the JSON files

    Returns:
        List of dicts with 'name' and 'address' keys
    """
    path = Path(data_dir)
    target_types = {"Executive Condominium", "Condominium"}
    condos = []
    seen_names = set()

    for file_path in path.glob("*.json"):
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if item.get("displayType") in target_types:
                            name = item.get("displayText")
                            address = item.get("displayDescription")
                            if name and name not in seen_names:
                                condos.append({"name": name, "address": address or name})
                                seen_names.add(name)
        except Exception:
            continue

    return sorted(condos, key=lambda x: x["name"])
