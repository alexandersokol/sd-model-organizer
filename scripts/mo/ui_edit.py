import re

import gradio as gr

import scripts.mo.ui_styled_html as styled
from scripts.mo.models import Record, ModelType
from scripts.mo.environment import env


def is_unix_directory_path(path):
    pattern = r'^\/(?:[\w\d]+\/?)*$'
    return bool(re.match(pattern, path))


def is_valid_url(url: str) -> bool:
    pattern = re.compile(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    return bool(pattern.match(url))


def is_valid_filename(filename: str) -> bool:
    pattern = re.compile(r'^\w+\.\w+$')
    return bool(pattern.match(filename))


def is_blank(s):
    return len(s.strip()) == 0


def on_save_click(record_id, name: str, model_type: str, download_url: str, url: str, download_path: str,
                  download_filename: str, preview_url: str, description: str, positive_prompts: str,
                  negative_prompts: str, groups: list[str]):
    errors = []
    if is_blank(name):
        errors.append('Name field is empty.')

    if is_blank(model_type):
        errors.append('Model type not selected.')

    if is_blank(download_url):
        errors.append('Download field is empty.')
    elif not is_valid_url(download_url):
        errors.append('Download URL is incorrect')

    if not is_blank(url) and not is_valid_url(url):
        errors.append('Model URL is incorrect.')

    if not is_blank(download_path) and not is_unix_directory_path(download_path):
        errors.append('Download path is incorrect.')

    if model_type == ModelType.OTHER.value and is_blank(download_path):
        errors.append('Download path for type "Other" must be defined.')

    if not is_blank(download_filename) and not is_valid_filename(download_filename):
        errors.append('Download filename is incorrect.')

    if not is_blank(preview_url) and not is_valid_url(preview_url):
        errors.append('Preview URL is incorrect.')

    if errors:
        return gr.HTML.update(value=styled.alert_danger(errors), visible=True)
    else:
        record = Record(
            id_=record_id,
            name=name.strip(),
            model_type=ModelType.by_value(model_type),
            download_url=download_url.strip(),
            url=url.strip(),
            download_path=download_path.strip(),
            download_filename=download_filename.strip(),
            preview_url=preview_url.strip(),
            description=description.strip(),
            positive_prompts=positive_prompts.strip(),
            negative_prompts=negative_prompts.strip(),
            groups=groups
        )

        print(record)

        if record_id is not None and record_id:
            env.storage.update_record(record)
        else:
            env.storage.add_record(record)

        return gr.Button.update(visible=False)


def _on_id_changed(record_id):
    if record_id is not None and record_id:
        record = env.storage.get_record_by_id(record_id)
    else:
        record = None

    title = '## Add model' if record is None else '## Edit model'
    name = '' if record is None else record.name
    model_type = '' if record is None else record.model_type.value
    download_url = '' if record is None else record.download_url
    preview_url = '' if record is None else record.preview_url
    url = '' if record is None else record.url
    download_path = '' if record is None else record.download_path
    download_filename = '' if record is None else record.download_filename
    description = '' if record is None else record.description
    positive_prompts = '' if record is None else record.positive_prompts
    negative_prompts = '' if record is None else record.negative_prompts
    record_groups = '' if record is None else record.groups

    available_groups = env.storage.get_available_groups()
    available_groups.sort()
    groups = gr.Dropdown.update(choices=available_groups, value=record_groups)

    return [title, name, model_type, download_url, preview_url, url, download_path, download_filename, description,
            positive_prompts, negative_prompts, groups, available_groups]


def _on_add_groups_button_click(new_groups_str: str, selected_groups, available_groups):
    print(f'new groups string: {new_groups_str}')
    print(f'selected groups: {selected_groups}')
    print(f'available_groups: {available_groups}')

    if available_groups is None:
        available_groups = []

    if selected_groups is None:
        selected_groups = []

    if new_groups_str:
        new_groups = new_groups_str.split(',')
        new_groups = [x.strip() for x in new_groups]
        available_groups.extend(new_groups)
        selected_groups.extend(new_groups)
        print(f'new groups list: {new_groups}')

    return [
        gr.Textbox.update(value=''),
        gr.Dropdown.update(choices=available_groups, value=selected_groups)
    ]


def edit_ui_block():
    with gr.Blocks():
        id_box = gr.Textbox(label='id_box')
        title_widget = gr.Markdown()
        available_groups_state = gr.State()

        with gr.Row():
            with gr.Column():
                cancel_widget = gr.Button('Cancel')
                name_widget = gr.Textbox(label='Name:',
                                         value='',
                                         max_lines=1,
                                         info='Model title to display (Required)')
                model_type_widget = gr.Dropdown(
                    [model_type.value for model_type in ModelType],
                    value='',
                    label='Model type:',
                    info='Model type (Required)')

                download_url_widget = gr.Textbox(label='Download URL:',
                                                 value='',
                                                 max_lines=1,
                                                 info='Link to the model file (Required)')
                preview_url_widget = gr.Textbox(label='Preview image URL:',
                                                value='',
                                                max_lines=1,
                                                info='Link to the image for preview (Optional)'
                                                )
                url_widget = gr.Textbox(label='Model page URL:',
                                        value='',
                                        max_lines=1,
                                        info='Link to the model page (Optional)')

                download_path_widget = gr.Textbox(label='Download Path:',
                                                  value='',
                                                  max_lines=1,
                                                  info='UNIX path to the download dir, default if empty. Must start '
                                                       'with "\\" (Required for "Other\" model type)', )
                download_filename_widget = gr.Textbox(label='Download File Name:',
                                                      value='',
                                                      max_lines=1,
                                                      info='Downloaded file name. Default if empty (Optional)')

            with gr.Column():
                save_widget = gr.Button('Save')
                error_widget = gr.HTML(visible=False)
                groups_widget = gr.Dropdown(label='Groups',
                                            multiselect=True,
                                            info='Select existing groups or add new.',
                                            interactive=True,
                                            elem_id='mo-groups-widget'
                                            )
                with gr.Accordion(label='Add groups', open=False):
                    with gr.Row():
                        add_groups_box = gr.Textbox(label='Add new group',
                                                    max_lines=1,
                                                    info='Type comma-separated group names',
                                                    elem_id='mo-add-groups-box')
                        add_groups_button = gr.Button('Add Group')

                description_widget = gr.Textbox(label='Description:',
                                                value='',
                                                max_lines=20,
                                                info='Model description (Optional)')
                positive_prompts_widget = gr.Textbox(label='Positive prompts:',
                                                     value='',
                                                     max_lines=20,
                                                     info='Model positive prompts (Optional)')
                negative_prompts_widget = gr.Textbox(label='Negative prompts:',
                                                     value='',
                                                     max_lines=20,
                                                     info='Model negative prompts (Optional)')

            id_box.change(_on_id_changed,
                          inputs=id_box,
                          outputs=[title_widget, name_widget, model_type_widget, download_url_widget,
                                   preview_url_widget, url_widget, download_path_widget, download_filename_widget,
                                   description_widget, positive_prompts_widget, negative_prompts_widget, groups_widget,
                                   available_groups_state]
                          )

            save_widget.click(on_save_click,
                              inputs=[id_box, name_widget, model_type_widget, download_url_widget, url_widget,
                                      download_path_widget, download_filename_widget, preview_url_widget,
                                      description_widget, positive_prompts_widget, negative_prompts_widget,
                                      groups_widget],
                              outputs=[error_widget])

            add_groups_button.click(_on_add_groups_button_click,
                                    inputs=[add_groups_box, groups_widget, available_groups_state],
                                    outputs=[add_groups_box, groups_widget])

            # groups_widget.change(fn=lambda x: print(f'on change: {x}'), inputs=groups_widget)
            # add_groups_box.change(_on_add_groups_box_change,
            #                       inputs=[add_groups_box, groups_widget)

            return id_box
