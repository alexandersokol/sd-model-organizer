import gradio as gr

from scripts.mo.ui_records_list import records_list_ui_block
from scripts.mo.environment import env


def main_ui_block():
    with gr.Blocks() as main_block:
        if env.is_storage_has_errors():
            gr.Markdown(f'<span style="color:red">{env.storage_error}</color>')
            return main_block
        elif not env.is_storage_initialized():
            gr.Markdown(f'<span style="color:red">Storage not initialized</color>')
            return main_block

        records_list_ui_block()
    return main_block
