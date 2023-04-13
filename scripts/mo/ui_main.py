import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.ui_records_list import records_list_ui_block
from scripts.mo.ui_edit_model import edit_model_ui_block
from scripts.mo.ui_record_details import record_details_ui_block
from scripts.mo.environment import env

# TODO add and check dark theme colors
css_styles = f"""
    <style>
        {open('colors-light.css', 'r').read()}
        {open('style.css', 'r').read()}
    </style>
"""


def main_ui_block():
    with gr.Blocks() as main_block:
        gr.HTML(css_styles)
        if env.is_storage_has_errors():
            gr.HTML(styled.alert_danger(env.storage_error))
            return main_block
        elif not env.is_storage_initialized():
            gr.HTML(styled.alert_danger('Storage not initialized'))
            return main_block

        # record_details_ui_block(9)
        records_list_ui_block()
        # edit_model_ui_block()

    return main_block
