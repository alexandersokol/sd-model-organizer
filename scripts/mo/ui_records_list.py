import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env, LAYOUT_CARDS


def prepare_data() -> str:
    data = env.storage.fetch_data()

    if env.mo_layout() == LAYOUT_CARDS:
        return styled.records_cards(data)
    else:
        return styled.records_table(data)


def records_list_ui_block():
    with gr.Blocks() as records_list_block:
        refresh_widget = gr.Button("Refresh")
        content_widget = gr.HTML(prepare_data())

        refresh_widget.click(prepare_data, outputs=[content_widget])

    return records_list_block
