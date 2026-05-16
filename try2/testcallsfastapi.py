import requests

# URL of your running FastAPI server
url = "http://127.0.0.1:8000/upload/"

# Path to the image you want to send
file_path = r"C:/Users/buste/OneDrive/Documents/GitHub/TeamRocket/try2/151zard.jpg"

# Open the file and send as multipart/form-data
with open(file_path, "rb") as f:
    files = {"file": (file_path, f, "image/jpeg")}
    response = requests.post(url, files=files)

# Print the JSON response
print(response.json())
