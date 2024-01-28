from typing import Optional

import gradio as gr
import modules.scripts as scripts
from fastapi import FastAPI
from gradio import Blocks
from modules import script_callbacks
from modules import shared, sd_models, sd_vae, paths, ui_extra_networks
from modules.shared import OptionInfo

from scripts.mo.api import init_extension_api
from scripts.mo.data.init_storage import initialize_storage
from scripts.mo.environment import *
from scripts.mo.ui_main import main_ui_block


def _default_model_path() -> str:
    if hasattr(shared.cmd_opts, 'ckpt_dir') and shared.cmd_opts.ckpt_dir:
        return shared.cmd_opts.ckpt_dir
    elif hasattr(sd_models, 'model_path') and sd_models.model_path:
        return sd_models.model_path
    else:
        return os.path.join(paths.models_path, 'Stable-diffusion')


def _default_vae_path() -> str:
    if hasattr(shared.cmd_opts, 'vae_dir') and shared.cmd_opts.vae_dir:
        return shared.cmd_opts.vae_dir
    elif hasattr(sd_vae, 'vae_path') and sd_vae.vae_path:
        return sd_vae.vae_path
    else:
        return os.path.join(paths.models_path, 'VAE')


def _default_lora_path() -> str:
    if hasattr(shared.cmd_opts, 'lora_dir') and shared.cmd_opts.lora_dir:
        return shared.cmd_opts.lora_dir
    else:
        return os.path.join(paths.models_path, 'Lora')


def _default_hypernetworks_path() -> str:
    if (
        hasattr(shared.cmd_opts, 'hypernetwork_dir')
        and shared.cmd_opts.hypernetwork_dir
    ):
        return shared.cmd_opts.hypernetwork_dir
    else:
        return os.path.join(paths.models_path, 'hypernetworks')


def _default_lycoris_path() -> str:
    if hasattr(shared.cmd_opts, 'lyco_dir') and shared.cmd_opts.lyco_dir:
        return shared.cmd_opts.lyco_dir
    else:
        return os.path.join(paths.models_path, 'LyCORIS')


def _default_embeddings_path() -> str:
    if hasattr(shared.cmd_opts, 'embeddings_dir') and shared.cmd_opts.embeddings_dir:
        return shared.cmd_opts.embeddings_dir
    else:
        return os.path.join(paths.data_path, 'embeddings')


def _lycoris_path() -> str:
    if hasattr(shared.opts, 'mo_lycoris_path') and shared.opts.mo_lycoris_path:
        return shared.opts.mo_lycoris_path
    else:
        return _default_lycoris_path()


env.layout = (
    lambda: shared.opts.mo_layout if hasattr(shared.opts, 'mo_layout') else LAYOUT_CARDS
)

env.card_width = (
    lambda: shared.opts.mo_card_width
    if hasattr(shared.opts, 'mo_card_width') and shared.opts.mo_card_width
    else DEFAULT_CARD_WIDTH
)

env.card_height = (
    lambda: shared.opts.mo_card_height
    if hasattr(shared.opts, 'mo_card_height') and shared.opts.mo_card_height
    else DEFAULT_CARD_HEIGHT
)

env.storage_type = (
    lambda: shared.opts.mo_storage_type
    if hasattr(shared.opts, 'mo_storage_type')
    else STORAGE_SQLITE
)

env.download_preview = (
    lambda: shared.opts.mo_download_preview
    if hasattr(shared.opts, 'mo_download_preview')
    else True
)

env.resize_preview = (
    lambda: shared.opts.mo_resize_preview
    if hasattr(shared.opts, "mo_resize_preview")
    else True
)

env.nsfw_blur = (
    lambda: shared.opts.mo_nsfw_blur
    if hasattr(shared.opts, 'mo_nsfw_blur')
    else True
)

env.prefill_pos_prompt = (
    lambda: shared.opts.mo_prefill_pos_prompt
    if hasattr(shared.opts, 'mo_prefill_pos_prompt')
    else True
)

env.prefill_neg_prompt = (
    lambda: shared.opts.mo_prefill_neg_prompt
    if hasattr(shared.opts, 'mo_prefill_neg_prompt')
    else True
)

env.autobind_file = (
    lambda: shared.opts.mo_autobind_file
    if hasattr(shared.opts, 'mo_autobind_file')
    else True
)
	
env.api_key = (
    lambda: shared.opts.mo_api_key
    if hasattr(shared.opts, 'mo_api_key')
    else ""
)

env.model_path = (
    lambda: shared.opts.mo_model_path
    if hasattr(shared.opts, 'mo_model_path') and shared.opts.mo_model_path
    else _default_model_path()
)

env.vae_path = (
    lambda: shared.opts.mo_vae_path
    if hasattr(shared.opts, 'mo_vae_path') and shared.opts.mo_vae_path
    else _default_vae_path()
)

