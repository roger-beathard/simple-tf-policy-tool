from voluptuous import (
    Schema,
    All,
    ALLOW_EXTRA,
    Msg,
    Invalid,
    Required,
    MatchInvalid,
    Any,
    Length,
    Optional,
)
import re

# passes true for anything
anything = object


def forbidden(_):
    """
    Forbidden resource validator
    """
    raise Invalid("Forbidden resource")


def valid_project_id(project_id):
    # Terraform resource values are lists -- get head of list
    if len(project_id) > 30:
        raise Invalid("Project ID greater than 30 chars")
    project_id_re = re.compile(r"^[a-z0-9]*\-[a-z0-9]*\-[a-z0-9]*\-[a-z0-9]*$")

    # Bad format
    # project_id_re = re.compile(r"^[a-z0-9]*\-[a-z0-9]*\-[a-z0-9]$")
    if not re.match(project_id_re, project_id):
        raise Invalid("Project ID invalid against regex.")


def valid_rotation_period(x):
    """
    Check that a key rotation is less than 90 days
    """
    ninety_days = 90 * 24 * 60 * 60
    if x > ninety_days:
        raise Invalid("Rotation period must be less than 90 days")


def make_schema(spec):
    """
    Convenience function for making all specs for resources
    require every declared key, but allow for extra keys 
    """
    for resource_type in spec:
        spec[resource_type] = Schema(
            spec[resource_type], required=True, extra=ALLOW_EXTRA
        )
    return Schema(spec, extra=ALLOW_EXTRA)


# The master schema
schema = make_schema(
    {
        "google_project": {
            "project_id": valid_project_id,
            Required("labels"): Schema({
                Required("product"): anything,
                Required("env"): anything,
            #    Required("newlabel"): anything,
            })
        },
        "google_compute_network": {
            "delete_default_routes_on_create": True
        },
        "google_kms_key_ring": {
            # Locations must be where HSM is available
            "location": Any(
                "us",
                "us-west1",
                "us-west2",
                "us-west3",
                "us-central1",
                "us-east1",
                "us-east4",
                msg="Key Ring location must be within specific regions",
            )
        },
        "google_kms_crypto_key": {
            Optional("rotation_period"): valid_rotation_period
        },
        "google_redis_instance": {
            "tier": Msg("STANDARD_HA", "Redis instance must be in HA configuration")
        },
        "google_bigquery_dataset": {
            "default_encryption_configuration": Length(
                min=1, msg="BigQuery must use CMEK"
            )
        },
        "google_sql_database_instance": {
            # replication_type is for 1st generation instances -- deprecated
            Optional("replication_type"): forbidden,
            # authorized_gae_applications is for 1st generation instances -- deprecated
            Optional("authorized_gae_applications"): forbidden,
            # Cloud SLQ wust use CMEK
            Msg("encryption_key_name", "Cloud SQL must use CMEK"): str,
            "region": str,
            "settings": [
                {
                    "availability_type": "REGIONAL",
                    "backup_configuration": [{"enabled": True}],
                }
            ],
        },
        "google_compute_subnetwork": {
            "log_config": Length(min=1, msg="Subnets must have VPC Flow Logs enabled"),
            "private_ip_google_access": Msg(
                True, "Private Google Access must be enabled for all subnets"
            ),
        },
        "google_storage_bucket": {
                "encryption": Length(min=1),
                Msg( "labels", "Must have label"): {
                    "team": anything,
                },
        },
        "google_compute_firewall": {"enable_logging": True},
        "google_compute_instance": {"boot_disk": [{"kms_key_self_link": str}]},
        "google_pubsub_topic": {"kms_key_name": str},
        "google_healthcare_dataset": forbidden,
        "google_game_services_game_server_cluster": forbidden,
    }
)

