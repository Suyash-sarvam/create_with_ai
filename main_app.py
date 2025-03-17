import gradio as gr
import app2
import states
import variables

with gr.Blocks() as demo:
    gr.Markdown("## AI Assistant Control Panel")

    with gr.Tabs():
        with gr.Tab("Main App"):
            app2.app.render()  
        
        with gr.Tab("States"):
            states.state_loader_app.render() 
        
        with gr.Tab("Variables"):
            variables.variable_loader_app.render() 

if __name__ == "__main__":
    demo.launch()
