#!/bin/sh

terraform plan -out plan.bin > /dev/null
terraform show -json plan.bin > plan.json
rm plan.bin
