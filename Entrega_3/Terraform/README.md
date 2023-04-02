# **Intallación de Terraform**

Desacrgar terraform corriendo el siguiente comando:

```bash
wget https://releases.hashicorp.com/terraform/1.2.7/terraform_1.2.7_linux_amd64.zip
```

Para descomprimir terraform utilice el siguiente comando:

```bash
unzip terraform_1.2.7_linux_amd64.zip
rm -rf terraform_1.2.7_linux_amd64.zip
```

Establezca la variable de entorno PATH para los binarios de Terraform:

```bash
export PATH="$PATH:$HOME/terraform"
cd /usr/bin
sudo ln -s $HOME/terraform
cd $HOME
source ~/.bashrc
```

Confirme la instalación de Terraform ejecutando el siguiente comando:

```bash
terraform --version
```

Exporte el proyecto de Google Cloud a una variable de entorno ejecutando el siguiente comando en Cloud Shell:

```bash
export PROJECT_ID=$(gcloud config get-value project)
```

Cree un directorio para su configuración Terraform ejecutando el siguiente comando:

```bash
mkdir tfnet
```

# **Inicializar de Terraform**

Dirigirse a la carpeta tfnet

```bash
cd tfnet
```

Crear el archivo ***provider.tf***

```bash
vim provider.tf
```


Copiar el siguiente código en ***provider.tf*** que sirve para definir el proveedor con el cual se va a trabajar.

```hcl
provider "google" {}
```

Inicialice Terraform ejecutando los siguientes comandos:

```bash
terraform init
```

# **Crear VPC y sus recursos**

Crear el archivo ***privatenet.tf***

```bash
vim privatenet.tf
```

Copiar el sigueinte codigo dentro de ***privatenet.tf***

```hcl
variable "region" {default = "us-central1"}
variable "zone" {default = "us-central1-a"}

# Crea una red privada
resource "google_compute_network" "privatenet" {
  name                    = "privatenet"
  auto_create_subnetworks = false
}

# Crear una subred privada
resource "google_compute_subnetwork" "privatesubnet-us" {
  name          = "privatesubnet"
  region        = "${var.region}"
  network       = google_compute_network.privatenet.self_link
  ip_cidr_range = "172.16.0.0/24"
}

# Cree una regla de firewall para permitir el tráfico  SSH 
resource "google_compute_firewall" "privatenet-allow-ssh" {
  name          = "privatenet-allow-ssh"
  network       = google_compute_network.privatenet.self_link
  priority      = 1000
  direction     = "INGRESS"
  source_ranges = ["0.0.0.0/0"]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

# Cree una regla de firewall para permitir el tráfico tcp:0-65535, udp:0-65535, icmp 
resource "google_compute_firewall" "privatenet-allow-internal" {
  name          = "privatenet-allow-internal"
  network       = google_compute_network.privatenet.self_link
  priority      = 1000
  direction     = "INGRESS"
  source_ranges = ["172.16.0.0/24"]

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }
}

module "frontend-vm" {
  source              = "./instance"
  instance_name       = "frontend"
  instance_zone       = "${var.zone}"
  instance_subnetwork = google_compute_subnetwork.privatesubnet-us.self_link
  internal_ip         = "172.16.0.4"
  nat_ip              = null
}

module "web-server-vm" {
  source              = "./instance"
  instance_name       = "web-server"
  instance_zone       = "${var.zone}"
  instance_subnetwork = google_compute_subnetwork.privatesubnet-us.self_link
  internal_ip         = "172.16.0.5"
  nat_ip              = null
}

module "worker-wm" {
  source              = "./instance"
  instance_name       = "worker"
  instance_zone       = "${var.zone}"
  instance_subnetwork = google_compute_subnetwork.privatesubnet-us.self_link
  internal_ip         = "172.16.0.6"
  nat_ip              = null
}

module "file-server-wm" {
  source              = "./instance"
  instance_name       = "file-server"
  instance_zone       = "${var.zone}"
  instance_subnetwork = google_compute_subnetwork.privatesubnet-us.self_link
  internal_ip         = "172.16.0.7"
  nat_ip              = null
}
```

# **Configurar la instancia VM**

Crear el archivo ***main.tf*** dentro de la carpeta ***instance***

```bash
mkdir instance && cd instance
vim main.tf
```

Copiar el sigueinte codigo dentro de ***main.tf***

```hcl
variable "instance_name" {}
variable "instance_zone" {}
variable "instance_subnetwork" {}
variable "internal_ip" {}
variable "nat_ip" {}

variable "instance_type" {
    default = "f1-micro"
}
 
resource "google_compute_instance" "vm_instance" {
    name         = "${var.instance_name}"
    zone         = "${var.instance_zone}"
    machine_type = "${var.instance_type}"
 
    boot_disk {
        initialize_params {
            image = "ubuntu-os-cloud/ubuntu-2204-lts"
        }
    }
 
    network_interface {
        subnetwork = "${var.instance_subnetwork}"
        network_ip = "${var.internal_ip}"

    access_config {
        nat_ip = "${var.nat_ip}"
        }
    }
}
```

# **Despliegue Infraestructura**

***Habilite el Compute Engine API.***

Para realizar el despliegue primero se reescribe los archivos de configuración de Terraform a un formato y estilo canónico ejecutando el siguiente comando:

```bash
cd ..
terraform fmt
```

Inicialice Terraform ejecutando el siguiente comando:

```bash
terraform init
```

Cree un plan de ejecución ejecutando el siguiente comando:

```bash
terraform plan
```

Aplique los cambios deseados ejecutando el siguiente comando:

```bash
terraform apply
```

Revise:

* **Compute Engine:** Deben aparecer las instancias necesarias para la ejecución de la aplicación.
* **Redes VPC:**
    * **Redes VPC:** Se debe crear una red VPC con una Sub red perteneciente a la Zona ***"us-central1-a"***
    * **Firewall:** Se deben crear 2 reglas dse Firewall que afectan a la VPC creada.
