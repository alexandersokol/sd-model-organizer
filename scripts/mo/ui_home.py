import json

import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env, LAYOUT_CARDS, logger
from scripts.mo.models import ModelType


def _prepare_data(state_json: str):
    state = json.loads(state_json)

    data = env.storage.query_records(
        name_query=state['query'],
        groups=state['groups'],
        model_types=state['model_types'],
        show_downloaded=state['show_downloaded'],
        show_not_downloaded=state['show_not_downloaded']
    )

    if env.mo_layout() == LAYOUT_CARDS:
        html = styled.records_cards(data)
    else:
        html = styled.records_table(data)

    record_ids = list(map(lambda r: r.id_, data))
    return [
        html,
        json.dumps(json.dumps(record_ids)),
        gr.Button.update(visible=len(record_ids) > 0)
    ]


def _get_available_groups():
    return env.storage.get_available_groups()


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
    initial_state = {
        'query': '',
        'model_types': [],
        'groups': [],
        'show_downloaded': True,
        'show_not_downloaded': True
    }
    initial_state_json = json.dumps(initial_state)

    with gr.Blocks():
        refresh_box = gr.Textbox(label='refresh_box',
                                 elem_classes='mo-alert-warning',
                                 visible=False,
                                 interactive=False)

        state_box = gr.Textbox(value=initial_state_json,
                               label='state_box',
                               elem_classes='mo-alert-warning',
                               visible=False,
                               interactive=False)

        with gr.Row():
            gr.Markdown('## Records list')
            gr.Markdown('')
            reload_button = gr.Button('Reload')
            download_all_button = gr.Button('Download All')
            add_button = gr.Button('Add')

        with gr.Accordion(label='Display options', open=False):
            with gr.Group():
                sort_box = gr.Dropdown(['Time Added ASC', 'Time Added DECS', 'Name ASC', 'Name DECS'],
                                       value='Time Added ASC',
                                       label='Sort By',
                                       multiselect=False,
                                       interactive=True)

                downloaded_first_checkbox = gr.Checkbox(value=False, label='Downloaded first')

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
        initial_html, initial_record_ids, _ = _prepare_data(initial_state_json)
        html_content_widget = gr.HTML(initial_html)
        record_ids_box = gr.Textbox(value=initial_record_ids,
                                    label='record_ids_box',
                                    elem_classes='mo-alert-warning',
                                    visible=False,
                                    interactive=False)
        download_all_button.visible = len(initial_record_ids) > 0

        reload_button.click(_prepare_data, inputs=state_box,
                            outputs=[html_content_widget, record_ids_box, download_all_button])
        refresh_box.change(_prepare_data, inputs=state_box,
                           outputs=[html_content_widget, record_ids_box, download_all_button])
        state_box.change(_prepare_data, inputs=state_box,
                         outputs=[html_content_widget, record_ids_box, download_all_button])

        download_all_button.click(fn=None, inputs=record_ids_box, _js='navigateDownloadRecordList')
        add_button.click(fn=None, _js='navigateAdd')

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
