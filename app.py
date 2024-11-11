import os
import paramiko
from google.cloud import storage, secretmanager
from flask import Flask

app = Flask(__name__)

def access_secret_version(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')

@app.route('/', methods=['GET'])
def transfer_files():
    # Récupérer les informations d'authentification depuis Secret Manager
    sftp_host = access_secret_version('sftp-host')
    sftp_username = access_secret_version('sftp-username')
    sftp_password = access_secret_version('sftp-password')

    # Configuration du bucket GCS
    bucket_name = f'sftp-transfer-bucket-{os.environ["GOOGLE_CLOUD_PROJECT"]}'

    # Connexion au serveur SFTP
    transport = paramiko.Transport((sftp_host, 22))
    transport.connect(username=sftp_username, password=sftp_password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    # Liste des fichiers dans le répertoire distant
    remote_directory = '.'
    files = sftp.listdir(remote_directory)

    # Initialiser le client GCS
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Transférer chaque fichier
    for file_name in files:
        remote_file_path = f'{remote_directory}/{file_name}'
        print(f'Téléchargement du fichier {remote_file_path}')
        with sftp.open(remote_file_path, 'rb') as remote_file:
            blob = bucket.blob(file_name)
            blob.upload_from_file(remote_file)
            print(f'Fichier {file_name} uploadé dans le bucket {bucket_name}')

    # Fermer la connexion SFTP
    sftp.close()
    transport.close()

    return 'Transfert terminé', 200
