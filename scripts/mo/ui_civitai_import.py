import json
import re
import time
from urllib.parse import urlparse, parse_qs

import gradio as gr
import requests

from scripts.mo.data.mapping_utils import create_version_dict
from scripts.mo.data.storage import map_record_to_dict
from scripts.mo.environment import env
from scripts.mo.models import ModelType, Record
from scripts.mo.ui_styled_html import alert_danger, alert_warning
from scripts.mo.utils import is_blank

all_available_tags = []

def _get_model_images(model_version_dict):
    result = []

    if model_version_dict.get('images') is not None:
        images = model_version_dict['images']
        for image in images:
            if image.get('url') is not None and image['url']:
                url = image['url']
                result.append((url, url))

    return result


def _list_contains_string_ignore_case(string_list, substring):
    for string in string_list:
        if substring.lower() in string.lower():
            return True
    return False


def create_model_dict(json_data):
    if json_data['type'] == 'Checkpoint':
        model_type = ModelType.CHECKPOINT
    elif json_data['type'] == 'TextualInversion':
        model_type = ModelType.EMBEDDING
    elif json_data['type'] == 'Hypernetwork':
        model_type = ModelType.EMBEDDING
    elif json_data['type'] == 'LORA':
        model_type = ModelType.LORA
    elif json_data['type'] == 'LoCon':
        model_type = ModelType.LYCORIS
    else:
        model_type = ModelType.OTHER

    model_tags = []

    if json_data.get('tags') is not None:
        tags = json_data['tags']
        for tag in tags:
            model_tags.append(tag)

    if json_data['nsfw'] and not _list_contains_string_ignore_case(model_tags, 'nsfw'):
        model_tags.append('NSFW')

    result = {
        'id': json_data['id'],
        'name': json_data['name'],
        'mode_type': model_type,
        'origin_type': json_data['type'],
        'nsfw': json_data['nsfw'],
        'tags': ', '.join(model_tags) if len(model_tags) > 0 else '',
        'description': json_data['description'] if json_data.get('description') is not None else ''
    }

    if json_data.get('modelVersions') is not None:
        model_versions_dict = json_data['modelVersions']
        versions = []
        for version_data in model_versions_dict:
            version = create_version_dict(version_data)
            versions.append(version)
        result['versions'] = versions
    return result


def _on_fetch_url_clicked(url):
    pattern = r'^https:\/\/civitai\.com\/models\/\d+'
    if not re.match(pattern, url) and not url.isdigit():
        return [
            None,
            gr.HTML.update(value=alert_danger('Invalid Url. The link should be a link to the model page or id.')),
            gr.Column.update(visible=False),
            *_create_ui_update()
        ]

    selected_model_version_id = None
    if url.isdigit():
        model_id = url
    else:
        parsed_url = urlparse(url)
        model_id = parsed_url.path.split('/')[2]

        query_params = parse_qs(parsed_url.query)
        # noinspection PyTypeChecker
        version_id = query_params.get('modelVersionId', [None])[0]
        if version_id is not None and version_id.isdigit():
            selected_model_version_id = int(version_id)

    if not model_id.isdigit():
        return [
            None,
            gr.HTML.update(value=alert_danger(
                'Failed to parse model id. Check your input is valid civitai.com model url '
                'or model id.')),
            gr.Column.update(visible=False),
            *_create_ui_update()
        ]

    url = f"https://civitai.com/api/v1/models/{model_id}"
    headers = {"Content-Type": "application/json"}

    response = requests.get(url, headers=headers)

    try:
        if response.status_code == 200:
            data = response.json()
            data_dict = create_model_dict(data)

            return [
                data_dict,
                gr.HTML.update(value='', visible=False),
                gr.Column.update(visible=True),
                *_create_ui_update(data_dict=data_dict, selected_version_id=selected_model_version_id)
            ]
        else:
            return [
                None,
                gr.HTML.update(value=alert_danger(f'Request failed with status code: {response.status_code}')),
                gr.Column.update(visible=False),
                *_create_ui_update()
            ]
    except Exception as e:
        return [
            None,
            gr.HTML.update(value=alert_danger(f'Request failed with error: {e}')),
            gr.Column.update(visible=False),
            *_create_ui_update()
        ]


