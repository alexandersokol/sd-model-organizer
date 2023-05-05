import gradio as gr
import modules.scripts as scripts
from modules import script_callbacks
from modules import shared, sd_models, sd_vae, paths
from modules.shared import OptionInfo

from scripts.mo.data.init_storage import initialize_storage
from scripts.mo.environment import *
from scripts.mo.ui_main import main_ui_block


def _lycoris_path() -> str:
    if hasattr(shared.opts, 'mo_lycoris_path') and shared.opts.mo_lycoris_path:
        return shared.opts.mo_lycoris_path
    elif hasattr(shared.cmd_opts, 'lyco_dir') and shared.cmd_opts.lyco_dir:
        return shared.cmd_opts.lyco_dir
    else:
        return os.path.join(paths.models_path, 'LyCORIS')


env.layout = lambda: shared.opts.mo_layout if hasattr(shared.opts, 'mo_layout') else LAYOUT_CARDS

env.card_width = lambda: shared.opts.mo_card_width if hasattr(shared.opts, 'mo_card_width') else 0

env.card_height = lambda: shared.opts.mo_card_height if hasattr(shared.opts, 'mo_card_height') else 0

env.storage_type = lambda: shared.opts.mo_storage_type if hasattr(shared.opts, 'mo_storage_type') else STORAGE_SQLITE

env.download_preview = lambda: shared.opts.mo_download_preview if hasattr(shared.opts,
                                                                          'mo_download_preview') else True

env.model_path = lambda: shared.opts.mo_model_path if hasattr(shared.opts, 'mo_model_path') and \
                                                      shared.opts.mo_model_path else sd_models.model_path

env.vae_path = lambda: shared.opts.mo_vae_path if hasattr(shared.opts, 'mo_vae_path') and \
                                                     shared.opts.mo_vae_path else sd_vae.vae_path

env.lora_path = lambda: shared.opts.mo_lora_path if hasattr(shared.opts, 'mo_lora_path') and \
                                                       shared.opts.mo_lora_path else shared.cmd_opts.lora_dir

env.hypernetworks_path = lambda: shared.opts.mo_hypernetworks_path if \
    hasattr(shared.opts,
            'mo_hypernetworks_path') and shared.opts.mo_hypernetworks_path else shared.cmd_opts.hypernetwork_dir

env.lycoris_path = _lycoris_path

env.embeddings_path = lambda: shared.opts.mo_embeddings_path if \
    hasattr(shared.opts, 'mo_embeddings_path') and shared.opts.mo_embeddings_path else shared.cmd_opts.embeddings_dir

env.script_dir = scripts.basedir()
env.theme = lambda: shared.cmd_opts.theme


def on_ui_settings():
    model_path = sd_models.model_path
    vae_path = sd_vae.vae_path
    lora_path = shared.cmd_opts.lora_dir
    hypernetworks_path = shared.cmd_opts.hypernetwork_dir
    embeddings_path = shared.cmd_opts.embeddings_dir
    if hasattr(shared.cmd_opts, 'lyco_dir') and shared.cmd_opts.lyco_dir:
        lycoris_path = shared.cmd_opts.lyco_dir
    else:
        lycoris_path = os.path.join(paths.models_path, 'LyCORIS')

    mo_options = shared.options_section(('mo', 'Model Organizer'), {
        'mo_layout': OptionInfo(LAYOUT_CARDS, "Layout Type:", gr.Radio,
                                {"choices": [LAYOUT_CARDS, LAYOUT_TABLE]}),
        'mo_card_width': OptionInfo(0, 'Card width (default if 0):'),
        'mo_card_height': OptionInfo(0, 'Card height (default if 0):'),
        'mo_storage_type': OptionInfo(STORAGE_SQLITE, "Storage Type:", gr.Radio,
                                      {"choices": [STORAGE_SQLITE, STORAGE_FIREBASE]}),
        'mo_download_preview': OptionInfo(True, 'Download Preview'),
        'mo_model_path': OptionInfo('', f'Model directory (If empty uses default: {model_path}):'),
        'mo_vae_path': OptionInfo('', f'VAE directory (If empty uses default: {vae_path}) :'),
        'mo_lora_path': OptionInfo('', f'Lora directory (If empty uses default: {lora_path}):'),
        'mo_hypernetworks_path': OptionInfo('',
                                            f'Hypernetworks directory (If empty uses default: {hypernetworks_path}):'),
        'mo_lycoris_path': OptionInfo('',
                                      f'LyCORIS directory (If empty uses default: {lycoris_path}):'),
        'mo_embeddings_path': OptionInfo('', f'Embeddings directory (If empty uses default: {embeddings_path}):')
    })
    shared.options_templates.update(mo_options)
    initialize_storage()


def on_ui_tabs():
    return (main_ui_block(), "Model Organizer", "model_organizer"),


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_ui_tabs(on_ui_tabs)
