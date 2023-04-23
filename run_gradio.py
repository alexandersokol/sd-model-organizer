import mimetypes
import os
import time

import gradio as gr
import gradio.routes

from scripts.mo.environment import *
from scripts.mo.init_storage import initialize_storage
from scripts.mo.ui_main import main_ui_block

SETTINGS_FILE = 'settings.txt'

mimetypes.init()
mimetypes.add_type("application/javascript", ".js")


class ScriptLoader:
    path_map = {
        "js": os.path.abspath(os.path.join(os.path.dirname(__file__), "javascript")),
    }

    def __init__(self, script_type):
        self.script_type = script_type
        self.path = ScriptLoader.path_map[script_type]
        self.loaded_scripts = []

    @staticmethod
    def get_scripts(path: str, file_type: str) -> list[tuple[str, str]]:
        """Returns list of tuples
        Each tuple contains the full filepath and filename as strings
        """
        scripts = []
        dir_list = [os.path.join(path, f) for f in os.listdir(path)]
        files_list = [f for f in dir_list if os.path.isfile(f)]
        for s in files_list:
            # Don't forget the "." for file extension
            if os.path.splitext(s)[1] == f".{file_type}":
                scripts.append((s, os.path.basename(s)))
        return scripts


class JavaScriptLoader(ScriptLoader):
    def __init__(self):
        # Script type set here
        super().__init__("js")
        # Copy the template response
        self.original_template = gradio.routes.templates.TemplateResponse
        # Prep the js files
        self.load_js()
        # reassign the template response to your method, so gradio calls your method instead
        gradio.routes.templates.TemplateResponse = self.template_response

    def load_js(self):
        js_scripts = ScriptLoader.get_scripts(self.path, self.script_type)
        for file_path, file_name in js_scripts:
            with open(file_path, 'r', encoding="utf-8") as file:
                self.loaded_scripts.append(f"\n<!--{file_name}-->\n<script>\n{file.read()}\n</script>")

    def template_response(self, *args, **kwargs):
        """Once gradio calls your method, you call the original, you modify it to include
        your scripts and you return the modified version
        """
        response = self.original_template(*args, **kwargs)
        response.body = response.body.replace(
            '</head>'.encode('utf-8'), f"{''.join(self.loaded_scripts)}\n</head>".encode("utf-8")
        )
        response.init_headers()
        return response


def read_settings():
    with open(SETTINGS_FILE) as f:
        lines = f.readlines()

    result = {}
    for line in lines:
        key, value = line.strip().split(': ')
        result[key] = value
        logger.info(f'{key}: {value}')
    logger.info('Settings loaded.')
    return result


settings = read_settings()

env.mo_storage_type = lambda: settings['mo_storage_type']
env.mo_notion_api_token = lambda: settings['mo_notion_api_token']
env.mo_notion_db_id = lambda: settings['mo_notion_db_id']
env.mo_model_path = lambda: settings['mo_model_path']
env.mo_vae_path = lambda: settings['mo_vae_path']
env.mo_lora_path = lambda: settings['mo_lora_path']
env.mo_hypernetworks_path = lambda: settings['mo_hypernetworks_path']
env.mo_embeddings_path = lambda: settings['mo_embeddings_path']
env.mo_script_dir = ''
env.mo_layout = lambda: settings['mo_layout']
env.mo_card_width = lambda: settings['mo_card_width']
env.mo_card_height = lambda: settings['mo_card_height']
initialize_storage()


def storage_type_change(value):
    settings['mo_storage_type'] = value
    logger.info(f'mo_storage_type updated: {value}')


def notion_api_token_change(value):
    settings['mo_notion_api_token'] = value
    logger.info(f'mo_notion_api_token updated: {value}')


def notion_db_id_change(value):
    settings['mo_notion_db_id'] = value
    logger.info(f'mo_notion_db_id updated: {value}')


def model_path_change(value):
    settings['mo_model_path'] = value
    logger.info(f'mo_model_path updated: {value}')


