import os 

from pathlib import Path
def write_file(path_to_file :str, content:str):
       "write a  file  in the sandbox  the  file  must  located  in sand box and the  file  must  be  python"
       
       if  not os.path.exists(path_to_file):
           raise Exception(f"path {path_to_file} does not exist")
       if "sandbox" not  in path_to_file :
               raise Exception("path to file  not valid")
       if  not path_to_file.endswith('.py'): 
           raise Exception(f"file {Path(path_to_file).name} format not  valid ")
       
       try:
           with open(path_to_file, 'w', encoding='utf-8') as file:
           file.write(content)
       except PermissionError as e
           raise PermissionError(f"No permission to write file {fullpath}: {e}")
       except Exception as e:
           raise Exception(f"Failed to write file {fullpath}: {e}")
           return False

       return True

     
       
     
