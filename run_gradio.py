import gradio as gr

from scripts.mo.environment import env, STORAGE_SQLITE, STORAGE_NOTION
from scripts.mo.ui_main import main_ui_block

SETTINGS_FILE = 'settings.txt'


def read_settings():
    with open(SETTINGS_FILE) as f:
        lines = f.readlines()

    result = {}
    for line in lines:
        key, value = line.strip().split(': ')
        result[key] = value
        print(f'{key}: {value}')
    print('Settings loaded.')
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


def storage_type_change(value):
    settings['mo_storage_type'] = value
    print(f'mo_storage_type updated: {value}')


def notion_api_token_change(value):
    settings['mo_notion_api_token'] = value
    print(f'mo_notion_api_token updated: {value}')


def notion_db_id_change(value):
    settings['mo_notion_db_id'] = value
    print(f'mo_notion_db_id updated: {value}')


def model_path_change(value):
    settings['mo_model_path'] = value
    print(f'mo_model_path updated: {value}')


def vae_path_change(value):
    settings['mo_vae_path'] = value
    print(f'mo_vae_path updated: {value}')


def lora_path_change(value):
    settings['mo_lora_path'] = value
    print(f'mo_lora_path updated: {value}')


def hypernetworks_path_change(value):
    settings['mo_hypernetworks_path'] = value
    print(f'mo_hypernetworks_path updated: {value}')


def embeddings_path_change(value):
    settings['mo_embeddings_path'] = value
    print(f'mo_embeddings_path updated: {value}')


def save_click():
    with open(SETTINGS_FILE, 'w') as f:
        for key, value in settings.items():
            f.write(f'{key}: {value}\n')
        print('Settings saved')


def settings_block():
    with gr.Column():
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
    button.click(save_click)


def testing_block():
    with gr.Column():
        gr.Textbox("Tab block for feature testing", interactive=False)


with gr.Blocks() as demo:
    with gr.Tab("Model Organizer"):
        main_ui_block()
    with gr.Tab("Settings"):
        settings_block()
    with gr.Tab("Testing"):
        testing_block()

demo.launch()
