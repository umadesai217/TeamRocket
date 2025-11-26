# TeamRocket

## Environment setup instructions
- Install VS code
You can use any other IDE that supports python and HTML VS code is recommended. https://code.visualstudio.com/

- Install Python Plugins
Install the Python plugins if required for your IDE

- Install Python
The version used here is 3.10 for best compatibility https://www.python.org/downloads/

### Frontend
- Install docker https://www.docker.com/products/docker-desktop/
  
- Install node.js https://nodejs.org/en/download
  (necessary for Vue.js)

### ML - model 
- Installing dependencies
Once you install python and pip run this command in the terminal:

`pip install torch faiss-cpu numpy Pillow ultralytics easyocr python-dotenv git+https://github.com/openai/CLIP.git`

This will install all dependencies required for the project

### Development
- Install node.js [https://www.docker.com/products/docker-desktop/](https://nodejs.org/en/download)
  
- Once installed, download the TeamRocket folder.
  
- Open the terminal, path to the folder, and run these commands:
  'npm init -y'
  'npm install @supabase/supabase-js'
  'node populate-db.js'
