from dotenv import load_dotenv
load_dotenv()
from divination.agent import DivinationAgent

agent = DivinationAgent()
result = agent.extract_basic_info("你好 男 2026/04/07")
print(result)
