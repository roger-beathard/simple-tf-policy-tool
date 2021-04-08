resource "google_healthcare_dataset" "default" {
  name      = "example-dataset"
  location  = "us-central1"
  time_zone = "UTC"
}