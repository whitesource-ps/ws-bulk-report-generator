import json
import logging
import os
import sys
from multiprocessing import Manager
from multiprocessing.pool import ThreadPool
import argparse

from ws_sdk import WS, ws_constants, ws_errors
from ws_bulk_report_generator._version import __tool_name__, __version__

logging.basicConfig(level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO,
                    format='%(levelname)s %(asctime)s %(thread)d %(name)s: %(message)s',
                    stream=sys.stdout)
logger = logging.getLogger(__tool_name__)


PROJECT_PARALLELISM_LEVEL = int(os.environ.get("PROJECT_PARALLELISM_LEVEL", "10"))
conf = args = None
JSON = 'json'
BINARY = 'binary'
UNIFIED_JSON = "unified_json"
UNIFIED_XLSX = "unified_xlsx"
CONSOLIDATE = [UNIFIED_JSON, UNIFIED_XLSX]
ALL_OUTPUT_TYPES = CONSOLIDATE + [BINARY, JSON]


def parse_args():
    parser = argparse.ArgumentParser(description='WhiteSource Bulk Reports Generator')
    parser.add_argument('-u', '--userKey', help="WS User Key", dest='ws_user_key', type=str, required=True)
    parser.add_argument('-k', '--token', help="WS Token", dest='ws_token', type=str, required=True)
    parser.add_argument('-r', '--report', help="Report Type to produce", type=str, choices=WS.get_report_types(), dest='report', required=True)
    parser.add_argument('-t', '--outputType', help="Type of output", choices=ALL_OUTPUT_TYPES, dest='output_type', default=BINARY)
    parser.add_argument('-s', '--ReportScope', help="Scope of report", type=str, choices=[ws_constants.ScopeTypes.PROJECT, ws_constants.ScopeTypes.PRODUCT], dest='scope', default=ws_constants.ScopeTypes.PROJECT)
    parser.add_argument('-a', '--wsUrl', help="WS URL", dest='ws_url', type=str, default="saas")
    parser.add_argument('-o', '--reportDir', help="Report Dir", dest='dir', default="reports", type=str)
    parser.add_argument('-c', '--config', help="Location of configuration file", dest='config', default='config.json')
    parser.add_argument('-x', '--extraReportArguments', help="Extra arguments (key=value) to pass the report", dest='extra_report_args', type=str)
    parser.add_argument('-i', '--includedTokens', help="Included token (Default: All)", dest='inc_tokens', default=[])
    parser.add_argument('-e', '--excludedTokens', help="Excluded token (Default: None)", dest='exc_tokens', default=[])
    parser.add_argument('-in', '--includedNames', help="Included Scope Names (Default: All)", dest='inc_names', default=[])
    parser.add_argument('-en', '--excludedNames', help="Included Scope Names (Default: None)", dest='exc_names', default=[])

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

    args.ws_conn = WS(url=args.ws_url,
                      user_key=args.ws_user_key,
                      token=args.ws_token,
                      tool_details=(f"ps-{__tool_name__.replace('_', '-')}", __version__))

    try:
        fp = open(args.config).read()
        conf = json.loads(fp)
        args.inc_tokens = conf.get('IncludedTokens')
        args.exc_tokens = conf.get('ExcludedTokens')
        args.inc_names = conf.get('IncludedNames')
        args.exc_names = conf.get('ExcludedNames')
    except FileNotFoundError:
        logger.warning(f"Configuration file: {args.config} was not found")
    except json.JSONDecodeError:
        logger.error(f"Unable to parse file: {args.config}")

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


