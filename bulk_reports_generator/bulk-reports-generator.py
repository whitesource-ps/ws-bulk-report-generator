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
logging.getLogger('WS').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.INFO)
logging.getLogger('chardet').setLevel(logging.INFO)

PROJECT_PARALLELISM_LEVEL = 10
ws_conn = conf = report_method = None


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Bulk Reports Generator')
    parser.add_argument('-u', '--userKey', help="WS User Key", dest='ws_user_key', required=True)
    parser.add_argument('-k', '--token', help="WS Token", dest='ws_token', required=True)
    parser.add_argument('-r', '--report', help="Report Type to produce", choices=ws_utilities.get_report_types(), dest='report', required=True)
    parser.add_argument('-s', '--ReportScope', help="Scope of report", choices=[ws_constants.PROJECT, ws_constants.PRODUCT], dest='scope', default=ws_constants.PROJECT)
    parser.add_argument('-a', '--wsUrl', help="WS URL", dest='ws_url', default="saas")
    parser.add_argument('-c', '--config', help="Location of configuration file", dest='config', default='config.json')

    return parser.parse_args()


def init():
    global ws_conn, conf, report_method
    ws_conn = WS(url=args.ws_url, user_key=args.ws_user_key, token=args.ws_token)
    try:
        fp = open(args.config).read()
        conf = json.loads(fp)
    except FileNotFoundError:
        logging.warning(f"Configuration file: {args.config} was not found")
    except json.JSONDecodeError:
        logging.error(f"Unable to parse file: {args.config}")

    report_method = f"get_{args.report}"
    try:
        report_method = getattr(WS, report_method)
    except AttributeError:
        logging.error(f"report: {args.report} was not found")


def get_report_scopes(conf_dict: dict) -> list:
    def __get_report_tokens__(tokens: list, get_all_scope: bool):
        ret_tokens = []
        if tokens:
            for tok in tokens:
                try:
                    tmp_scope = (ws_conn.get_scope_by_token(token=tok))
                    if tmp_scope['type'] == args.scope:
                        ret_tokens.append(tok)
                    elif tmp_scope['type'] == ws_constants.PRODUCT and args.scope == ws_constants.PROJECT:  # Extract projects from products
                        logging.debug(f"Token: {tok} is of product {tmp_scope['name']}. Adding its projects into scope")
                        prod_scopes = (ws_conn.get_projects(product_token=tok))
                        for s in prod_scopes:
                            ret_tokens.append(s['token'])
                    else:
                        logging.warning(f"Token: {tok} is not of report scope type: {args.scope} and will be skipped")
                except ws_errors.WsSdkError:
                    logging.warning(f"Token: {tok} does not exist and will be skipped")
        elif get_all_scope:                                                                # If no value in inc tokens then take all
            logging.info(f"Getting all tokens of {args.scope}s of the organization")
            prod_scopes = ws_conn.get_scopes(scope_type=args.scope)
            for s in prod_scopes:
                ret_tokens.append(s['token'])
        else:
            logging.debug("No tokens were passed")

        return ret_tokens
    inc_tokens = conf_dict.get('IncludedTokens')
    exc_tokens = conf_dict.get('ExcludedTokens')

    inc_names = conf_dict.get('IncludedNames')
    exc_names = conf_dict.get('ExcludedNames')
    for name in inc_names:
        inc_tokens.extend(ws_conn.get_tokens_from_name(name))

    for name in exc_names:
        exc_tokens.extend(ws_conn.get_tokens_from_name(name))

    # Subtracting tokens from same scope type
    int_tokens = [t for t in inc_tokens if t in exc_tokens]      # Collecting intersected tokens
    inc_tokens = [t for t in inc_tokens if t not in int_tokens]
    exc_tokens = [t for t in exc_tokens if t not in int_tokens]
    logging.debug(f"Shallow filter: removed {len(int_tokens)} from scopes")
    inc_tokens = __get_report_tokens__(inc_tokens, True)
    exc_tokens = __get_report_tokens__(exc_tokens, False)
    total_tokens = [t for t in inc_tokens if t not in exc_tokens]
    logging.debug(f"Deep filter: removed {len(inc_tokens) - len(total_tokens)}  from scopes")

    scopes = []
    if not total_tokens:
        logging.error("No scopes were found to generate reports. Please check configuration")
    else:
        logging.info(f"Found {len(total_tokens)} tokens to generate reports")
        for token in total_tokens:
            scope = ws_conn.get_scope_by_token(token=token)
            filename = f"{scope['type']}_{scope['name']}_{args.report}.{report_method(ws_constants.ReportsData.REPORT_BIN_TYPE)}"
            scope['report_full_name'] = os.path.join(conf['ReportsDir'], filename)
            scopes.append(scope)

    return scopes


def generate_reports_manager(reports_desc_list: list):
    with ThreadPool(processes=PROJECT_PARALLELISM_LEVEL) as pool:
        pool.starmap(worker_generate_report, [(report_desc, ws_conn) for report_desc in reports_desc_list])


def worker_generate_report(report_desc, ws_connector):
    try:
        logging.debug(f"Running {args.report} report on {report_desc['type']}: {report_desc['name']}. location: {report_desc['report_full_name']}")
        report = report_method(ws_connector, token=report_desc['token'], report=True)
        f = open(report_desc['report_full_name'], 'bw')
        f.write(report)
        f.close()
    except ws_errors.WsSdkError or OSError:
        logging.exception("Error producing report")


if __name__ == '__main__':
    args = parse_args()
    init()
    report_scopes = get_report_scopes(conf)
    generate_reports_manager(report_scopes)
