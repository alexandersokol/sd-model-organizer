import json
import os.path
from datetime import datetime

import gradio as gr

from scripts.mo.data.record_utils import load_records_and_filter
from scripts.mo.data.storage import map_record_to_dict, map_dict_to_record
from scripts.mo.environment import env
from scripts.mo.ui_civitai_import import civitai_import_ui_block


def _on_import_file_change(import_file):
    if import_file is None or not import_file or not os.path.exists(import_file.name):
        return gr.HTML.update('')

    with open(import_file.name, 'r') as f:
        records_dict_list = json.load(f)

    if len(records_dict_list) == 0:
        return gr.HTML.update('Nothing to import')
    else:
        records_imported = []
        for record_dict in records_dict_list:
            record = map_dict_to_record('', record_dict)
            env.storage.add_record(record)
            records_imported.append(record.name)

        output = f'<b>Imported records: ({len(records_imported)})</b>'
        for name in records_imported:
            output += '<br>'
            output += name
        return gr.HTML.update(value=output)


def _on_export_click(filter_state_json, export_option):
    if export_option == 'Export All':
        records = env.storage.get_all_records()
    else:
        filter_state = json.loads(filter_state_json)
        records = load_records_and_filter(filter_state, False)

    records_dict_list = []

    for record in records:
        records_dict_list.append(map_record_to_dict(record))

    if len(records_dict_list) > 0:
        export_dir = os.path.join(env.script_dir, 'export')
        if not os.path.isdir(export_dir):
            os.mkdir(export_dir)

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(export_dir, filename)
        with open(path, 'w') as f:
            json.dump(records_dict_list, f)

        return gr.File.update(value=path, label='Exported, Click "Download"', visible=True)
    else:
        return gr.File.update(visible=False)


def import_export_ui_block():
    with gr.Blocks():
        with gr.Row():
            gr.Markdown('## Records import/export')
            gr.Markdown('')
            back_button = gr.Button('Back')
        with gr.Tab("Import JSON"):
            import_file_widget = gr.File(label='Import .json file', file_types=['.json'])
            import_result_widget = gr.HTML()
        with gr.Tab("Export JSON"):
            filter_state_box = gr.Textbox(value='',
                                          label='filter_state_box',
                                          elem_classes='mo-alert-warning',
                                          elem_id='mo-home-state-box',
                                          visible=False,
                                          interactive=False)

            export_option_radio = gr.Radio(choices=['Export All', 'Export filtered from home screen'],
                                           interactive=True,
                                           value='Export All')
            export_button = gr.Button(value='Export')
            export_file_widget = gr.File(visible=False)
        with gr.Tab("Import Civitai URL"):
            with gr.Column():
                civitai_import_ui_block()

    back_button.click(fn=None, _js='navigateBack')

    import_file_widget.change(_on_import_file_change, inputs=import_file_widget,
                              outputs=import_result_widget)
    export_button.click(_on_export_click, inputs=[filter_state_box, export_option_radio], outputs=export_file_widget)

    return filter_state_box
