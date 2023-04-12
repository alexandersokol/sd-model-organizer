import gradio as gr

from scripts.mo.environment import env
from scripts.mo.models import Record
import scripts.mo.ui_styled_html as styled


def prepare_data(record_id) -> str:
    data = env.storage.fetch_data_by_id(record_id)
    return styled.record_details(data)


def record_details_ui_block(record_id):
    with gr.Blocks() as records_list_block:
        details_state = gr.State(record_id)
        refresh_widget = gr.Button("Refresh")
        content_widget = gr.HTML(prepare_data(record_id))

        refresh_widget.click(prepare_data, inputs=[details_state], outputs=[content_widget])

    return records_list_block
