import os

import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env, logger, find_preview_file
from scripts.mo.ui_navigation import generate_ui_token


def _on_id_change(record_id):
    logger.info(f'_on_id_change record_id: {record_id}', )

    if not record_id:
        return [
            gr.HTML.update(value='Record is missing.'),
            gr.Button.update(visible=True),
            gr.Button.update(visible=False),
            gr.Checkbox.update(visible=False),
            gr.Checkbox.update(visible=False)
        ]

    record = env.storage.get_record_by_id(record_id)
    if record is None:
        return [
            gr.HTML.update(value='Record was not found in database.'),
            gr.Button.update(visible=True),
            gr.Button.update(visible=False),
            gr.Checkbox.update(visible=False),
            gr.Checkbox.update(visible=False)
        ]

    return [
        gr.HTML.update(value=styled.alert_danger(f'Are you sure you what to remove "{record.name}"?')),
        gr.Button.update(visible=True),
        gr.Button.update(visible=True),
        gr.Checkbox.update(visible=bool(record.location), value=True),
        gr.Checkbox.update(visible=bool(record.location), value=True)
    ]


def _on_remove_click(record_id, remove_record, remove_files):
    logger.info(f'_on_remove_click record_id: {record_id} remove_record: {remove_record} remove_files: {remove_files}')
    record = env.storage.get_record_by_id(record_id)

    if remove_record:
        env.storage.remove_record(record_id)

    if record.location and remove_files:
        if record.location and os.path.exists(record.location):
            os.remove(record.location)

        preview_path = find_preview_file(record)
        if preview_path and os.path.exists(record.location):
            os.remove(preview_path)

    return generate_ui_token()


def remove_ui_block():
    with gr.Blocks():
        remove_id_box = gr.Textbox(label='remove_id_box', elem_classes='mo-alert-warning', visible=False)
        remove_back_box = gr.Textbox(label='remove_back_box', elem_classes='mo-alert-warning', visible=False)

        gr.Markdown('## Record removal')
        html_widget = gr.HTML()

        with gr.Column():
            gr.Markdown()
            remove_record_checkbox = gr.Checkbox(value=True, label='Remove record', interactive=True)
            remove_files_checkbox = gr.Checkbox(value=True, label='Remove files', interactive=True)
            gr.Markdown()

        with gr.Row():
            gr.Markdown()
            cancel_button = gr.Button('Cancel', visible=False)
            remove_button = gr.Button('Remove', visible=False, elem_id='mo_button_remove')
            gr.Markdown()

        cancel_button.click(fn=None, _js='navigateBack')
        remove_button.click(_on_remove_click, inputs=[remove_id_box, remove_record_checkbox, remove_files_checkbox],
                            outputs=remove_back_box)

        remove_id_box.change(_on_id_change, inputs=remove_id_box,
                             outputs=[html_widget, cancel_button, remove_button, remove_record_checkbox,
                                      remove_files_checkbox])

        remove_back_box.change(fn=None, _js='navigateHome')
    return remove_id_box
