variable "region" { default = "us-central1" }
variable "zone" { default = "us-central1-a" }
variable "project_id" { default = "terra-pru" }
variable "machine_type" { default = "f1-micro" }

# --------------------------------------- Secuencias de inicio -------------------------------------------
# --------------------------------------------------------------------------------------------------------

variable "backend-template" {
  default = <<-EOF
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
    "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
    "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
    gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
    git clone https://github.com/camandhuercue/Entrega-1---Sistema-de-Conversi-n-Cloud.git
    cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_4/Backend/
    docker compose up -d
  EOF
}

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

variable "frontend-sh" {
  default = <<-EOF
    cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Frontend/
    docker compose up -d
  EOF
}