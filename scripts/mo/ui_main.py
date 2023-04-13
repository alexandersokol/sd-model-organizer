import re
import os
import gradio as gr
import json

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


def _content_list_state() -> str:
    return '{}'


def _details_state(record_id) -> str:
    state = {
        'screen': 'record_details',
        'record_id': record_id
    }
    return json.dumps(state)


def _edit_state(record_id, previous_state=None) -> str:
    state = {
        'screen': 'record_edit',
        'record_id': record_id
    }
    if previous_state is not None:
        state['previous'] = previous_state

    return json.dumps(state)


def _add_state() -> str:
    state = {
        'screen': 'record_edit'
    }
    return json.dumps(state)


def on_json_box_change(json_state):
    state = json.loads(json_state)

    is_content_list_visible = False
    is_details_visible = False
    is_edit_visible = False
    details_record_id = ''
    edit_record_id = ''

    if state.get('screen') is None:
        is_content_list_visible = True
    else:
        if state['screen'] == 'record_details':
            is_details_visible = True
            details_record_id = state['record_id']
        elif state['screen'] == 'record_edit':
            is_edit_visible = True
            if state.get('record_id') is not None:
                edit_record_id = state['record_id']
    return [
        gr.Column.update(visible=is_content_list_visible),
        gr.Column.update(visible=is_details_visible),
        gr.Column.update(visible=is_edit_visible),
    ]


def on_content_list_click():
    return _content_list_state()


def on_details_click():
    return _details_state(9)


def on_add_click():
    return _add_state()


def on_edit_click(previous_state):
    return _edit_state(9, previous_state)


def main_ui_block():
    with gr.Blocks() as main_block:
        gr.HTML(_load_mo_css())
        if env.is_storage_has_errors():
            gr.HTML(styled.alert_danger(env.storage_error))
            return main_block
        elif not env.is_storage_initialized():
            gr.HTML(styled.alert_danger('Storage not initialized'))
            return main_block

        json_box = gr.Textbox(_content_list_state())

        with gr.Row():
            content_list_button = gr.Button('Content List')
            details_button = gr.Button('Details (9)')
            add_button = gr.Button('Add')
            edit_button = gr.Button('Edit (9)')

        with gr.Column(visible=True) as content_list_block:
            records_list_ui_block()

        with gr.Column(visible=False) as record_details_block:
            record_details_ui_block(9)

        with gr.Column(visible=False) as edit_record_block:
            edit_model_ui_block()

        json_box.change(on_json_box_change,
                        inputs=json_box,
                        outputs=[content_list_block, record_details_block, edit_record_block])

        content_list_button.click(on_content_list_click, outputs=json_box)
        details_button.click(on_details_click, outputs=json_box)
        add_button.click(on_add_click, outputs=json_box)
        edit_button.click(on_edit_click, inputs=json_box, outputs=json_box)

    return main_block
