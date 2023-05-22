import re
from urllib.parse import urlparse

import gradio as gr
import requests

from scripts.mo.models import ModelType
from scripts.mo.ui_format import format_kilobytes
from scripts.mo.ui_styled_html import alert_danger


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


def _create_model_dict(json_data):
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
        'tags': ', '.join(model_tags) if len(model_tags) > 0 else ''
    }

    if json_data.get('modelVersions') is not None:
        model_versions_dict = json_data['modelVersions']
        versions = []
        for version_data in model_versions_dict:
            version = {
                'id': version_data['id'],
                'name': version_data['name'],
                'updated_at': version_data['updatedAt'],
            }

            trained_words = []
            if version_data.get('trainedWords') is not None:
                words = version_data['trainedWords']
                for word in words:
                    trained_words.append(word)

            version['trained_words'] = ', '.join(trained_words) if len(trained_words) > 0 else ''

            if version_data.get('images') is not None:
                images_data = version_data['images']
                images = []
                for image_data in images_data:
                    url = image_data['url']
                    images.append((url, url))
                version['images'] = images

            if version_data.get('files') is not None:
                files_data = version_data['files']
                files = []

                for file_data in files_data:
                    file_name = file_data['name'] if file_data.get('name') is not None else ''
                    file_type = file_data['type'] if file_data.get('type') is not None else ''
                    fp = file_data['metadata']['fp'] if file_data['metadata'].get('fp') is not None else ''
                    file_size = file_data['metadata']['size'] if file_data['metadata'].get('size') is not None else ''
                    file_format = file_data['metadata']['format'] if file_data['metadata'].get(
                        'format') is not None else ''
                    file_size_formatted = format_kilobytes(file_data['sizeKB']) if file_data.get(
                        'sizeKB') is not None else ''

                    display_name = ''

                    if file_name:
                        display_name += file_name

                    if file_type:
                        display_name += ' | '
                        display_name += file_type

                    if fp:
                        display_name += ' | '
                        display_name += fp

                    if file_size:
                        display_name += ' | '
                        display_name += file_size

                    if file_format:
                        display_name += ' | '
                        display_name += file_format

                    if file_size_formatted:
                        display_name += ' | '
                        display_name += file_size_formatted

                    file = {
                        'id': file_data['id'],
                        'file_name': file_data['name'],
                        'display_name': display_name,
                        'download_url': file_data['downloadUrl'],
                        'is_primary': file_data['primary'] if file_data.get('primary') else False
                    }
                    files.append(file)
                version['files'] = files
            versions.append(version)
        result['versions'] = versions
    return result


