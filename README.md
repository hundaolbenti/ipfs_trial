# IPFS File Uploader

A simple web application that allows you to upload files to IPFS and view them through an IPFS gateway.

## Prerequisites

1. Python 3.7 or higher
2. IPFS daemon running locally

## Setup Instructions

1. Install IPFS on your system if you haven't already:
   - Visit https://docs.ipfs.tech/install/ipfs-desktop/
   - Download and install IPFS Desktop for your operating system

2. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the IPFS daemon:
   - Launch IPFS Desktop application
   - Make sure the IPFS daemon is running

4. Run the Flask application:
   ```bash
   python app.py
   ```

5. Open your web browser and visit:
   ```
   http://localhost:5000
   ```

## Usage

1. Click the "Choose File" button to select a file from your computer
2. Click "Upload to IPFS" to upload the file
3. Once uploaded, you'll see the IPFS hash and a link to view the file on IPFS gateway
4. Click the "View on IPFS Gateway" link to access your uploaded file

## Notes

- The application assumes IPFS is running locally on the default port (5001)
- Files are temporarily stored during upload and then removed
- The IPFS gateway link uses ipfs.io as the public gateway
