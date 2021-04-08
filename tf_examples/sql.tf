resource "google_sql_database_instance" "good_sql_instance" {
  provider = "google-beta"
  name   = "private-instance"
  region = "us-central1"

  encryption_key_name = "abc/key"
  settings {
    tier = "db-f1-micro"
    availability_type = "REGIONAL"
    backup_configuration {
      enabled = true
    }
  }
}