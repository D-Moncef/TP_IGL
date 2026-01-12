import os 

from pathlib import Path
def write_file(path_to_file :str,file_name:str, content:str):
       "write a  file  in the send box  the  file  must  located  in sand box and the  file  must  be  python"
       fullpath=os.path.join(path_to_file,file_name)
        
       if  not os.path.exists(path_to_file):
           raise Exception(f"path {path_to_file} does not exist")
       if "sendbox" not  in fullpath :
               raise Exception("path to file  not valid")
       if  not file_name.endswith('.py'): 
           raise Exception("file {file_name} format not  valid ")
       
       try:
        with open(fullpath, 'w', encoding='utf-8') as file:
           file.write(content)
       except Exception as e:
         print(f"Failed to write file {fullpath}: {e}")
         return False

       return True
content="# yo)\n"
write_file("/home/yacineyo/refactoring-swarm-template/sendbox","c.py",content)
     
       
     