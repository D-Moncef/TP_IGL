import os
def analyse_file(path_to_file:str):
       "analyse a python file using pylint and return the report as string"
       if  not os.path.exists(path_to_file):
           raise Exception(f"path {path_to_file} does not exist")
       if  not path_to_file.endswith('.py'): 
           raise Exception("file {path_to_file} format not  valid ")  
       try:
            os.system("pylint "+path_to_file+" > pylint_report.txt")
            with open("pylint_report.txt", "r") as f:
                report = f.read()
                informations={
                     "score":report.split("Your code has been rated at ")[1].split("/10")[0].strip(),
                     "details":report
                     
                 }
                os.remove("pylint_report.txt")

            return informations
       except Exception as e:
            print(f"Failed to analyse file {path_to_file}: {e}")
            return None
