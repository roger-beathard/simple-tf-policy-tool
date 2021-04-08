resource "google_game_services_game_server_cluster" "default" {
  provider   = google-beta

  cluster_id = ""
  realm_id = 1234

  connection_info {
    gke_cluster_reference {
      cluster = "locations/us-west1/clusters/foo"
    }
    namespace = "default"
  }
}