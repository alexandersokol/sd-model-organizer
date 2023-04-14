import gradio as gr
import requests
import os
from tqdm import tqdm

from scripts.mo.environment import env

temp_dir = os.path.join(env.mo_script_dir, 'tmp')

def _download_file(progress = gr.Progress(track_tqdm=True)):


    url = 'https://huggingface.co/Linaqruf/anything-v3.0/resolve/main/vae/diffusion_pytorch_model.bin'
    # url = 'https://huggingface.co/wavymulder/Analog-Diffusion/raw/main/tokenizer/vocab.json'
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc='File 1')

    with open('downloaded_file.zip', 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

    # download 2
    url = 'https://huggingface.co/Linaqruf/anything-v3.0/resolve/main/vae/diffusion_pytorch_model.bin'
    # url = 'https://huggingface.co/wavymulder/Analog-Diffusion/raw/main/tokenizer/vocab.json'
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc='File 2')

    with open('downloaded_file.zip', 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    #
    # # download 3
    # g_url = 'https://drive.google.com/file/d/15ShP6-hKiiEkzIGRLP_xDr7EeQtc1Fy/view?usp=share_link'
    #
    # block_size = 1024  # 1 Kibibyte
    # progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc='File 3')
    #
    # gdown.download(url=g_url, output='downloaded_file.zip', quiet=False, fuzzy=True)

    if total_size != 0 and progress_bar.n != total_size:
        return 'ERROR: Failed to download the file'
    else:
        return 'The file has been downloaded successfully'


def download_ui_block():
    with gr.Blocks():
        id_box = gr.Textbox()
        gr.Markdown('## Downloading')
        load_button = gr.Button('Download')
        dummy_widget = gr.HTML('<br><br><br>')

        load_button.click(_download_file, outputs=dummy_widget)

    return id_box
