
from agents import Agent, Runner, function_tool


planner = Agent(
    name="IssuePlanner",
    model="gpt-5.2",  # use your preferred model
    instructions=(
        "You convert a GitHub research issue into a short, actionable investigation plan.\n"
        "Output MUST be JSON with keys:\n"
        "topic, hypotheses[], search_queries[], steps[], success_criteria[], risks[]\n"
        "Keep steps concrete and tool-friendly.\n"
    ),
)