def _create_ui_update(data_dict=None, selected_version=None, selected_version_id=None, selected_file=None) -> list:
    if data_dict is None:
        return [
            gr.Textbox.update(value=''),
            gr.Dropdown.update(value=''),
            gr.Dropdown.update(value='', choices=[]),
            gr.Dropdown.update(value='', choices=[]),
            gr.Textbox.update(value=''),
            gr.Gallery.update(value=None),
            gr.Textbox.update(value=''),
            gr.Dropdown.update(value='', choices=[]),
            gr.Checkbox.update(value=False, visible=False),
            gr.HTML.update(value='', visible=False),
            gr.Accordion.update(visible=False),
            gr.Button.update(visible=False),
            gr.Button.update(visible=False)
        ]

    version = None
    if selected_version is not None:
        versions = data_dict['versions']
        for ver in versions:
            if ver['name'] == selected_version:
                version = ver
                break
    elif selected_version_id is not None:
        versions = data_dict['versions']
        for ver in versions:
            if ver['id'] == selected_version_id:
                version = ver
                break

    if version is None:
        version = data_dict['versions'][0]

    file = None
    if selected_file is None:
        file = next(item for item in version['files'] if item['is_primary'])
    else:
        for fl in version['files']:
            if fl['display_name'] == selected_file:
                file = fl
                break
        if file is None:
            file = next(item for item in version['files'] if item['is_primary'])
    if file is None:
        file = version['files'][0]

    name = f"{data_dict['name']} ({version['name']})"

    model_type = data_dict['mode_type'].value
    tags = data_dict['tags']
    tags = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []

    if version['base_model']:
        if version['base_model'] == 'Illustrious':
            base_model_name = 'Illustrious XL'
        elif version['base_model'] == 'Pony':
            base_model_name = 'Pony XL'
        else:
            base_model_name = version['base_model']

        name = f"{name} [{base_model_name}]"
        tags.append(base_model_name)

    available_groups = env.storage.get_available_groups()
    all_tags = list(set(available_groups + tags))
    all_tags.sort()

    global all_available_tags

    all_available_tags = list(set(all_tags))

    model_version = version['name']
    model_versions = list(map(lambda x: x['name'], data_dict['versions']))

    image_url = version['images'][0][0] if len(version['images']) else ''

    file_version = file['display_name']
    file_versions = list(map(lambda x: x['display_name'], version['files']))

    prompts = version['trained_words']

    description = data_dict['description']

    return [
        gr.Textbox.update(value=name),
        gr.Dropdown.update(value=model_type),
        gr.Dropdown.update(value=tags, choices=all_tags),
        gr.Dropdown.update(value=model_version, choices=model_versions),
        gr.Textbox.update(value=image_url),
        gr.Gallery.update(version['images']),
        gr.Dropdown.update(value=file_version, choices=file_versions),
        gr.Textbox.update(value=prompts),
        gr.Checkbox.update(value=bool(description), visible=bool(description)),
        gr.HTML.update(value=data_dict['description'], visible=bool(description)),
        gr.Accordion.update(visible=bool(description)),
        *_on_model_type_changed(model_type)
    ]


def _on_model_version_selected(data_dict, selected_version):
    return _create_ui_update(data_dict=data_dict, selected_version=selected_version)


def _on_model_type_changed(model_type_value):
    is_edit_visible = True
    is_import_visible = True
    if not bool(model_type_value) or model_type_value == ModelType.OTHER.value:
        is_import_visible = False

    return [
        gr.Button.update(visible=is_edit_visible),
        gr.Button.update(visible=is_import_visible)
    ]


def _prepare_import_data(state, import_url, name, use_model_name_as_download_filename, model_type_value, tags,
                         model_version_value, preview_url, file_value,
                         prompts, include_description):
    errors = []
    if is_blank(name):
        errors.append('Name field is empty.')

    if not is_blank(model_type_value):
        model_type = ModelType.by_value(model_type_value)
    else:
        errors.append('Model type not selected.')
        model_type = None

    if import_url.isdigit():
        model_url = ''
    else:
        model_url = import_url

    version = None
    if model_version_value is None or not bool(model_version_value):
        errors.append('Model version not selected.')
    else:
        versions = state['versions']
        for ver in versions:
            if ver['name'] == model_version_value:
                version = ver
                break

    file = None
    if file_value is None or not bool(file_value):
        errors.append('File version not selected.')
    else:
        if version is not None:
            for fl in version['files']:
                if fl['display_name'] == file_value:
                    file = fl
                    break

    if file is None:
        errors.append('File version not defined.')

    if errors:
        return errors

    download_url = file['download_url']
    description = state['description'] if include_description else ''
    groups = tags
    sha256 = file['sha256']

    if use_model_name_as_download_filename:
        download_filename = f'{name}.safetensors'
    else:
        download_filename = ''

    return Record(
        id_=None,
        name=name,
        model_type=model_type,
        download_url=download_url,
        download_filename=download_filename,
        url=model_url.strip(),
        preview_url=preview_url.strip(),
        description=description,
        positive_prompts=prompts.strip(),
        groups=groups,
        sha256_hash=sha256,
        created_at=time.time()
    )


