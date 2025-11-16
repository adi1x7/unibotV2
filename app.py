import gradio as gr
from sidekick import UniBot
import os
from dotenv import load_dotenv

load_dotenv(override=True)

async def setup():
    college_url = os.getenv("COLLEGE_WEBSITE_URL", None)
    unibot = UniBot(college_website_url=college_url)
    await unibot.setup()
    return unibot

def filter_feedback_messages(history):
    """Remove evaluator feedback messages from history"""
    if not history:
        return history
    filtered = []
    for msg in history:
        # Skip messages that are evaluator feedback
        content = msg.get("content", "") if isinstance(msg, dict) else ""
        if "Evaluator Feedback" not in str(content):
            filtered.append(msg)
    return filtered

async def process_message(unibot, message, success_criteria, history):
    # Don't process empty messages
    if not message or not message.strip():
        return history, unibot
    
    # Filter out any existing feedback messages from history
    history = filter_feedback_messages(history)
    
    results = await unibot.run_superstep(message, success_criteria, history)
    
    # Filter out feedback from results as well (just in case)
    results = filter_feedback_messages(results)
    
    return results, unibot
    
async def reset():
    college_url = os.getenv("COLLEGE_WEBSITE_URL", None)
    new_unibot = UniBot(college_website_url=college_url)
    await new_unibot.setup()
    return "", "", None, new_unibot

def free_resources(unibot):
    print("Cleaning up")
    try:
        if unibot:
            unibot.cleanup()
    except Exception as e:
        print(f"Exception during cleanup: {e}")


with gr.Blocks(title="UniBot", theme=gr.themes.Default(primary_hue="emerald")) as ui:
    gr.Markdown("## UniBot - College Query Assistant")
    gr.Markdown("Ask questions about your college! UniBot uses RAG to answer questions from scraped college website data.")
    unibot = gr.State(delete_callback=free_resources)
    
    with gr.Row():
        chatbot = gr.Chatbot(label="UniBot", height=400, type="messages")
    with gr.Group():
        with gr.Row():
            message = gr.Textbox(show_label=False, placeholder="Ask a question about your college (e.g., 'What courses are offered?', 'What are the admission requirements?')")
        with gr.Row():
            success_criteria = gr.Textbox(show_label=False, placeholder="Success criteria (optional - leave empty for default)")
    with gr.Row():
        reset_button = gr.Button("Reset", variant="stop")
        go_button = gr.Button("Ask UniBot", variant="primary")
        
    ui.load(setup, [], [unibot])
    message.submit(process_message, [unibot, message, success_criteria, chatbot], [chatbot, unibot])
    success_criteria.submit(process_message, [unibot, message, success_criteria, chatbot], [chatbot, unibot])
    go_button.click(process_message, [unibot, message, success_criteria, chatbot], [chatbot, unibot])
    reset_button.click(reset, [], [message, success_criteria, chatbot, unibot])

    
ui.launch(inbrowser=True)