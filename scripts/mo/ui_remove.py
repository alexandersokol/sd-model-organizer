import os

import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env, logger
from scripts.mo.ui_navigation import generate_ui_token
from scripts.mo.utils import find_preview_file, find_info_file


def _on_id_change(record_id):
    logger.info('_on_id_change record_id: %s', record_id)

    if not record_id:
        return [
            gr.HTML.update(value='Record is missing.'),
            gr.Button.update(visible=False),
            gr.Button.update(visible=False),
            gr.Button.update(visible=False),
            gr.Button.update(visible=False)
        ]

    if os.path.isfile(record_id):
        return [
            gr.HTML.update(
                value=styled.alert_danger(f'Are you sure you what to remove "{os.path.basename(record_id)}"?')),
            gr.Button.update(visible=True),
            gr.Button.update(visible=False),
            gr.Button.update(visible=True),
            gr.Button.update(visible=False)
        ]
    else:
        record = env.storage.get_record_by_id(record_id)
        if record is None:
            return [
                gr.HTML.update(value='Record was not found in database.'),
                gr.Button.update(visible=False),
                gr.Button.update(visible=False),
                gr.Button.update(visible=False),
                gr.Button.update(visible=False)
            ]
        elif os.path.exists(record.location):
            return [
                gr.HTML.update(value=styled.alert_danger(f'Are you sure you what to remove "{record.name}"?')),
                gr.Button.update(visible=True),
                gr.Button.update(visible=True),
                gr.Button.update(visible=True),
                gr.Button.update(visible=True)
            ]
        else:
            return [
                gr.HTML.update(value=styled.alert_danger(f'Are you sure you what to remove "{record.name}"?')),
                gr.Button.update(visible=True),
                gr.Button.update(visible=True),
                gr.Button.update(visible=False),
                gr.Button.update(visible=False)
            ]

def _on_remove_record_button_click(record_id):
    env.storage.remove_record(record_id)
    logger.info('removed record: %s', record_id)
    return generate_ui_token()

def _on_remove_files_button_click(record_id):
    if os.path.isfile(record_id):
        logger.info('removed local model file: %s', record_id)
        os.remove(record_id)

        preview_path = find_preview_file(record_id)
        if preview_path and os.path.exists(preview_path):
            logger.info('removed local preview files: %s', preview_path)
            os.remove(preview_path)
    else:
        record = env.storage.get_record_by_id(record_id)
        if record.location and os.path.exists(record.location):
            logger.info('removed model file: %s', record.location)
            os.remove(record.location)

        preview_path = find_preview_file(record.location)
        if preview_path and os.path.exists(preview_path):
            logger.info('removed preview file: %s', preview_path)
            os.remove(preview_path)

        info_file = find_info_file(record.location)
        if info_file is not None and os.path.isfile(info_file):
            logger.info('removed info file: %s', info_file)
            os.remove(info_file)

    return generate_ui_token()

def _on_remove_both_button(record_id):
    _on_remove_files_button_click(record_id)
    _on_remove_record_button_click(record_id)

    return generate_ui_token()

def remove_ui_block():
    with gr.Blocks():
        remove_id_box = gr.Textbox(label='remove_id_box', elem_classes='mo-alert-warning', visible=False)
        remove_back_box = gr.Textbox(label='remove_back_box', elem_classes='mo-alert-warning', visible=False)

        gr.Markdown('## Record removal')
        html_widget = gr.HTML()

        with gr.Row():
            gr.Markdown()
            cancel_button = gr.Button('Cancel')
            remove_record_button = gr.Button('Remove Record', visible=False, elem_id='mo_button_remove')
            remove_files_button = gr.Button('Remove Files', visible=False, elem_id='mo_button_remove')
            remove_both_button = gr.Button('Remove Record and Files', visible=False, elem_id='mo_button_remove')
            gr.Markdown()

        remove_record_button.click(_on_remove_record_button_click,
                                   inputs=remove_id_box,
                                   outputs=remove_back_box)

        remove_files_button.click(_on_remove_files_button_click,
                                  inputs=remove_id_box,
                                  outputs=remove_back_box)

        remove_both_button.click(_on_remove_both_button,
                                 inputs=remove_id_box,
                                 outputs=remove_back_box)

        cancel_button.click(fn=None, _js='navigateBack')

        remove_id_box.change(_on_id_change, inputs=remove_id_box,
                             outputs=[html_widget, cancel_button, remove_record_button, remove_files_button,
                                      remove_both_button])

        remove_back_box.change(fn=None, _js='navigateHome')
    return remove_id_box
