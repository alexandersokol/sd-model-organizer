import json
import os.path
import time

import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env, LAYOUT_CARDS
from scripts.mo.models import Record, ModelType, ModelSort
from scripts.mo.utils import get_model_files_in_dir, find_preview_file, link_preview


def _sort_records(records: list[Record], sort_order: ModelSort, sort_downloaded_first: bool) -> list[Record]:
    if sort_downloaded_first:
        if sort_order == ModelSort.TIME_ADDED_ASC:
            sorted_records = sorted(records,
                                    key=lambda r: (not (bool(r.location) and os.path.exists(r.location)), r.created_at))
        elif sort_order == ModelSort.TIME_ADDED_DESC:
            sorted_records = sorted(records,
                                    key=lambda r: (bool(r.location) and os.path.exists(r.location), r.created_at),
                                    reverse=True)
        elif sort_order == ModelSort.NAME_ASC:
            sorted_records = sorted(records,
                                    key=lambda r: (not (bool(r.location) and os.path.exists(r.location)), r.name))
        elif sort_order == ModelSort.NAME_DESC:
            sorted_records = sorted(records, key=lambda r: (bool(r.location) and os.path.exists(r.location), r.name),
                                    reverse=True)
        else:
            raise ValueError(f'An unhandled sort_order value: {sort_order.value}')
    else:
        if sort_order == ModelSort.TIME_ADDED_ASC:
            sorted_records = sorted(records, key=lambda record: record.created_at)
        elif sort_order == ModelSort.TIME_ADDED_DESC:
            sorted_records = sorted(records, key=lambda record: record.created_at, reverse=True)
        elif sort_order == ModelSort.NAME_ASC:
            sorted_records = sorted(records, key=lambda record: record.name)
        elif sort_order == ModelSort.NAME_DESC:
            sorted_records = sorted(records, key=lambda record: record.name, reverse=True)
        else:
            raise ValueError(f'An unhandled sort_order value: {sort_order.value}')
    return sorted_records


def _get_local_model_files() -> list[Record]:
    result = []

    def search_in_dir(model_type) -> list[Record]:
        dir_path = env.get_model_path(model_type)
        local = []
        files = get_model_files_in_dir(dir_path)
        for file in files:
            preview_file = find_preview_file(file)
            rec = Record(
                id_=None,
                name=os.path.basename(file),
                model_type=model_type,
                location=file,
                download_url='',
                created_at=time.time(),
                preview_url=link_preview(preview_file) if preview_file is not None and preview_file else ''
            )
            local.append(rec)
        return local

    result.extend(search_in_dir(ModelType.CHECKPOINT))
    result.extend(search_in_dir(ModelType.VAE))
    result.extend(search_in_dir(ModelType.LORA))
    result.extend(search_in_dir(ModelType.HYPER_NETWORK))
    result.extend(search_in_dir(ModelType.EMBEDDING))
    result.extend(search_in_dir(ModelType.LYCORIS))

    return result


def _prepare_data(state_json: str):
    state = json.loads(state_json)

    records = env.storage.query_records(
        name_query=state['query'],
        groups=state['groups'],
        model_types=state['model_types'],
        show_downloaded=state['show_downloaded'],
        show_not_downloaded=state['show_not_downloaded']
    )

    records.extend(_get_local_model_files())

    records = _sort_records(
        records=records,
        sort_order=ModelSort.by_value(state['sort_order']),
        sort_downloaded_first=state['sort_downloaded_first']
    )

    if env.layout() == LAYOUT_CARDS:
        html = styled.records_cards(records)
    else:
        html = styled.records_table(records)

    record_ids = list(map(lambda r: r.id_, records))
    return [
        html,
        json.dumps(json.dumps(record_ids)),
        gr.Button.update(visible=len(record_ids) > 0),
        gr.Dropdown.update(value=state['groups'], choices=_get_available_groups())
    ]


def _get_available_groups():
    return env.storage.get_available_groups()


def _on_sort_order_changed(sort_order, state_json):
    state = json.loads(state_json)
    state['sort_order'] = sort_order
    settings = env.read_settings()
    settings['sort_order'] = sort_order
    env.save_settings(settings)
    return json.dumps(state)


def _on_downloaded_first_changed(sort_downloaded_first, state_json):
    state = json.loads(state_json)
    state['sort_downloaded_first'] = sort_downloaded_first
    settings = env.read_settings()
    settings['sort_downloaded_first'] = sort_downloaded_first
    env.save_settings(settings)
    return json.dumps(state)


def _on_search_query_changed(query, state_json):
    state = json.loads(state_json)
    state['query'] = query
    return json.dumps(state)


def _on_model_type_box_changed(selected, state_json):
    state = json.loads(state_json)
    state['model_types'] = selected
    return json.dumps(state)


def _on_group_box_changed(selected, state_json):
    state = json.loads(state_json)
    state['groups'] = selected
    return json.dumps(state)


def _on_show_downloaded_changed(show_downloaded, state_json):
    state = json.loads(state_json)
    state['show_downloaded'] = show_downloaded
    return json.dumps(state)


