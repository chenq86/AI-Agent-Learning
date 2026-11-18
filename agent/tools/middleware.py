from utils.prompt_loader import load_report_prompts, load_system_prompts
from typing import Callable
from langchain.agents import AgentState
from langchain.agents.middleware import ModelRequest, before_model, dynamic_prompt, wrap_tool_call
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger


@wrap_tool_call
def monitor_tool(
    #Wrapped tool-call request
    request: ToolCallRequest,
    #The underlying tool handler
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:          #Monitor tool execution
    logger.info(f"[tool monitor]Executing tool: {request.tool_call['name']}")
    logger.info(f"[tool monitor]Input arguments: {request.tool_call['args']}")

    try:
        result = handler(request)
        logger.info(f"[tool monitor]工具{request.tool_call['name']} completed successfully")

        if request.tool_call['name'] == "fill_context_for_report":
            request.runtime.context["report"] = True
        
        return result
    except Exception as e:
        logger.error(f"Tool {request.tool_call['name']} failed: {str(e)}")
        raise e


@before_model
def log_before_model(
    state:AgentState,       #State maintained throughout agent execution
    runtime: Runtime,       #Runtime context for the execution
):     #Log before model execution
    logger.info(f"[log_before_model]Calling the model with {len(state['messages'])} messages.")
    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()}")

    return None


@dynamic_prompt                 #Call this function before generating each system prompt.
def report_prompt_switch(request: ModelRequest):     #Switch the prompt dynamically
    is_report = request.runtime.context.get("report", False)
    if is_report:               #Return the report prompt in report-generation mode.
        return load_report_prompts()

    return load_system_prompts()