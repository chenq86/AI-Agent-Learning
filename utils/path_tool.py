"""
Provide consistent absolute paths throughout the project.
"""

import os

def get_project_root() -> str:
    """
    Get the project root directory.
    :return:Project root as a string
    """
    #Absolute path of the current file
    current_file = os.path.abspath(__file__)
    #Get the file directory before resolving the project root
    current_dir = os.path.dirname(current_file)
    #Get the project root directory
    project_root = os.path.dirname(current_dir)

    return project_root


def get_abs_path(relative_path: str) -> str:
    """
    Convert a relative path into an absolute path.
    :param relative_path:Relative path
    :return: Absolute path
    """
    projet_root = get_project_root()
    return os.path.join(projet_root, relative_path)


if __name__ == "__main__":
    print(get_abs_path("config/config.txt"))