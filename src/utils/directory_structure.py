import os

def export_directory_structure(directory_path: str = None, export_path: str = None) -> None:
    """
    Exports directory structure recursively of a given path to a file
    
    Parameters
        directory_path(str): path to directory to traverse
        export_path(str): path to file to store the traveresed directory tree structure
    """
    if directory_path is None:
        directory_path = str(input("Enter path to directory whose structre is required: "))
        export_path = str(input("Enter path to file to save the directory structure: "))
    with open(export_path,"w+") as f:
        prefix = "|_ "
        for root, dirs, files in os.walk(directory_path):
            path = root.split(os.sep)
            abs_path = os.path.abspath(root)
            f.write("  " * (len(path)-1) + prefix + abs_path + '\n')
            print("Traversing {dirpath}".format(dirpath=abs_path))
            if len(abs_path.split('.')[-1]) > 1:
                continue
            for file in files:
                f.write("  " * (len(path)) + prefix + file + '\n')
    return None

if __name__ == "__main__":
    export_directory_structure()