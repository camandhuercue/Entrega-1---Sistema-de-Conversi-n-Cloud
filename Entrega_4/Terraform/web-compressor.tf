# -------------------------------- Network / Subnetwork ----------------------------
# ----------------------------------------------------------------------------------

# Se crea una red privada
resource "google_compute_network" "privatenet" {
  name                    = "privatenet"
  auto_create_subnetworks = false
}

# Se crear una subred privada
resource "google_compute_subnetwork" "privatesubnet" {
  name          = "privatesubnet"
  region        = var.region
  network       = google_compute_network.privatenet.self_link
  ip_cidr_range = "172.16.0.0/24"
}

# ---------------------------------- Rules Firewall --------------------------------
# ----------------------------------------------------------------------------------

# Se crea una regla de firewall para permitir el tráfico  SSH 
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

# Se crea una regla de firewall para permitir el tráfico tcp:0-65535, udp:0-65535, icmp 
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

# ----------------------------- Account Service - IAM ------------------------------
# ----------------------------------------------------------------------------------
resource "google_service_account" "service_account" {
    account_id   = "admin-storage-pubsub"
    display_name = "admin-storage-pubsub"
}

resource "google_project_iam_member" "storege" {
    project = "terra-pru"
    role = "roles/storage.admin"
    member = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_project_iam_member" "pubsub" {
    project = "terra-pru"
    role = "roles/pubsub.admin"
    member = "serviceAccount:${google_service_account.service_account.email}"
}

# ----------------------------------- Frontend -------------------------------------
# ----------------------------------------------------------------------------------
module "frontend-vm" {
  source              = "./instance"
  instance_name       = "frontend"
  machine_type        = "${var.machine_type}"
  instance_zone       = "${var.zone}"
  instance_subnetwork = google_compute_subnetwork.privatesubnet.self_link
  internal_ip         = "172.16.0.4"
  metadata            = "${var.metadata}${var.frontend-sh}"
  nat_ip              = null
}

# ------------------------------------ Backend -------------------------------------
# ----------------------------------------------------------------------------------
module "backlend-template" {
    source              = "./backend-resource"
    template_name       = "backend-template"
    base_instance_name  = "backend"
    instance_region     = "${var.region}"
    instance_zone       = "${var.zone}"
    machine_type        = "${var.machine_type}"
    instance_subnetwork = google_compute_subnetwork.privatesubnet.self_link
    project_id          = "${var.project_id}"
    metadata            = "${var.backend-template}"
}

# ---------------------------------------- DNS -------------------------------------
# ----------------------------------------------------------------------------------

resource "google_dns_managed_zone" "dns_cloud" {
    name          = "soluciones-cloud-dns"
    dns_name      = "soluciones.cloud."
    description   = "Private DNS zone for soluciones.cloud"
    visibility    = "private"
    force_destroy = true 
}

resource "google_dns_record_set" "sql" {
    name         = "sql.${google_dns_managed_zone.dns_cloud.dns_name}"
    managed_zone = google_dns_managed_zone.dns_cloud.name
    type         = "A"
    ttl          = 300
    rrdatas      = ["172.16.2.3"]
}

# ------------------------------------- Pub - Sub ----------------------------------
# ----------------------------------------------------------------------------------
resource "google_pubsub_topic" "compress_queue" {
    name = "compress_queue"
}

# ----------------------------------- CLoud - Funtion ------------------------------
# ----------------------------------------------------------------------------------



# -------------------------------------- Cloud SQL ---------------------------------
# ----------------------------------------------------------------------------------

#module "sql-server" {
#    source           = "./sql-instance"
#    instance_network = google_compute_network.privatenet.id
#}