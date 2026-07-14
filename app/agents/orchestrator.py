"""Runs the end-to-end research pipeline:

Researcher (web_search tool) -> Analyst -> Strategist -> Writer -> final report
"""

from app.agents.agents import (
    build_researcher,
    build_analyst,
    build_strategist,
    build_writer,
)


def _get_last_text(chat_result) -> str:
    """Pulls the last non-empty message content out of an AutoGen chat result."""
    for msg in reversed(chat_result.chat_history):
        content = (msg.get("content") or "").strip()
        if content and content != "TERMINATE":
            return content.replace("TERMINATE", "").strip()
    return ""


def run_research_pipeline(company_name: str) -> dict:
    """Runs the full multi-agent pipeline for a given company name.

    Returns:
        dict with keys: raw_research, structured_summary, suggestions, final_report
    """
    # 1. Researcher gathers raw findings via web_search tool calls
    researcher, executor = build_researcher()
    research_prompt = (
        f"Research the company '{company_name}'. Gather information on: "
        f"company overview, products/services, recent news (last 6-12 months), "
        f"market position, competitors, and leadership. Use the web_search tool "
        f"for each topic."
    )
    chat_result = executor.initiate_chat(
        researcher,
        message=research_prompt,
        max_turns=8,
    )
    raw_research = _get_last_text(chat_result)

    # 2. Analyst structures the raw findings
    analyst = build_analyst()
    structured_summary = analyst.generate_reply(
        messages=[
            {
                "role": "user",
                "content": f"Raw research notes on '{company_name}':\n\n{raw_research}",
            }
        ]
    )
    structured_summary = _as_text(structured_summary)

    # 3. Strategist generates suggestions
    strategist = build_strategist()
    suggestions = strategist.generate_reply(
        messages=[
            {
                "role": "user",
                "content": (
                    f"Structured research summary for '{company_name}':\n\n"
                    f"{structured_summary}"
                ),
            }
        ]
    )
    suggestions = _as_text(suggestions)

    # 4. Writer compiles the final report
    writer = build_writer()
    final_report = writer.generate_reply(
        messages=[
            {
                "role": "user",
                "content": (
                    f"Company: {company_name}\n\n"
                    f"Research summary:\n{structured_summary}\n\n"
                    f"Suggestions section:\n{suggestions}"
                ),
            }
        ]
    )
    final_report = _as_text(final_report)

    return {
        "company_name": company_name,
        "raw_research": raw_research,
        "structured_summary": structured_summary,
        "suggestions": suggestions,
        "final_report": final_report,
    }


def _as_text(reply) -> str:
    """AssistantAgent.generate_reply can return a string or a dict; normalize to str."""
    if isinstance(reply, dict):
        return reply.get("content", "") or ""
    return reply or ""
