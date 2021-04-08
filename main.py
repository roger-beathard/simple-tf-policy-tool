import json
import argparse
import sys
from voluptuous import MultipleInvalid
from policy import schema


def err(msg=''):
    print(msg, file=sys.stderr)


def _parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('tfplan', type=argparse.FileType(
        'r'), help='Terraform plan JSON file')
    parser.add_argument('--warn', dest='warn', default=False, nargs='?', const=True,
                        help='Only warn on policy violations and terminate successfully')
    args = parser.parse_args()
    return args


def _get_resources(tfplan):
    changes = tfplan.get('resource_changes', [])
    resources = []

    for change in changes:
        actions = change['change']['actions']
        # if we are not creating nor updating a resource, pass over
        if 'create' not in actions and 'update' not in actions:
            continue
        kind = change['type']
        name = change['name']
        values = change['change']['after']
        resource = {
            'name': name,
            'kind': kind,
            'config': {kind: values}
        }
        resources.append(resource)
    return resources


def main():
    args = _parse()
    tfplan = json.load(args.tfplan)
    resources = _get_resources(tfplan)
    exit_code = 0
    for res in resources:
        config = res['config']
        name = res['name']
        kind = res['kind']
        try:
            schema(config)
        except MultipleInvalid as e:
            err(f'{kind} {name} : {e}')
            exit_code = 1

    # exit with success if in "warn" mode
    if args.warn:
        exit()

    exit(exit_code)


if __name__ == '__main__':
    main()
