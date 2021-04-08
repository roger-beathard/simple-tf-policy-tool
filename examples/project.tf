resource "google_project" "project" {
  name       = "My Project"
  project_id = "apex-docmgmt-dev-1111"
  org_id     = "1234567"

  labels = {
    product = "docmgmt"
    env = "dev"
  }
}