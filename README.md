![Logo](https://whitesource-resources.s3.amazonaws.com/ws-sig-images/Whitesource_Logo_178x44.png)  
[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/whitesource-ps/ws-bulk-report-generator/actions/workflows/ci-master.yml/badge.svg)](https://github.com/whitesource-ps/ws-bulk-report-generator/actions/workflows/ci-master.yml)
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
1. Install Python dependencies: `pip install -r requirements.txt` 
1. Edit `config.json` file with desired parameters  
1. Run the tool:
```shell
python bulk_reports_generator.py -u <USER_KEY> -k <ORG_TOKEN> -r <REPORT_NAME> -s <REPORT_SCOPE>  
```
## Full Usage:
```shell
bulk-reports-generator.py [-h] -u WS_USER_KEY -k WS_TOKEN -r
                                 {library_location,inventory,alerts,source_file_inventory,risk,attributes,in_house_libraries,bugs,license_compatibility,vulnerability,effective_licenses,attribution,due_diligence,source_files
,resolved_alerts,container_vulnerability,in_house,request_history,ignored_alerts}
                                 [-s {project,product}] [-a WS_URL] [-o DIR]
                                 [-t {binary,json}] [-c CONFIG]

Bulk Reports Generator

optional arguments:
  -h, --help            show this help message and exit
  -u WS_USER_KEY, --userKey WS_USER_KEY
                        WS User Key
  -k WS_TOKEN, --token WS_TOKEN
                        WS Token
  -r {library_location,inventory,alerts,source_file_inventory,risk,attributes,in_house_libraries,bugs,license_compatibility,vulnerability,effective_licenses,attribution,due_diligence,source_files,resolved_alerts,container_v
ulnerability,in_house,request_history,ignored_alerts}, --report {library_location,inventory,alerts,source_file_inventory,risk,attributes,in_house_libraries,bugs,license_compatibility,vulnerability,effective_licenses,attribu
tion,due_diligence,source_files,resolved_alerts,container_vulnerability,in_house,request_history,ignored_alerts}
                        Report Type to produce
  -s {project,product}, --ReportScope {project,product}
                        Scope of report
  -a WS_URL, --wsUrl WS_URL
                        WS URL
  -o DIR, --reportDir DIR
                        Report Dir
  -t {binary,json}, --outputType {binary,json}
                        Type of output
  -c CONFIG, --config CONFIG
                        Location of configuration file
```
