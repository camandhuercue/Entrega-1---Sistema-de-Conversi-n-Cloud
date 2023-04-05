variable "metadata" {
  default = <<-EOF
    #!/bin/bash
    sudo su
    sudo apt-get update && apt-get install ca-certificates curl gnupg
    mkdir -m 0755 -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --yes --dearmor -o /etc/apt/keyrings/docker.gpg
    echo \
    "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
    "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update && sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
    git clone https://github.com/camandhuercue/Entrega-1---Sistema-de-Conversi-n-Cloud.git
  EOF
}

variable "file-server-sh" {
  default = <<-EOF
    sudo apt-get update -y && sudo apt-get install nfs-kernel-server -y
    sudo mkdir -p /shared/files
    sudo chown nobody:nogroup /shared/files/
    echo "/shared/files/   172.16.0.0/24(rw,sync,no_root_squash,no_subtree_check)" >> /etc/exports
    systemctl restart nfs-server
  EOF
}

variable "backend-worker-sh" {
  default = <<-EOF
    sudo apt-get update -y && sudo apt-get install nfs-common -y
  EOF
}

variable "backend-sh" {
  default = <<-EOF
    cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Backend/
    mkdir files
    sudo mount 172.16.0.7:/shared/files ./files/
  EOF
}

variable "worker-sh" {
  default = <<-EOF
    cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Worker
    mkdir files
    sudo mount 172.16.0.7:/shared/files ./files/
  EOF
}

variable "frontend-sh" {
  default = <<-EOF
    cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Frontend/
    docker compose up -d
  EOF
}


