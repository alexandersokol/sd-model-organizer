import gradio as gr


def left_block():
    pass


def right_block():
    pass


def model_ui_block():
    with gr.Column() as model_block:
        gr.Markdown("Model block")
    return model_block