def _on_fetch_url_clicked(url):
    pattern = r'^https:\/\/civitai\.com\/models\/\d+\/[a-zA-Z0-9-]+$'
    if not re.match(pattern, url) and not url.isdigit():
        return [
            None,
            gr.HTML.update(value=alert_danger('Invalid Url. The link should be a link to the model page like '
                                              'https://civitai.com/models/00000/model_name '
                                              'OR model id like 00000')),
            gr.Accordion.update(visible=False),
            gr.JSON.update(value='{}'),
            gr.Column.update(visible=False),
            *_create_ui_update()
        ]

    if url.isdigit():
        model_id = url
    else:
        model_id = urlparse(url).path.split('/')[2]

    if not model_id.isdigit():
        return [
            None,
            gr.HTML.update(value=alert_danger(
                'Failed to parse model id. Check your input is valid civitai.com model url '
                'or model id.')),
            gr.Accordion.update(visible=False),
            gr.JSON.update(value='{}'),
            gr.Column.update(visible=False),
            *_create_ui_update()
        ]

    url = f"https://civitai.com/api/v1/models/{model_id}"
    headers = {"Content-Type": "application/json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        data_dict = _create_model_dict(data)

        return [
            data_dict,
            gr.HTML.update(value=''),
            gr.Accordion.update(visible=True),
            gr.JSON.update(value=data),
            gr.Column.update(visible=True),
            *_create_ui_update(data_dict)
        ]
    else:
        return [
            None,
            gr.HTML.update(value=alert_danger(f'Request failed with status code: {response.status_code}')),
            gr.Accordion.update(visible=False, open=False),
            gr.JSON.update(value='{}'),
            gr.Column.update(visible=False),
            *_create_ui_update()
        ]


def _create_ui_update(data_dict=None, selected_version=None, selected_file=None) -> list:
    if data_dict is None:
        return [
            gr.Textbox.update(value=''),
            gr.Dropdown.update(value='', ),
            gr.Textbox.update(value=''),
            gr.Dropdown.update(value='', choices=[]),
            gr.Textbox.update(value=''),
            gr.Gallery.update(value=None),
            gr.Textbox.update(value=''),
            gr.Dropdown.update(value='', choices=[]),
        ]

    version = None
    if selected_version is None:
        version = data_dict['versions'][0]
    else:
        versions = data_dict['versions']
        for ver in versions:
            if ver['name'] == selected_version:
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

    name = f"{data_dict['name']} [{version['name']}]"
    model_type = data_dict['mode_type'].value
    tags = data_dict['tags']
    model_version = version['name']
    model_versions = list(map(lambda x: x['name'], data_dict['versions']))

    image_url = version['images'][0][0] if len(version['images']) else ''

    file_version = file['display_name']
    file_versions = list(map(lambda x: x['display_name'], version['files']))

    prompts = version['trained_words']

    return [
        gr.Textbox.update(value=name),
        gr.Dropdown.update(value=model_type),
        gr.Textbox.update(value=tags),
        gr.Dropdown.update(value=model_version, choices=model_versions),
        gr.Textbox.update(value=image_url),
        gr.Gallery.update(version['images']),
        gr.Dropdown.update(value=file_version, choices=file_versions),
        gr.Textbox.update(value=prompts)
    ]


def _on_model_version_selected(data_dict, selected_version):
    return _create_ui_update(data_dict=data_dict, selected_version=selected_version)


def civitai_import_ui_block():
    import_url_textbox = gr.Textbox('https://civitai.com/models/4468/counterfeit-v30',
                                    label='civitai.com model url')
    with gr.Row():
        gr.Markdown()
        gr.Markdown()
        gr.Markdown()
        fetch_url_button = gr.Button('Fetch URL')

    import_result_html = gr.HTML('')
    import_model_state = gr.State(None)

    with gr.Column(visible=False) as content_container:
        name_widget = gr.Textbox(label='Name', interactive=True)

        model_type_dropdown = gr.Dropdown(choices=[model_type.value for model_type in ModelType],
                                          value='',
                                          label='Model type:', interactive=True)

        tags_textbox = gr.Textbox(label='Tags', interactive=True)
        model_version_dropdown = gr.Dropdown(label='Model Version', interactive=True)
        files_dropdown = gr.Dropdown(label='Model Files:', interactive=True)
        prompts_textbox = gr.Textbox(label='Trained words (Prompts):', interactive=True)

        preview_url_widget = gr.Textbox(label='Preview image URL. Or copy-paste another preview url from the'
                                              ' \"Image Previews\" gallery below', interactive=True)

        with gr.Accordion(label='Image previews', open=False):
            preview_gallery = gr.Gallery(elem_id='preview_gallery').style(grid=10, height="auto")

        with gr.Accordion(label='JSON Response', visible=False, open=False) as json_accordion:
            import_result_json = gr.JSON()

    fetch_url_button.click(_on_fetch_url_clicked,
                           inputs=import_url_textbox,
                           outputs=[import_model_state,
                                    import_result_html,
                                    json_accordion,
                                    import_result_json,
                                    content_container,
                                    name_widget,
                                    model_type_dropdown,
                                    tags_textbox,
                                    model_version_dropdown,
                                    preview_url_widget,
                                    preview_gallery,
                                    files_dropdown,
                                    prompts_textbox
                                    ])

    model_version_dropdown.select(fn=_on_model_version_selected,
                                  inputs=[import_model_state, model_version_dropdown],
                                  outputs=[
                                      name_widget,
                                      model_type_dropdown,
                                      tags_textbox,
                                      model_version_dropdown,
                                      preview_url_widget,
                                      preview_gallery,
                                      files_dropdown,
                                      prompts_textbox
                                  ])
