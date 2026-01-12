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
              content = file.read();
     
      
       
       return content
def read_dir(path_to_dir:str):
       content={}
       path = Path(path_to_dir)
       if not path.is_dir():
         raise Exception(f"{path_to_dir} is not a valid directory")
       for file_path in path.rglob("*.py"):
        try:
            content[str(file_path)] = read_file(path_to_dir, file_path.name)
        except Exception as e:
            content[str(file_path)] = f"ERROR: {e}"

       return content
