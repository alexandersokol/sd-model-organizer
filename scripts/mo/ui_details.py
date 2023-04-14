import gradio as gr

from scripts.mo.environment import env
from scripts.mo.models import Record
import scripts.mo.ui_styled_html as styled


def on_id_changed(record_id) -> str:
    if record_id is not None and record_id:
        data = env.storage.fetch_data_by_id(record_id)
        return styled.record_details(data)
    else:
        return 'No record id.'


def details_ui_block():
    with gr.Blocks():
        details_id_box = gr.Textbox()

        refresh_widget = gr.Button("Refresh")
        content_widget = gr.HTML()

        refresh_widget.click(on_id_changed, inputs=details_id_box, outputs=content_widget)
        details_id_box.change(on_id_changed, inputs=details_id_box, outputs=content_widget)

    return details_id_box
