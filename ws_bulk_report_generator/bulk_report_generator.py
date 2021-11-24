import json
import logging
import os
import sys
from multiprocessing.pool import ThreadPool

from ws_sdk import WS, ws_constants, ws_errors, ws_utilities

logging.basicConfig(level=logging.INFO,
                    # format='%(levelname)s %(asctime)s %(thread)d: %(message)s',
                    stream=sys.stdout
                    )
from ws_bulk_report_generator._version import __tool_name__, __version__

PROJECT_PARALLELISM_LEVEL = 10
ws_conn = conf = args = None
JSON = 'json'
BINARY = 'binary'


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Bulk Reports Generator')
    parser.add_argument('-u', '--userKey', help="WS User Key", dest='ws_user_key', required=True)
    parser.add_argument('-k', '--token', help="WS Token", dest='ws_token', required=True)
    parser.add_argument('-r', '--report', help="Report Type to produce", choices=WS.get_report_types(), dest='report', required=True)
    parser.add_argument('-s', '--ReportScope', help="Scope of report", choices=[ws_constants.ScopeTypes.PROJECT, ws_constants.ScopeTypes.PRODUCT], dest='scope', default=ws_constants.ScopeTypes.PROJECT)
    parser.add_argument('-a', '--wsUrl', help="WS URL", dest='ws_url', default="saas")
    parser.add_argument('-o', '--reportDir', help="Report Dir", dest='dir', default="reports")
    parser.add_argument('-t', '--outputType', help="Type of output", choices=[BINARY, JSON], dest='output_type', default=BINARY)
    parser.add_argument('-c', '--config', help="Location of configuration file", dest='config', default='config.json')

    parser.add_argument('-i', '--includedTokens', help="Report Dir", dest='inc_tokens', default=[])
    parser.add_argument('-e', '--excludedTokens', help="Report Dir", dest='exc_tokens', default=[])
    parser.add_argument('-in', '--includedNames', help="Report Dir", dest='inc_names', default=[])
    parser.add_argument('-en', '--excludedNames', help="Report Dir", dest='exc_names', default=[])

    return parser.parse_args()


def init():
    global ws_conn, conf, args
    ws_conn = WS(url=args.ws_url,
                 user_key=args.ws_user_key,
                 token=args.ws_token,
                 tool_details=(f"ps-{__tool_name__.replace('_','-')}", __version__))

    try:
        fp = open(args.config).read()
        conf = json.loads(fp)
        args.inc_tokens = conf.get('IncludedTokens')
        args.exc_tokens = conf.get('ExcludedTokens')
        args.inc_names = conf.get('IncludedNames')
        args.exc_names = conf.get('ExcludedNames')
    except FileNotFoundError:
        logging.warning(f"Configuration file: {args.config} was not found")
    except json.JSONDecodeError:
        logging.error(f"Unable to parse file: {args.config}")

    args.report_method = f"get_{args.report}"
    try:
        args.report_method = getattr(WS, args.report_method)
    except AttributeError:
        logging.error(f"report: {args.report} was not found")

    if not os.path.exists(args.dir):
        logging.info(f" Creating directory: {args.dir}")
        os.makedirs(args.dir)

    args.is_binary = True if args.output_type == BINARY else False
    args.write_mode = 'bw' if args.is_binary else 'w'


def get_report_scopes() -> list:
    def __get_report_tokens__(tokens: list, get_all_scope: bool):
        ret_tokens = []
        if tokens:
            for tok in tokens:
                try:
                    tmp_scope = (ws_conn.get_scope_by_token(token=tok))
                    if tmp_scope['type'] == args.scope:
                        ret_tokens.append(tok)
                    elif tmp_scope['type'] == ws_constants.ScopeTypes.PRODUCT and args.scope == ws_constants.ScopeTypes.PROJECT:  # Extract projects from products
                        logging.debug(f"Token: {tok} is of product {tmp_scope['name']}. Adding its projects into scope")
                        prod_scopes = (ws_conn.get_projects(product_token=tok))
                        for s in prod_scopes:
                            ret_tokens.append(s['token'])
                    else:
                        logging.warning(f"Token: {tok} is not of report scope type: {args.scope} and will be skipped")
                except ws_errors.WsSdkError:
                    logging.warning(f"Token: {tok} does not exist and will be skipped")
        elif get_all_scope:  # If no value in inc tokens then take all
            logging.info(f"Getting all tokens of {args.scope}s of the organization")
            prod_scopes = ws_conn.get_scopes(scope_type=args.scope)
            for s in prod_scopes:
                ret_tokens.append(s['token'])
        else:
            logging.debug("No tokens were passed")

        return ret_tokens

    global args
    for name in args.inc_names:
        args.inc_tokens.extend(ws_conn.get_tokens_from_name(name))

    for name in args.exc_names:
        args.exc_tokens.extend(ws_conn.get_tokens_from_name(name))

    # Subtracting tokens from same scope type
    args.int_tokens = [t for t in args.inc_tokens if t in args.exc_tokens]  # Collecting intersected tokens
    args.inc_tokens = [t for t in args.inc_tokens if t not in args.int_tokens]
    args.exc_tokens = [t for t in args.exc_tokens if t not in args.int_tokens]
    logging.debug(f"Shallow filter: removed {len(args.int_tokens)} from scopes")
    inc_tokens = __get_report_tokens__(args.inc_tokens, True)
    exc_tokens = __get_report_tokens__(args.exc_tokens, False)
    total_tokens = [t for t in inc_tokens if t not in exc_tokens]
    logging.debug(f"Deep filter: removed {len(inc_tokens) - len(total_tokens)}  from scopes")

    scopes = []
    if not total_tokens:
        logging.error("No scopes were found to generate reports. Please check configuration")
    else:
        logging.info(f"Found {len(total_tokens)} tokens to generate reports")
        for token in total_tokens:
            scope = ws_conn.get_scope_by_token(token=token)
            report_extension = JSON if args.output_type == JSON else args.report_method(WS, ws_constants.ReportsMetaData.REPORT_BIN_TYPE)
            filename = f"{scope['type']}_{scope['name']}_{args.report}.{report_extension}"
            scope['report_full_name'] = os.path.join(args.dir, filename)
            scopes.append(scope)

    return scopes


def generate_reports_manager(reports_desc_list: list):
    with ThreadPool(processes=PROJECT_PARALLELISM_LEVEL) as pool:
        pool.starmap(worker_generate_report, [(report_desc, ws_conn) for report_desc in reports_desc_list])


def worker_generate_report(report_desc, ws_connector):
    try:
        logging.debug(f"Running {args.report} report on {report_desc['type']}: {report_desc['name']}. location: {report_desc['report_full_name']}")
        output = args.report_method(ws_connector, token=report_desc['token'], report=args.is_binary)
        f = open(report_desc['report_full_name'], args.write_mode)
        report = output if args.is_binary else json.dumps(output)
        f.write(report)
        f.close()
    except ws_errors.WsSdkError or OSError:
        logging.exception("Error producing report")


def main():
    global args, conf
    args = parse_args()
    init()
    report_scopes = get_report_scopes()
    generate_reports_manager(report_scopes)


if __name__ == '__main__':
    main()

