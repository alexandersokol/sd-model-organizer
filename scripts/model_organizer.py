import gradio as gr
from modules import script_callbacks, shared, sd_models, sd_vae
from modules.shared import OptionInfo

from scripts.src.main import get_main_ui_block

MO_STORAGE = 'mo_storage'
MO_NOTION_API_TOKEN = 'mo_notion_api_token'
MO_NOTION_DB_ID = 'mo_notion_db_id'
MO_MODEL_PATH = 'mo_model_path'
MO_VAE_PATH = 'mo_vae_path'
MO_LORA_PATH = 'mo_lora_path'
MO_HYPERNETWORKS_PATH = 'mo_hypernetworks_path'
MO_EMBEDDINGS_PATH = 'mo_embeddings_path'


def on_ui_tabs():
    return (get_main_ui_block(), "Model Organizer", "model_organizer"),


def on_ui_settings():
    model_path = sd_models.model_path
    vae_path = sd_vae.vae_path
    lora_path = shared.cmd_opts.lora_dir
    hypernetworks_path = shared.cmd_opts.hypernetwork_dir
    embeddings_path = shared.cmd_opts.embeddings_dir

    mo_options = shared.options_section(('model_organizer', 'Model Organizer'), {
        MO_STORAGE: OptionInfo('SQLite', "Storage Type:", gr.Radio, {"choices": ['SQLite', 'Notion']}),
        MO_NOTION_API_TOKEN: OptionInfo('', 'Notion API Token:'),
        MO_NOTION_DB_ID: OptionInfo('', 'Notion Database Id:'),

        MO_MODEL_PATH: OptionInfo('', f'Model directory (If empty uses default: {model_path}):'),
        MO_VAE_PATH: OptionInfo('', f'VAE directory (If empty uses default: {vae_path}) :'),
        MO_LORA_PATH: OptionInfo('', f'Lora directory (If empty uses default: {lora_path}):'),
        MO_HYPERNETWORKS_PATH: OptionInfo('',
                                          f'Hypernetworks directory (If empty uses default: {hypernetworks_path}):'),
        MO_EMBEDDINGS_PATH: OptionInfo('', f'Embeddings directory (If empty uses default: {embeddings_path}):')
    })
    shared.options_templates.update(mo_options)


script_callbacks.on_ui_tabs(on_ui_tabs)
script_callbacks.on_ui_settings(on_ui_settings)
