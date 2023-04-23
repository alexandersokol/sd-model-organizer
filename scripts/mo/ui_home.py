import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env, LAYOUT_CARDS


def prepare_data() -> str:
    data = env.storage.get_all_records()

    if env.mo_layout() == LAYOUT_CARDS:
        return styled.records_cards(data)
    else:
        return styled.records_table(data)


def home_ui_block():
    with gr.Blocks():
        with gr.Row():
            refresh_button = gr.Button('Refresh')
            add_button = gr.Button('Add')

        content_widget = gr.HTML(prepare_data())

        refresh_button.click(prepare_data, outputs=[content_widget])
        add_button.click(fn=None, _js='navigateAdd')