def vae_path_change(value):
    settings['mo_vae_path'] = value
    logger.info(f'mo_vae_path updated: {value}')


def lora_path_change(value):
    settings['mo_lora_path'] = value
    logger.info(f'mo_lora_path updated: {value}')


def hypernetworks_path_change(value):
    settings['mo_hypernetworks_path'] = value
    logger.info(f'mo_hypernetworks_path updated: {value}')


def embeddings_path_change(value):
    settings['mo_embeddings_path'] = value
    logger.info(f'mo_embeddings_path updated: {value}')


def layout_type_change(value):
    settings['mo_layout'] = value
    logger.info(f'mo_layout updated: {value}')


def card_width_change(value):
    settings['mo_card_width'] = value
    logger.info(f'mo_card_width updated: {value}')


def card_height_change(value):
    settings['mo_card_height'] = value
    logger.info(f'mo_card_height updated: {value}')


def save_click():
    with open(SETTINGS_FILE, 'w') as f:
        for key, value in settings.items():
            f.write(f'{key}: {value}\n')
        logger.info('Settings saved')


def settings_block():
    with gr.Column():
        layout_type = gr.Dropdown([LAYOUT_CARDS, LAYOUT_TABLE], value=[env.mo_layout()],
                                  label="Layout type:", info='Select records layout type.')
        card_width = gr.Textbox(env.mo_card_width, label='Cards width:')
        card_height = gr.Textbox(env.mo_card_height, label='Cards height:')

        storage_type = gr.Dropdown([STORAGE_SQLITE, STORAGE_NOTION], value=[env.mo_storage_type()],
                                   label="Storage type:", info='Select storage type to save data.')
        notion_api_token = gr.Textbox(env.mo_notion_api_token(), label="Notion Api Token:")
        notion_db_id = gr.Textbox(env.mo_notion_db_id(), label="Notion Database Id")
        model_path = gr.Textbox(env.mo_model_path(), label='Model path:')
        vae_path = gr.Textbox(env.mo_vae_path(), label='VAE path:')
        lora_path = gr.Textbox(env.mo_lora_path(), label='LORA path:')
        hypernetworks_path = gr.Textbox(env.mo_hypernetworks_path(), label='Hypernetworks path:')
        embeddings_path = gr.Textbox(env.mo_embeddings_path(), label="Embeddings path:")
        button = gr.Button("Save")

    storage_type.change(storage_type_change, inputs=storage_type)
    notion_api_token.change(notion_api_token_change, inputs=notion_api_token)
    notion_db_id.change(notion_db_id_change, inputs=notion_db_id)
    model_path.change(model_path_change, inputs=model_path)
    vae_path.change(vae_path_change, inputs=vae_path)
    lora_path.change(lora_path_change, inputs=lora_path)
    hypernetworks_path.change(hypernetworks_path_change, inputs=hypernetworks_path)
    embeddings_path.change(embeddings_path_change, inputs=embeddings_path)
    layout_type.change(layout_type_change, inputs=layout_type)
    card_width.change(card_width_change, inputs=card_height)
    card_height.change(card_height_change, inputs=card_height)

    button.click(save_click)


def generator_outer():
    numbers = [1, 2, 3, 4, 5]
    yield 'start'
    for number in numbers:
        yield from generator_inner(number)
    yield 'end'


def generator_inner(number):
    time.sleep(1)
    yield f'my number is {number}'


def testing_block():
    with gr.Column():
        output_widget = gr.Textbox("Tab block for feature testing", interactive=False)
        button = gr.Button("Start")
    button.click(generator_outer, outputs=output_widget)


with gr.Blocks() as demo:
    with gr.Tab("Model Organizer"):
        main_ui_block()
    with gr.Tab("Settings"):
        settings_block()
    with gr.Tab("Testing"):
        testing_block()

js_loader = JavaScriptLoader()
demo.queue()
demo.launch()