env.lora_path = (
    lambda: shared.opts.mo_lora_path
    if hasattr(shared.opts, 'mo_lora_path') and shared.opts.mo_lora_path
    else _default_lora_path()
)

env.hypernetworks_path = (
    lambda: shared.opts.mo_hypernetworks_path
    if hasattr(shared.opts, 'mo_hypernetworks_path')
    and shared.opts.mo_hypernetworks_path
    else _default_hypernetworks_path()
)

env.lycoris_path = _lycoris_path

env.embeddings_path = (
    lambda: shared.opts.mo_embeddings_path
    if hasattr(shared.opts, 'mo_embeddings_path') and shared.opts.mo_embeddings_path
    else _default_embeddings_path()
)

env.is_debug_mode_enabled = (
    lambda: hasattr(shared.cmd_opts, 'mo_debug') and shared.cmd_opts.mo_debug
)

env.script_dir = scripts.basedir()
env.theme = lambda: shared.cmd_opts.theme


def on_ui_settings():
    opts = {
        'mo_layout': OptionInfo(
            LAYOUT_CARDS,
            "Layout Type:",
            gr.Radio,
            {"choices": [LAYOUT_CARDS, LAYOUT_TABLE]},
        ),
        'mo_card_width': OptionInfo(250, 'Card width (250 default value):'),
        'mo_card_height': OptionInfo(350, 'Card height (350 default value):'),
        'mo_storage_type': OptionInfo(
            STORAGE_SQLITE,
            "Storage Type:",
            gr.Radio,
            {"choices": [STORAGE_SQLITE, STORAGE_FIREBASE]},
        ),
        'mo_download_preview': OptionInfo(True, 'Download Preview'),
        'mo_resize_preview': OptionInfo(True, 'Resize Preview'),
        'mo_nsfw_blur': OptionInfo(True, 'Blur NSFW Previews (models with "nsfw" tag)'),
        'mo_prefill_pos_prompt': OptionInfo(True, 'When creating a record based on local file, automatically import the added positive prompts'),
        'mo_prefill_neg_prompt': OptionInfo(True, 'When creating a record based on local file, automatically import the added negative prompts'),
        'mo_autobind_file': OptionInfo(True, 'Automatically bind record to local file'),
        'mo_api_key': OptionInfo("", "Civitai API Key. Create an API key under 'https://civitai.com/user/account' all the way at the bottom. Don't share the token!"),
    }

    dir_opts = {
        'mo_model_path': OptionInfo(
            '', f'Model directory (If empty uses default: {_default_model_path()}):'
        ),
        'mo_vae_path': OptionInfo(
            '', f'VAE directory (If empty uses default: {_default_vae_path()}) :'
        ),
        'mo_lora_path': OptionInfo(
            '', f'Lora directory (If empty uses default: {_default_lora_path()}):'
        ),
        'mo_hypernetworks_path': OptionInfo(
            '',
            f'Hypernetworks directory (If empty uses default: '
            f'{_default_hypernetworks_path()}):',
        ),
        'mo_lycoris_path': OptionInfo(
            '', f'LyCORIS directory (If empty uses default: {_default_lycoris_path()}):'
        ),
        'mo_embeddings_path': OptionInfo(
            '',
            f'Embeddings directory (If empty uses default: '
            f'{_default_embeddings_path()}):',
        ),
    }

    if (
        hasattr(shared.cmd_opts, 'mo_show_dir_settings')
        and shared.cmd_opts.mo_show_dir_settings
    ):
        opts.update(dir_opts)

    mo_options = shared.options_section(('mo', 'Model Organizer'), opts)
    shared.options_templates.update(mo_options)
    initialize_storage()


def on_ui_tabs():
    # if env.is_debug_mode_enabled():  # TODO Remove these lines
    #     ui_extra_networks.allowed_dirs.add(
    #         '/Users/alexander/Downloads/sd-downloads/ckpt'
    #     )
    #     ui_extra_networks.allowed_dirs.add(
    #         '/Users/alexander/Downloads/sd-downloads/vae'
    #     )
    #     ui_extra_networks.allowed_dirs.add(
    #         '/Users/alexander/Downloads/sd-downloads/embeddings'
    #     )
    #     ui_extra_networks.allowed_dirs.add(
    #         '/Users/alexander/Downloads/sd-downloads/hypernetworks'
    #     )
    #     ui_extra_networks.allowed_dirs.add(
    #         '/Users/alexander/Downloads/sd-downloads/lora'
    #     )
    #     ui_extra_networks.allowed_dirs.add(
    #         '/Users/alexander/Downloads/sd-downloads/lyco'
    #     )

    return ((main_ui_block(), "Model Organizer", "model_organizer"),)


def on_app_started(demo: Optional[Blocks], app: FastAPI):
    init_extension_api(app)


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_ui_tabs(on_ui_tabs)
script_callbacks.on_app_started(on_app_started)
