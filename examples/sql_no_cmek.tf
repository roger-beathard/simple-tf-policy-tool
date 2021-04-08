resource "google_sql_database_instance" "sql_no_key" {
  provider = "google-beta"
  name   = "private-instance"
  region = "us-central1"

  settings {
    tier = "db-f1-micro"
    availability_type = "REGIONAL"
  }
}