[![Logo](https://whitesource-resources.s3.amazonaws.com/ws-sig-images/Whitesource_Logo_178x44.png)](https://www.whitesourcesoftware.com/)  
[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/whitesource-ps/ws-bulk-report-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/whitesource-ps/ws-bulk-report-generator/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/ws-bulk-report-generator?style=plastic)](https://pypi.org/project/ws-bulk-report-generator/)
# [WhiteSource Bulk Report Generator](https://github.com/whitesource-ps/ws-bulk-report-generator)
Tool to execute reports on multiple products or projects.
* The tool allows including and excluding scopes by stating their tokens.
* Report scope (`-s, --ReportScope`) determines whether reports will be run on projects or products.
* If Included scopes (via `-i, --includedTokens`) is not specified, the tool will run reports on **all** scopes.
* Report data is exported by default in binary format (i.e. Excel or PDF) or JSON.

## Supported Operating Systems
- **Linux (Bash):**	CentOS, Debian, Ubuntu, RedHat
- **Windows (PowerShell):**	10, 2012, 2016

## Prerequisites
* Python 3.6+

## Installation and Execution by pulling package from PyPi:
1. Execute `pip install ws-bulk-report-generator`
2. Run report: `ws_bulk_report_generator -u <USER_KEY> -k <ORG_TOKEN> -r <REPORT_NAME> -s <REPORT_SCOPE>`
>**Note**:  If installing packages as a non-root user, be sure to include the path to the executables within the Operating System paths.

## Examples:
Generate Due Diligence Reports (file per project) on all project within organization in JSON format (reports will be saved in the working dir):  
`ws_bulk_report_generator -u <USER_KEY> -k <ORG_TOKEN> -s project -r due_diligence -t json`  

---

Generate Risk Reports (PDF format) on all products (file per product) within organization:  
`ws_bulk_report_generator -a app-eu -u <USER_KEY> -k <ORG_TOKEN> -o /tmp/reports/ -r risk`  

---

Search for log4j 3 recent vulnerabilities in all the organization and get output in a single JSON:  
`ws_bulk_report_generator -a di.whitesourcesoftware.com -u <USER_KEY> -k <ORG_TOKEN> -o /tmp/reports/ -r vulnerability -t unified_json -x vulnerability_names="CVE-2021-45046,CVE-2021-44228,CVE-2021-4104"`  

---

Execute Inventory report filtered on 'libwebp-dev_0.6.1-2_amd64.deb' and get a unified JSON on all the organization:  
`ws_bulk_report_generator -u <USER_KEY> -k <ORG_TOKEN> -o /tmp/reports/ -r inventory -t unified_json -x lib_name=libwebp-dev_0.6.1-2_amd64.deb`  

---

Execute Alerts report and get a unified JSON on all the organizations within a Global organization (Note: user must be defined in all the organization):  
`ws_bulk_report_generator -u <USER_KEY> -k <ORG_TOKEN> -o /tmp/reports/ -r inventory -t unified_json -y globalOrganization`  

---

Execute Vulnerability report and get a unified Excel report on 2 specific products in the organization (-s project means the API calls run on the project level behind the scenes, used when timeouts in the API response):  
`ws_bulk_report_generator -u <USER_KEY>  -k <ORG_TOKEN> -r vulnerability -t unified_xlsx -i "<PRODCUCT_TOKEN_1> , <PRODCUCT_TOKEN_2> -s project"`  

---


>**NEW!** USING ASYNCHRONOUS API for large organizations.  
Supported reports: `inventory`, `vulnerability`, `alerts`, `plugin request history`  

Generate Vulnerability report using asynchronous API call in excel format:  
`ws_bulk_report_generator -u <USER_KEY>  -k <ORG_TOKEN> -r vulnerability -t binary -c True`  

---

Search for log4j 3 recent vulnerabilities in all the organization using asynchronous API call in JSON format:  
`-x vulnerability_names="CVE-2021-45046,CVE-2021-44228,CVE-2021-4104" -c True`  

---

Generate Alerts report using asynchronous API call in excel format:  
`ws_bulk_report_generator -u <USER_KEY>  -k <ORG_TOKEN> -r alerts -t binary -c True`  

---

Generate Plugin Request history report using asynchronous API call in excel format (unlimited results):  
`ws_bulk_report_generator -u <USER_KEY>  -k <ORG_TOKEN> -r request_history -t binary -c True -x plugin=True`  

---

Generate Inventory report using asynchronous API call in excel format:  
`ws_bulk_report_generator -u <USER_KEY>  -k <ORG_TOKEN> -r inventory -t binary -c True`  

<br/>  

# Full Usage:
```shell
usage: ws_bulk_report_generator [-h] -u WS_USER_KEY -k WS_TOKEN [-y {organization,globalOrganization}] -r
                                {alerts,ignored_alerts,resolved_alerts,inventory,lib_dependencies,vulnerability,container_vulnerability,source_files,source_file_inventory,in_house_libraries,in_house,risk,library_location,license_compatibility,due_diligence,attributes,attribution,effective_licenses,bugs,request_history}
                                [-t {unified_json,unified_xlsx,binary,json}] [-s {project,product}] [-a WS_URL] [-o DIR] [-x EXTRA_REPORT_ARGS] [-i INC_TOKENS] [-e EXC_TOKENS]

WhiteSource Bulk Reports Generator

optional arguments:
  -h, --help            show this help message and exit
  -u WS_USER_KEY, --userKey WS_USER_KEY
                        WS User Key
  -k WS_TOKEN, --token WS_TOKEN
                        WS Token
  -y {organization,globalOrganization}, --token_type {organization,globalOrganization}
                        WS Token Type
  -r {alerts,ignored_alerts,resolved_alerts,inventory,lib_dependencies,vulnerability,container_vulnerability,source_files,source_file_inventory,in_house_libraries,in_house,risk,library_location,license_compatibility,due_diligence,at
tributes,attribution,effective_licenses,bugs,request_history}, --report {alerts,ignored_alerts,resolved_alerts,inventory,lib_dependencies,vulnerability,container_vulnerability,source_files,source_file_inventory,in_house_libraries,in
_house,risk,library_location,license_compatibility,due_diligence,attributes,attribution,effective_licenses,bugs,request_history}
                        Report Type to produce
  -t {unified_json,unified_xlsx,binary,json}, --outputType {unified_json,unified_xlsx,binary,json}
                        Type of output
  -s {project,product}, --ReportScope {project,product}
                        Scope of report
  -a WS_URL, --wsUrl WS_URL
                        WS URL
  -o DIR, --reportDir DIR
                        Report Dir
  -x EXTRA_REPORT_ARGS, --extraReportArguments EXTRA_REPORT_ARGS
                        Extra arguments (key=value) to pass the report
  -i INC_TOKENS, --includedTokens INC_TOKENS
                        Included token (Default: All)
  -e EXC_TOKENS, --excludedTokens EXC_TOKENS
                        Excluded token (Default: None)
  -c ASYNCR, --asynchronousCalls ASYNCR
                        Asynchronous API (Default: False)
```
