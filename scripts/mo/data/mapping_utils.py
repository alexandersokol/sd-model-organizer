from scripts.mo.ui_format import format_kilobytes


def create_version_dict(version_data):
    version = {
        "id": version_data["id"],
        "name": version_data["name"],
        "updated_at": version_data["updatedAt"],
    }

    trained_words = []
    if version_data.get("trainedWords") is not None:
        words = version_data["trainedWords"]
        for word in words:
            trained_words.append(word)

    version["trained_words"] = ", ".join(trained_words) if len(trained_words) > 0 else ""

    if version_data.get("images") is not None:
        images_data = version_data["images"]
        images = []
        for image_data in images_data:
            url = (
                image_data["url"].replace("/width=450", "")
                if "/width=450" in image_data["url"]
                else image_data["url"]
            )
            images.append((url, url))
        version["images"] = images

    if version_data.get("files") is not None:
        files_data = version_data["files"]
        files = []

        for file_data in files_data:
            file_name = file_data["name"] if file_data.get("name") is not None else ""
            file_type = file_data["type"] if file_data.get("type") is not None else ""
            fp = file_data["metadata"]["fp"] if file_data["metadata"].get("fp") is not None else ""
            file_size = (
                file_data["metadata"]["size"]
                if file_data["metadata"].get("size") is not None
                else ""
            )
            file_format = (
                file_data["metadata"]["format"]
                if file_data["metadata"].get("format") is not None
                else ""
            )
            file_size_formatted = (
                format_kilobytes(file_data["sizeKB"]) if file_data.get("sizeKB") is not None else ""
            )

            display_name = ""

            if file_name:
                display_name += file_name

            if file_type:
                display_name += " | "
                display_name += file_type

            if fp:
                display_name += " | "
                display_name += fp

            if file_size:
                display_name += " | "
                display_name += file_size

            if file_format:
                display_name += " | "
                display_name += file_format

            if file_size_formatted:
                display_name += " | "
                display_name += file_size_formatted

            sha256 = (
                file_data["hashes"]["SHA256"]
                if file_data.get("hashes") is not None
                and file_data.get("hashes").get("SHA256") is not None
                else ""
            )
            file = {
                "id": file_data["id"],
                "file_name": file_data["name"],
                "display_name": display_name,
                "download_url": file_data["downloadUrl"],
                "is_primary": file_data["primary"] if file_data.get("primary") else False,
                "sha256": sha256,
            }
            files.append(file)
        version["files"] = files
    return version
