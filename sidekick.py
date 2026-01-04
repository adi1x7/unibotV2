from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import List, Any, Optional, Dict
from pydantic import BaseModel, Field
from sidekick_tools import playwright_tools, other_tools
from rag_system import RAGSystem
import uuid
import asyncio
import os
from datetime import datetime

load_dotenv(override=True)

class State(TypedDict):
    messages: Annotated[List[Any], add_messages]
    success_criteria: str
    feedback_on_work: Optional[str]
    success_criteria_met: bool
    user_input_needed: bool


class EvaluatorOutput(BaseModel):
    feedback: str = Field(description="Feedback on the assistant's response")
    success_criteria_met: bool = Field(description="Whether the success criteria have been met")
    user_input_needed: bool = Field(description="True if more input is needed from the user, or clarifications, or the assistant is stuck")


class UniBot:
    def __init__(self, college_website_url: Optional[str] = None):
        self.worker_llm_with_tools = None
        self.evaluator_llm_with_output = None
        self.tools = None
        self.llm_with_tools = None
        self.graph = None
        self.unibot_id = str(uuid.uuid4())
        self.memory = MemorySaver()
        self.browser = None
        self.playwright = None
        self.rag_system = RAGSystem()
        self.college_website_url = college_website_url

    async def setup(self):
        # Verify API key is set
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Please set it in your .env file or environment variables."
            )
        
        self.tools, self.browser, self.playwright = await playwright_tools()
        self.tools += await other_tools(rag_system=self.rag_system)
        
        # Use gemini-2.5-flash (latest, fast, widely available)
        # If this doesn't work, try gemini-1.5-pro or check available models with list_available_models.py
        worker_model = "gemini-2.5-flash"
        worker_llm = ChatGoogleGenerativeAI(model=worker_model)
        self.worker_llm_with_tools = worker_llm.bind_tools(self.tools)
        evaluator_llm = ChatGoogleGenerativeAI(model=worker_model)
        self.evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)
        await self.build_graph()

    def worker(self, state: State) -> Dict[str, Any]:
        system_message = f"""You are UniBot, a college query assistant for answering questions about the college.
    You have access to a knowledge base containing information scraped from the college website.
    
    CRITICAL RULE: For ANY question about the college, courses, admissions, faculty, facilities, policies, events, or ANY college-related information,
    you MUST ALWAYS call the query_college_knowledge_base tool FIRST before providing any answer. 
    DO NOT answer directly without searching the knowledge base first.
    
    WORKFLOW:
    1. User asks a question about the college
    2. You MUST call query_college_knowledge_base with the user's question
    3. Wait for the tool to return results
    4. Use the information from the tool results to answer the user
    5. Include the source links from the tool output
    
    IMPORTANT: Do NOT scrape the website unless the user explicitly asks you to do so. The knowledge base should already have the information you need.
    Only use the scrape_college_website tool if:
    - The user explicitly requests you to scrape the website
    - The user asks you to update or refresh the knowledge base
    
    If the knowledge base doesn't have enough information for a user's question, simply tell the user that the information is not available in the knowledge base. Do not suggest any alternative actions or scraping.
    
    SOURCE CITATION: When you provide information from the knowledge base, ALWAYS include the source links at the end of your response.
    The knowledge base tool will provide a "Sources:" section with URLs formatted as markdown links like [URL](URL).
    You MUST copy these markdown links EXACTLY as they appear - do NOT summarize, rename, abbreviate, or change the format.
    Simply copy the entire "Sources:" section from the tool output and include it at the end of your response.
    Example format:
    Sources:
    1. [https://bmsit.ac.in/admissions](https://bmsit.ac.in/admissions)
    2. [https://bmsit.ac.in/public/assets/pdf/fee/structure.pdf](https://bmsit.ac.in/public/assets/pdf/fee/structure.pdf)
    
    DO NOT use generic names like "BMSIT Administration" - copy the EXACT markdown links from the sources section.
    
    You keep working on a task until either you have a question or clarification for the user, or the success criteria is met.
    You have many tools to help you, including tools to browse the internet, navigating and retrieving web pages.
    You have a tool to run python code, but note that you would need to include a print() statement if you wanted to receive output.
    The current date and time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    This is the success criteria:
    {state['success_criteria']}
    
    REMEMBER: For college-related questions, you MUST call query_college_knowledge_base tool first. 
    Do not provide answers without searching the knowledge base first.
    
    You should reply either with a question for the user about this assignment, or with your final response.
    If you have a question for the user, you need to reply by clearly stating your question. An example might be:

    Question: please clarify whether you want a summary or a detailed answer

    If you've finished, reply with the final answer, and don't ask a question; simply reply with the answer.
    """
        
        if state.get("feedback_on_work"):
            system_message += f"""
    Previously you thought you completed the assignment, but your reply was rejected because the success criteria was not met.
    Here is the feedback on why this was rejected:
    {state['feedback_on_work']}
    With this feedback, please continue the assignment, ensuring that you meet the success criteria or have a question for the user."""
        
        # Add in the system message

        found_system_message = False
        messages = state["messages"]
        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = system_message
                found_system_message = True
        
        if not found_system_message:
            messages = [SystemMessage(content=system_message)] + messages
        
        # Invoke the LLM with tools
        response = self.worker_llm_with_tools.invoke(messages)
        
        # Return updated state
        return {
            "messages": [response],
        }


    def worker_router(self, state: State) -> str:
        last_message = state["messages"][-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        else:
            return "evaluator"
        
    def format_conversation(self, messages: List[Any]) -> str:
        conversation = "Conversation history:\n\n"
        for message in messages:
            if isinstance(message, HumanMessage):
                conversation += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                text = message.content or "[Tools use]"
                conversation += f"Assistant: {text}\n"
        return conversation
        
    def evaluator(self, state: State) -> State:
        if not state["messages"]:
            return {
                "messages": [{"role": "assistant", "content": "No messages to evaluate"}],
                "feedback_on_work": "No messages found",
                "success_criteria_met": False,
                "user_input_needed": True
            }
        last_message = state["messages"][-1]
        # Handle both message objects and dicts
        if hasattr(last_message, 'content'):
            last_response = last_message.content or ""
        elif isinstance(last_message, dict):
            last_response = last_message.get('content', '')
        else:
            last_response = str(last_message) if last_message else ""

        system_message = f"""You are an evaluator that determines if a task has been completed successfully by an Assistant.
    Assess the Assistant's last response based on the given criteria. Respond with your feedback, and with your decision on whether the success criteria has been met,
    and whether more input is needed from the user."""
        
        user_message = f"""You are evaluating a conversation between the User and Assistant. You decide what action to take based on the last response from the Assistant.

    The entire conversation with the assistant, with the user's original request and all replies, is:
    {self.format_conversation(state['messages'])}

    The success criteria for this assignment is:
    {state['success_criteria']}

    And the final response from the Assistant that you are evaluating is:
    {last_response}

    Respond with your feedback, and decide if the success criteria is met by this response.
    Also, decide if more user input is required, either because the assistant has a question, needs clarification, or seems to be stuck and unable to answer without help.

    The Assistant has access to a tool to write files. If the Assistant says they have written a file, then you can assume they have done so.
    Overall you should give the Assistant the benefit of the doubt if they say they've done something. But you should reject if you feel that more work should go into this.

    """
        if state["feedback_on_work"]:
            user_message += f"Also, note that in a prior attempt from the Assistant, you provided this feedback: {state['feedback_on_work']}\n"
            user_message += "If you're seeing the Assistant repeating the same mistakes, then consider responding that user input is required."
        
        evaluator_messages = [SystemMessage(content=system_message), HumanMessage(content=user_message)]

        eval_result = self.evaluator_llm_with_output.invoke(evaluator_messages)
        new_state = {
            "messages": [{"role": "assistant", "content": f"Evaluator Feedback on this answer: {eval_result.feedback}"}],
            "feedback_on_work": eval_result.feedback,
            "success_criteria_met": eval_result.success_criteria_met,
            "user_input_needed": eval_result.user_input_needed
        }
        return new_state

    def route_based_on_evaluation(self, state: State) -> str:
        if state["success_criteria_met"] or state["user_input_needed"]:
            return "END"
        else:
            return "worker"


    async def build_graph(self):
        # Set up Graph Builder with State
        graph_builder = StateGraph(State)

        # Add nodes
        graph_builder.add_node("worker", self.worker)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_node("evaluator", self.evaluator)

        # Add edges
        graph_builder.add_conditional_edges("worker", self.worker_router, {"tools": "tools", "evaluator": "evaluator"})
        graph_builder.add_edge("tools", "worker")
        graph_builder.add_conditional_edges("evaluator", self.route_based_on_evaluation, {"worker": "worker", "END": END})
        graph_builder.add_edge(START, "worker")

        # Compile the graph
        self.graph = graph_builder.compile(checkpointer=self.memory)

    async def run_superstep(self, message, success_criteria, history):
        config = {"configurable": {"thread_id": self.unibot_id}}

        # Convert history to message format if provided
        messages = []
        if history:
            for msg in history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))

        # Add the current message
        if isinstance(message, str):
            messages.append(HumanMessage(content=message))
        elif isinstance(message, list):
            messages.extend(message)
        else:
            messages.append(HumanMessage(content=str(message)))

        state = {
            "messages": messages,
            "success_criteria": success_criteria or "The answer should be clear and accurate",
            "feedback_on_work": None,
            "success_criteria_met": False,
            "user_input_needed": False
        }
        result = await self.graph.ainvoke(state, config=config)
        
        # Extract user message content for history
        user_content = message if isinstance(message, str) else (messages[0].content if messages else str(message))
        user = {"role": "user", "content": user_content}
        
        # Get the assistant's reply (skip evaluator feedback which is the last message)
        # The assistant's reply is the second-to-last message (before evaluator feedback)
        assistant_message = result["messages"][-2] if len(result["messages"]) >= 2 else None
        if assistant_message:
            # Extract content, handling different formats (string, list, etc.)
            assistant_content = assistant_message.content
            if isinstance(assistant_content, list):
                # Handle list format from new Gemini models
                text_parts = []
                for item in assistant_content:
                    if isinstance(item, dict) and 'text' in item:
                        text_parts.append(item['text'])
                    elif isinstance(item, str):
                        text_parts.append(item)
                assistant_reply = '\n'.join(text_parts) if text_parts else str(assistant_content)
            elif isinstance(assistant_content, dict):
                assistant_reply = assistant_content.get('text', str(assistant_content))
            else:
                assistant_reply = str(assistant_content) if assistant_content else ""
        else:
            assistant_reply = ""
        reply = {"role": "assistant", "content": assistant_reply}
        
        # Return only user and assistant messages (no evaluator feedback)
        return history + [user, reply]
    
    def cleanup(self):
        """Cleanup browser and playwright resources"""
        if self.browser or self.playwright:
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, schedule cleanup
                if self.browser:
                    loop.create_task(self.browser.close())
                if self.playwright:
                    loop.create_task(self.playwright.stop())
            except RuntimeError:
                # If no loop is running, create one and run cleanup
                async def cleanup_async():
                    if self.browser:
                        await self.browser.close()
                    if self.playwright:
                        await self.playwright.stop()
                try:
                    asyncio.run(cleanup_async())
                except Exception as e:
                    print(f"Warning: Error during cleanup: {e}")
