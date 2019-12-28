# ultra_dns_helper

This script performs the following actions currently

* Delete A records for existing zones 
* Creation of new zone using zone template file
* Lookup of NS records for existing zone
* Lookup of SOA records for existing zone

```
/ultra_dns_helper.py --help
Usage: ultra_dns_helper.py [OPTIONS]

Options:
  --password TEXT           Please enter your UltraDns password
  --token TEXT              Please enter your UltraDns 2FA token
  -z, --zone_file FILE      Path to file containing list of zones for
                            processing  [required]
  -t, --zone_template FILE  Path to zone Jinja2 template for creation of new
                            Zones. Please reference zones_template.js
  -l, --list_type [soa|ns]  List existing NS or SOA records for zone
  -d, --delete_record TEXT  Delete existing A record type for a zone
  --help                    Show this message and exit.
```

## Dependencies/setup
Note this requires following additional libraries 

```
ultra-rest-client
click
```

Please run following to install dependencies before using ultra_dns_helper 

* Install python library dependencies as follows:

```
pip install -r requirements.txt
```

* Setup environment variable for ULTRADNS_USERNAME as follows:
Recommend adding this to ~/.bashrc 
```
export ULTRADNS_USERNAME="ultra_username"

```

To manage A records (deletion) on existing zone you should ensure that the following file zone_update.txt contains the correct zone 

```
more zones_update.txt
mytestzone.com
```

To add new Zones based on Jinja2 generated zone file ensure that following file zone_add.txt contains the new zone to be added 
```
more zones_add.txt
www.mytestzone.com
```

## Usage examples

To remove A record www from existing zone e.g mytestzone.com perform following action 
Note you will be prompted to enter your UltraDNS username and the 2FA Symantec token

**The script will prompt you to enter Y/N to deletion of this record**
```
./ultra_dns_helper.py -z zones_update.txt -d www
Please enter your UltraDns password:
Please enter your UltraDns 2FA token:
Delete Ultra record www.mytestzone.com? [y/N]: n
Aborted!
```

To create a new zone using a zone template file for NS and SOA records e.g www.mytestzone.com
**The script will prompt you to enter Y/N to create this zone**

```
./ultra_dns_helper.py -z zones_add.txt -t zone_template.js
Please enter your UltraDns password:
Please enter your UltraDns 2FA token:
Zone template created /opt/ghe.megaleo.com/ultra_dns_helper/zone_files/www.mytestzone.com
Create Ultra Zone from template www.mytestzone.com? [y/N]: n
Aborted!
```

The script above will generate the following zone template file which is rendered from Jinja2 and contains correct values for NS and SOA. 

```
more zone_files/impl-wd100.myworkdaysite.com
$ORIGIN impl-wd100.myworkdaysite.com.
@       3600    IN      SOA pdns1.ultradns.net.  (
                2019111915      ;Serial
                        60                  ;Refresh
                        60                  ;Retry
                        604800          ;Expire
                        300                 ;Minimum
                )
@       3600    IN      NS      dns2.p06.nsone.net.
@       3600    IN      NS      dns3.p06.nsone.net.
@       3600    IN      NS      pdns1.ultradns.net.
@       3600    IN      NS      pdns2.ultradns.net.
@       3600    IN      NS      pdns3.ultradns.org.
@       3600    IN      NS      dns1.p06.nsone.net.
```
To validate the SOA and NS records for newly created zone run following - testing this with existing zone mytestzone.com

```

more zones_add.txt
mytestzone.com

./ultra_dns_helper.py -z zones_add.txt -l soa
Please enter your UltraDns password:
Please enter your UltraDns 2FA token:
[
    {
        "ownerName": "mytestzone.com.",
        "rdata": [
            "pdns1.ultradns.net. 1555408917 60 60 604800 300"
        ],
        "rrtype": "SOA (6)",
        "ttl": 3600
    }
]

./ultra_dns_helper.py -z zones_add.txt -l ns
Please enter your UltraDns password:
Please enter your UltraDns 2FA token:
[
    {
        "ownerName": "mytestzone.com.",
        "rdata": [
            "dns1.p06.nsone.net.",
            "dns2.p06.nsone.net.",
            "dns3.p06.nsone.net.",
            "pdns1.ultradns.net.",
            "pdns2.ultradns.net.",
            "pdns3.ultradns.org."
        ],
        "rrtype": "NS (2)",
        "ttl": 3600
    }
]
```


