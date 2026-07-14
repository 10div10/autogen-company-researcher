"""Defines the four AutoGen agents used in the research pipeline:

1. Researcher  - calls the web_search tool to gather raw information
2. Analyst     - synthesizes raw findings into structured sections
3. Strategist  - generates actionable suggestions/recommendations
4. Writer      - compiles everything into a polished final report
"""

import autogen
from app.config import LLM_CONFIG
from app.tools.web_search import web_search


def build_researcher():
    researcher = autogen.AssistantAgent(
        name="Researcher",
        system_message=(
            "You are a meticulous research analyst. Your job is to use the "
            "web_search tool to gather up-to-date, factual information about "
            "a company across these areas: company overview, products/services, "
            "recent news (last 6-12 months), market position, competitors, and "
            "leadership. Call web_search multiple times with focused queries "
            "(one topic per query). After gathering enough information, "
            "summarize all raw findings in plain text with source URLs. "
            "End your final message with the word TERMINATE."
        ),
        llm_config=LLM_CONFIG,
    )

    executor = autogen.UserProxyAgent(
        name="ToolExecutor",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda msg: "TERMINATE" in (msg.get("content") or ""),
        code_execution_config=False,
    )

    autogen.register_function(
        web_search,
        caller=researcher,
        executor=executor,
        name="web_search",
        description="Search the web for a query and return titles, snippets, and source URLs.",
    )

    return researcher, executor


def build_analyst():
    return autogen.AssistantAgent(
        name="Analyst",
        system_message=(
            "You are a sharp business analyst. Given raw research notes about "
            "a company, organize them into clear structured sections with "
            "markdown headings: Company Overview, Products & Services, "
            "Recent News & Developments, Market Position, Competitors, "
            "Leadership. Be factual, concise, and note the source URL next "
            "to key claims where available. Do not invent facts not present "
            "in the notes. Reply with the structured sections only."
        ),
        llm_config=LLM_CONFIG,
    )


def build_strategist():
    return autogen.AssistantAgent(
        name="Strategist",
        system_message=(
            "You are a strategy consultant. Given a structured company "
            "research summary, produce a section titled 'Suggestions & "
            "Opportunities' with 5-8 concrete, actionable suggestions "
            "(e.g. growth ideas, risk mitigations, competitive positioning, "
            "product gaps, partnership opportunities). Each suggestion should "
            "be 1-3 sentences, specific to the company, not generic advice. "
            "Reply with this section only."
        ),
        llm_config=LLM_CONFIG,
    )


def build_writer():
    return autogen.AssistantAgent(
        name="Writer",
        system_message=(
            "You are a professional report writer. Combine the structured "
            "research summary and the suggestions section into a single, "
            "polished markdown report with a title, a 2-3 sentence executive "
            "summary at the top, then the research sections, then the "
            "suggestions section. Keep formatting clean with markdown "
            "headings (#, ##) and bullet points. Do not add commentary "
            "outside the report."
        ),
        llm_config=LLM_CONFIG,
    )
