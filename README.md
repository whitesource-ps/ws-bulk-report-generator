![Logo](https://whitesource-resources.s3.amazonaws.com/ws-sig-images/Whitesource_Logo_178x44.png)  

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub release](https://img.shields.io/github/v/release/whitesource-ps/ws-bulk-report-generator)](https://github.com/whitesource-ps/ws-bulk-report-generator/releases/latest)
# WhiteSource Bulk Report Generator
Tool to execute report on multiple projects.  
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
2. Edit `config.json` file with desired paramaters  
3. Run the tool:
```python
python bulk_reports_generator.py -u <USER_KEY> -k <ORG_TOKEN> -r <REPORT_NAME> -s <REPORT_SCOPE>  
```
## Full Usage:
```
bulk-reports-generator.py [-h] -u WS_USER_KEY -k WS_TOKEN -r
                                 {ignored_alerts,request_history,source_files,in_house_libraries,library_location,license_compatibility,effective_licenses,alerts,attributes,att
ribution,vulnerability,risk,in_house,resolved_alerts,due_diligence,container_vulnerability,bugs,inventory,source_file_inventory}
                                 [-s {project,product}] [-a WS_URL]
                                 [-c CONFIG]

Bulk Reports Generator

optional arguments:
  -h, --help            show this help message and exit
  -u WS_USER_KEY, --userKey WS_USER_KEY
                        WS User Key
  -k WS_TOKEN, --token WS_TOKEN
                        WS Organization Key
  -r {ignored_alerts,request_history,source_files,in_house_libraries,library_location,license_compatibility,effective_licenses,alerts,attributes,attribution,vulnerability,risk,
in_house,resolved_alerts,due_diligence,container_vulnerability,bugs,inventory,source_file_inventory}, --report {ignored_alerts,request_history,source_files,in_house_libraries,l
ibrary_location,license_compatibility,effective_licenses,alerts,attributes,attribution,vulnerability,risk,in_house,resolved_alerts,due_diligence,container_vulnerability,bugs,in
ventory,source_file_inventory}
                        Report Type to produce
  -s {project,product}, --ReportScope {project,product}
                        Scope of report
  -a WS_URL, --wsUrl WS_URL
                        WS URL
  -c CONFIG, --config CONFIG
                        Location of configuration file
```
