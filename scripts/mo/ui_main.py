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
from scripts.mo.ui_import_export import import_export_ui_block
from scripts.mo.ui_remove import remove_ui_block


def _load_mo_css() -> str:
    if env.theme() == 'dark':
        colors_css_path = os.path.join(env.script_dir, 'colors-dark.css')
    else:
        colors_css_path = os.path.join(env.script_dir, 'colors-light.css')

    with open(colors_css_path, 'r') as colors_file:
        colors_css = colors_file.read()

    styles_css_path = os.path.join(env.script_dir, 'styles.css')
    with open(styles_css_path, 'r') as styles_file:
        styles_css = styles_file.read()

    card_width = env.card_width()
    card_height = env.card_height()
    if card_width:
        styles_css = re.sub(r'--mo-card-width:\s*\d+px;', f'--mo-card-width: {card_width}px;', styles_css)
    if card_height:
        styles_css = re.sub(r'--mo-card-height:\s*\d+px;', f'--mo-card-height: {card_height}px;', styles_css)

    return f"""
            {colors_css}
            {styles_css}
    """


def on_json_box_change(json_state, home_refresh_token):
    state = nav.get_nav_state(json_state)

    is_home_visible = state['is_home_visible']
    if is_home_visible:
        home_refresh_token = nav.generate_ui_token()

    return [
        gr.Column.update(visible=is_home_visible),
        gr.Column.update(visible=state['is_details_visible']),
        gr.Column.update(visible=state['is_edit_visible']),
        gr.Column.update(visible=state['is_remove_visible']),
        gr.Column.update(visible=state['is_download_visible']),
        gr.Column.update(visible=state['is_import_export_visible']),

        gr.Textbox.update(value=home_refresh_token),
        gr.Textbox.update(value=state['details_record_id']),
        gr.Textbox.update(value=state['edit_data']),
        gr.Textbox.update(value=state['remove_record_id']),
        gr.Textbox.update(value=state['download_info'])
    ]


def main_ui_block():
    css_styles = _load_mo_css()
    with gr.Blocks(css=css_styles) as main_block:
        gr.HTML(f'<style>{css_styles}</style>')
        if env.is_storage_has_errors():
            gr.HTML(styled.alert_danger(env.storage_error))
            return main_block
        elif not env.is_storage_initialized():
            gr.HTML(styled.alert_danger('Storage not initialized'))
            return main_block

        _json_nav_box = gr.Textbox(value=nav.navigate_home(), label='mo_json_nav_box', elem_id='mo_json_nav_box',
                                   elem_classes='mo-alert-warning', visible=False)

        with gr.Column(visible=True) as home_block:
            home_refresh_box = home_ui_block()

        with gr.Column(visible=False) as record_details_block:
            details_id_box = details_ui_block()

        with gr.Column(visible=False) as edit_record_block:
            edit_id_box = edit_ui_block()

        with gr.Column(visible=False) as remove_record_block:
            remove_id_box = remove_ui_block()

        with gr.Column(visible=False) as download_block:
            download_id_box = download_ui_block()

        with gr.Column(visible=False) as import_export_block:
            import_export_ui_block()

        _json_nav_box.change(on_json_box_change,
                             inputs=[_json_nav_box, home_refresh_box],
                             outputs=[home_block,
                                      record_details_block,
                                      edit_record_block,
                                      remove_record_block,
                                      download_block,
                                      import_export_block,

                                      home_refresh_box,
                                      details_id_box,
                                      edit_id_box,
                                      remove_id_box,
                                      download_id_box])

    return main_block
