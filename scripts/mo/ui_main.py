import gradio as gr


def main_ui_block():
    with gr.Blocks() as main_block:
        gr.Markdown("Hello there")
    return main_block
