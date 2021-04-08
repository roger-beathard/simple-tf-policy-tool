resource "google_redis_instance" "redis_no_ha" {
  name           = "ha-memory-cache"
  tier           = "BASIC"
  memory_size_gb = 1

  location_id             = "us-central1-a"
  alternative_location_id = "us-central1-f"


  redis_version     = "REDIS_3_2"
  display_name      = "Terraform Test Instance"
  reserved_ip_range = "192.168.0.0/29"

  labels = {
    my_key    = "my_val"
    other_key = "other_val"
  }
}
