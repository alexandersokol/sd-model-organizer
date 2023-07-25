import json
import os

import gradio as gr

from scripts.mo.environment import env
from scripts.mo.models import ModelType
from scripts.mo.utils import get_model_files_in_dir, find_preview_file, link_preview, read_hash_cache, \
    calculate_file_temp_hash, write_hash_cache, calculate_sha256


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


def _on_read_hash_click():
    cache = read_hash_cache()
    return [
        gr.JSON.update(value=json.dumps(cache)),
        gr.Button.update(visible=False)
    ]


def _on_calculate_hash_click():
    result = []

    def calc_in_dir(model_type) -> list:
        dir_path = env.get_model_path(model_type)
        local = []
        files = get_model_files_in_dir(dir_path)
        for file in files:
            rec = {
                'path': file,
                'temp_hash': calculate_file_temp_hash(file),
                'sha256': calculate_sha256(file)
            }
            local.append(rec)
        return local

    result.extend(calc_in_dir(ModelType.CHECKPOINT))
    result.extend(calc_in_dir(ModelType.VAE))
    result.extend(calc_in_dir(ModelType.LORA))
    result.extend(calc_in_dir(ModelType.HYPER_NETWORK))
    result.extend(calc_in_dir(ModelType.EMBEDDING))
    result.extend(calc_in_dir(ModelType.LYCORIS))

    return [
        gr.JSON.update(value=json.dumps(result)),
        gr.Button.update(visible=True)
    ]


def _on_compare_hash_click():
    result = []

    cache = read_hash_cache()

    def find_in_cache(file_path, temp_hash):
        for entry in cache:
            if entry.get('path') == file_path and entry.get('temp_hash') == temp_hash and \
                    entry.get('sha256') is not None:
                return entry['sha256']

    def search_in_dir(model_type) -> list:
        dir_path = env.get_model_path(model_type)
        local = []
        files = get_model_files_in_dir(dir_path)
        for file in files:
            temp_hash = calculate_file_temp_hash(file)

            rec = {
                'path': file,
                'temp_hash': temp_hash,
                'sha256': find_in_cache(file, temp_hash)
            }

            local.append(rec)
        return local

    result.extend(search_in_dir(ModelType.CHECKPOINT))
    result.extend(search_in_dir(ModelType.VAE))
    result.extend(search_in_dir(ModelType.LORA))
    result.extend(search_in_dir(ModelType.HYPER_NETWORK))
    result.extend(search_in_dir(ModelType.EMBEDDING))
    result.extend(search_in_dir(ModelType.LYCORIS))

    return [
        gr.JSON.update(value=json.dumps(result)),
        gr.Button.update(visible=False)
    ]


def _on_hash_cache_save_click(json_data):
    write_hash_cache(json_data)


def _ui_hash_cache():
    with gr.Column():
        read_button = gr.Button('Read hash cache')
        compare_hash_button = gr.Button('Compare hash with cache')
        calculate_button = gr.Button('Calculate hashes')
        save_hash_button = gr.Button('Save hash', visible=False)

        hash_cache_json = gr.JSON(label='Local files')

    read_button.click(fn=_on_read_hash_click, outputs=[hash_cache_json, save_hash_button])
    calculate_button.click(fn=_on_calculate_hash_click, outputs=[hash_cache_json, save_hash_button])
    compare_hash_button.click(fn=_on_compare_hash_click, outputs=[hash_cache_json, save_hash_button])

    save_hash_button.click(fn=_on_hash_cache_save_click, inputs=hash_cache_json)


def _on_remove_duplicates_click():
    records = env.storage.get_all_records()
    counter_set = set()
    duplicates_list = []

    for record in records:
        key = f'{record.name}-{record.url}'
        if key in counter_set:
            duplicates_list.append(record)
        else:
            counter_set.add(key)

    for record in duplicates_list:
        env.storage.remove_record(record.id_)

    return f'{len(duplicates_list)} duplicates has been removed.'


def _on_remove_all_records_click():
    records = env.storage.get_all_records()
    for record in records:
        env.storage.remove_record(record.id_)
        
    return "All records has been removed."


def _ui_debug_utils():
    with gr.Row():
        with gr.Column():
            remove_duplicates_button = gr.Button("Remove Records duplicate")
            remove_all_records = gr.Button("Remove all Records")
        with gr.Column():
            debug_html_output = gr.HTML()

    remove_duplicates_button.click(fn=_on_remove_duplicates_click, outputs=[debug_html_output])
    remove_all_records.click(fn=_on_remove_all_records_click, outputs=[debug_html_output])


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

        with gr.Tab('Hash cache'):
            _ui_hash_cache()

        with gr.Tab('Utils'):
            _ui_debug_utils()

    back_button.click(fn=None, _js='navigateBack')
