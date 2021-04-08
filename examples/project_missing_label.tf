resource "google_project" "project_missing_label" {
  name       = "My Project"
  project_id = "apex-cashmanagement-dev-1111"
  org_id     = "1234567"

  #  labels = {
  #    random_label = 123
  #  }
}
