variable "region" { default = "us-central1" }
variable "zone" { default = "us-central1-a" }

# Crea una red privada
resource "google_compute_network" "privatenet" {
  name                    = "privatenet"
  auto_create_subnetworks = false
}

# Crear una subred privada
resource "google_compute_subnetwork" "privatesubnet" {
  name          = "privatesubnet"
  region        = var.region
  network       = google_compute_network.privatenet.self_link
  ip_cidr_range = "172.16.0.0/24"
}

# Cree una regla de firewall para permitir el tráfico  SSH 
resource "google_compute_firewall" "privatenet-allow-tcp" {
    name          = "privatenet-allow-tcp"
    network       = google_compute_network.privatenet.self_link
    priority      = 1000
    direction     = "INGRESS"
    source_ranges = ["0.0.0.0/0"]

    allow {
        protocol = "tcp"
        ports    = ["22","8080","5001"]
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
  instance_zone       = var.zone
  instance_subnetwork = google_compute_subnetwork.privatesubnet.self_link
  internal_ip         = "172.16.0.4"
  metadata            = "${var.metadata}${var.frontend-sh}"
  nat_ip              = null
}

module "web-server-vm" {
  source              = "./instance"
  instance_name       = "backend"
  instance_zone       = var.zone
  instance_subnetwork = google_compute_subnetwork.privatesubnet.self_link
  internal_ip         = "172.16.0.5"
  metadata            = "${var.metadata}${var.backend-worker-sh}${var.backend-sh}"
  nat_ip              = null
}

module "worker-vm" {
  source              = "./instance"
  instance_name       = "worker"
  instance_zone       = var.zone
  instance_subnetwork = google_compute_subnetwork.privatesubnet.self_link
  internal_ip         = "172.16.0.6"
  metadata            = "${var.metadata}${var.backend-worker-sh}${var.worker-sh}"
  nat_ip              = null
}

module "file-server-vm" {
  source              = "./instance"
  instance_name       = "file-server"
  instance_zone       = var.zone
  instance_subnetwork = google_compute_subnetwork.privatesubnet.self_link
  internal_ip         = "172.16.0.7"
  metadata            = "${var.file-server-sh}"
  nat_ip              = null
}