def _on_import_clicked(state, import_url, name, use_model_name_as_download_filename, model_type_value, tags,
                       model_version_value, preview_url, file_value,
                       prompts, include_description):
    result = _prepare_import_data(
        state=state,
        import_url=import_url,
        name=name,
        use_model_name_as_download_filename=use_model_name_as_download_filename,
        model_type_value=model_type_value,
        tags=tags,
        model_version_value=model_version_value,
        preview_url=preview_url,
        file_value=file_value,
        prompts=prompts,
        include_description=include_description
    )

    if isinstance(result, list):
        return [
            gr.HTML.update(value=alert_danger(result), visible=True),
            gr.Column.update()
        ]
    elif isinstance(result, Record):
        env.storage.add_record(result)
        return [
            gr.HTML.update(value='', visible=False),
            gr.Column.update(visible=False)
        ]
    else:
        return [
            gr.HTML.update(value=alert_danger('Unpredicted behaviour, try to reload page and fill data again'),
                           visible=True),
            gr.Column.update()
        ]


def _on_edit_clicked(state, import_url, name, use_model_name_as_download_filename, model_type_value, tags,
                     model_version_value, preview_url, file_value,
                     prompts, include_description):
    result = _prepare_import_data(
        state=state,
        import_url=import_url,
        name=name,
        use_model_name_as_download_filename=use_model_name_as_download_filename,
        model_type_value=model_type_value,
        tags=tags,
        model_version_value=model_version_value,
        preview_url=preview_url,
        file_value=file_value,
        prompts=prompts,
        include_description=include_description
    )

    if isinstance(result, list):
        return [
            gr.HTML.update(value=alert_danger(result), visible=True),
            gr.Column.update(),
            gr.Textbox.update()
        ]
    elif isinstance(result, Record):
        record_dict = map_record_to_dict(result)
        record_json = json.dumps(record_dict)
        return [
            gr.HTML.update(value='', visible=False),
            gr.Column.update(visible=False),
            gr.Textbox.update(value=record_json)
        ]
    else:
        return [
            gr.HTML.update(value=alert_danger('Unpredicted behaviour, try to reload page and fill data again'),
                           visible=True),
            gr.Column.update(),
            gr.Textbox.update()
        ]


def _on_gallery_select(data: gr.SelectData):
    return data.value


def _on_new_tags_to_add(tags_add_textbox, tags_dropdown):
    tags = [tag.strip() for tag in tags_add_textbox.split(',') if tag.strip()] if tags_add_textbox else []
    choices_tags = tags_dropdown + [tag for tag in tags if tag not in tags_dropdown]

    global all_available_tags
    all_tags = all_available_tags + [tag for tag in tags if tag not in all_available_tags]

    return [
        gr.Textbox.update(value=''),
        gr.Dropdown.update(value=choices_tags, choices=all_tags),
    ]


def _on_name_changed(name, import_url, use_name_as_filename):
    records_with_same_name = env.storage.get_records_by_name(name)

    warnings_list = []

    if records_with_same_name:
        record_names = ', '.join(record.name for record in records_with_same_name)
        warnings_list.append(f'Records with the same name: {record_names}')

    records_with_same_url = env.storage.get_records_by_url(import_url)
    if records_with_same_url:
        record_names = ', '.join(record.name for record in records_with_same_url)
        warnings_list.append(f'Records with the same url: {record_names}')

    if use_name_as_filename:
        records_with_same_dest = env.storage.get_records_by_download_destination('', f'{name}.safetensors')
        if records_with_same_dest:
            record_names = ', '.join(record.name for record in records_with_same_dest)
            warnings_list.append(f'Records with the same download filename: {record_names}')

    warning_message = '\n'.join(warnings_list)

    return gr.HTML.update(value=alert_warning(warnings_listgi), visible=bool(warning_message))


