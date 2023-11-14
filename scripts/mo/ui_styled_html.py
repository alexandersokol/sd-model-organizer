import html
import json
import os
from typing import List

import scripts.mo.ui_format as ui_format
from scripts.mo.data.storage import map_record_to_dict
from scripts.mo.environment import env
from scripts.mo.models import Record, ModelType
from scripts.mo.utils import get_best_preview_url

_NO_PREVIEW_DARK = 'file=extensions/sd-model-organizer/pic/no-preview-dark-blue.png'
_NO_PREVIEW_LIGHT = 'file=extensions/sd-model-organizer/pic/no-preview-light.png'


def alert_danger(value) -> str:
    if isinstance(value, list):
        text = "<br>".join(value)
    else:
        text = value
    return f'<div class="mo-alert mo-alert-danger">{html.escape(text)}</div>'


def alert_primary(value) -> str:
    if isinstance(value, list):
        text = "<br>".join(value)
    else:
        text = value
    return f'<div class="mo-alert mo-alert-primary">{html.escape(text)}</div>'


def alert_success(value) -> str:
    if isinstance(value, list):
        text = "<br>".join(value)
    else:
        text = value
    return f'<div class="mo-alert mo-alert-success">{html.escape(text)}</div>'


def alert_warning(value) -> str:
    if isinstance(value, list):
        text = "<br>".join(value)
    else:
        text = value
    return f'<div class="mo-alert mo-alert-warning">{html.escape(text)}</div>'


def _limit_description(text):
    if text and len(text) > 600:
        return text[:600] + '...'
    else:
        return text


def _limit_card_name(text):
    if text and len(text) > 150:
        return text[:150] + '...'
    else:
        return text


def _model_type_css_class(model_type: ModelType) -> str:
    if model_type == ModelType.CHECKPOINT:
        css_class = 'mo-badge-checkpoint'
    elif model_type == ModelType.VAE:
        css_class = 'mo-badge-vae'
    elif model_type == ModelType.LORA:
        css_class = 'mo-badge-lora'
    elif model_type == ModelType.HYPER_NETWORK:
        css_class = 'mo-badge-hyper-network'
    elif model_type == ModelType.LYCORIS:
        css_class = 'mo-badge-lycoris'
    elif model_type == ModelType.EMBEDDING:
        css_class = 'mo-badge-embedding'
    elif model_type == ModelType.OTHER:
        css_class = 'mo-badge-other'
    else:
        raise ValueError(f'Unhandled model_type value: {model_type}')
    return css_class


def _model_card_type_css_class(model_type: ModelType) -> str:
    if model_type == ModelType.CHECKPOINT:
        css_class = 'mo-card-checkpoint'
    elif model_type == ModelType.VAE:
        css_class = 'mo-card-vae'
    elif model_type == ModelType.LORA:
        css_class = 'mo-card-lora'
    elif model_type == ModelType.HYPER_NETWORK:
        css_class = 'mo-card-hyper-network'
    elif model_type == ModelType.LYCORIS:
        css_class = 'mo-card-lycoris'
    elif model_type == ModelType.EMBEDDING:
        css_class = 'mo-card-embedding'
    elif model_type == ModelType.OTHER:
        css_class = 'mo-card-other'
    else:
        raise ValueError(f'Unhandled model_type value: {model_type}')
    return css_class


def _no_preview_image_url() -> str:
    if env.theme() == 'dark':
        return _NO_PREVIEW_DARK
    else:
        return _NO_PREVIEW_LIGHT


