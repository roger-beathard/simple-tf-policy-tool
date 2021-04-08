resource "google_sql_database_instance" "instance_with_replication_type" {
  provider = "google-beta"
  name   = "private-instance"
  region = "us-central1"

  encryption_key_name = "abc/key"
  settings {
    tier = "db-f1-micro"
    availability_type = "REGIONAL"
    replication_type = "SYNCHRONOUS"
  }
}