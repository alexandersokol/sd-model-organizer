import os
import re

import gradio as gr

import scripts.mo.ui_navigation as nav
import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env
from scripts.mo.ui_details import details_ui_block
from scripts.mo.ui_download import download_ui_block
from scripts.mo.ui_edit import edit_ui_block
from scripts.mo.ui_home import home_ui_block
from scripts.mo.ui_remove import remove_ui_block


def _load_mo_css() -> str:
    # TODO add and check dark theme colors
    colors_css_path = os.path.join(env.mo_script_dir, 'colors-light.css')
    with open(colors_css_path, 'r') as colors_file:
        colors_css = colors_file.read()

    styles_css_path = os.path.join(env.mo_script_dir, 'styles.css')
    with open(styles_css_path, 'r') as styles_file:
        styles_css = styles_file.read()

    card_width = env.mo_card_width()
    card_height = env.mo_card_height()
    if card_width:
        styles_css = re.sub(r'--mo-card-width:\s*\d+px;', f'--mo-card-width: {card_width}px;', styles_css)
    if card_height:
        styles_css = re.sub(r'--mo-card-height:\s*\d+px;', f'--mo-card-height: {card_height}px;', styles_css)

    return f"""
        <style>
            {colors_css}
            {styles_css}
        </style>
    """


def _content_list_state() -> str:
    return nav.navigate_home()


def _edit_state() -> str:
    return nav.navigate_edit(9)


def _add_state() -> str:
    return nav.navigate_add()


def on_json_box_change(json_state):
    state = nav.get_nav_state(json_state)
    return [
        gr.Column.update(visible=state['is_home_visible']),
        gr.Column.update(visible=state['is_details_visible']),
        gr.Column.update(visible=state['is_edit_visible']),
        gr.Column.update(visible=state['is_remove_visible']),
        gr.Column.update(visible=state['is_download_visible']),
        gr.Textbox.update(value=state['details_record_id']),
        gr.Textbox.update(value=state['edit_record_id']),
        gr.Textbox.update(value=state['remove_record_id']),
        gr.Textbox.update(value=state['download_info'])
    ]


def on_home_click():
    return _content_list_state()


def on_add_click():
    return _add_state()


def on_edit_click(previous_state):
    return nav.navigate_edit(20)


def on_remove_click():
    return nav.navigate_remove(19)


def on_download_click():
    return nav.navigate_download_single(20)


def on_download_group_click():
    return nav.navigate_download_group('First')


def main_ui_block():
    with gr.Blocks() as main_block:
        gr.HTML(_load_mo_css())
        if env.is_storage_has_errors():
            gr.HTML(styled.alert_danger(env.storage_error))
            return main_block
        elif not env.is_storage_initialized():
            gr.HTML(styled.alert_danger('Storage not initialized'))
            return main_block

        _json_nav_box = gr.Textbox(label='mo_json_nav_box', elem_id='mo_json_nav_box')

        with gr.Row():
            home_button = gr.Button('Content List')
            add_button = gr.Button('Add')
            edit_button = gr.Button('Edit (20)')
            remove_button = gr.Button('Remove (19)')
            download_button = gr.Button('Download (20)')
            download_group_button = gr.Button('Download ("First")')

        with gr.Column(visible=True) as home_block:
            home_ui_block()

        with gr.Column(visible=False) as record_details_block:
            details_id_box = details_ui_block()

        with gr.Column(visible=False) as edit_record_block:
            edit_id_box = edit_ui_block()

        with gr.Column(visible=False) as remove_record_block:
            remove_id_box = remove_ui_block()

        with gr.Column(visible=False) as download_block:
            download_id_box = download_ui_block()

        _json_nav_box.change(on_json_box_change,
                             inputs=_json_nav_box,
                             outputs=[home_block,
                                      record_details_block,
                                      edit_record_block,
                                      remove_record_block,
                                      download_block,

                                      details_id_box,
                                      edit_id_box,
                                      remove_id_box,
                                      download_id_box])

        home_button.click(on_home_click, outputs=_json_nav_box)
        add_button.click(on_add_click, outputs=_json_nav_box)
        edit_button.click(on_edit_click, inputs=_json_nav_box, outputs=_json_nav_box)
        remove_button.click(on_remove_click, outputs=_json_nav_box)
        download_button.click(on_download_click, outputs=_json_nav_box)
        download_group_button.click(on_download_group_click, outputs=_json_nav_box)

    return main_block