def civitai_import_ui_block():
    import_url_textbox = gr.Textbox('',
                                    label='civitai model url or id.',
                                    info='Field accepts urls like: "https://civitai.com/models/0000",'
                                         ' "https://civitai.com/models/0000?modelVersionId=xxxx", or model id "0000",'
                                         'where 0000 is model id from civitai.com')
    with gr.Row():
        gr.Markdown()
        gr.Markdown()
        gr.Markdown()
        fetch_url_button = gr.Button('Fetch URL')

    fetch_result_html = gr.HTML('')
    import_model_state = gr.State(None)

    with gr.Column(visible=False) as content_container:
        name_widget = gr.Textbox(label='Name', interactive=True)
        use_name_as_filename = gr.Checkbox(label='Use name as download filename',
                                           interactive=True,
                                           info='Adds a custom filename to for downloading file name from the model '
                                                'name with .safetensors extension.')

        model_type_dropdown = gr.Dropdown(choices=[model_type.value for model_type in ModelType],
                                          value='',
                                          label='Model type:',
                                          info='Be careful selecting model type, not all models from Civitai has '
                                               'correct model type.',
                                          interactive=True)

        tags_dropdown = gr.Dropdown(label='Tags',
                                    value='',
                                    info='Edit model tags(groups)',
                                    multiselect=True,
                                    interactive=True)

        with gr.Column():
            tags_add_textbox = gr.Textbox(label='Add comma-separated tags new tags here',
                                          interactive=True,
                                          info='Add comma-separated tags new tags here. '
                                               'For example: "tag1,tag2,tag3" and hit the button to add tags.'
                                          )
            with gr.Row():
                gr.Markdown()
                gr.Markdown()
                gr.Markdown()
                gr.Markdown()
                tags_add_button = gr.Button('Add tags')

        model_version_dropdown = gr.Dropdown(label='Model Version',
                                             interactive=True,
                                             info='Select model version.')

        files_dropdown = gr.Dropdown(label='Model Files:',
                                     interactive=True,
                                     info='Model file variants for download.')
        prompts_textbox = gr.Textbox(label='Trained words (Prompts):', interactive=True)

        preview_url_textbox = gr.Textbox(label='Preview image URL',
                                         interactive=True,
                                         info='First image selected by default. You can select another preview url '
                                              'from the \"Image Previews\" gallery below.')

        with gr.Accordion(label='Image previews', open=False):
            preview_gallery = gr.Gallery(elem_id='preview_gallery',
                                         columns=10,
                                         allow_preview=True)
            preview_gallery.select(_on_gallery_select,
                                   None, preview_url_textbox)

        description_checkbox = gr.Checkbox(label='Include description',
                                           interactive=True,
                                           info='Include description below to the record import')
        with gr.Accordion(label='Description (Click to expand):', open=False) as description_accordion:
            description_html = gr.HTML()

        import_warning_html = gr.HTML('', visible=False)
        import_result_html = gr.HTML('', visible=False)

        with gr.Row():
            edit_button = gr.Button("Edit before save")
            import_button = gr.Button("Import")

        prefill_json_box = gr.Textbox(label='prefill_json_box',
                                      elem_classes='mo-alert-warning',
                                      interactive=False,
                                      visible=False)

    name_widget.change(_on_name_changed,
                       inputs=[name_widget, import_url_textbox, use_name_as_filename],
                       outputs=[import_warning_html])

    tags_add_button.click(_on_new_tags_to_add,
                          inputs=[tags_add_textbox, tags_dropdown],
                          outputs=[tags_add_textbox, tags_dropdown])

    fetch_url_button.click(_on_fetch_url_clicked,
                           inputs=import_url_textbox,
                           outputs=[import_model_state,
                                    fetch_result_html,
                                    content_container,
                                    name_widget,
                                    model_type_dropdown,
                                    tags_dropdown,
                                    model_version_dropdown,
                                    preview_url_textbox,
                                    preview_gallery,
                                    files_dropdown,
                                    prompts_textbox,
                                    description_checkbox,
                                    description_html,
                                    description_accordion,
                                    edit_button,
                                    import_button
                                    ])

    model_version_dropdown.select(fn=_on_model_version_selected,
                                  inputs=[import_model_state, model_version_dropdown],
                                  outputs=[
                                      name_widget,
                                      model_type_dropdown,
                                      tags_dropdown,
                                      model_version_dropdown,
                                      preview_url_textbox,
                                      preview_gallery,
                                      files_dropdown,
                                      prompts_textbox,
                                      description_checkbox,
                                      description_html,
                                      description_accordion,
                                      edit_button,
                                      import_button
                                  ])

    model_type_dropdown.select(fn=_on_model_type_changed,
                               inputs=model_type_dropdown,
                               outputs=[edit_button, import_button])

    import_button.click(fn=_on_import_clicked,
                        inputs=[import_model_state,
                                import_url_textbox,
                                name_widget,
                                use_name_as_filename,
                                model_type_dropdown,
                                tags_dropdown,
                                model_version_dropdown,
                                preview_url_textbox,
                                files_dropdown,
                                prompts_textbox,
                                description_checkbox],
                        outputs=[
                            import_result_html,
                            content_container
                        ])

    edit_button.click(fn=_on_edit_clicked,
                      inputs=[import_model_state,
                              import_url_textbox,
                              name_widget,
                              use_name_as_filename,
                              model_type_dropdown,
                              tags_dropdown,
                              model_version_dropdown,
                              preview_url_textbox,
                              files_dropdown,
                              prompts_textbox,
                              description_checkbox],
                      outputs=[
                          import_result_html,
                          content_container,
                          prefill_json_box
                      ])

    prefill_json_box.change(fn=None, inputs=prefill_json_box, _js='navigateEditPrefilled')
