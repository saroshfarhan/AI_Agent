from google.adk.agents import Agent, LlmAgent
from google.adk.tools import AgentTool, google_search
from tools import get_fundamentals, get_outlook, parse_sec_filing

MODEL_NAME = "gemini-2.5-flash-lite"

# 1. Quant Agent
quant_agent = Agent(
    name="QuantAgent",
    model=MODEL_NAME,
    description="A financial analyst that provides fundamental data.",
    instruction="You are a financial analyst. Use the `get_fundamentals` tool to analyze the company's financial health. Return a concise text summary of the fundamentals.",
    tools=[get_fundamentals]
)

# 2. Investigator Agent
# currently not being used as google_search agent does the job for now. Maybe I can
# make this a sentiment analysis agent which gets sentiments from varios solical media sites.
# investigator_agent = Agent(
#     name="InvestigatorAgent",
#     model=MODEL_NAME,
#     description="A risk investigator that finds news, regulatory issues, and sentiment.",
#     instruction="""You are a risk investigator. Use the `google_search` tool to identify risks, regulatory issues, and market sentiment.
#     Search for terms like 'lawsuits', 'regulatory investigation', 'scandal', and 'analyst sentiment'.
#     Use `score_sentiment` to evaluate the mood of recent headlines if needed.
#     Return a concise text summary of the risks and sentiment found.""",
#     tools=[score_sentiment]
# )

# 2 Research Agent
research_agent = Agent(
    name = "ReasearchAgent",
    model = MODEL_NAME,
    description = "A research agent that finds new, headlines, issues.",
    instruction="""You are a reasearch agent thatuses 'google_search' tool to identify the latest news, regulatory issues, investigations against the firm, scandals, analyst sentiments, user sentiments from various sorces as shown but the 'google_search' agent.
    Focus on:
        - Lawsuits and regulatory investigations
        - Major product or strategy news
        - Analyst upgrades/downgrades

    Summarize the key risks and overall sentiment, with short inline citations like [1], [2].

    CRITICAL: Do not add information from your own, use the available online results from 'google_search' tool and then return a concise text summary.
    """,
    tools = [google_search]
)

# 3. Filings Agent
filings_agent = Agent(
    name="FilingsAgent",
    model=MODEL_NAME,
    description="A specialist in SEC filings.",
    instruction="""You are an expert in analyzing SEC filings (10-K, 10-Q). 
    Use the `parse_sec_filing` tool to extract key risks and financial highlights from the latest reports.
    Summarize the top 3 critical insights.""",
    tools=[parse_sec_filing]
)

# 4. Futurist Agent
futurist_agent = Agent(
    name="FuturistAgent",
    model=MODEL_NAME,
    description="A market futurist that provides an experimental short-term outlook.",
    instruction="You are a market futurist. Use the `get_outlook` tool to provide an experimental forecast. Return a concise text summary of the outlook.",
    tools=[get_outlook]
)


# 5. Manager Agent (The Orchestrator)
class ManagerAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="ManagerAgent",
            model=MODEL_NAME,
            instruction="""You are the Chief Financial Analyst of an investment firm.

            Your goal is to produce a comprehensive 3-paragraph report on a company
            based on input from your specialist agents.

            You can call these agent-tools:
            - QuantAgent: fetches and summarizes fundamentals using market data.
            - ResearchAgent: searches the web (via google_search) for news & risks.
            - FilingsAgent: extracts key risks & highlights from recent SEC filings.
            - FuturistAgent: provides an experimental short-term outlook.

            Process:
            1. Call QuantAgent to get the financial fundamentals.
            2. Call ResearchAgent to get recent news, risks, and sentiment.
            3. Call FilingsAgent to get SEC filing insights.
            4. Call FuturistAgent to get the outlook.
            5. Synthesize everything into EXACTLY three sections:

            - **Summary** (Fundamentals & Filings Highlights)
            - **Risks & Recent Developments** (News/Risks/Sentiment)
            - **Experimental Outlook** (Forecast; clearly marked as experimental, not advice)

            Each section should be 2-4 sentences. Keep the tone clear and professional.
    """,
            tools=[
               AgentTool(agent=quant_agent),
               AgentTool(agent=research_agent),
               AgentTool(agent=filings_agent),
               AgentTool(agent=futurist_agent),
            ]
        )

manager_agent = ManagerAgent()