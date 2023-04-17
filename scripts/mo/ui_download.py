import json
import os
import time

import gradio as gr
import requests
from mega import Mega
from tqdm import tqdm

import scripts.mo.ui_navigation as nav
import scripts.mo.ui_styled_html as styled
from scripts.mo.environment import env
from scripts.mo.download_state import DownloadState


def _download_file_mega():
    progress_bar = tqdm(total=1000, unit='iB', unit_scale=True, desc='Downloading from mega.nz')
    temp_dir = os.path.join(env.mo_script_dir, 'tmp')
    m_url = 'https://mega.nz/file/4tcUgZiJ#tRrUVipDCdiQI5IiqXaEJ06iJSM_AEZ4L7G-qcctRpY'
    mega = Mega()
    m = mega.login()
    m.download_url(m_url, dest_path=temp_dir)


def _download_file_2():
    temp_dir = os.path.join(env.mo_script_dir, 'tmp')
    url = 'https://huggingface.co/Linaqruf/anything-v3.0/resolve/main/vae/diffusion_pytorch_model.bin'
    # url = 'https://huggingface.co/wavymulder/Analog-Diffusion/raw/main/tokenizer/vocab.json'
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc='File 2')

    with open(os.path.join(temp_dir, 'downloaded_file_2.zip'), 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)


def _download_file(progress=gr.Progress(track_tqdm=True)):
    temp_dir = os.path.join(env.mo_script_dir, 'tmp')
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)

    url = 'https://huggingface.co/Linaqruf/anything-v3.0/resolve/main/vae/diffusion_pytorch_model.bin'
    # url = 'https://huggingface.co/wavymulder/Analog-Diffusion/raw/main/tokenizer/vocab.json'
    # https://civitai.com/api/download/models/11745
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc='File 1')
    downloaded = 0
    previous_posted = -1

    print('5')
    with open(os.path.join(temp_dir, 'downloaded_file_1.zip'), 'wb') as file:
        print('4')
        for data in response.iter_content(block_size):
            print('3')
            progress_bar.update(len(data))
            file.write(data)
            print('2')
            downloaded += len(data)
            percents_done = int((downloaded / total_size) * 100)
            print('1')
            if previous_posted != percents_done:
                print('yield ', percents_done)
                yield f'{percents_done}'
                previous_posted = percents_done

    # download 2
    _download_file_2()
    _download_file_mega()
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


def _download_without_progress():
    temp_dir = os.path.join(env.mo_script_dir, 'tmp')
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)

    url = 'https://huggingface.co/Linaqruf/anything-v3.0/resolve/main/vae/diffusion_pytorch_model.bin'
    # url = 'https://huggingface.co/wavymulder/Analog-Diffusion/raw/main/tokenizer/vocab.json'
    # https://civitai.com/api/download/models/11745
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc='File 1')

    block_size = 1024  # 1 Kibibyte
    downloaded = 0
    with open(os.path.join(temp_dir, 'downloaded_file_1.zip'), 'wb') as file:
        for data in response.iter_content(block_size):
            file.write(data)
            progress_bar.update(len(data))

            downloaded += len(data)
            percents_done = int((downloaded / total_size) * 100)
            percents_left = 100 - percents_done

            print(f"Progress: {progress_bar.n}/{progress_bar.total}")
            print(f"Format dict: {progress_bar.format_dict}")

            print(f'Downloading: {percents_done}/{percents_left}')
            yield f"""
            <div class="mo-progress" style="height: 20px;">
                <div id="progress-moid" class="mo-progress-bar" role="progressbar" style="width: {percents_done}%" aria-valuenow="{percents_done}" aria-valuemin="0" aria-valuemax="100">{percents_done}%</div>
            </div>
            """

        # Find and hide it in root element by elem_id
        # <div class="wrap center svelte-gjihhp generating" style="position: absolute; height: 0px; padding: 0px;"></div>

        # .generating.svelte-gjihhp {
    # animation: svelte-gjihhp-pulse 2s cubic-bezier(.4,0,.6,1) infinite;
    # border: 2px solid var(--color-accent);
    # background: transparent;
    # }

    return 'Done'


# def download_ui_block():
#     with gr.Blocks():
#         id_box = gr.Textbox()
#         gr.Markdown('## Downloading')
#         load_button = gr.Button('Download')
#         dummy_widget = gr.HTML('<br><br><br>')
#         progress_box = gr.Textbox()
#         progress_widget = gr.HTML(f"""
#                        <div class="mo-progress" style="height: 20px;">
#                            <div id="progress-moid-x" class="mo-progress-bar" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
#                        </div>
#                        """, elem_id='html-progress-buddy')
#
#         load_button.click(_download_file, outputs=progress_box)
#         progress_box.change(None, inputs=progress_box, _js='progressBuddy')
#
#     return id_box


