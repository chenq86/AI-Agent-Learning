from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import rag_summarize, get_weather, get_user_location, get_user_id, get_current_month, fetch_external_data, fill_context_for_report
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
from langchain_core.messages import AIMessage

class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model= chat_model,
            system_prompt=load_system_prompts(),
            tools=[rag_summarize, get_weather, get_user_location, get_user_id, get_current_month, fetch_external_data, fill_context_for_report],
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )



    def execute_stream(self, prompt):
        input_dict = {
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        result = self.agent.invoke(
            input_dict,
            context={"report": False}
        )
        print("\n========== AGENT MESSAGE TRACE ==========")

        for i, message in enumerate(result["messages"]):
            print(f"\nMessage {i}")
            print("Type:", type(message).__name__)
            print("Content:", repr(message.content)[:1500])

            if isinstance(message, AIMessage):
                print("Tool calls:", message.tool_calls)

        print("========================================\n")

        # Debug: inspect the final message
        print("\n========== FINAL AI MESSAGE ==========")
        print(repr(result["messages"][-1].content))
        print("======================================\n")

        for message in reversed(result["messages"]):
            if isinstance(message, AIMessage):
                if message.content and not message.tool_calls:
                    yield message.content.strip()
                    return


if __name__ == "__main__":
    agent = ReactAgent()

    for chunk in agent.execute_stream("Generate my usage report"):
        print(chunk, end="", flush=True)