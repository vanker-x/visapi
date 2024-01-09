import inspect


def get_obj_file(obj, depth=-1) -> str:
    """
    Retrieve the file path associated with the given object, and this
    function aims to identify and return the file path where the specified object is located.
    :param obj: target object
    :param depth: stack depth
    :return: string filepath or "Unknow"
    """
    try:
        return inspect.getfile(obj)
    except Exception as e:
        possible_location = ["Unknown"]
        current_filepath = __file__
        frame = inspect.currentframe()
        while frame and depth:
            for v in frame.f_locals.values():
                if v is not obj:
                    continue
                target_filepath = frame.f_globals.get("__file__", "Unknown")
                if not target_filepath == current_filepath:
                    possible_location.append(target_filepath)
            frame = frame.f_back
            depth -= 1
        return possible_location[-1]
