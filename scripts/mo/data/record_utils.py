import json
import os
from typing import List, Dict

from scripts.mo.data.mapping_utils import create_version_dict
from scripts.mo.environment import env
from scripts.mo.models import ModelSort, Record, ModelType
from scripts.mo.utils import get_model_files_in_dir, find_info_file, find_info_json_file


def _sort_records(records: List, sort_order: ModelSort, sort_downloaded_first: bool) -> List:
    if sort_downloaded_first:
        if sort_order == ModelSort.TIME_ADDED_ASC:
            sorted_records = sorted(records,
                                    key=lambda r: (not (bool(r.location) and os.path.exists(r.location)), r.created_at))
        elif sort_order == ModelSort.TIME_ADDED_DESC:
            sorted_records = sorted(records,
                                    key=lambda r: (bool(r.location) and os.path.exists(r.location), r.created_at),
                                    reverse=True)
        elif sort_order == ModelSort.NAME_ASC:
            sorted_records = sorted(records,
                                    key=lambda r: (not (bool(r.location) and os.path.exists(r.location)), r.name))
        elif sort_order == ModelSort.NAME_DESC:
            sorted_records = sorted(records, key=lambda r: (bool(r.location) and os.path.exists(r.location), r.name),
                                    reverse=True)
        else:
            raise ValueError(f'An unhandled sort_order value: {sort_order.value}')
    else:
        if sort_order == ModelSort.TIME_ADDED_ASC:
            sorted_records = sorted(records, key=lambda record: record.created_at)
        elif sort_order == ModelSort.TIME_ADDED_DESC:
            sorted_records = sorted(records, key=lambda record: record.created_at, reverse=True)
        elif sort_order == ModelSort.NAME_ASC:
            sorted_records = sorted(records, key=lambda record: record.name)
        elif sort_order == ModelSort.NAME_DESC:
            sorted_records = sorted(records, key=lambda record: record.name, reverse=True)
        else:
            raise ValueError(f'An unhandled sort_order value: {sort_order.value}')
    return sorted_records


def _find_local_model_files() -> List:
    result = []

    def search_in_dir(model_type) -> List:
        dir_path = env.get_model_path(model_type)
        return get_model_files_in_dir(dir_path)

    result.extend(search_in_dir(ModelType.CHECKPOINT))
    result.extend(search_in_dir(ModelType.VAE))
    result.extend(search_in_dir(ModelType.LORA))
    result.extend(search_in_dir(ModelType.HYPER_NETWORK))
    result.extend(search_in_dir(ModelType.EMBEDDING))
    result.extend(search_in_dir(ModelType.LYCORIS))

    return result


def _create_model_from_info_file(path, info_file_path, model_type):
    with open(info_file_path) as file:
        json_data = json.load(file)
    version_dict = create_version_dict(json_data)
    filename = os.path.basename(path)
    return Record(
        id_=None,
        name=filename,
        model_type=model_type,
        location=path,
        created_at=os.path.getctime(path),
        download_filename=filename,
        download_path=os.path.dirname(path),
        preview_url=version_dict['images'][0][0],
        download_url=version_dict['files'][0]['download_url'],
        sha256_hash=version_dict['files'][0]['sha256'],
        positive_prompts=version_dict['trained_words']
    )


def _create_model_from_local_file(path, model_type):
    filename = os.path.basename(path)
    record = Record(
        id_=None,
        name=filename,
        model_type=model_type,
        location=path,
        created_at=os.path.getctime(path),
        download_filename=filename,
        download_path=os.path.dirname(path)
    )
    jsonFile = find_info_json_file(path)
    if jsonFile:
        try:
            jsontxt = open(jsonFile)
            jsonobj = json.load(jsontxt)
            if ("activation text" in jsonobj) and (env.prefill_pos_prompt()):
                record.positive_prompts = jsonobj["activation text"]
            if ("negative text" in jsonobj) and (env.prefill_neg_prompt()):  
                record.negative_prompts = jsonobj["negative text"]
            if("preferred weight" in jsonobj):
                record.weight = jsonobj["preferred weight"]
            jsontxt.close()    
        except Exception as ex:
            jsontxt.close()
    return record


def _get_model_type_from_file(path):
    if env.get_model_path(ModelType.CHECKPOINT) in path:
        return ModelType.CHECKPOINT
    elif env.get_model_path(ModelType.VAE) in path:
        return ModelType.VAE
    elif env.get_model_path(ModelType.LORA) in path:
        return ModelType.LORA
    elif env.get_model_path(ModelType.HYPER_NETWORK) in path:
        return ModelType.HYPER_NETWORK
    elif env.get_model_path(ModelType.EMBEDDING) in path:
        return ModelType.EMBEDDING
    elif env.get_model_path(ModelType.LYCORIS) in path:
        return ModelType.LYCORIS
    return None


def _create_record_from_file(model_file_path):
    model_type = _get_model_type_from_file(model_file_path)

    info_file = find_info_file(model_file_path)

    if info_file is None:
        return _create_model_from_local_file(model_file_path, model_type)
    try:
        return _create_model_from_info_file(model_file_path, info_file, model_type)
    except Exception as ex:
        return _create_model_from_local_file(model_file_path, model_type)


def _create_record_from_files(model_file_list):
    result = []
    for file in model_file_list:
        rec = _create_record_from_file(file)
        if rec is not None:
            result.append(rec)
    return result


def _filter_records_by_state(records: List, state: Dict):
    if state['query']:
        records = list(filter(lambda r: state['query'].lower() in r.name.lower(), records))

    groups = state['groups']
    if len(groups) > 0:
        records = list(filter(lambda r: all(group in r.groups for group in groups), records))

    model_types = state['model_types']
    if len(model_types) > 0:
        records = list(filter(lambda r: r.model_type.value in model_types, records))

    return records


def load_records_and_filter(state: Dict, include_local_files: bool):
    records = env.storage.query_records(
        name_query=state['query'],
        groups=state['groups'],
        model_types=state['model_types'],
        show_downloaded=state['show_downloaded'],
        show_not_downloaded=state['show_not_downloaded']
    )

    if state['show_local_files'] and include_local_files:
        model_files_list = _find_local_model_files()

        if len(model_files_list) > 0:
            bound_files = env.storage.get_all_records_locations()
            bound_files = list(filter(lambda r: bool(r), bound_files))
            not_bound_files = list(filter(lambda r: r not in bound_files, model_files_list))
            if len(not_bound_files) > 0:
                local_records = _create_record_from_files(not_bound_files)
                local_records = _filter_records_by_state(local_records, state)
                if len(local_records) > 0:
                    records.extend(local_records)

    records = _sort_records(
        records=records,
        sort_order=ModelSort.by_value(state['sort_order']),
        sort_downloaded_first=state['sort_downloaded_first']
    )
    return records
