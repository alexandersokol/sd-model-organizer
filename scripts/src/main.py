# from typing import List
#
# import gradio as gr
# import sys
#
# from scripts.mo.models import Record
# from scripts.mo.notion_repository import NotionRepository
#
# # from Lora import lora
#
# from modules import ui_extra_networks, shared, paths, sd_models, sd_samplers, shared, extensions
#
# # repository = NotionRepository("", "")
#
#
# css_styles = f"""
#     <style>
#     {open('style.css', 'r').read()}
#     </style>
# """
#
#
# def generate_table(records: List[Record]):
#     table_html = ""
#     # print("styles: ", css_styles)
#     # table_html += css_styles
#     table_html += '<div class="table">'
#
#     # Add table headers
#     table_html += '<div class="table-row table-header">'
#     table_html += '<div class="table-cell picture-column">Preview</div>'
#     table_html += '<div class="table-cell title-column">Title</div>'
#     table_html += '<div class="table-cell description-column">Type</div>'
#     table_html += '<div class="table-cell actions-column">Actions</div>'
#     table_html += '</div>'
#
#     for record in records:
#         name = record.name
#         type_ = record.type_
#         preview_url = record.previewUrl
#
#         # Add row
#         table_html += '<div class="table-row">'
#
#         # Add preview URL column
#         table_html += f'<div class="table-cell picture-column"><img class="preview-image" src="{preview_url}" alt' \
#                       f'="Preview image"></div>'
#
#         # Add name column
#         table_html += f'<div class="table-cell title-column">'
#         table_html += f'<button class="button-name" onclick="handleClick(\'{name}\')">{name}</button>'
#         table_html += '</div>'
#
#         # Add type column
#         table_html += f'<div class="table-cell description-column">{type_}</div>'
#
#         # Add actions column
#         table_html += '<div class="table-cell actions-column">'
#         table_html += '<button class="button-action button-download">Download</button>'
#         table_html += '<button class="button-action button-remove">Remove</button>'
#         table_html += '</div>'
#         # Close row
#         table_html += '</div>'
#     # Close table
#     table_html += '</div>'
#     return table_html
#
#
# # def get_models():
# #     return sorted([x.title for x in sd_models.checkpoints_list.values()])
#
#
# # def get_embeddings():
# #     return sorted([f'{v} ({sd_hijack.model_hijack.embedding_db.word_embeddings[v].vectors})' for i, v in enumerate(sd_hijack.model_hijack.embedding_db.word_embeddings)])
#
# # def get_loras():
# #     loras = []
# #     try:
# #         sys.path.append(extensions.extensions_builtin_dir)
# #         from Lora import lora
# #         loras = sorted([l for l in lora.available_loras.keys()])
# #     except:
# #         pass
# #     return loras
#
# def load_data():
#     repository = NotionRepository(shared.opts.mo_notion_api_token, shared.opts.mo_notion_db_id)
#     records = repository.fetch_data()
#     # 'hypernetworks': [name for name in shared.hypernetworks],
#     # shared.opts.wildcards_same_seed else
#
#     print("------")
#     print("mo_storage: ", shared.opts.mo_storage)
#     print("mo_notion_api_token: ", shared.opts.mo_notion_api_token)
#     print("mo_notion_db_id: ", shared.opts.mo_notion_db_id)
#     print("mo_model_path: ", shared.opts.mo_model_path)
#     print("mo_vae_path: ", shared.opts.mo_vae_path)
#     print("mo_lora_path: ", shared.opts.mo_lora_path)
#     print("mo_hypernetworks_path: ", shared.opts.mo_hypernetworks_path)
#     print("mo_embeddings_path: ", shared.opts.mo_embeddings_path)
#     print("------")
#
#     return generate_table(records)
#
#
# def get_main_ui_block():
#     with gr.Blocks() as main_ui_block:
#         gr.HTML(css_styles)
#         html = gr.HTML()
#         load_button = gr.Button("Load")
#         load_button.click(load_data, outputs=html)
#
#     return main_ui_block
