[![Logo](https://resources.mend.io/mend-sig/logo/mend-dark-logo-horizontal.png)](https://www.mend.io/)
[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/whitesource-ps/ws-bulk-report-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/whitesource-ps/ws-bulk-report-generator/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/ws-bulk-report-generator?style=plastic)](https://pypi.org/project/ws-bulk-report-generator/)
# [Mend Bulk Report Generator](https://github.com/whitesource-ps/ws-bulk-report-generator)
CLI Tool to generate reports on multiple products or projects.
* The tool allows including and excluding scopes by stating their tokens.
* Report scope (`-s, --ReportScope`) determines whether reports run on projects or products.
* If included scopes (via `-i, --includedTokens`) are not specified, the tool runs reports on **all** scopes.
* Report data exported by default in binary format (i.e., Excel or PDF) or JSON.
* Recommended using -o parameter for specifying output-dir. Otherwise, the output stored in the running dir (which is pip install cmd work with, and it depends on your OS)

## Supported Operating Systems
- **Linux (Bash):**	CentOS, Debian, Ubuntu, RedHat
- **Windows (PowerShell):**	10, 2012, 2016

## Prerequisites
* Python 3.6+

## Installation and Execution by pulling package from PyPi:
1. Execute `pip install ws-bulk-report-generator`
2. Run report: `ws_bulk_report_generator -u <USER_KEY> -k <ORG_TOKEN> -r <REPORT_NAME> -o <OUTPUT_PATH>`
>* *Note:  If installing packages as a non-root user, insure to include the path to the executables within the Operating System paths.*

## Examples:
Generate Due Diligence Reports (file per product) on all products within an organization in JSON format:  
`ws_bulk_report_generator -u <USER_KEY> -k <ORG_TOKEN> -o <OUTPUT_PATH> -r due_diligence -t json`

---

Generate Due Diligence Reports (file per project) on all projects within an organization in JSON format:  
`ws_bulk_report_generator -u <USER_KEY> -k <ORG_TOKEN> -o <OUTPUT_PATH> -s project -r due_diligence -t json`

---

Generate Risk Reports (PDF format) on all products (file per product) within an organization:  
`ws_bulk_report_generator -a app-eu -u <USER_KEY> -k <ORG_TOKEN> -o <OUTPUT_PATH> -r risk`

---

Search for log4j 3 recent vulnerabilities in the entire organization and get output in a single unified JSON:  
`ws_bulk_report_generator -a di.whitesourcesoftware.com -u <USER_KEY> -k <ORG_TOKEN> -o <OUTPUT_PATH> -r vulnerability -t unified_json -x vulnerability_names="CVE-2021-45046,CVE-2021-44228,CVE-2021-4104"`  
* *Note: The output produces only if the specified CVEs were discovered.*

---

Generate Inventory report filtered by 'libwebp-dev_0.6.1-2_amd64.deb' and get a unified JSON for the entire organization:  
`ws_bulk_report_generator -u <USER_KEY> -k <ORG_TOKEN> -o <OUTPUT_PATH> -r inventory -t unified_json -x lib_name=libwebp-dev_0.6.1-2_amd64.deb`

---

Generate Security Alerts report and get a unified JSON for all organizations within a Global organization (Note: user must be defined in each organization):  
`ws_bulk_report_generator -u <USER_KEY> -k <ORG_TOKEN> -o <OUTPUT_PATH> -r inventory -t unified_json -y globalOrganization`

---

Generate Vulnerability report and get a unified Excel report on 2 specific products in the organization (-s project means the API calls run on the project level behind the scenes, used when timeouts in the API response):  
`ws_bulk_report_generator -u <USER_KEY>  -k <ORG_TOKEN> -o <OUTPUT_PATH> -r vulnerability -t unified_xlsx -i "<PRODCUCT_TOKEN_1> , <PRODCUCT_TOKEN_2> -s project"`

---


>**NEW!** USING ASYNCHRONOUS API for large organizations.  
Supported reports: `inventory`, `vulnerability`, `alerts`, `plugin request history`

The TIMEOUT is 6 minutes, meaning it's checking for the report status READY for 6 min before moving to the next one. If it's not ready in 6 minutes, the tool logs the reportStatusId for manually checking the status (and downloading), and moves along. The timeout will be configurable in the following releases.

Generate Vulnerability report using asynchronous API calls in Excel format:  
`ws_bulk_report_generator -u <USER_KEY>  -k <ORG_TOKEN> -o <OUTPUT_PATH> -r vulnerability -t binary -c True`

---

Search for log4j 3 recent vulnerabilities in the entire organization using asynchronous API call and get output per each Product in JSON format:  
`ws_bulk_report_generator -u <USER_KEY> -k <ORG_TOKEN> -o <OUTPUT_PATH> -r vulnerability -t json -x vulnerability_names="CVE-2021-45046,CVE-2021-44228,CVE-2021-4104" -c True`  
* *Note: The output produces only if the specified CVEs were discovered.* 

---

Generate Security Alerts report using asynchronous API calls in Excel format:  
`ws_bulk_report_generator -u <USER_KEY>  -k <ORG_TOKEN> -o <OUTPUT_PATH> -r alerts -t binary -c True`

---

Generate Plugin Request history report using asynchronous API calls in Excel format (unlimited results):  
`ws_bulk_report_generator -u <USER_KEY>  -k <ORG_TOKEN> -o <OUTPUT_PATH> -r request_history -t binary -c True -x plugin=True`

---

Generate Inventory report using asynchronous API calls in Excel format:  
`ws_bulk_report_generator -u <USER_KEY>  -k <ORG_TOKEN> -o <OUTPUT_PATH> -r inventory -t binary -c True`

<br/>  

# Full Usage:
```shell
usage: ws_bulk_report_generator [-h] -u WS_USER_KEY -k WS_TOKEN [-y {organization,globalOrganization}] -r
                                {alerts,ignored_alerts,resolved_alerts,inventory,lib_dependencies,vulnerability,container_vulnerability,source_files,source_file_inventory,in_house_libraries,in_house,risk,library_location,license_compatibility,due_diligence,attributes,attribution,effective_licenses,bugs,request_history(-x plugin=true)}
                                [-t {unified_json,unified_xlsx,binary,json}] [-s {project,product}] [-a WS_URL] [-o DIR] [-x EXTRA_REPORT_ARGS] [-i INC_TOKENS] [-e EXC_TOKENS] [-c {True,False}]

Mend Bulk Reports Generator

optional arguments:
  -h, --help            show this help message and exit
  -u WS_USER_KEY, --userKey WS_USER_KEY
                        WS User Key
  -k WS_TOKEN, --token WS_TOKEN
                        WS Token(s) (Comma Separated)
  -y {organization,globalOrganization}, --token_type {organization,globalOrganization}
                        WS Token Type
  -r {alerts,ignored_alerts,resolved_alerts,inventory,lib_dependencies,vulnerability,container_vulnerability,source_files,source_file_inventory,in_house_libraries,in_house,risk,library_location,license_compatibility,due_diligence,at
               tributes,attribution,effective_licenses,bugs,request_history}, --report 
                        Report Type to produce
  -t {unified_json,unified_xlsx,binary(i.e., Excel or PDF),json}, --outputType 
                        Type of output
  -s {project,product}, --ReportScope 
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