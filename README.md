[![Logo](https://whitesource-resources.s3.amazonaws.com/ws-sig-images/Whitesource_Logo_178x44.png)](https://www.whitesourcesoftware.com/)  
[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/whitesource-ps/ws-bulk-report-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/whitesource-ps/ws-bulk-report-generator/actions/workflows/ci.yml)
[![GitHub release](https://img.shields.io/github/v/release/whitesource-ps/ws-bulk-report-generator)](https://github.com/whitesource-ps/ws-bulk-report-generator/releases/latest)
[![PyPI](https://img.shields.io/pypi/v/ws-bulk-report-generator?style=plastic)](https://pypi.org/project/ws-bulk-report-generator/)
# [WhiteSource Bulk Report Generator](https://github.com/whitesource-ps/ws-bulk-report-generator)
Tool to execute a report on multiple projects.
* The tool allows including and excluding scopes by stating names and tokens.
* Report scope determines whether reports will be run on projects or products.
* If Included scopes is not stated (_via -i/--includedTokens_), the tool will run reports on **all** scopes within (i.e. if _--token/-k_ is organization than on all the organization).
* Report data is exported by default in binary (i.e. Excel or PDF) format or JSON.

## Supported Operating Systems
- **Linux (Bash):**	CentOS, Debian, Ubuntu, RedHat
- **Windows (PowerShell):**	10, 2012, 2016

## Prerequisites
* Python 3.6+

## Installation and Execution by pulling package from PyPi:
1. Execute `pip install ws-bulk-report-generator`
2. Run report: `bulk-report-generator -u <USER_KEY> -k <ORG_TOKEN> -r <REPORT_NAME> -s <REPORT_SCOPE>`

## Installation and Execution by downloading project code from GitHub:
1. Download the latest release
1. Install Python dependencies: `pip install -r requirements.txt` 
1. Edit `config.json` file with desired parameters  
1. Run the tool:
```shell
python bulk_reports_generator.py -u <USER_KEY> -k <ORG_TOKEN> -r <REPORT_NAME> -s <REPORT_SCOPE>  
```
## Full Usage:
```shell
> bulk_report_generator -h
usage: bulk_report_generator [-h] -u WS_USER_KEY -k WS_TOKEN -r
                             {alerts,ignored_alerts,resolved_alerts,inventory,vulnerability,container_vulnerability,source_files,source_file_inventory,in_house_libraries,in_house,risk,library_location,license_compatibility,due_diligence,attributes,attribution,effect
ive_licenses,bugs,request_history}
                             [-s {project,product}] [-a WS_URL] [-o DIR] [-t {binary,json}] [-c CONFIG] [-i INC_TOKENS] [-e EXC_TOKENS] [-in INC_NAMES] [-en EXC_NAMES]

Bulk Reports Generator

optional arguments:
  -h, --help            show this help message and exit
  -u WS_USER_KEY, --userKey WS_USER_KEY
                        WS User Key
  -k WS_TOKEN, --token WS_TOKEN
                        WS Token
  -r {alerts,ignored_alerts,resolved_alerts,inventory,vulnerability,container_vulnerability,source_files,source_file_inventory,in_house_libraries,in_house,risk,library_location,license_compatibility,due_diligence,attributes,attribution,effective_licenses,bugs,reques
t_history}, --report {alerts,ignored_alerts,resolved_alerts,inventory,vulnerability,container_vulnerability,source_files,source_file_inventory,in_house_libraries,in_house,risk,library_location,license_compatibility,due_diligence,attributes,attribution,effective_lice
nses,bugs,request_history}
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
  -i INC_TOKENS, --includedTokens INC_TOKENS
                        Report Dir
  -e EXC_TOKENS, --excludedTokens EXC_TOKENS
                        Report Dir
  -in INC_NAMES, --includedNames INC_NAMES
                        Report Dir
  -en EXC_NAMES, --excludedNames EXC_NAMES
                        Report Dir
```
