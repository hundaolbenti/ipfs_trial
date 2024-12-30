# Download IPFS for Windows
$url = "https://dist.ipfs.tech/kubo/v0.27.0/kubo_v0.27.0_windows-amd64.zip"
$output = "kubo.zip"
Invoke-WebRequest -Uri $url -OutFile $output

# Extract the zip file
Expand-Archive -Path $output -DestinationPath "ipfs-kubo" -Force

# Move to the correct location
Move-Item -Path "ipfs-kubo\kubo\ipfs.exe" -Destination "." -Force

# Clean up
Remove-Item -Path $output -Force
Remove-Item -Path "ipfs-kubo" -Recurse -Force

# Initialize IPFS
.\ipfs.exe init
