import json

_HOME = 'home'
_DETAILS = 'details'
_EDIT = 'edit'
_REMOVE = 'remove'

_NODE_SCREEN = 'screen'
_NODE_RECORD_ID = 'record_id'


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


def get_nav_state(json_nav) -> dict:
    nav_dict = json.loads(json_nav)
    state = {
        'is_home_visible': False,
        'is_details_visible': False,
        'is_edit_visible': False,
        'is_remove_visible': False,
        'details_record_id': '',
        'edit_record_id': '',
        'remove_record_id': ''
    }

    if nav_dict.get(_NODE_SCREEN) is None:
        state['is_home_visible'] = True
    else:
        if nav_dict[_NODE_SCREEN] == _DETAILS:
            state['is_details_visible'] = True
            state['details_record_id'] = nav_dict[_NODE_RECORD_ID]

        elif nav_dict[_NODE_SCREEN] == _EDIT:
            state['is_edit_visible'] = True
            if nav_dict.get('record_id') is not None:
                state['edit_record_id'] = nav_dict[_NODE_RECORD_ID]

        elif nav_dict[_NODE_SCREEN] == _REMOVE:
            state['is_remove_visible'] = True
            state['remove_record_id'] = nav_dict[_NODE_RECORD_ID]

    return state
