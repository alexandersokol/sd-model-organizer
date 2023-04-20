import os
import queue
import threading
import time
import traceback

import gradio as gr
import requests
from tqdm import tqdm


class MySingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

        self._running = False
        self.downloading = False
        self.output = {}
        self._thread = None
        self.in_queue = queue.Queue()
        self.out_queue = queue.Queue()

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop)
        self._thread.start()

    def stop(self):
        if not self._running:
            return
        self._running = False
        self._thread.join()

    def _loop(self):
        while self._running:
            while True:
                time.sleep(1)
                value = self.in_queue.get()
                if value is not None:
                    print(value)
                    self.out_queue.put('How are you?')
            pass

    def _download_from_url_internal(self, url: str, destination_file: str, temp_dir: str):
        try:
            self.downloading = True
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))

            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc=destination_file)

            self.output = {
                'bytes_ready': 0,
                'bytes_total': total_size,
                'speed_rate': 0,
                'elapsed': 0
            }

            with open(os.path.join(temp_dir, destination_file), 'wb') as file:
                for data in response.iter_content(1024):

                    if not self._running:
                        self.downloading = False
                        print('time to finish, sorry :(')
                        return

                    file.write(data)
                    progress_bar.update(len(data))
                    # print(progress_bar.format_meter(**progress_bar.format_dict))
                    format_dict = progress_bar.format_dict
                    self.output = {
                        'bytes_ready': format_dict['n'],
                        'bytes_total': format_dict['total'],
                        'speed_rate': format_dict['rate'],
                        'elapsed': format_dict['elapsed']
                    }

                progress_bar.close()
                self.downloading = False

        except Exception as ex:
            self.output = {
                'error': ex
            }
            traceback.print_exc()
            self.downloading = False

    def start_download(self):
        if self._running:
            return
        self._running = True
        self.output = {}
        url = 'https://civitai.com/api/download/models/11523'
        destination_file = 'yae.miko'
        temp_dir = 'tmp'
        self._thread = threading.Thread(target=self._download_from_url_internal,
                                        args=(url, destination_file, temp_dir,))
        self._thread.start()

    def stop_download(self):
        if not self._running:
            print('Nothing to stop')
            return
        self._running = False
        print('requesting to stop')
        self._thread.join()


def shit_fn():
    # MySingleton().in_queue.put('Hello?')
    # time.sleep(1)
    #
    # while not MySingleton().out_queue.empty():
    #     print(MySingleton().out_queue.get())

    MySingleton().start_download()

    while MySingleton().downloading:
        output = MySingleton().output
        if output.get('error') is not None:
            yield output['error'].args[0]
        else:
            yield output
        time.sleep(0.1)

    output = MySingleton().output
    if output.get('error') is not None:
        yield str(output['error'])


def cancel_fn():
    MySingleton().stop_download()


with gr.Blocks() as main:
    shit_box = gr.Textbox(label='Shit Box')
    shit_button = gr.Button('Shit Button')
    cancel_button = gr.Button('Cancel')

    shit_button.click(shit_fn, outputs=shit_box)
    cancel_button.click(cancel_fn, queue=False)

# MySingleton().start()

main.queue()
main.launch()
# MySingleton().stop()