def records_table(records: List) -> str:
    table_html = '<div class="mo-container">'
    table_html += '<div class="mo-row mo-row-header">'
    table_html += '<div class="mo-col mo-col-preview"><span class="mo-text-header">Preview</span></div>'
    table_html += '<div class="mo-col mo-col-type"><span class="mo-text-header">Type</span></div>'
    table_html += '<div class="mo-col mo-col-name"><span class="mo-text-header">Name</span></div>'
    table_html += '<div class="mo-col mo-col-description"><span class="mo-text-header">Description</span></div>'
    table_html += '<div class="mo-col mo-col-actions"><span class="mo-text-header">Actions</span></div>'
    table_html += '</div>'
    for record in records:
        name = html.escape(record.name)
        type_ = record.model_type.value
        preview_url = get_best_preview_url(record)
        description = _limit_description(record.description)

        # Add row
        table_html += '<div class="mo-row">'

        # Add preview URL column
        table_html += '<div class="mo-col mo-col-preview">'
        table_html += f'<img class="mo-preview-image" src="{preview_url}" ' \
                      f'alt="Preview image"' \
                      f' onerror="this.onerror=null; this.src=\'{_no_preview_image_url()}\';"/>'
        table_html += '</div>'

        # Add type column
        type_badge_class = _model_type_css_class(record.model_type)
        table_html += f'<div class="mo-col mo-col-type"><span class="mo-badge {type_badge_class}">{type_}</span></div>'

        # Add name column
        table_html += f'<div class="mo-col mo-col-name">'
        table_html += f'<button class="mo-button-name" onclick="navigateDetails(\'{record.id_}\')">{name}</button>'
        table_html += '</div>'

        # Add description column
        table_html += f'<div class="mo-col mo-col-description">'
        table_html += f'<span class="mo-text-description">{html.escape(description)}</span>'
        table_html += '</div>'

        # Add actions column
        table_html += '<div class="mo-col mo-col-actions ">'

        if record.is_local_file_record():
            json_record = html.escape(json.dumps(map_record_to_dict(record)))

            table_html += '<button type="button" class="mo-btn mo-btn-success" ' \
                          f'onclick="navigateEditPrefilled(\'{json_record}\')">Add</button><br>'

            table_html += '<button type="button" class="mo-btn mo-btn-danger" ' \
                          f'onclick="navigateRemove(\'{record.location}\')">Remove</button><br>'
        else:
            table_html += '<button type="button" class="mo-btn mo-btn-success" ' \
                          f'onclick="navigateDetails(\'{record.id_}\')">Details</button><br>'

            if record.is_download_possible():
                table_html += '<button type="button" class="mo-btn mo-btn-primary" ' \
                              f'onclick="navigateDownloadRecord(\'{record.id_}\')">Download</button><br>'

            table_html += '<button type="button" class="mo-btn mo-btn-warning" ' \
                          f'onclick="navigateEdit(\'{record.id_}\')">Edit</button><br>'

            table_html += '<button type="button" class="mo-btn mo-btn-danger" ' \
                          f'onclick="navigateRemove(\'{record.id_}\')">Remove</button><br>'

        table_html += '</div>'
        # Close row
        table_html += '</div>'
    # Close table
    table_html += '</div>'
    return table_html


def _create_content_text(text: str) -> str:
    return f'<span class="mo-text-content">{text}</span>'


def _create_content_model_type(model_type: ModelType) -> str:
    return f'<span class="mo-badge {_model_type_css_class(model_type)} mo-details-badge">{model_type.value}</span>'


def _create_content_hash(value: str) -> str:
    return f'<samp class="mo-text-content">{value}</samp>'


def _create_content_link(link: str) -> str:
    return f'<a class="mo-nav-link" target="_blank" href="{link}">{link}</a>'


def _create_groups(groups: List) -> str:
    groups_html = ''
    for group in groups:
        groups_html += f'<span class="mo-badge mo-badge-group" onclick="">{html.escape(group)}</span>'
    return groups_html


def _create_top_fields_dict(record: Record) -> dict:
    result = {
        'Name': _create_content_text(html.escape(record.name)),
        'Type': _create_content_model_type(record.model_type)
    }

    if record.location and os.path.exists(record.location):
        size = os.path.getsize(record.location)
        result['Size'] = _create_content_hash(ui_format.format_bytes(size))

    if record.sha256_hash:
        result['SHA256'] = _create_content_hash(record.sha256_hash)

    if record.location and os.path.exists(record.location):
        result['Location'] = _create_content_hash(record.location)

    if record.url:
        result['Model page'] = _create_content_link(record.url)

    if record.groups:
        result['Groups'] = _create_groups(record.groups)

    if record.download_url:
        result['Download URL'] = _create_content_link(record.download_url)

    if record.download_path:
        result['Download path'] = _create_content_text(record.download_path)

    if record.download_filename:
        result['Download filename'] = _create_content_text(record.download_filename)

    if record.subdir:
        result['Subdir'] = _create_content_text(record.subdir)

    return result


