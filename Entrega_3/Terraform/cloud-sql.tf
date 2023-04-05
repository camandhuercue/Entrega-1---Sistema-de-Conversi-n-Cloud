#module "sql-server" {
#  source           = "./sql-instance"
#  instance_network = google_compute_network.privatenet.id
#}