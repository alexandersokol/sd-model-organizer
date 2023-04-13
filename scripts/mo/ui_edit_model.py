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
                  negative_prompts: str):
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
            negative_prompts=negative_prompts.strip()
        )

        print(record)

        if record_id is not None and record_id:
            env.storage.update_record(record)
        else:
            env.storage.add_record(record)

        return gr.Button.update(visible=False)


def _on_id_changed(record_id):
    if record_id is not None and record_id:
        record = env.storage.fetch_data_by_id(record_id)
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

    return [title, name, model_type, download_url, preview_url, url, download_path, download_filename, description,
            positive_prompts, negative_prompts]


def edit_model_ui_block():
    with gr.Blocks():
        edit_id_box = gr.Textbox('## Add model')

        title_widget = gr.Markdown()
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

            edit_id_box.change(_on_id_changed,
                               inputs=edit_id_box,
                               outputs=[title_widget, name_widget, model_type_widget, download_url_widget,
                                        preview_url_widget, url_widget, download_path_widget, download_filename_widget,
                                        description_widget, positive_prompts_widget, negative_prompts_widget]
                               )

            save_widget.click(on_save_click,
                              inputs=[edit_id_box, name_widget, model_type_widget, download_url_widget, url_widget,
                                      download_path_widget, download_filename_widget, preview_url_widget,
                                      description_widget, positive_prompts_widget, negative_prompts_widget],
                              outputs=[error_widget])

            return edit_id_box
