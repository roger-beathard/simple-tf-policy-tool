resource "google_storage_bucket" "bucket" {
  name          = "auto-expiring-bucket"
  location      = "US"
  force_destroy = true
  encryption {
      default_kms_key_name = "key"
  }
}