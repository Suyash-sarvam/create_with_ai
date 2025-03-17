
import gradio as gr
import json
import os
import pandas as pd

paths_file = "paths.txt"

def get_latest_config_path():
    """Retrieve the latest configuration file path from paths.txt."""
    if os.path.exists(paths_file):
        with open(paths_file, "r") as f:
            paths = f.read().strip().split("\n")
            if paths:
                return paths[-1]  # Use the last saved config path
    return None

def load_variables():
    """Loads agent variables from the latest configuration file."""
    config_file_path = get_latest_config_path()

    if config_file_path is None:
        return None  # Return empty to show blank page initially
    
    try:
        with open(config_file_path, 'r') as f:
            data = json.load(f)['agent_config']['agent_variables']
        
        df = pd.DataFrame(list(data.values()))
        return df
    except Exception as e:
        return f"Error loading variables: {str(e)}"

with gr.Blocks() as variable_loader_app:
    gr.Markdown("## Load Agent Variables")

    load_btn = gr.Button("Load Variables")
    output_df = gr.Dataframe(interactive=True)

    load_btn.click(load_variables, outputs=output_df)

if __name__ == "__main__":
    variable_loader_app.launch()
