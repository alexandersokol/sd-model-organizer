class Record:
    def __init__(
            self,
            id_,
            name,
            type_,
            url,
            download_url,
            preview_url
    ):
        self.id_ = id_
        self.name = name
        self.type_ = type_
        self.url = url
        self.downloadUrl = download_url
        self.previewUrl = preview_url

    def __str__(self):
        return f"id={self.id_}, name={self.name}, type={self.type_}, url={self.url}, downloadUrl={self.downloadUrl}, previewUrl={self.previewUrl}"
