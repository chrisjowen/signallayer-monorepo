"""Activities for PropertyGuru data ingestion."""

import json
import re
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx

from ...lib.decorators import configured_activity

if TYPE_CHECKING:
    from ...lib.decorators.activity import ExecutableActivity


API_URL = "https://prefix-search.propertyguru.com/v1/sg/autocomplete"
API_PARAMS = {
    "region": "sg",
    "locale": "en",
    "limit": "100",
    "property_type_group_exclude[0]": "COMMERCIAL",
    "property_type_group_exclude[1]": "OTHERS",
    "object_type[0]": "HDB_ESTATE",
    "object_type[1]": "DISTRICT",
    "object_type[2]": "PROPERTY",
    "object_type[3]": "STREET",
}


def normalize_street_name(street_name: str) -> str:
    """
    Normalize street name for use in filename.

    Examples:
        "Admiralty Drive" -> "admiralty_drive"
        "Ang Mo Kio Avenue 1" -> "ang_mo_kio_avenue_1"
        "St. George's Lane" -> "st_georges_lane"
    """
    normalized = street_name.lower()
    normalized = re.sub(r"['\"]", "", normalized)
    normalized = re.sub(r"[.\s-]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    normalized = normalized.strip("_")
    return normalized


@configured_activity(
    name="fetch_propertyguru_autocomplete",
    start_to_close_timeout=timedelta(seconds=30),
)
async def fetch_propertyguru_autocomplete(street_name: str) -> dict[str, Any]:
    """
    Fetch PropertyGuru autocomplete data for a single street.

    Args:
        street_name: The street name to query

    Returns:
        API response data

    Raises:
        httpx.HTTPError: If the API request fails
    """
    async with httpx.AsyncClient() as client:
        params = {**API_PARAMS, "query": street_name}
        response = await client.get(API_URL, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()


@configured_activity(
    name="save_propertyguru_data",
    start_to_close_timeout=timedelta(seconds=10),
)
async def save_propertyguru_data(
    street_name: str, data: dict[str, Any], output_dir: str = "data"
) -> str:
    """
    Save PropertyGuru data to a JSON file.

    Args:
        street_name: The street name (used for filename)
        data: The data to save
        output_dir: Directory to save the file in

    Returns:
        Path to the saved file
    """
    normalized_name = normalize_street_name(street_name)
    output_path = Path(output_dir) / f"condo.{normalized_name}.json"

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save the data
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return str(output_path)


@configured_activity(
    name="load_streets_list",
    start_to_close_timeout=timedelta(seconds=5),
)
async def load_streets_list(file_path: str = "data/singapore.streets.json") -> list[str]:
    """
    Load the list of streets from a JSON file.

    Args:
        file_path: Path to the streets JSON file

    Returns:
        List of street names
    """
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


# Type hints for IDE support
if TYPE_CHECKING:
    fetch_propertyguru_autocomplete: ExecutableActivity[[str], dict[str, Any]]
    save_propertyguru_data: ExecutableActivity[[str, dict[str, Any], str], str]
    load_streets_list: ExecutableActivity[[str], list[str]]