_STATE_PENDING = 'Pending'
_STATE_IN_PROGRESS = 'In Progress'
_STATE_COMPLETED = 'Completed'
_STATE_EXISTS = 'Exists'
_STATE_ERROR = 'Error'


def _on_id_change(data):
    records = []
    record_id = nav.get_download_record_id(data)
    group = nav.get_download_group(data)

    if record_id is not None:
        records.append(env.storage.get_record_by_id(record_id))

    if group is not None:
        records.extend(env.storage.get_records_by_group(group))

    return [
        gr.HTML.update(value=styled.download_cards(records)),
        gr.Button.update(visible=True)
    ]


def _build_update_dict(record_id, state=None, result_text=None, result_title=None, progress_info_left=None,
                       progress_info_center=None, progress_info_right=None, progress_preview_info_left=None,
                       progress_preview_info_center=None, progress_preview_info_right=None, progress=None,
                       progress_preview=None) -> str:
    update = {'id': record_id}

    if state is not None:
        update['state'] = state

    if result_text is not None:
        update['result_text'] = result_text

    if result_title is not None:
        update['result_title'] = result_title

    if progress_info_left is not None:
        update['progress_info_left'] = progress_info_left

    if progress_info_center is not None:
        update['progress_info_center'] = progress_info_center

    if progress_info_right is not None:
        update['progress_info_right'] = progress_info_right

    if progress_preview_info_left is not None:
        update['progress_preview_info_left'] = progress_preview_info_left

    if progress_preview_info_center is not None:
        update['progress_preview_info_center'] = progress_preview_info_center

    if progress_preview_info_right is not None:
        update['progress_preview_info_right'] = progress_preview_info_right

    if progress is not None:
        update['progress'] = progress

    if progress_preview is not None:
        update['progress_preview'] = progress_preview

    return json.dumps(update)


def _on_test_clicked():
    id_ = 20

    DownloadState.get_instance().is_download_cancelled = False

    yield _build_update_dict(record_id=id_,
                             state=_STATE_IN_PROGRESS,
                             result_title='Here is some result',
                             result_text=['result 1', 'result 2', 'result 3'],
                             progress_info_left='left',
                             progress_info_center='center',
                             progress_info_right='right',
                             progress_preview_info_left='left preview',
                             progress_preview_info_center='center preview',
                             progress_preview_info_right='right preview',
                             progress=0,
                             progress_preview=0)
    for i in range(1, 101):
        print(DownloadState.get_instance().is_download_cancelled)
        if DownloadState.get_instance().is_download_cancelled:
            yield _build_update_dict(record_id=id_, state=_STATE_ERROR, result_title='Download canceled',
                                     result_text='Download has been canceled by user.')
            return
        yield _build_update_dict(record_id=id_, progress=i)
        time.sleep(0.5)

    for i in range(1, 101):
        print(DownloadState.get_instance().is_download_cancelled)
        if DownloadState.get_instance().is_download_cancelled:
            yield _build_update_dict(record_id=id_, state=_STATE_ERROR, result_title='Download canceled',
                                     result_text='Download has been canceled by user.')
            return
        yield _build_update_dict(record_id=id_, progress_preview=i)
        time.sleep(0.2)

    yield _build_update_dict(record_id=id_, state=_STATE_COMPLETED)
    return _build_update_dict(record_id=id_, state=_STATE_COMPLETED)


def _on_cancel_click():
    print('Cancel clicked')
    DownloadState.get_instance().is_download_cancelled = True


def download_ui_block():
    with gr.Blocks():
        id_box = gr.Textbox()
        gr.Markdown('## Downloads')
        with gr.Row():
            gr.Markdown()
            start_button = gr.Button('Start download')
            gr.Markdown()
        html_widget = gr.HTML()
        test_box = gr.Textbox()
        test_button = gr.Button('Test')
        cancel_button = gr.Button('Cancel')

    id_box.change(_on_id_change, inputs=id_box, outputs=[html_widget, start_button])

    test_box.change(fn=None, inputs=test_box, _js='handleProgressUpdates')
    test_button.click(_on_test_clicked, outputs=test_box)
    cancel_button.click(_on_cancel_click)

    return id_box
