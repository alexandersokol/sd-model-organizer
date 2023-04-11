import gradio as gr

from scripts.mo.environment import env


def records_list_ui_block():
    with gr.Blocks() as records_list_block:
        gr.Markdown(f'Records List {env.mo_storage_type()}')
    return records_list_block
