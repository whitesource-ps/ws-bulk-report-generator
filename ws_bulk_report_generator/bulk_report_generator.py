import concurrent
import json
import logging
import os
from copy import copy
from datetime import datetime
import argparse
from concurrent.futures import ThreadPoolExecutor

from ws_sdk import WS, ws_constants, ws_errors
from ws_bulk_report_generator._version import __tool_name__, __version__, __description__

is_debug = logging.DEBUG if bool(os.environ.get("DEBUG", 0)) else logging.INFO

logger = logging.getLogger(__tool_name__)
logger.setLevel(logging.DEBUG)

sdk_logger = logging.getLogger(WS.__module__)
sdk_logger.setLevel(is_debug)

formatter = logging.Formatter('%(levelname)s %(asctime)s %(thread)d %(name)s: %(message)s')
s_handler = logging.StreamHandler()
s_handler.setFormatter(formatter)
s_handler.setLevel(is_debug)
logger.addHandler(s_handler)
sdk_logger.addHandler(s_handler)
sdk_logger.propagate = False


PROJECT_PARALLELISM_LEVEL = int(os.environ.get("PROJECT_PARALLELISM_LEVEL", "10"))
conf = args = None
JSON = 'json'
BINARY = 'binary'
UNIFIED_JSON = "unified_json"
UNIFIED_XLSX = "unified_xlsx"
UNIFIED = [UNIFIED_JSON, UNIFIED_XLSX]
ALL_OUTPUT_TYPES = UNIFIED + [BINARY, JSON]


def parse_args():
    parser = argparse.ArgumentParser(description='WhiteSource Bulk Reports Generator')
    parser.add_argument('-u', '--userKey', help="WS User Key", dest='ws_user_key', type=str, required=True)
    parser.add_argument('-k', '--token', help="WS Token", dest='ws_token', type=str, required=True)
    parser.add_argument('-y', '--token_type', help="WS Token Type", dest='ws_token_type', choices=[ws_constants.ScopeTypes.ORGANIZATION, ws_constants.ScopeTypes.GLOBAL], type=str, default=None)
    parser.add_argument('-r', '--report', help="Report Type to produce", type=str, choices=WS.get_report_types(), dest='report', required=True)
    parser.add_argument('-t', '--outputType', help="Type of output", choices=ALL_OUTPUT_TYPES, dest='output_type', default=BINARY)
    parser.add_argument('-s', '--ReportScope', help="Scope of report", type=str, choices=[ws_constants.ScopeTypes.PROJECT, ws_constants.ScopeTypes.PRODUCT], dest='report_scope_type', default=ws_constants.ScopeTypes.PRODUCT)
    parser.add_argument('-a', '--wsUrl', help="WS URL", dest='ws_url', type=str, default="saas")
    parser.add_argument('-o', '--reportDir', help="Report Dir", dest='dir', default="reports", type=str)
    parser.add_argument('-x', '--extraReportArguments', help="Extra arguments (key=value) to pass the report", dest='extra_report_args', type=str)
    parser.add_argument('-i', '--includedTokens', help="Included token (Default: All)", dest='inc_tokens', default=[])
    parser.add_argument('-e', '--excludedTokens', help="Excluded token (Default: None)", dest='exc_tokens', default=[])

    return parser.parse_args()


def init():
    def get_extra_report_args(extra_report_args: str) -> dict:
        """
        Function to extract extra report argument and parse it to key value dictionary where value can be a string or a list (comma seperated).
        :param extra_report_args: string that of key=val or key=val1,val2...
        :return: dictionary
        """
        ret = {}
        if extra_report_args:
            extra_report_args_l = extra_report_args.split("=")
            report_args_val_l = extra_report_args_l[1].split(',')

            if len(report_args_val_l) > 1:
                extra_report_args_l[1] = [value.strip() for value in report_args_val_l]
            ret = {extra_report_args_l[0]: extra_report_args_l[1]}
            logger.debug(f"Extra arguments to pass the report: {ret}")

        return ret

    global conf, args
    if args.ws_token_type is None:
        # args.ws_token_type = WS.discover_token_type(user_key=args.ws_user_key, token=args.ws_user_key)    # TBD
        args.ws_token_type = ws_constants.ScopeTypes.ORGANIZATION

    args.ws_conn = WS(url=args.ws_url,
                      user_key=args.ws_user_key,
                      token=args.ws_token,
                      token_type=args.ws_token_type,
                      tool_details=(f"ps-{__tool_name__.replace('_', '-')}", __version__),
                      timeout=3600)

    args.report_method = f"get_{args.report}"
    try:
        args.report_method = getattr(WS, args.report_method)
    except AttributeError:
        logger.error(f"report: {args.report} was not found")

    if not os.path.exists(args.dir):
        logger.info(f"Creating directory: {args.dir}")
        os.makedirs(args.dir)

    args.extra_report_args_d = get_extra_report_args(args.extra_report_args)
    args.is_binary = True if args.output_type == BINARY else False
    args.write_mode = 'bw' if args.is_binary else 'w'


def get_reports_scopes() -> list:
    orgs = None
    if args.ws_token_type == ws_constants.ScopeTypes.GLOBAL:
        orgs = args.ws_conn.get_organizations()
        logger.info(f"Found: {len(orgs)} Organizations under Global Organization token: {args.ws_token}")

    orgs = [org['orgToken'] for org in orgs] if isinstance(orgs, list) else [args.ws_token]
    scopes, errors = generic_thread_pool_m(orgs, get_reports_scopes_from_org_w)
    if args.exc_tokens:
        scopes = [s for s in scopes if s['token'] in args.exc_tokens]

    return scopes


