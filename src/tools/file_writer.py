import os 

from pathlib import Path
def write_file(path_to_file :str, content:str, test : bool):
    "write a  file  in the sandbox  the  file  must  located  in sand box and the  file  must  be  python"

        if "sandbox" not  in path_to_file :
            raise Exception("path to file  not valid")
        if not path_to_file.endswith('.py'): 
            raise Exception(f"file {Path(path_to_file).name} format not  valid ")
              
        if not test:
           if  not os.path.exists(path_to_file):
               raise Exception(f"path {path_to_file} does not exist")
        else
           if not (Path(path_to_file).name.startswith("test_") or Path(path_to_file).name.endswith("_test.py")):
               raise Exception(f"path {path_to_file} is not a valid test file path")
           Path(path_to_file).parent.mkdir(parents=True, exist_ok=True)
       
       try:
           with open(path_to_file, 'w', encoding='utf-8') as file:
           file.write(content)
       except PermissionError as e
           raise PermissionError(f"No permission to write file {fullpath}: {e}")
       except Exception as e:
           raise Exception(f"Failed to write file {path_to_file}: {e}")
           return False

       return True

     
       
     
