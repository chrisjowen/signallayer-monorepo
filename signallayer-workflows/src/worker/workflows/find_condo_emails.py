"""Workflow for finding condo contact emails."""

import re

from agents import Runner
from pydantic import BaseModel, Field
from temporalio import workflow

from src.worker.agents import email_extractor
from src.worker.lib.decorators import workflow_api
from src.worker.workflows.activities.condo_emails import (
    brave_search_condo,
    extract_emails_from_results,
    save_condo_emails,
)


class FindCondoEmailsInput(BaseModel):
    """Input for find condo emails workflow."""

    condo_name: str = Field(..., description="Name of the condo to find emails for")
    address: str = Field(default="", description="Full address or description of the condo")
    location: str = Field(default="Singapore", description="Location of the condo")
    min_emails: int = Field(
        default=1, description="Minimum emails needed before skipping agent fallback"
    )


class FindCondoEmailsOutput(BaseModel):
    """Output from find condo emails workflow."""

    condo_name: str = Field(..., description="Name of the condo")
    emails_found: int = Field(..., description="Number of emails found")
    emails: list[str] = Field(..., description="List of email addresses found")
    output_file: str = Field(..., description="Path to the file containing emails")
    used_agent: bool = Field(..., description="Whether AI agent was used for extraction")


@workflow_api(name="find-condo-emails", version="v1")
@workflow.defn
class FindCondoEmailsWorkflow:
    """Workflow that finds contact emails for a condo using Brave Search.

    Uses a two-stage approach:
    1. Fast regex extraction from search results
    2. AI agent fallback if not enough emails found
    """

    @workflow.run
    async def run(self, input: FindCondoEmailsInput) -> FindCondoEmailsOutput:
        """Execute the find condo emails workflow.

        Args:
            input: Workflow input with condo name

        Returns:
            Result with found emails and file path
        """
        condo_name = input.condo_name
        condo_address = input.address
        location = input.location
        min_emails = input.min_emails

        workflow.logger.info(
            f"Finding emails for condo: {condo_name} at {condo_address or 'unknown address'}"
        )

        # Step 1: Search for condo information using Brave Search
        workflow.logger.info("Searching Brave for condo contact information...")
        search_results = await brave_search_condo.execute(condo_name, condo_address, location)
        workflow.logger.info(f"Found {len(search_results)} search results")

        # Step 2: Try fast regex extraction first
        workflow.logger.info("Attempting regex extraction from search results...")
        emails = await extract_emails_from_results.execute(search_results)
        workflow.logger.info(f"Regex extraction found {len(emails)} emails")

        used_agent = False

        # Step 3: If not enough emails found, use AI agent fallback
        if len(emails) < min_emails:
            workflow.logger.info(
                f"Only found {len(emails)} emails (need {min_emails}), "
                "falling back to AI agent for web scraping..."
            )
            try:
                # Run the agent directly in the workflow context
                agent_emails = await self._extract_emails_with_agent(
                    condo_name, condo_address, search_results
                )
                workflow.logger.info(f"Agent found {len(agent_emails)} additional emails")

                # Combine and deduplicate
                all_emails = set(emails) | set(agent_emails)
                emails = sorted(all_emails)
                used_agent = True

                workflow.logger.info(f"Total unique emails after agent: {len(emails)}")
            except Exception as e:
                workflow.logger.warning(f"Agent extraction failed: {e}, using regex results only")

        # Step 4: Save emails to file
        workflow.logger.info("Saving emails to file...")
        output_file = await save_condo_emails.execute(condo_name, emails)
        workflow.logger.info(f"Saved {len(emails)} emails to: {output_file}")

        return FindCondoEmailsOutput(
            condo_name=condo_name,
            emails_found=len(emails),
            emails=emails,
            output_file=output_file,
            used_agent=used_agent,
        )

    async def _extract_emails_with_agent(
        self, condo_name: str, condo_address: str, search_results: list[dict[str, str]]
    ) -> list[str]:
        """
        Use AI agent to scrape websites and extract emails (runs in workflow context).

        Args:
            condo_name: Name of the condo
            condo_address: Full address/description of the condo
            search_results: List of search results from Brave

        Returns:
            List of extracted email addresses
        """
        # Create context for the agent
        results_text = "\n\n".join(
            [
                f"Title: {r['title']}\nURL: {r['url']}\nDescription: {r['description']}"
                for r in search_results[:5]  # Limit to top 5 to avoid too much context
            ]
        )

        location_info = f' at address "{condo_address}"' if condo_address else " in Singapore"
        context = f"""You are helping find contact email addresses for "{condo_name}"{location_info}.

Here are the top search results:

{results_text}

Your task:
1. Visit the most promising URLs above to find contact email addresses
2. Look for management office emails, sales office emails, or general inquiry emails
3. Extract all valid email addresses you find
4. Return ONLY the email addresses, one per line, with no additional text

Focus on official emails from property management, sales offices, or official condo websites.
"""

        # Run the agent in the workflow context
        result = await Runner.run(email_extractor, context, max_turns=15)

        # Extract emails from the agent's output
        output = result.final_output
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, output)

        # Deduplicate and return
        return sorted(set(emails))
