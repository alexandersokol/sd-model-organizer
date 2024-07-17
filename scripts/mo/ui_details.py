import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env


def on_id_changed(record_id):
    if record_id is not None and record_id:
        record = env.storage.get_record_by_id(record_id)
        if record is None:
            return [
                gr.HTML.update(value=f'Record with id {record_id} was not found.'),
                gr.HTML.update(visible=False),
                gr.Textbox.update(value=''),
                gr.Button.update(visible=False),
                gr.Button.update(visible=False)
            ]
        else:
            return [
                gr.HTML.update(value=styled.record_details(record)),
                gr.HTML.update(visible=bool(record.description)),
                gr.Textbox.update(value=record.description),
                gr.Button.update(visible=True),
                gr.Button.update(visible=record.is_download_possible())
            ]

    return [
        gr.HTML.update(value=f'No record id passed.'),
        gr.HTML.update(visible=False),
        gr.Textbox.update(value=''),
        gr.Button.update(visible=False),
        gr.Button.update(visible=False)
    ]


def details_ui_block():
    with gr.Blocks():
        details_id_box = gr.Textbox(label='details_id_box', elem_classes='mo-alert-warning', visible=False)
        with gr.Row():
            back_button = gr.Button("⬅️ Back")
            remove_button = gr.Button("🗑️ Remove")
            edit_button = gr.Button('✏️ Edit')
            download_button = gr.Button("🌐 Download")

        content_widget = gr.HTML()
        description_html = '<div><p style="margin-left: 0.2rem;">Description:</p>' \
                           '<textarea id="mo-description-preview"></textarea></div>'
        description_html_widget = gr.HTML(label='Description:', value=description_html)
        description_input_widget = gr.Textbox(label='description_input_widget',
                                              elem_classes='mo-alert-warning',
                                              interactive=False,
                                              visible=False)

        details_id_box.change(on_id_changed, inputs=details_id_box,
                              outputs=[content_widget, description_html_widget, description_input_widget, edit_button,
                                       download_button])

        description_input_widget.change(fn=None, inputs=description_input_widget,
                                        _js='handleDescriptionPreviewContentChange')

        back_button.click(fn=None, _js='navigateBack')
        download_button.click(fn=None, inputs=details_id_box, _js='navigateDownloadRecord')
        remove_button.click(fn=None, inputs=details_id_box, _js='navigateRemove')
        edit_button.click(fn=None, inputs=details_id_box, _js='navigateEdit')

    return details_id_box
