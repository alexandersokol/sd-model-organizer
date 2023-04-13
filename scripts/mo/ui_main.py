import re
import os
import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.ui_records_list import records_list_ui_block
from scripts.mo.ui_edit_model import edit_model_ui_block
from scripts.mo.ui_record_details import record_details_ui_block
from scripts.mo.environment import env


def _load_mo_css() -> str:
    # TODO add and check dark theme colors
    colors_css_path = os.path.join(env.mo_script_dir, 'colors-light.css')
    with open(colors_css_path, 'r') as colors_file:
        colors_css = colors_file.read()

    styles_css_path = os.path.join(env.mo_script_dir, 'styles.css')
    with open(styles_css_path, 'r') as styles_file:
        styles_css = styles_file.read()

    card_width = env.mo_card_width()
    card_height = env.mo_card_height()
    if card_width:
        styles_css = re.sub(r'--mo-card-width:\s*\d+px;', f'--mo-card-width: {card_width}px;', styles_css)
    if card_height:
        styles_css = re.sub(r'--mo-card-height:\s*\d+px;', f'--mo-card-height: {card_height}px;', styles_css)

    return f"""
        <style>
            {colors_css}
            {styles_css}
        </style>
    """


def main_ui_block():
    with gr.Blocks() as main_block:
        gr.HTML(_load_mo_css())
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