def _on_show_not_downloaded_changed(show_not_downloaded, state_json):
    state = json.loads(state_json)
    state['show_not_downloaded'] = show_not_downloaded
    return json.dumps(state)


def home_ui_block():
    settings = env.read_settings()

    if settings.get('sort_order') is not None:
        sort_order = settings['sort_order']
    else:
        sort_order = ModelSort.TIME_ADDED_ASC.value

    if settings.get('sort_downloaded_first') is not None:
        sort_downloaded_first = True if settings['sort_downloaded_first'].lower() == "true" else False
    else:
        sort_downloaded_first = False

    initial_state = {
        'query': '',
        'model_types': [],
        'groups': [],
        'show_downloaded': True,
        'show_not_downloaded': True,
        'sort_order': sort_order,
        'sort_downloaded_first': sort_downloaded_first
    }
    initial_state_json = json.dumps(initial_state)

    with gr.Blocks():
        refresh_box = gr.Textbox(label='refresh_box',
                                 elem_classes='mo-alert-warning',
                                 visible=False,
                                 interactive=False)

        state_box = gr.Textbox(value='',
                               label='state_box',
                               elem_classes='mo-alert-warning',
                               elem_id='mo-home-state-box',
                               visible=False,
                               interactive=False)

        gr.Textbox(value=initial_state_json,
                   label='initial_state_box',
                   elem_classes='mo-alert-warning',
                   elem_id='mo-initial-state-box',
                   visible=False,
                   interactive=False)

        with gr.Row():
            gr.Markdown('## Records list')
            if not env.is_debug_mode_enabled():
                gr.Markdown('')
            debug_button = gr.Button('Debug', visible=env.is_debug_mode_enabled())
            reload_button = gr.Button('Reload')
            download_all_button = gr.Button('Download All', visible=False)
            import_export_button = gr.Button('Import/Export')
            add_button = gr.Button('Add')

        with gr.Accordion(label='Display options', open=False):
            with gr.Group():
                sort_box = gr.Dropdown([model_sort.value for model_sort in ModelSort],
                                       value=sort_order,
                                       label='Sort By',
                                       multiselect=False,
                                       interactive=True)

                downloaded_first_checkbox = gr.Checkbox(value=sort_downloaded_first, label='Downloaded first')

            with gr.Group():
                search_box = gr.Textbox(label='Search by name',
                                        value=initial_state['query'])
                model_types_dropdown = gr.Dropdown([model_type.value for model_type in ModelType],
                                                   value=initial_state['model_types'],
                                                   label='Model types',
                                                   multiselect=True)
                groups_dropdown = gr.Dropdown(_get_available_groups(),
                                              multiselect=True,
                                              label='Groups',
                                              value=initial_state['groups'])
                show_downloaded_checkbox = gr.Checkbox(label='Show downloaded',
                                                       value=initial_state['show_downloaded'])
                show_not_downloaded_checkbox = gr.Checkbox(label='Show not downloaded',
                                                           value=initial_state['show_not_downloaded'])

        html_content_widget = gr.HTML()
        record_ids_box = gr.Textbox(value='',
                                    label='record_ids_box',
                                    elem_classes='mo-alert-warning',
                                    visible=False,
                                    interactive=False)

        reload_button.click(_prepare_data, inputs=state_box,
                            outputs=[html_content_widget, record_ids_box, download_all_button, groups_dropdown])
        refresh_box.change(_prepare_data, inputs=state_box,
                           outputs=[html_content_widget, record_ids_box, download_all_button, groups_dropdown])
        state_box.change(_prepare_data, inputs=state_box,
                         outputs=[html_content_widget, record_ids_box, download_all_button, groups_dropdown])

        debug_button.click(fn=None, _js='navigateDebug')
        download_all_button.click(fn=None, inputs=record_ids_box, _js='navigateDownloadRecordList')
        import_export_button.click(fn=None, _js='navigateImportExport')
        add_button.click(fn=None, _js='navigateAdd')

        sort_box.change(_on_sort_order_changed,
                        inputs=[sort_box, state_box],
                        outputs=state_box)

        downloaded_first_checkbox.change(_on_downloaded_first_changed,
                                         inputs=[downloaded_first_checkbox, state_box],
                                         outputs=state_box)

        search_box.change(_on_search_query_changed, inputs=[search_box, state_box], outputs=state_box)
        model_types_dropdown.change(_on_model_type_box_changed, inputs=[model_types_dropdown, state_box],
                                    outputs=state_box)
        groups_dropdown.change(_on_group_box_changed, inputs=[groups_dropdown, state_box], outputs=state_box)

        show_downloaded_checkbox.change(_on_show_downloaded_changed,
                                        inputs=[show_downloaded_checkbox, state_box],
                                        outputs=state_box)
        show_not_downloaded_checkbox.change(_on_show_not_downloaded_changed,
                                            inputs=[show_not_downloaded_checkbox, state_box],
                                            outputs=state_box)

    return refresh_box
