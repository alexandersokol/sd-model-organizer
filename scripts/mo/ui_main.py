import gradio as gr

from scripts.mo.ui_edit_model import edit_model_ui_block


def main_ui_block():
    with gr.Blocks() as main_block:
        edit_model_ui_block()
    return main_block
