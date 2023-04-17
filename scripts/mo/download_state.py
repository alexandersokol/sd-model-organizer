import threading


class DownloadState:
    __instance = None
    __lock = threading.Lock()

    def __init__(self):
        self.is_download_cancelled = False

    @staticmethod
    def get_instance():
        if DownloadState.__instance is None:
            with DownloadState.__lock:
                if DownloadState.__instance is None:
                    DownloadState.__instance = DownloadState()
        return DownloadState.__instance
