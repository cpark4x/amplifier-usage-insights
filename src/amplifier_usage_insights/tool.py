"""Amplifier tool module for usage insights.

This module implements the Amplifier Tool protocol to make usage insights
available in any Amplifier session via settings.yaml configuration.
"""

from typing import Any


def get_tool_definitions() -> list[dict[str, Any]]:
    """
    Return tool definitions for Amplifier.

    Returns:
        List of tool definition dictionaries with name, description, and parameters
    """
    return [
        {
            "name": "get_usage_insights",
            "description": (
                "Get insights about your AI collaboration effectiveness. "
                "Ask natural language questions like 'How am I doing?', "
                "'What tools do I use most?', 'Am I improving?'. "
                "Analyzes your Amplifier session history to provide personalized feedback."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "What you want to know about your AI usage. Examples: "
                            "'How am I doing this week?', "
                            "'Show my tool usage', "
                            "'Am I improving?'"
                        ),
                        "default": "How am I doing this week?",
                    }
                },
                "required": [],
            },
        }
    ]


async def handle_tool_call(
    tool_name: str, tool_input: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    """
    Handle tool invocations from Amplifier.

    Args:
        tool_name: Name of the tool being called
        tool_input: Input parameters from the tool call
        context: Additional context from Amplifier (unused currently)

    Returns:
        Dictionary with response or error
    """
    if tool_name != "get_usage_insights":
        return {"error": f"Unknown tool: {tool_name}"}

    # Get query parameter with default
    query = tool_input.get("query", "How am I doing this week?")

    # Call the insights function
    from .insights import get_personal_insights

    result = get_personal_insights(query)

    return result


def mount(coordinator: Any, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Mount the tool to Amplifier coordinator.

    This function is called by Amplifier when loading the tool module.
    It registers all tool definitions with the coordinator.

    Args:
        coordinator: Amplifier coordinator instance
        config: Optional configuration dictionary (unused currently)

    Returns:
        Dictionary with module metadata (name, version, tools)
    """
    tools = get_tool_definitions()

    # Register each tool with the coordinator
    for tool_def in tools:
        coordinator.register_tool(tool_def, handle_tool_call)

    return {
        "name": "tool-usage-insights",
        "version": "0.5.0",
        "tools": [t["name"] for t in tools],
    }
