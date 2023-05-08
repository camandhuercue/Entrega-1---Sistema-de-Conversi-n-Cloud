variable "template_name" {}
variable "machine_type" {}
variable "instance_subnetwork" {}
variable "project_id" {}
variable "metadata" {}
variable "base_instance_name" {}
variable "instance_zone" {}
variable "instance_region" {}

resource "google_compute_autoscaler" "backend" {
  name   = "my-autoscaler"
  zone   = "${var.instance_zone}"
  target = google_compute_instance_group_manager.backend.id

  autoscaling_policy {
    max_replicas    = 3
    min_replicas    = 1
    cooldown_period = 600

    cpu_utilization {
      target = 0.5
    }
  }
}

resource "google_compute_instance_template" "backend" {
    name        = "${var.template_name}"
    description = "This template is used to create backend server instances."

    machine_type         = "${var.machine_type}"
    can_ip_forward       = false

    scheduling {
        automatic_restart   = true
        on_host_maintenance = "MIGRATE"
    }

    disk {
        source_image      = "debian-cloud/debian-11"
    }

    network_interface {
        subnetwork = "${var.instance_subnetwork}"
    }

    service_account {
        email = "admin-storage-pubsub@${var.project_id}.iam.gserviceaccount.com"
        scopes = ["cloud-platform"]
    }
    
    metadata_startup_script = "${var.metadata}"
}

resource "google_compute_target_pool" "backend" {
  name = "load-balancer"
  region = "${var.instance_region}"
}

resource "google_compute_forwarding_rule" "frontend" {
  name                  = "load-balancer-frontend"
  port_range            = "8080"
  ip_protocol           = "TCP"
  target                = google_compute_target_pool.backend.self_link
  load_balancing_scheme = "EXTERNAL"
  region                = "${var.instance_region}"
  network_tier          = "PREMIUM"
}

resource "google_compute_instance_group_manager" "backend" {
    name               = "backend-group"
    base_instance_name = "${var.base_instance_name}"
    zone               = "${var.instance_zone}"
    target_pools       = [google_compute_target_pool.backend.id]

    version {
        instance_template  = google_compute_instance_template.backend.self_link_unique
    }
}