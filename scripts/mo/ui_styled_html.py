from typing import List

from scripts.mo.models import Record, ModelType
from scripts.mo.environment import env


def alert_danger(value) -> str:
    if isinstance(value, list):
        text = "<br>".join(value)
    else:
        text = value
    return f'<div id="mo-alert-danger">{text}</div>'


def _limit_description(text):
    if text and len(text) > 600:
        return text[:600] + '...'
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


def _no_preview_image_path() -> str:
    return f'./pic/no-preview.png'


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
        table_html += f'<img class="preview-image" src="{_no_preview_image_path()}" ' \
                      f'alt="Preview image"' \
                      f' onerror="this.onerror=null; this.src=\'{_no_preview_image_path()}\';">'
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