def _details_field_row(title: str, field: str, is_even: bool) -> str:
    highlight = 'mo-details-row-even' if is_even else 'mo-details-row-odd'
    content = f'<div class="mo-details-row {highlight}">'

    content += '<div class="mo-details-sub-col mo-details-sub-col-header">'
    content += f'<span class="mo-text-header">{title}:</span>'
    content += '</div>'

    content += '<div class="mo-details-sub-col">'
    content += field
    content += '</div>'

    content += '</div>'
    return content


def _details_top(record: Record) -> str:
    preview_url = get_best_preview_url(record)

    content = '<div class="mo-details-row">'

    # Preview image
    content += '<div class="mo-details-col mo-details-col-preview">'
    content += f'<img class="mo-details-image" src="{preview_url}" alt="Preview Image" ' \
               f'onerror="this.onerror=null; this.src=\'{_no_preview_image_url()}\';"/>'
    content += '</div>'

    # Details column
    content += '<div class="mo-details-col">'
    content += '<div class="mo-details-sub-container">'

    fields = _create_top_fields_dict(record)
    counter = 0
    for key, value in fields.items():
        content += _details_field_row(key, value, counter % 2 == 0)
        counter += 1

    # End Top Details column
    content += '</div>'
    content += '</div>'
    content += '</div>'

    if record.positive_prompts or record.negative_prompts:
        content += '<div class="mo-details-row mo-details-row-padding">'
        content += '<div class="mo-details-col">'
        content += '<div class="mo-details-row">'
        content += '<div class="mo-details-sub-container">'

        content += '<div class="mo-details-sub-row">'
        if record.positive_prompts:
            content += '<div class="mo-details-sub-col mo-details-row-positive">'
            content += '<span class="mo-text-header mo-text-positive-header">Positive Prompts:</span>'
            content += '</div>'

        if record.negative_prompts:
            content += '<div class="mo-details-sub-col mo-details-row-negative">'
            content += '<span class="mo-text-header mo-text-negative-header">Negative Prompts</span>'
            content += '</div>'
        content += '</div>'

        content += '<div class="mo-details-sub-row">'
        if record.positive_prompts:
            content += '<div class="mo-details-sub-col mo-details-row-positive">'
            content += '<span class="mo-text-content mo-text-positive">'
            content += html.escape(record.positive_prompts)
            content += '</span>'
            content += '</div>'

        if record.negative_prompts:
            content += '<div class="mo-details-sub-col mo-details-row-negative">'
            content += '<span class="mo-text-content mo-text-negative">'
            content += html.escape(record.negative_prompts)
            content += '</span>'
            content += '</div>'
        content += '</div>'

        content += '</div>'
        content += '</div>'
        content += '</div>'
        content += '</div>'

    content += '</div>'
    return content


def record_details(record: Record) -> str:
    content = '<div class="mo-details-container">'
    content += _details_top(record)
    content += '</div>'
    return content


