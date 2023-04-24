import threading

import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env, LAYOUT_CARDS

_html_content_widget = gr.HTML()


def prepare_data() -> str:
    data = env.storage.get_all_records()

    if env.mo_layout() == LAYOUT_CARDS:
        html = styled.records_cards(data)
    else:
        html = styled.records_table(data)

    lock = threading.Lock()
    with lock:
        _html_content_widget.value = html

    return html


def home_ui_block():
    with gr.Blocks():
        global _html_content_widget
        refresh_box = gr.Textbox(label='refresh_box', elem_classes='mo-alert-warning', visible=False)

        add_button = gr.Button('Add')
        # _html_content_widget = gr.HTML(prepare_data())
        _html_content_widget.value = prepare_data()
        _html_content_widget.render()
        # content_widget = gr.HTML(prepare_data())

        add_button.click(fn=None, _js='navigateAdd')
        refresh_box.change(prepare_data, outputs=[_html_content_widget])

    return refresh_box
