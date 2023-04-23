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
        refresh_box = gr.Textbox(label='refresh_box', elem_classes='mo-alert-warning', visible=False)

        add_button = gr.Button('Add')
        content_widget = gr.HTML(prepare_data())

        add_button.click(fn=None, _js='navigateAdd')
        refresh_box.change(prepare_data, outputs=[content_widget])

    return refresh_box