def records_cards(records: List) -> str:
    content = '<div class="mo-card-grid">'

    nsfw_blur = env.nsfw_blur()

    for record in records:
        contains_nsfw = any('nsfw' in group.lower() for group in record.groups) and nsfw_blur
        content += f'<div class="mo-card {_model_card_type_css_class(record.model_type)} {"blur" if contains_nsfw else ""}">'

        preview_url = get_best_preview_url(record)
        content += f'<img src="{preview_url}" alt="Preview Image" ' \
                   f'onerror="this.onerror=null; this.src=\'{_no_preview_image_url()}\';"/>'

        content += f'<div class="mo-card-blur-overlay-bottom">{html.escape(_limit_card_name(record.name))}</div>'

        content += '<div class="mo-card-content-top">'
        content += f'<div class="mo-card-text-left"><span class="mo-badge {_model_type_css_class(record.model_type)}"' \
                   f'>{record.model_type.value}</span></div>'
        content += '</div>'

        content += '<div class="mo-card-hover">'
        content += '<div class="mo-card-hover-buttons">'

        if record.is_local_file_record():
            json_record = html.escape(json.dumps(map_record_to_dict(record)))

            content += '<button type="button" class="mo-btn mo-btn-success" ' \
                       f'onclick="navigateEditPrefilled(\'{json_record}\')">Add</button><br>'

            location = record.location.replace("\\", "\\\\")
            content += '<button type="button" class="mo-btn mo-btn-danger" ' \
                       f'onclick="navigateRemove(\'{location}\')">Remove</button><br>'
        else:
            content += '<button type="button" class="mo-btn mo-btn-success" ' \
                       f'onclick="navigateDetails(\'{record.id_}\')">Details</button><br>'

            if record.is_download_possible():
                content += '<button type="button" class="mo-btn mo-btn-primary" ' \
                           f'onclick="navigateDownloadRecord(\'{record.id_}\')">Download</button><br>'

            content += '<button type="button" class="mo-btn mo-btn-warning" ' \
                       f'onclick="navigateEdit(\'{record.id_}\')">Edit</button><br>'

            content += '<button type="button" class="mo-btn mo-btn-danger" ' \
                       f'onclick="navigateRemove(\'{record.id_}\')">Remove</button><br>'

        content += '</div>'
        content += '</div>'

        content += '</div>'

    content += '</div>'
    return content


def _downloads_header(record_id, title) -> str:
    content = '<div class="mo-downloads-header">'
    content += f'<h2 style="margin: 0;" id="title-{record_id}">{html.escape(title)}</h2>'
    content += f'<p style="margin: 0; white-space: nowrap;" id="status-{record_id}">Pending</p>'
    content += '</div>'
    return content


def _download_url(record_id, url: str, is_preview: bool) -> str:
    preview = '-preview' if is_preview else ''
    hint = 'Preview URL' if is_preview else 'Model URL'
    content = f'<p style="margin-top: 2rem; display: block; overflow-wrap: anywhere;" id="url{preview}-{record_id}">' \
              f'[{hint}]: {url}</p>'
    return content


def _download_info(record_id, is_preview: bool) -> str:
    preview = '-preview' if is_preview else ''
    content = f'<div class="mo-download-info" id="info-bar{preview}-{record_id}" style="display: none !important">'
    content += f'<p style="margin: 0;" id="progress-info-left{preview}-{record_id}"></p>'
    content += f'<p style="margin: 0;" id="progress-info-center{preview}-{record_id}"></p>'
    content += f'<p style="margin: 0;" id="progress-info-right{preview}-{record_id}"></p>'
    content += '</div>'
    return content


def _download_progress_bar(record_id, is_preview: bool) -> str:
    preview = '-preview' if is_preview else ''
    content = '<div class="mo-progress" style="height: 1.2rem; margin-top: 1rem; display: none" ' \
              f'id="progress{preview}-{record_id}">'
    content += '<div class="mo-progress-bar" role="progressbar" style="width: 0"'
    content += 'aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"'
    content += f'id="progress-bar{preview}-{record_id}">0%</div>'
    content += '</div>'
    return content


def download_cards(records: List, token) -> str:
    content = f'<div class="mo-downloads-container" token="{token}">'
    counter = 0
    for record in records:
        id_ = record.id_

        card_margin_top = '0' if counter == 0 else '2rem'
        content += f'<div class="mo-downloads-card mo-alert-secondary" id="download-card-{id_}" ' \
                   f'style="margin-top: {card_margin_top}">'

        content += _downloads_header(id_, record.name)

        content += _download_url(id_, record.download_url, False)
        content += _download_info(id_, False)
        content += _download_progress_bar(id_, False)

        if record.preview_url and env.download_preview():
            content += _download_url(id_, record.preview_url, True)
            content += _download_info(id_, True)
            content += _download_progress_bar(id_, True)

        content += f'<div id="result-box-{id_}" style="margin-top: 1rem">'
        content += '</div>'

        content += '</div>'
        counter += 1

    content += '</div>'
    return content
