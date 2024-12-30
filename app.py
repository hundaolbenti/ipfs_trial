from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import requests
import os
import json
import secrets
from cryptography.fernet import Fernet
from pathlib import Path
from io import BytesIO

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Local IPFS API endpoint
IPFS_API = "http://127.0.0.1:5001"

# Generate or load encryption key
KEY_FILE = "encryption.key"
def get_encryption_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return key

def encrypt_file(file_path, key):
    f = Fernet(key)
    with open(file_path, 'rb') as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    encrypted_path = file_path + '.encrypted'
    with open(encrypted_path, 'wb') as file:
        file.write(encrypted_data)
    return encrypted_path

def decrypt_file(encrypted_data, key):
    f = Fernet(key)
    return f.decrypt(encrypted_data)

def upload_to_ipfs(file_path):
    try:
        # Read file content
        with open(file_path, 'rb') as f:
            files = {'file': f}
            # Upload to local IPFS node
            response = requests.post(f'{IPFS_API}/api/v0/add?pin=true', files=files)
            if response.status_code != 200:
                print(f"Error response from IPFS: {response.text}")
                return None
            
            result = response.json()
            ipfs_hash = result['Hash']
            
            # Explicitly pin the file
            pin_response = requests.post(f'{IPFS_API}/api/v0/pin/add?arg={ipfs_hash}')
            if pin_response.status_code != 200:
                print(f"Warning: Could not pin file: {pin_response.text}")
            
            return ipfs_hash
    except Exception as e:
        print(f"Error uploading to IPFS: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    try:
        # Save file temporarily
        temp_path = os.path.join('temp', file.filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_path)

        # Encrypt the file
        key = get_encryption_key()
        encrypted_path = encrypt_file(temp_path, key)

        # Upload encrypted file to IPFS
        ipfs_hash = upload_to_ipfs(encrypted_path)
        if ipfs_hash is None:
            flash('Error uploading to IPFS. Make sure IPFS Desktop is running!', 'error')
            return redirect(url_for('index'))

        # Clean up temp files
        os.remove(temp_path)
        os.remove(encrypted_path)

        # Store the mapping of hash to original filename
        filename_mapping = {}
        if os.path.exists('filename_mapping.json'):
            with open('filename_mapping.json', 'r') as f:
                filename_mapping = json.load(f)
        
        filename_mapping[ipfs_hash] = file.filename
        with open('filename_mapping.json', 'w') as f:
            json.dump(filename_mapping, f)

        flash(f'File uploaded successfully! IPFS Hash: {ipfs_hash}', 'success')
        flash('Your file has been encrypted and uploaded securely.', 'info')
        return redirect(url_for('index'))

    except Exception as e:
        flash(f'Error uploading file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<hash>')
def download_file(hash):
    try:
        # Get the file from IPFS
        response = requests.post(f'{IPFS_API}/api/v0/cat?arg={hash}')
        if response.status_code != 200:
            flash('Error downloading file from IPFS', 'error')
            return redirect(url_for('list_files'))

        try:
            # Decrypt the file
            key = get_encryption_key()
            decrypted_data = decrypt_file(response.content, key)

            # Get original filename
            filename = hash
            if os.path.exists('filename_mapping.json'):
                with open('filename_mapping.json', 'r') as f:
                    mapping = json.load(f)
                    if hash in mapping:
                        filename = mapping[hash]

            # Send the decrypted file
            return send_file(
                BytesIO(decrypted_data),
                download_name=filename,
                as_attachment=True
            )
        except Exception as e:
            flash(f'Error decrypting file. Make sure you have the correct encryption key: {str(e)}', 'error')
            return redirect(url_for('list_files'))

    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('list_files'))

@app.route('/files')
def list_files():
    try:
        # Get list of pinned files
        response = requests.post(f'{IPFS_API}/api/v0/pin/ls')
        if response.status_code == 200:
            pins = response.json()
            # Format the pins data for the template
            formatted_pins = {}
            
            # Load filename mapping
            filename_mapping = {}
            if os.path.exists('filename_mapping.json'):
                with open('filename_mapping.json', 'r') as f:
                    filename_mapping = json.load(f)
            
            for hash_key, pin_info in pins['Keys'].items():
                formatted_pins[hash_key] = {
                    'type': pin_info['Type'],
                    'filename': filename_mapping.get(hash_key, 'Unknown File'),
                    'download_url': url_for('download_file', hash=hash_key)
                }
            return render_template('files.html', pins=formatted_pins)
        else:
            flash('Error getting pinned files', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure temp directory exists
    os.makedirs('temp', exist_ok=True)
    
    # Check if IPFS is running
    try:
        response = requests.post(f'{IPFS_API}/api/v0/version')
        if response.status_code == 200:
            print("Successfully connected to IPFS")
        else:
            print("Warning: IPFS seems to be not responding correctly")
    except Exception as e:
        print("Warning: Could not connect to IPFS. Please make sure IPFS Desktop is running!")
    
    app.run(debug=True)
