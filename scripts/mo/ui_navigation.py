import json
import random
import string

_HOME = 'home'
_DETAILS = 'details'
_EDIT = 'edit'
_REMOVE = 'remove'
_DOWNLOAD = 'download'
_IMPORT_EXPORT = 'import_export'
_DEBUG = 'debug'
_RECORD_INFO = 'record_info'

_NODE_SCREEN = 'screen'
_NODE_RECORD_ID = 'record_id'
_NODE_PREFILLED_JSON = 'prefilled_json'
_NODE_GROUP = 'group'
_NODE_RECORD_INFO_ID = 'record_info_id'

def navigate_home() -> str:
    return '{}'


def navigate_details(record_id) -> str:
    nav_dict = {
        _NODE_SCREEN: _DETAILS,
        _NODE_RECORD_ID: record_id
    }
    return json.dumps(nav_dict)


def navigate_add() -> str:
    nav_dict = {
        _NODE_SCREEN: _EDIT,
    }
    return json.dumps(nav_dict)


def navigate_edit(record_id) -> str:
    nav_dict = {
        _NODE_SCREEN: _EDIT,
        _NODE_RECORD_ID: record_id
    }
    return json.dumps(nav_dict)


def navigate_remove(record_id) -> str:
    nav_dict = {
        _NODE_SCREEN: _REMOVE,
        _NODE_RECORD_ID: record_id
    }
    return json.dumps(nav_dict)


def navigate_download_single(record_id) -> str:
    nav_dict = {
        _NODE_SCREEN: _DOWNLOAD,
        _NODE_RECORD_ID: record_id
    }
    return json.dumps(nav_dict)


def navigate_download_group(group) -> str:
    nav_dict = {
        _NODE_SCREEN: _DOWNLOAD,
        _NODE_GROUP: group
    }
    return json.dumps(nav_dict)


def get_nav_state(json_nav) -> dict:
    nav_dict = json.loads(json_nav)
    state = {
        'is_home_visible': False,
        'is_details_visible': False,
        'is_edit_visible': False,
        'is_remove_visible': False,
        'is_download_visible': False,
        'is_import_export_visible': False,
        'is_debug_visible': False,
        'details_record_id': '',
        'edit_data': {},
        'remove_record_id': '',
        'download_info': '',
        'filter_state': {},
        'details_record_info_id': ''
    }

    if nav_dict.get(_NODE_SCREEN) is None:
        state['is_home_visible'] = True
    else:
        if nav_dict[_NODE_SCREEN] == _DETAILS:
            state['is_details_visible'] = True
            state['details_record_id'] = nav_dict[_NODE_RECORD_ID]

        elif nav_dict[_NODE_SCREEN] == _EDIT:
            state['is_edit_visible'] = True
            edit_data = {'token': generate_ui_token()}
            if nav_dict.get(_NODE_RECORD_ID) is not None:
                edit_data[_NODE_RECORD_ID] = nav_dict[_NODE_RECORD_ID]
            if nav_dict.get(_NODE_PREFILLED_JSON) is not None:
                edit_data[_NODE_PREFILLED_JSON] = nav_dict[_NODE_PREFILLED_JSON]
            state['edit_data'] = json.dumps(edit_data)

        elif nav_dict[_NODE_SCREEN] == _REMOVE:
            state['is_remove_visible'] = True
            state['remove_record_id'] = nav_dict[_NODE_RECORD_ID]

        elif nav_dict[_NODE_SCREEN] == _DOWNLOAD:
            state['is_download_visible'] = True
            download_dict = {'token': generate_ui_token()}

            if nav_dict.get(_NODE_RECORD_ID) is not None:
                download_dict[_NODE_RECORD_ID] = nav_dict[_NODE_RECORD_ID]

            if nav_dict.get(_NODE_GROUP) is not None:
                download_dict[_NODE_GROUP] = nav_dict[_NODE_GROUP]

            if nav_dict.get('filter_state') is not None:
                download_dict['filter_state'] = nav_dict['filter_state']

            state['download_info'] = json.dumps(download_dict)

        elif nav_dict[_NODE_SCREEN] == _IMPORT_EXPORT:
            state['is_import_export_visible'] = True
            state['filter_state'] = nav_dict['filter_state']
        elif nav_dict[_NODE_SCREEN] == _DEBUG:
            state['is_debug_visible'] = True
        elif nav_dict[_NODE_SCREEN] == _RECORD_INFO:
            state['details_record_info_id'] = nav_dict[_NODE_RECORD_INFO_ID]
            state['is_home_visible'] = True

    return state


def get_download_record_id(data):
    download_dict = json.loads(data)
    if download_dict.get(_NODE_RECORD_ID) is None:
        return None
    else:
        return download_dict[_NODE_RECORD_ID]


def get_download_group(data):
    download_dict = json.loads(data)
    if download_dict.get(_NODE_GROUP) is None:
        return None
    else:
        return download_dict[_NODE_GROUP]


def get_download_filter_state(data):
    download_dict = json.loads(data)
    if download_dict.get('filter_state') is None:
        return None
    else:
        return download_dict['filter_state']


def generate_ui_token() -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))
