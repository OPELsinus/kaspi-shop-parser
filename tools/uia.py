def find_elements(timeout=30, **selector):
    from pywinauto.controls.uiawrapper import UIAWrapper
    from pywinauto.findwindows import find_elements
    from pywinauto.timings import wait_until_passes

    selector['top_level_only'] = selector['top_level_only'] if 'top_level_only' in selector else False

    def func():
        all_elements = find_elements(backend="uia", **selector)
        all_elements = [e for e in all_elements if e.control_type]
        all_elements = [UIAWrapper(e) for e in all_elements]
        if not len(all_elements):
            raise Exception('not found')
        return all_elements

    return wait_until_passes(timeout, 0.05, func)


if __name__ == '__main__':
    print(find_elements(30, **{
        "title": "Пуск", "class_name": "Start", "control_type": "Button",
        "visible_only": True, "enabled_only": True, "found_index": 0
    }))
