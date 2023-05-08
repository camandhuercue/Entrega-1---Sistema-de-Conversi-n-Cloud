variable "instance_network" {}

# Cloud SQL

resource "google_compute_global_address" "private_ip_address" {
    provider      = google-beta
    name          = "private-ip-address"
    purpose       = "VPC_PEERING"
    address_type  = "INTERNAL"
    prefix_length = 24
    network       = "${var.instance_network}"
    address       = "172.16.2.0"
}

resource "google_service_networking_connection" "private_vpc_connection" {
    provider                = google-beta
    network                 = "${var.instance_network}"
    service                 = "servicenetworking.googleapis.com"
    reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

resource "google_sql_database_instance" "main" {
    provider         = google-beta
    name             = "sql-file-compresor"
    region           = "us-central1"
    database_version = "POSTGRES_14"

    depends_on = [google_service_networking_connection.private_vpc_connection]

    settings {
        tier = "db-f1-micro"
        ip_configuration {
            ipv4_enabled                                  = false
            private_network                               = "${var.instance_network}"
            enable_private_path_for_google_cloud_services = true
        }
        disk_size = 10
        disk_type = "PD_SSD"
    }
}

provider "google-beta" {
    region = "us-central1"
    zone   = "us-central1-a"
}