import os
import inspect
import typing as t


def get_obj_file(
        obj: t.Any,
        depth: t.Optional[int] = -1,
        project_dir: t.Optional[t.Union[str, os.PathLike]] = None
) -> str:
    """
    Retrieve the file path associated with the given object, and this
    function aims to identify and return the file path where the specified object is located.
    :param obj: target object
    :param depth: stack depth
    :param project_dir: only find child file of the project_dir
    :return: string filepath or "Unknow"
    """
    try:
        return inspect.getfile(obj)
    except Exception as e:
        possible_location = ["Unknown"]
        frame = inspect.currentframe()
        project_dir = str(project_dir)
        while depth:
            depth -= 1
            frame = frame.f_back
            if not frame:
                break
            target_filepath = frame.f_globals["__file__"]
            if project_dir and not os.path.commonprefix([project_dir, target_filepath]) == project_dir:
                continue

            for v in frame.f_locals.values():
                if v is not obj:
                    possible_location.append(target_filepath)
        return possible_location[-1]
