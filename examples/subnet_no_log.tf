resource "google_compute_subnetwork" "subnet-with-no-logging" {
  name          = "log-test-subnetwork"
  ip_cidr_range = "10.2.0.0/16"
  region        = "us-central1"
  network       = "net"
  private_ip_google_access = true
}