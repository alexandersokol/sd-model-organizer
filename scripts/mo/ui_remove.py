import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env, logger
from scripts.mo.ui_navigation import generate_back_token


def _on_id_change(record_id):
    logger.info(f'Remove: on id change: {record_id}', )

    record = env.storage.get_record_by_id(record_id)
    if record is None:
        return [
            gr.HTML.update(value='Record was not found in database.'),
            gr.Button.update(visible=True),
            gr.Button.update(visible=False)
        ]

    return [
        gr.HTML.update(value=styled.alert_danger(f'Are you sure you what to remove "{record.name}"?')),
        gr.Button.update(visible=True),
        gr.Button.update(visible=True)
    ]


def _on_remove_click(record_id, back_token):
    env.storage.remove_record(record_id)
    logger.info(f'record removed {record_id}')
    return generate_back_token()


def remove_ui_block():
    with gr.Blocks():
        remove_id_box = gr.Textbox(label='remove_id_box', elem_classes='mo-alert-warning', visible=False)
        remove_back_box = gr.Textbox(label='remove_back_box', elem_classes='mo-alert-warning', visible=False)

        gr.Markdown('## Record removal')
        html_widget = gr.HTML()

        with gr.Row():
            cancel_button = gr.Button('Cancel', visible=False)
            remove_button = gr.Button('Remove', visible=False, elem_id='mo_button_remove')

        cancel_button.click(fn=None, _js='navigateBack')
        remove_button.click(_on_remove_click, inputs=[remove_id_box, remove_back_box], outputs=remove_back_box)

        remove_id_box.change(_on_id_change, inputs=remove_id_box, outputs=[html_widget, cancel_button, remove_button])

        remove_back_box.change(fn=None, _js='navigateHome')
    return remove_id_box
