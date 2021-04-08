resource "google_storage_bucket" "bucket_no_cmek" {
  name          = "auto-expiring-bucket"
  location      = "US"
  force_destroy = true
}