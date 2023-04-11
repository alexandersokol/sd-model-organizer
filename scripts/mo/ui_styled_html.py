from typing import List

from scripts.mo.models import Record


def alert_danger(value) -> str:
    if isinstance(value, list):
        text = "<br>".join(value)
    else:
        text = value
    return f'<div id="mo-alert-danger">{text}</div>'


def records_table(records: List[Record]) -> str:
    table_html = '<div class="table">'
    table_html += '<div class="table-row table-header">'
    table_html += '<div class="table-cell picture-column">Preview</div>'
    table_html += '<div class="table-cell title-column">Title</div>'
    table_html += '<div class="table-cell description-column">Type</div>'
    table_html += '<div class="table-cell actions-column">Actions</div>'
    table_html += '</div>'
    for record in records:
        name = record.name
        type_ = record.model_type.value
        preview_url = record.preview_url

        # Add row
        table_html += '<div class="table-row">'

        # Add preview URL column
        table_html += f'<div class="table-cell picture-column"><img class="preview-image" src="{preview_url}" alt' \
                      f'="Preview image"></div>'

        # Add name column
        table_html += f'<div class="table-cell title-column">'
        table_html += f'<button class="button-name" onclick="handleClick(\'{name}\')">{name}</button>'
        table_html += '</div>'

        # Add type column
        table_html += f'<div class="table-cell description-column">{type_}</div>'

        # Add actions column
        table_html += '<div class="table-cell actions-column">'
        table_html += '<button class="button-action button-download">Download</button>'
        table_html += '<button class="button-action button-remove">Remove</button>'
        table_html += '</div>'
        # Close row
        table_html += '</div>'
    # Close table
    table_html += '</div>'
    return table_html
