import gradio as gr
import json
from author import render_template
from llm import get_completion, async_client
import os 
import uuid
import pandas as pd

config_file_path = None
paths_file = "paths.txt"

def save_config_path(file_path):
    """ Append the config file path to paths.txt """
    if file_path:
        with open(paths_file, "a") as f:
            f.write("\n" + file_path + "\n")

def expand_input(input_text):
    if not input_text:
        return "Please provide some input text to expand."
    
    kwargs = {"user_input": input_text}
    prompt = render_template("transform.j2", **kwargs)
    response = get_completion(prompt, model_id='3-5')

    return response

async def generate_agent_config(usecase_details):
    os.makedirs("configs", exist_ok=True)

    kwargs = {"usecase_details": usecase_details}
    prompt = render_template("v2v.j2", **kwargs)

    llm_config = {
        "max_tokens": 15000,
        "thinking": {
            "type": "enabled",
            "budget_tokens": 3000
        },
    }

    final_response = ""
    thinking_text = ""

    async with async_client.messages.stream(
        model="claude-3-7-sonnet-20250219",
        messages=[{"role": "user", "content": prompt}],
        **llm_config
    ) as stream:
        async for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "thinking_delta":
                    thinking_text += event.delta.thinking  
                    yield thinking_text, {}, None
                elif event.delta.type == "text_delta":
                    final_response += event.delta.text  

    final_response = json.loads(final_response)

    file_name = f'{uuid.uuid4()}.json'
    file_path = os.path.join("configs", file_name)

    with open(file_path, 'w') as f:
        json.dump(final_response, f, indent=4)   

    yield None, json.dumps({"message": "Configuration saved", "file_path": file_path, "config": final_response}, indent=2), file_path

async def create_agent_config(expanded_text):
    global config_file_path
    async for thinking_text, config_json, file_path in generate_agent_config(expanded_text):
        if file_path:  
            config_file_path = file_path 
            save_config_path(config_file_path)  # Save the path to `paths.txt`
        yield thinking_text, config_json, gr.update(visible=True), gr.update(visible=True)

with gr.Blocks() as app:
    gr.Markdown("## Create with AI")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Enter input")
            input_text = gr.Textbox(lines=5, placeholder="Type your input here...")
            expand_btn = gr.Button("Expand input")
        
        with gr.Column():
            gr.Markdown("### Expanded input")
            expanded_output = gr.Textbox(lines=15, show_copy_button=True, interactive=True)
    
    with gr.Row():
        with gr.Column(scale=1):
            pass
        with gr.Column(scale=2):
            create_btn = gr.Button("Create with AI")
        with gr.Column(scale=1):
            pass
    
    thinking_output = gr.Textbox(label="Thinking...", lines=10, interactive=False)
    config_output = gr.JSON(label="Generated Configuration")

    expand_btn.click(expand_input, inputs=input_text, outputs=expanded_output)
    create_btn.click(create_agent_config, inputs=expanded_output, outputs=[thinking_output, config_output])
# Launch the app
if __name__ == "__main__":
    app.queue() 
    app.launch()
