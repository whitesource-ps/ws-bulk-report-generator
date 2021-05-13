![Logo](https://whitesource-resources.s3.amazonaws.com/ws-sig-images/Whitesource_Logo_178x44.png)  

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub release](https://img.shields.io/github/v/release/whitesource-ps/ws-bulk-report-generator)](https://github.com/whitesource-ps/ws-bulk-report-generator/releases/latest)
# WhiteSource Bulk Report Generator
Tool to execute a report on multiple projects.
* The tool allows including and excluding scopes by stating names and tokens.
* Report scope determines whether reports will be run on projects or products.
* If Included scopes is not stated, the tool will run reports on **all** of scopes.

## Supported Operating Systems
- **Linux (Bash):**	CentOS, Debian, Ubuntu, RedHat
- **Windows (PowerShell):**	10, 2012, 2016

## Prerequisites
* Python 3.6+

## Installation and Execution:
1. Download the latest release 
2. Edit `config.json` file with desired parameters  
3. Run the tool:
```shell
python bulk_reports_generator.py -u <USER_KEY> -k <ORG_TOKEN> -r <REPORT_NAME> -s <REPORT_SCOPE>  
```
## Full Usage:
```shell
bulk-reports-generator.py [-h] -u WS_USER_KEY -k WS_TOKEN -r
                                 {alerts,inventory,attributes,vulnerability,resolved_alerts,effective_licenses,in_house,due_diligence,library_location,risk,attribution,license_compatibility,request_history,ignored_alerts,bugs,contai
ner_vulnerability,source_file_inventory,in_house_libraries,source_files}
                                 [-s {project,product}] [-a WS_URL] [-o DIR]
                                 [-c CONFIG]
Bulk Reports Generator
optional arguments:
  -h, --help            show this help message and exit
  -u WS_USER_KEY, --userKey WS_USER_KEY
                        WS User Key
  -k WS_TOKEN, --token WS_TOKEN
                        WS Token
  -r {alerts,inventory,attributes,vulnerability,resolved_alerts,effective_licenses,in_house,due_diligence,library_location,risk,attribution,license_compatibility,request_history,ignored_alerts,bugs,container_vulnerability,source_file_inventory,in_house_libraries,sou
rce_files}, --report {alerts,inventory,attributes,vulnerability,resolved_alerts,effective_licenses,in_house,due_diligence,library_location,risk,attribution,license_compatibility,request_history,ignored_alerts,bugs,container_vulnerability,source_file_inventory,in_hou
se_libraries,source_files}
                        Report Type to produce
  -s {project,product}, --ReportScope {project,product}
                        Scope of report
  -a WS_URL, --wsUrl WS_URL
                        WS URL
  -o DIR, --reportDir DIR
                        Report Dir
  -c CONFIG, --config CONFIG
                        Location of configuration file
```
