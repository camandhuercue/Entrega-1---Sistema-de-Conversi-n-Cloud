variable "instance_name" {}
variable "instance_zone" {}
variable "instance_subnetwork" {}
variable "internal_ip" {}
variable "nat_ip" {}
variable "metadata" {}

variable "instance_type" {
    default = "f1-micro"
}
 
# Compute Engine VM

resource "google_compute_instance" "vm_instance" {
    name         = "${var.instance_name}"
    zone         = "${var.instance_zone}"
    machine_type = "${var.instance_type}"
 
    boot_disk {
        initialize_params {
            #image = "ubuntu-os-cloud/ubuntu-2204-lts"
            image = "debian-cloud/debian-11"
        }
    }
 
    network_interface {
        subnetwork = "${var.instance_subnetwork}"
        network_ip = "${var.internal_ip}"

    access_config {
        nat_ip = "${var.nat_ip}"
        }
    }

    metadata_startup_script = "${var.metadata}"
}