from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

# Path to your CSV file
CSV_FILE_PATH = r"D:\ras_sh\waypoints.csv"

# Authenticate and create Google Drive client
gauth = GoogleAuth()

# Try to load saved client credentials
gauth.LoadCredentialsFile("credentials.json")

if gauth.credentials is None:
    # Authenticate if no credentials are available
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh credentials if expired
    gauth.Refresh()
else:
    # Initialize the saved credentials
    gauth.Authorize()

# Save the current credentials to a file
gauth.SaveCredentialsFile("credentials.json")

drive = GoogleDrive(gauth)

# Upload the CSV file to Google Drive
file_name = os.path.basename(CSV_FILE_PATH)
gfile = drive.CreateFile({'title': file_name})
gfile.SetContentFile(CSV_FILE_PATH)
gfile.Upload()

print(f"File '{file_name}' uploaded to Google Drive.")