def get_report_scopes() -> list:
    def __get_report_tokens__(tokens: list, get_all_scope: bool):
        ret_tokens = []
        if tokens:
            for tok in tokens:
                try:
                    tmp_scope = (args.ws_conn.get_scope_by_token(token=tok))
                    if tmp_scope['type'] == args.scope:
                        ret_tokens.append(tok)
                    elif tmp_scope['type'] == ws_constants.ScopeTypes.PRODUCT and args.scope == ws_constants.ScopeTypes.PROJECT:  # Extract projects from products
                        logger.debug(f"Token: {tok} is of product {tmp_scope['name']}. Adding its projects into scope")
                        prod_scopes = (args.ws_conn.get_projects(product_token=tok))
                        for s in prod_scopes:
                            ret_tokens.append(s['token'])
                    else:
                        logger.warning(f"Token: {tok} is not of report scope type: {args.scope} and will be skipped")
                except ws_errors.WsSdkError:
                    logger.warning(f"Token: {tok} does not exist and will be skipped")
        elif get_all_scope:  # If no value in inc tokens then take all
            logger.info(f"Getting all tokens of {args.scope}s of the organization")
            prod_scopes = args.ws_conn.get_scopes(scope_type=args.scope)
            for s in prod_scopes:
                ret_tokens.append(s['token'])
        else:
            logger.debug("No tokens were passed")

        return ret_tokens

    def replace_invalid_chars(directory: str) -> str:
        for char in ws_constants.INVALID_FS_CHARS:
            directory = directory.replace(char, "_")

        return directory

    global args
    for name in args.inc_names:
        args.inc_tokens.extend(args.ws_conn.get_tokens_from_name(name))

    for name in args.exc_names:
        args.exc_tokens.extend(args.ws_conn.get_tokens_from_name(name))

    # Subtracting tokens from same scope type
    args.int_tokens = [t for t in args.inc_tokens if t in args.exc_tokens]  # Collecting intersected tokens
    args.inc_tokens = [t for t in args.inc_tokens if t not in args.int_tokens]
    args.exc_tokens = [t for t in args.exc_tokens if t not in args.int_tokens]
    logger.debug(f"Shallow filter: removed {len(args.int_tokens)} from scopes")
    inc_tokens = __get_report_tokens__(args.inc_tokens, True)
    exc_tokens = __get_report_tokens__(args.exc_tokens, False)
    total_tokens = [t for t in inc_tokens if t not in exc_tokens]
    logger.debug(f"Deep filter: removed {len(inc_tokens) - len(total_tokens)}  from scopes")

    scopes = []
    if not total_tokens:
        logger.error("No scopes were found to generate reports. Please check configuration")
    else:
        logger.info(f"Found {len(total_tokens)} tokens to generate reports")
        for token in total_tokens:
            scope = args.ws_conn.get_scope_by_token(token=token)
            args.report_extension = JSON if args.output_type.endswith(JSON) else args.report_method(WS, ws_constants.ReportsMetaData.REPORT_BIN_TYPE)
            report_name = f"{scope['name']}_{scope['productName']}" if scope['type'] == ws_constants.PROJECT else scope['name']
            filename = f"{scope['type']}_{replace_invalid_chars(report_name)}_{args.report}.{args.report_extension}"
            scope['report_full_name'] = os.path.join(args.dir, filename)
            scopes.append(scope)

    return scopes


def generate_reports_manager(reports_desc_list: list):
    def consolidate_output(q) -> list:
        unified_output = []
        while not q.empty():
            unified_output.extend(q.get(block=True, timeout=0.05))

        return unified_output

    manager = Manager()
    scopes_data_q = manager.Queue()

    with ThreadPool(processes=PROJECT_PARALLELISM_LEVEL) as pool:
        pool.starmap(worker_generate_report, [(report_desc, args, scopes_data_q) for report_desc in reports_desc_list])

    ret = None
    if not scopes_data_q.empty():
        logger.debug("Consolidating queue output from generated reports")
        ret = consolidate_output(scopes_data_q)

    return ret


def worker_generate_report(report_desc, arguments, scopes_data_q):
    try:
        logger.debug(f"Running '{arguments.report}' report on {report_desc['type']}: '{report_desc['name']}'")
        output = arguments.report_method(arguments.ws_conn,
                                         token=report_desc['token'],
                                         report=arguments.is_binary,
                                         **arguments.extra_report_args_d)
        if arguments.output_type in CONSOLIDATE:
            scopes_data_q.put(output)
        else:
            logger.debug(f"Saving report in: {report_desc['report_full_name']}")
            f = open(report_desc['report_full_name'], arguments.write_mode)
            report = output if arguments.is_binary else json.dumps(output)
            f.write(report)
            f.close()

    except ws_errors.WsSdkError or OSError:
        logger.exception("Error producing report")


def generate_xlsx(output, full_path):
    try:
        import xlsxwriter
    except ImportError:
        logger.error(f"Report type is '{args.output_type}' but package 'XlsxWriter' is not installed. Make sure the tool is installed with optional dependency: 'pip install ws-{__tool_name__.replace('-', '_')}[xslx]' ")
        exit(-1)

    # with xlsxwriter.Workbook(full_path) as workbook:
    #     worksheet = workbook.add_worksheet()
    #     # Writing column headers
    #     cell_format = workbook.add_format({'bold': True, 'italic': False})
    #     columns = create_column_data(project_name)


def write_file(output: list):
    report_name = f"{args.ws_conn.get_name()} - {args.report} report"
    filename = f"{report_name}.{args.report_extension}"
    full_path = os.path.join(args.dir, filename)

    if args.output_type == UNIFIED_XLSX:
        logger.debug("TBD: Converting output to Excel")
        generate_xlsx(output, full_path)
    else:
        json.dump(output, full_path, indent=4) 

    logger.info(f"Finished writing filename: '{full_path}'")


def main():
    global args, conf
    args = parse_args()
    init()
    report_scopes = get_report_scopes()
    ret = generate_reports_manager(report_scopes)

    if ret:
        write_file(ret)

    logger.info("Finished running bulk report generator")


if __name__ == '__main__':
    main()

