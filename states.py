import gradio as gr
import json
import os

paths_file = "paths.txt"

def get_latest_config_path():
    """Retrieve the latest configuration file path from paths.txt."""
    if os.path.exists(paths_file):
        with open(paths_file, "r") as f:
            paths = f.read().strip().split("\n")
            if paths:
                return paths[-1]  # Use the last saved config path
    return None

def extract_states_as_markdown():
    """Extracts global prompts and states from JSON and returns markdown."""
    config_file_path = get_latest_config_path()

    if config_file_path is None:
        return "Config file path is not available yet. Please create a configuration first."
    
    try:
        with open(config_file_path, 'r') as f:
            json_data = json.load(f)
        
        markdown_content = ""

        # Extract global prompts
        if 'global_prompt' in json_data['agent_config']:
            markdown_content += f"### Global Prompts\n\n{json_data['agent_config']['global_prompt']}\n\n"

        # Extract states
        agent_states = json_data['agent_config'].get('states', {})
        for state_name, state_data in agent_states.items():
            if 'instructions' in state_data:
                markdown_content += f"### {state_name}\n\n{state_data['instructions']}\n\n"

        return markdown_content
    except Exception as e:
        return f"Error extracting states: {str(e)}"

with gr.Blocks() as state_loader_app:
    gr.Markdown("## Load Agent States")

    load_btn = gr.Button("Load States")
    output_md = gr.Markdown()

    load_btn.click(extract_states_as_markdown, outputs=output_md)

if __name__ == "__main__":
    state_loader_app.launch()
