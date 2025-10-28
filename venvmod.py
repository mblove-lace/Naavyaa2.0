# import os
# import subprocess
# import sys
 
 
# # Get the project root directory where this script is located........................................................................
# project_root_dir = os.getcwd()  
# # os.getcwd basically fetched the current working directory locating teh path of this python script 'Flask_Tutorial_Code_With_Josh_Feb12'
# print(f"Project root directory: {project_root_dir}")
 
 
 
# # Change the working directory to the project directory...............................................................................
# os.chdir(project_root_dir)
# print(f"Changed working directory to: {project_root_dir}")
 
 
 
# # Define virtual environment name.......................................................................................................
# venv_name = "venv2trial"
 
 
# # Windows Python Program Path............................................................................................................
# python_path = r"C:\Users\moith\AppData\Local\Microsoft\WindowsApps\python.exe"
 
 
 
# # Create the virtual environment path..........................................................................................................
# venv_path = os.path.join(project_root_dir, venv_name)
# # Defining venv folder path by simply joing in project root directory path "C:/Onedrive/user/project" to "venv_name"
# # to get venv_path = "C:/Onedrive/user/project/venv_name"
 
 
 
 
# # Create new venv only if it doesnt already exist..........................................................................................
# if not os.path.exists(venv_path):
   
#     # Here, our python installation path in windows is at python path = “C:\Users\shoud\AppData\Local\Programs\Python\Python311\python.exe “
#     # And we want to create teh venv folder in 'venv path'
#     # This is the code we run in Terminal to create a new venv "C:\Users\shoud\AppData\Local\Programs\Python\Python311\python.exe -m venv "venv_name"
#     subprocess.run([python_path, "-m", "venv", venv_path], check=True)
#     print(f"\n✅ Connected to python path: {python_path}")
#     print(f"\n✅ Created virtual environment: {venv_name}")
 
   
# else:
#     print(f"\n⚠️ Virtual environment {venv_name} already exists.")
 
 
 
 
# # Activate the created virtual environment................................................................................................
# # This is the code we run in Terminal to actiavte new venv " 'venv_name'\Scripts\activate "
# activate_script = os.path.join(venv_path, "Scripts", "activate")
# print(f"\n✅ Activated {venv_name}")
# # Define path for pip installation
# pip_executable = os.path.join(venv_path, "Scripts", "pip")
 
 
 
 
 
# # Install dependencies from requirements.txt..............................................................................................
# # Defining the requirements.txt file path  
# requirements_file_path = os.path.join(project_root_dir, "requirements.txt")
 
# if os.path.exists(requirements_file_path):
#     #  Code to install packages from 'requirements.txt' file in Terminal : pip install -r requirements.txt
#     subprocess.run([pip_executable, "install", "-r", requirements_file_path], check=True)
#     print("\n✅ Installed packages from requirements.txt")
   
# else:
#     print("\n⚠️ requirements.txt not found !")
 
 
 
# # Printing out the list of packages installe din the created venv..........................................................................
# print("\n📦 Installed packages in the virtual environment:")
# result = subprocess.run([pip_executable, "list"], capture_output=True, text=True)
 
 
# # Print the actual list of installed packages..............................................................................................
# print(result.stdout)
 
 
 
# # Run `pip freeze` inside the virtual environment and save output to requirements.txt for using it for future references....................
# with open(requirements_file_path, "w") as req_file:
#     subprocess.run([pip_executable, "freeze"], stdout=open(requirements_file_path, "w"), check=True)
   
   
   
# # # Install Jupyter in the Virtual Environment................................................................................................
# # # We are doing this step because we want to run a VSCode Jupyter Notebook Python kernel
# # subprocess.run([python_path , "-m", "pip", "install", "jupyter"])
# # print("✅ Jupyter installed successfully.")
 
# # # Add Virtual Environment to Jupyter as a Kernel..................................................................................
# # # We are doing this step because we want to run a VSCode Jupyter Notebook Python kernel
# # subprocess.run([python_path , "-m", "ipykernel", "install", "--user", "--name", venv_name, "--display-name", f"Python ({venv_name})"])
# # print("✅ Virtual environment added as a Jupyter kernel.")
 
# # print(f"\n🎉 Setup Complete! Restart VSCode and select 'Python ", venv_name ," in Jupyter !")
 