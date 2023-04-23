import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env


def on_id_changed(record_id) -> str:
    if record_id is not None and record_id:
        data = env.storage.get_record_by_id(record_id)
        return styled.record_details(data)
    else:
        return 'No record id.'


def details_ui_block():
    with gr.Blocks():
        details_id_box = gr.Textbox()

        with gr.Row():
            refresh_button = gr.Button("Refresh")
            download_button = gr.Button("Download")     # TODO hide if file exists?
            remove_button = gr.Button("Remove")
            edit_button = gr.Button('Edit')

        content_widget = gr.HTML()

        refresh_button.click(on_id_changed, inputs=details_id_box, outputs=content_widget)
        details_id_box.change(on_id_changed, inputs=details_id_box, outputs=content_widget)
        download_button.click(fn=None, inputs=details_id_box, _js='navigateDownloadRecord')
        remove_button.click(fn=None, inputs=details_id_box, _js='navigateRemove')
        edit_button.click(fn=None, inputs=details_id_box, _js='navigateEdit')

    return details_id_box
