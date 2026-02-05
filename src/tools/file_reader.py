import os 
from pathlib import Path
def read_file(path_to_file :str,file_name:str ):
       "read a  file  in the send box  the  file  must  located  in sand box and the  file  must  be  python"
       fullpath=os.path.join(path_to_file,file_name)
       if "sendbox" not  in fullpath :
               raise Exception("path to file  not valid")
       if  not file_name.endswith('.py'): 
           raise Exception("file {file_name} format not  valid ")
       
       with open(fullpath, 'r') as file:
              content = file.read()
     
      
       
       return content
def read_dir(path_to_dir:str):
       content={}
       path = Path(path_to_dir)
       if not path.is_dir():
         raise FileNotFoundError(f"{path_to_dir} is not a valid directory")
       for file_path in path.rglob("*.py"):
           try:
               content[str(file_path)] = read_file(path_to_dir, file_path.name)
           except FileNotFoundError as e:
                raise
           except PermissionError as e:
                raise

       return content

def read_dir_separate(path_to_dir: str):
    content = {"source_files": {}, "test_files": {}}
    path = Path(path_to_dir)

    if not path.is_dir():
        raise FileNotFoundError(f"{path_to_dir} is not a valid directory")

    for file_path in path.rglob("*.py"):
        try:
            file_content = read_file(path_to_dir, file_path.name)  # your existing read_file function
            
            # Decide if it is a test file
            if "test" in file_path.stem.lower() or "tests" in file_path.parts:
                content["test_files"][str(file_path)] = file_content
            else:
                content["source_files"][str(file_path)] = file_content

        except FileNotFoundError:
            raise
        except PermissionError:
            raise

    return content