def generic_thread_pool_m(ent_l: list, worker: callable) -> tuple:
    data_l = []
    errors = []
    with ThreadPoolExecutor(max_workers=PROJECT_PARALLELISM_LEVEL) as executer:
        futures = [executer.submit(worker, ent) for ent in ent_l]
        for future in concurrent.futures.as_completed(futures):
            temp_l = future.result()
            if temp_l:
                data_l.extend(temp_l)

        return data_l, errors


def get_reports_scopes_from_org_w(org_token) -> list:
    def replace_invalid_chars(directory: str) -> str:
        for char in ws_constants.INVALID_FS_CHARS:
            directory = directory.replace(char, "_")

        return directory

    def prep_scope(report_scopes):
        for s in report_scopes:
            args.report_extension = JSON if args.output_type.endswith(JSON) else args.report_method(WS, ws_constants.ReportsMetaData.REPORT_BIN_TYPE)
            report_name = f"{s['name']}_{s.get('productName')}" if s['type'] == ws_constants.PROJECT else s['name']
            filename = f"{s['type']}_{replace_invalid_chars(report_name)}_{args.report}.{args.report_extension}"
            s['report_full_name'] = os.path.join(args.dir, filename)
            s['ws_conn'] = org_conn

    global args
    org_conn = copy(args.ws_conn)
    org_conn.token_type = ws_constants.ScopeTypes.ORGANIZATION
    org_conn.token = org_token
    if args.inc_tokens:
        inc_tokens_l = [t.strip() for t in args.inc_tokens.split(',')]
        scopes = []
        for token in inc_tokens_l:
            scopes.append(org_conn.get_scope_by_token(token=token, token_type=args.report_scope_type))
    else:
        try:
            scopes = org_conn.get_scopes(scope_type=args.report_scope_type)
        except ws_errors.WsSdkServerInactiveOrg:
            logger.warning(f"Organization: '{org_token}' is disabled and will be skipped")

    prep_scope(scopes)

    return scopes


def generate_report_w(report_desc):
    ret = None
    logger.info(f"Running '{args.report}' report on {report_desc['type']}: '{report_desc['name']}'")
    output = args.report_method(report_desc['ws_conn'],
                                token=(report_desc['token'], args.report_scope_type),
                                report=args.is_binary,
                                **args.extra_report_args_d)
    if args.output_type in UNIFIED:
        if output:
            ret = output
        else:
            logging.debug(f"Report '{args.report}' returned empty on {report_desc['type']}: '{report_desc['name']}'")
    else:
        logger.debug(f"Saving report in: {report_desc['report_full_name']}")
        f = open(report_desc['report_full_name'], args.write_mode)
        report = output if args.is_binary else json.dumps(output)
        f.write(report)
        f.close()

    return ret


def generate_xlsx(output, full_path):
    def generate_row_data(col_names: list, d: dict) -> list:
        row_data_l = []
        for c in col_names:
            cell_val = d.get(c)
            if isinstance(cell_val, (list, dict)):
                cell_val = json.dumps(cell_val)
            row_data_l.append(cell_val)

        return row_data_l

    def generate_table_labels(o: list) -> list:
        col_names = args.report_method(WS, ws_constants.ReportsMetaData.COLUMN_NAMES)
        if not col_names:
            col_names = o[0].keys()

        for c_num, c_name in enumerate(col_names):
            worksheet.write(0, c_num, c_name, cell_format)

        return col_names

    try:
        import xlsxwriter
    except ImportError:
        logger.error(f"Report type is '{args.output_type}' but package 'XlsxWriter' is not installed. Make sure the tool is installed with optional dependency: 'pip install ws-{__tool_name__.replace('-', '_')}[xslx]' ")
        exit(-1)

    with xlsxwriter.Workbook(full_path) as workbook:
        worksheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'bold': True, 'italic': False})
        column_names = generate_table_labels(output)

        last_row = 1
        for row_num, row_data in enumerate(output):
            worksheet.write_row(row_num + last_row, 0, generate_row_data(column_names, row_data))


def write_unified_file(output: list):
    report_name = f"{args.ws_conn.get_name()} - {args.report} report"
    filename = f"{report_name}.{args.report_extension}"
    full_path = os.path.join(args.dir, filename)

    if args.output_type == UNIFIED_XLSX:
        logger.debug("Converting output to Excel")
        generate_xlsx(output, full_path)
    else:
        with open(full_path, args.write_mode) as fp:
            json.dump(output, fp)

    logger.info(f"Finished writing filename: '{full_path}'")


def generate_reports(report_scopes: list):
    return generic_thread_pool_m(ent_l=report_scopes, worker=generate_report_w)


def handle_unified_report(output):
    if output:
        write_unified_file(output)
    else:
        logger.info("No data returned. No report will be saved")


def print_errors(errors: list):
    for error in errors:
        logger.error(f"Error: {error}")


def main():
    global args, conf
    start_time = datetime.now()
    args = parse_args()
    logger.info(f"Start running {__description__} on token {args.ws_token}. Parallelism level: {PROJECT_PARALLELISM_LEVEL}")
    init()
    report_scopes = get_reports_scopes()
    ret, errors = generate_reports(report_scopes)

    if args.output_type in UNIFIED:
        handle_unified_report(ret)

    print_errors(errors)
    logger.info(f"Finished running {__description__}. Run time: {datetime.now() - start_time}")


if __name__ == '__main__':
    main()
