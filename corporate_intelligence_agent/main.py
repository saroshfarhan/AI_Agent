import asyncio
import os
import logging
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from agents import manager_agent, quant_agent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Load API Key
    load_dotenv()
    if "GOOGLE_API_KEY" not in os.environ:
        print("⚠️ GOOGLE_API_KEY not found in environment. Please add it to your .env file.")
        return

    print("✅ API Key loaded successfully.")
    
    # Initialize Runner
    runner = InMemoryRunner(agent=manager_agent)
    
    # Example Query
    ticker = "AAPL"
    query = f"Get fundamentals for {ticker}"
    
    print(f"\n🤖 Corporate Intelligence Agent initialized. Running analysis for: {ticker}...\n")
    
    # Run the agent
    # Note: run_debug prints the output to stdout
    await runner.run_debug(query)

if __name__ == "__main__":
    asyncio.run(main())
