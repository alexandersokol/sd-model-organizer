import gradio as gr

from scripts.src.main import get_main_ui_block




def on_click():
    print("clicked")


with gr.Blocks() as demo:
    with gr.Tab("Model Organizer"):
        get_main_ui_block()
    with gr.Tab("Testing"):
        gr.Textbox("Tab block for feature testing", interactive=False)
        button = gr.Button("Button")
        button.click(on_click())

demo.launch()
