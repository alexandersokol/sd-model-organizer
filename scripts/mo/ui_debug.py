import json
import os

import gradio as gr

from scripts.mo.environment import env
from scripts.mo.models import ModelType
from scripts.mo.utils import get_model_files_in_dir, find_preview_file, link_preview


def _ui_state_report():
    with gr.Column():
        gr.Button('Generate state report')


def _on_local_files_scan_click():
    result = []

    def search_in_dir(model_type) -> list:
        dir_path = env.get_model_path(model_type)
        local = []
        files = get_model_files_in_dir(dir_path)
        for file in files:
            preview_file = find_preview_file(file)
            rec = {
                'filename': os.path.basename(file),
                'model_type': model_type.value,
                'path': file,
            }

            if preview_file is not None and preview_file:
                prev = {
                    'preview_filename': os.path.basename(preview_file),
                    'preview_path': preview_file,
                    'preview_link': link_preview(preview_file)
                }
                rec.update(prev)

            local.append(rec)
        return local

    result.extend(search_in_dir(ModelType.CHECKPOINT))
    result.extend(search_in_dir(ModelType.VAE))
    result.extend(search_in_dir(ModelType.LORA))
    result.extend(search_in_dir(ModelType.HYPER_NETWORK))
    result.extend(search_in_dir(ModelType.EMBEDDING))
    result.extend(search_in_dir(ModelType.LYCORIS))

    return gr.JSON.update(value=json.dumps(result))


def _ui_local_files():
    with gr.Column():
        scan_button = gr.Button('Scan Local Model files')

        local_files_json = gr.JSON(label='Local files')

        scan_button.click(fn=_on_local_files_scan_click,
                          outputs=local_files_json)


def debug_ui_block():
    with gr.Column():
        with gr.Row():
            gr.Markdown('## Debug')
            gr.Markdown('')
            gr.Markdown('')
            gr.Markdown('')
            back_button = gr.Button('Back')

        with gr.Tab('State report'):
            _ui_state_report()

        with gr.Tab('Local files'):
            _ui_local_files()

    back_button.click(fn=None, _js='navigateBack')
