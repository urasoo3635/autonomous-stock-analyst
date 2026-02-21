#!/bin/bash
set -e

echo "Updating package index..."
sudo apt-get update

echo "Installing prerequisites..."
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
echo "Adding Docker GPG key..."
sudo install -m 0755 -d /etc/apt/keyrings
if [ -f /etc/apt/keyrings/docker.gpg ]; then
    sudo rm /etc/apt/keyrings/docker.gpg
fi
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources
echo "Adding Docker repository..."
echo \
  "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Installing Docker Engine..."
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add current user to the docker group so you can run docker without sudo
echo "Adding user '$USER' to docker group..."
sudo usermod -aG docker $USER

echo "============================================================"
echo "Docker installation completed!"
echo "To use docker without sudo, you need to apply the group changes:"
echo "Run: newgrp docker"
echo ""
echo "Note for WSL2: You may need to start the docker service manually if not using systemd:"
echo "Run: sudo service docker start"
echo "============================================================"
