import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env


def load_records():
    return env.storage.fetch_data()


def on_refresh_click() -> str:
    data = load_records()
    return styled.records_table(data)


def records_list_ui_block():
    with gr.Blocks() as records_list_block:
        refresh_widget = gr.Button("Refresh")
        data = load_records()
        content_widget = gr.HTML(styled.records_table(data))

        refresh_widget.click(on_refresh_click, outputs=[content_widget])

    return records_list_block
