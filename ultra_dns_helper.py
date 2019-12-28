#!/usr/bin/env python

from __future__ import print_function
import ultra_rest_client
import shutil
import time
import os
import json
import click
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

USER_NAME = os.environ.get('ULTRADNS_USERNAME', None)
API_DOMAIN = "restapi.ultradns.com"
USE_HTTP = False
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ZONE_TEMPLATE_DIR = os.path.join(THIS_DIR, 'zone_files')


def api_connect(username, password, token, use_http, domain):
    """
    Authenticate to UltraDNS api portal using username and
    password plus token
    """
    password = '{0}{1}'.format(password, token)
    api = ultra_rest_client.RestApiClient(username, password, use_http, domain)
    return api


def account_details(api):
    """
    Dump out Ultra Account name
    """
    account_details = api.get_account_details()
    account_name = account_details[u'accounts'][0][u'accountName']
    return account_name


def zone_report_soa(api, zone_name):
    """
    Dump out RRSET SOA data for a zone
    """
    try:
        zone_meta = api.get_rrsets_by_type(zone_name, "SOA")
        return json.dumps(zone_meta['rrSets'], indent=4, sort_keys=True)
    except Exception:
        print("\nZone {} does not exist\n".format(zone_name))


def zone_report_ns(api, zone_name):
    """
    Dump out RRSET NS data for a zone
    """
    try:
        zone_meta = api.get_rrsets_by_type(zone_name, "NS")
        return json.dumps(zone_meta['rrSets'], indent=4, sort_keys=True)
    except Exception:
        print("\nZone {} does not exist\n".format(zone_name))


def zone_read_file(filename):
    """
    Read in TXT file containing zones and create a list of zones
    """
    with open(filename) as zonefile:
        zones = [n.rstrip('\n') for n in zonefile]
        return zones


def dir_cleanup():
    """
    Directory housekeeping cleanup after each run
    and recreate directory for zone files.
    """
    if os.path.isdir(ZONE_TEMPLATE_DIR):
        shutil.rmtree(ZONE_TEMPLATE_DIR)
    os.mkdir(ZONE_TEMPLATE_DIR)


def zone_template_render(filename, zone_name):
    """
    Read in Jinja2 template and substitute ORIGIN field per zone
    Write zone file to /zone_files directory
    """
    isodate_format = iso8601_datetime()
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)
    template = j2_env.get_template(filename)
    zone_dest_location = os.path.join(ZONE_TEMPLATE_DIR, zone_name)
    print("Zone template created {}".format(zone_dest_location))
    with open(zone_dest_location, 'w') as fh:
        fh.write(template.render(
            domain=zone_name,
            serial=isodate_format
        ))


def iso8601_datetime():
    zone_serial = datetime.now().strftime("%Y%m%d%H%M%S")
    zone_serial_yymmddhhss = zone_serial[:-4]
    return zone_serial_yymmddhhss


def create_ultra_zone(api, account_name, zone_name):
    """
    Create Zone containing NS and SOA records using Jinja2
    templates.
    """
    zone_dest_location = os.path.join(ZONE_TEMPLATE_DIR, zone_name)
    result = api.create_primary_zone_by_upload(account_name, zone_name,
    zone_dest_location)
    while True:
        task_status = api.get_task(result['task_id'])
        print('task status: {}'.format(api.get_task(result['task_id'])))
        if task_status['code'] != 'IN_PROCESS':
            break
        time.sleep(1)


def delete_rrset_A_record(api, zone_name, record):
    """
    Delete A record entries for specific zone.
    """
    api.delete_rrset(zone_name, "A", record)
    validate_delete = api.get_rrsets_by_type_owner(zone_name, "A", record)
    if validate_delete[0]['errorMessage'] == 'Data not found.':
        print("Record successfully deleted {}".format(record))


@click.command()
@click.option('--password', prompt="Please enter your UltraDns password",
    help="Please enter your UltraDns password",
    hide_input=True
    )
@click.option('--token', prompt="Please enter your UltraDns 2FA token",
    help="Please enter your UltraDns 2FA token",
    hide_input=True
    )
@click.option("--zone_file", "-z", required=True,
    help="Path to file containing list of zones for processing",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    )
@click.option("--zone_template", "-t",
    help="Path to zone Jinja2 template for creation of new Zones. Please reference zones_template.js ",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    )
@click.option(
    '--list_type', '-l',
    help="List existing NS or SOA records for zone",
    type=click.Choice(['soa', 'ns'])
    )
@click.option('--delete_record', "-d",
    help="Delete existing A record type for a zone",
    )
def main(token, password, zone_file, zone_template, list_type, delete_record):
    zones = zone_read_file(zone_file)
    dir_cleanup()
    api = api_connect(USER_NAME, password, token, USE_HTTP, API_DOMAIN)
    ultra_account_name = account_details(api)
    for zone in zones:
        if list_type:
            if list_type.lower() in ['soa']:
                zone_meta_soa = zone_report_soa(api, zone)
                if zone_meta_soa is not None:
                    print(zone_meta_soa)
            elif list_type.lower() in ['ns']:
                zone_meta_ns = zone_report_ns(api, zone)
                print(zone_meta_ns)
        elif zone_template:
            zone_template_render(zone_template, zone)
            click.confirm('Create Ultra Zone from template {}?'.format(zone),
            default=False, abort=True
            )
            create_ultra_zone(api, ultra_account_name, zone)
        elif delete_record:
            click.confirm('Delete Ultra record {}.{}?'.format(delete_record,
            zone), default=False, abort=True
            )
            delete_rrset_A_record(api, zone, delete_record)


if __name__ == "__main__":
    main()
