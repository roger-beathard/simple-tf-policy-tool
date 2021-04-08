resource "google_kms_key_ring" "example-keyring" {
  name     = "keyring-example"
  location = "us-east1"
}