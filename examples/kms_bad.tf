resource "google_kms_key_ring" "us-bad" {
  name     = "keyring-example"
  location = "us-west4"
}

resource "google_kms_key_ring" "asia" {
  name     = "keyring-example"
  location = "asia-east1"
}