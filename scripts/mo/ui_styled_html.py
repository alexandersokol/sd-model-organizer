import html
import json
from typing import List

from scripts.mo.models import Record, ModelType

_NO_PREVIEW_DARK = 'https://github.com/alexandersokol/sd-model-organizer/raw/master/pic/no-preview-dark.png'
_NO_PREVIEW_LIGHT = 'https://github.com/alexandersokol/sd-model-organizer/raw/master/pic/no-preview-light.png'


def alert_danger(value) -> str:
    if isinstance(value, list):
        text = "<br>".join(value)
    else:
        text = value
    return f'<div class="mo-alert-danger">{text}</div>'


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
    elif model_type == ModelType.EMBEDDING:
        css_class = 'mo-badge-embedding'
    elif model_type == ModelType.OTHER:
        css_class = 'mo-badge-other'
    else:
        raise ValueError(f'Unhandled model_type value: {model_type}')
    return css_class


def _no_preview_image_url() -> str:
    return f'https://github.com/alexandersokol/sd-model-organizer/raw/master/pic/no-preview-light.png'


def records_table(records: List[Record]) -> str:
    table_html = '<div class="mo-container">'
    table_html += '<div class="mo-row mo-row-header">'
    table_html += '<div class="mo-col mo-col-preview"><span class="mo-text-header">Preview</span></div>'
    table_html += '<div class="mo-col mo-col-type"><span class="mo-text-header">Type</span></div>'
    table_html += '<div class="mo-col mo-col-name"><span class="mo-text-header">Name</span></div>'
    table_html += '<div class="mo-col mo-col-description"><span class="mo-text-header">Description</span></div>'
    table_html += '<div class="mo-col mo-col-actions"><span class="mo-text-header">Actions</span></div>'
    table_html += '</div>'
    for record in records:
        name = record.name
        type_ = record.model_type.value
        preview_url = record.preview_url
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
        table_html += f'<button class="mo-button-name" onclick="handleModelClick(\'{name}\')">{name}</button>'
        table_html += '</div>'

        # Add description column
        table_html += f'<div class="mo-col mo-col-description">'
        table_html += f'<span class="mo-text-description">{description}</span>'
        table_html += '</div>'

        # Add actions column
        table_html += '<div class="mo-col mo-col-actions ">'
        table_html += '<button class="mo-btn mo-btn-primary">Download</button>'
        table_html += '<br>'
        table_html += '<button type="button" class="mo-btn mo-btn-warning">Edit</button>'
        table_html += '<br>'
        table_html += '<button type="button" class="mo-btn mo-btn-danger">Remove</button>'
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


def _create_top_fields_dict(record: Record) -> dict:
    result = {
        'Name': _create_content_text(record.name),
        'Type': _create_content_model_type(record.model_type)
    }

    if record.location:
        result['Location'] = _create_content_text(record.location)

    if record.model_hash:
        result['Model Hash'] = _create_content_hash(record.model_hash)

    if record.md5_hash:
        result['MD5 Hash'] = _create_content_hash(record.md5_hash)

    if record.url:
        result['Model page'] = _create_content_link(record.url)

    if record.download_url:
        result['Download URL'] = _create_content_link(record.download_url)

    if record.download_path:
        result['Download path'] = _create_content_text(record.download_path)

    if record.download_filename:
        result['Download filename'] = _create_content_text(record.download_filename)

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
    preview_url = record.preview_url

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

    # Description
    if record.description:
        highlight = 'mo-details-row-even' if counter % 2 == 0 else 'mo-details-row-odd'
        content += f'<div class="mo-details-row mo-details-row-padding {highlight}">'
        content += '<div class="mo-details-col mo-details-col-full">'
        content += '<span class="mo-text-header">Description:</span>'
        content += '</div>'
        content += '</div>'

        content += f'<div class="mo-details-row mo-details-row-padding {highlight}">'
        content += '<div class="mo-details-col mo-details-col-full">'
        content += f'<span class="mo-text-content">{record.description}</span>'
        content += '</div>'
        content += ' </div>'

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
            content += record.positive_prompts
            content += '</span>'
            content += '</div>'

        if record.negative_prompts:
            content += '<div class="mo-details-sub-col mo-details-row-negative">'
            content += '<span class="mo-text-content mo-text-negative">'
            content += record.negative_prompts
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


def records_cards(records: List[Record]) -> str:
    content = '<div class="mo-card-grid">'
    content += """
    <script>
    function handleRemoveClick(recordId) {
    console.log('remove: ' + recordId)
    }
    </script>
    """

    for record in records:
        content += '<div class="mo-card">'

        content += f'<img src="{record.preview_url}" alt="Preview Image" ' \
                   f'onerror="this.onerror=null; this.src=\'{_no_preview_image_url()}\';"/>'

        content += f'<div class="mo-card-blur-overlay-bottom">{_limit_card_name(record.name)}</div>'

        content += '<div class="mo-card-content-top">'
        content += f'<div class="mo-card-text-left"><span class="mo-badge {_model_type_css_class(record.model_type)}"' \
                   f'>{record.model_type.value}</span></div>'
        content += '</div>'

        content += '<div class="mo-card-hover">'
        content += '<div class="mo-card-hover-buttons">'

        content += '<button type="button" class="mo-btn mo-btn-success" '

        details = {
            'screen': 'record_details',
            'record_id': record.id_
        }
        details_json = html.escape(json.dumps(details))

        content += '<button type="button" class="mo-btn mo-btn-success" ' \
                   f'onclick="moJsonDelivery(\'{details_json}\')"">Details</button><br>'

        content += '<button type="button" class="mo-btn mo-btn-primary" ' \
                   f'onclick="handleDownloadClick(\'{record.id_}\')"">Download</button><br>'
        content += '<button type="button" class="mo-btn mo-btn-warning" ' \
                   f'onclick="handleEditClick(\'{record.id_}\')"">Edit</button><br>'
        content += '<button type="button" class="mo-btn mo-btn-danger" ' \
                   f'onclick="handleRemoveClick(\'{record.id_}\')">Remove</button><br>'

        content += '</div>'
        content += '</div>'

        content += '</div>'

    content += '</div>'
    return content
