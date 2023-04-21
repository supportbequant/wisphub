#!/usr/bin/python3

################################################################################
#
# Copyright (c) 2022 Bequant S.L.
# All rights reserved.
#
# This product or document is proprietary to and embodies the
# confidential technology of Bequant S.L., Spain.
# Possession, use, duplication or distribution of this product
# or document is authorized only pursuant to a valid written
# license from Bequant S.L.
#
#
################################################################################

# Avoid insecure warning when issuing REST queries
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import argparse
import requests
import json
import logging
import sys

################################################################################

def printResponseDetails(rsp):
  logger = logging.getLogger(__name__)
  if logger.getEffectiveLevel() != logging.DEBUG:
    return

  logger.debug("")
  logger.debug("====== Request =======")
  logger.debug("%s to URL %s" % (rsp.request.method, rsp.request.url))
  for h in rsp.request.headers:
    logger.debug("%s: %s" % (h, rsp.request.headers[h]))
  logger.debug("")
  if rsp.request.body:
    logger.debug(rsp.request.body)
    logger.debug("")
  logger.debug("====== Response ======")
  logger.debug("HTTP/1.1 %d" % rsp.status_code)
  for h in rsp.headers:
    logger.debug("%s: %s" % (h, rsp.headers[h]))
  logger.debug("")
  logger.debug(json.dumps(rsp.json(), indent=4, separators=(',', ': ')))

################################################################################

def getWisphubEntries(url, headers):

  offset = 0
  page = 1
  pageSize = 5000
  remaining = True
  entries = []
  logger = logging.getLogger(__name__)

  while remaining:
    logger.info("GET to %s, page %d" % (url, page))
    rsp = requests.get(url, headers=headers, params={"offset": offset, "limit": pageSize}, verify=False)  
    printResponseDetails(rsp)
    rspJson = rsp.json()
    if rsp.status_code != 200:
      raise Exception("Bad query %d (page %d)" % (rsp.status_code, page))
    for e in rspJson["results"]:
      entries.append(e)
    total = rspJson["count"]
    remaining = (total > len(entries))
    offset += pageSize
    page += 1

  return entries

################################################################################

if __name__ == "__main__":

  parser = argparse.ArgumentParser(
    description="""
  Synchronizes speed limits in Wisphub clients with BQN rate policies.

  Requires an API KEY in Wisphub and the REST API enabled in BQN.

  BQN Rate policies are identified by Wisphub "plan_internet"->"nombre", with spaces replaced by undescores.
  BQN subscribers are identified by "nombre" in Wisphub.
  Clients in "estado" == "Suspendido" have their traffic blocked by BQN (Wisphub_block policy).

  Known limitations:
  - Policy speed limits cannot be obtained from Wisphub. They must be configured in the BQN.
  - Multiple IP addresses in same client are not supported.
  - The first time it may take minutes to run. Following executions will send to BQN only client changes
    and will be quicker.
  - If the synchronization fails, no retry is attempted (must be done externally).
  - No scheduling of script execution (must be done externally).
  """, formatter_class=argparse.RawTextHelpFormatter)

  parser.add_argument('-w', dest="wisphub", type=str, default="api.wisphub.net",
      help='Wispro billing URL (default api.wisphub.net')
  parser.add_argument('-b', dest="bqn", type=str, default="192.168.0.120",
      help='BQN OAM IP (default 192.168.0.120')
  parser.add_argument('-v', '--verbose', action='count', dest='verbose', default=0,
                    help="Display extra informationt (repeat for increased verbosity)")
  parser.add_argument('user', metavar='BQN-USER', type=str, help='BQN REST API user')
  parser.add_argument('password', metavar='BQN-PASSWORD', type=str, help='BQN REST API password')
  parser.add_argument('key', metavar='API-KEY', type=str, help='Wisphub REST API key')
  args = parser.parse_args()

  logger = logging.getLogger(__name__)
  if args.verbose == 0:
    logger.setLevel(logging.WARNING)
  elif args.verbose == 1:
    logger.setLevel(logging.INFO)
  else:
    logger.setLevel(logging.DEBUG)
  logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
  
  wishubUrl = "https://" + args.wisphub + "/api"
  wisproHeaders = {
   "Authorization": "Api-Key %s" % args.key,
   "Accept": "application/json",
   "Accept-Encoding": "gzip, deflate",
   "Connection": "keep-alive"
  }

  clients = getWisphubEntries(wishubUrl + '/clientes', wisproHeaders)

  bqnUrl = "https://" + args.bqn + ":3443/api/v1"
  bqnHeaders = {
    "content-type": "application/json", 
    "Accept-Charset": "UTF-8"
  }

  # Generate a block policy to enforce inactive clients
  blockPolicy = "Wisphub_block"
  payload = {"policyId": "block", "rateLimitDownlink": {"rate": 0}, "rateLimitUplink": {"rate": 0}}
  rsp = requests.post(bqnUrl + "/policies/rate/" + blockPolicy, headers=bqnHeaders, json=payload, auth=(args.user, args.password), verify=False) 
  printResponseDetails(rsp)

  rsp = requests.get(bqnUrl + "/subscribers", auth=(args.user, args.password), verify=False)
  subsInBqn = rsp.json()["items"]
   
  logger.info('{:<15} {:<20} {:<9} {:<9} {:<9} {:<12}'.format("IP", "PLAN", "PLAN-ID", "state", "Id", "Name"))
  for c in clients:
    logger.info('{:>15} {:<20} {:>9} {:>9} {:>9} {:<12}'.format(c["ip"], c["plan_internet"]["nombre"], c["plan_internet"]["id"], c["estado"], c["id_servicio"], c["nombre"]))
    # Inactive clients are blocked
    if c["estado"] == "Suspendido":
      payload = {"subscriberId": "%s" % c["nombre"], "policyRate": "%s" % blockPolicy}
      rsp = requests.post(bqnUrl + "/subscribers/" + c["ip"], headers=bqnHeaders, json=payload, auth=(args.user, args.password), verify=False)
      printResponseDetails(rsp)
    else:
      planName = c["plan_internet"]["nombre"].replace(' ', '_')
      matches = [x for x in subsInBqn if x["subscriberIp"] == c["ip"]]
      if len(matches) == 1 and matches[0]["policyRate"] == planName:
        pass  # No update needed
      else:
        payload = {"subscriberId": "%s" % c["nombre"], "policyRate": "%s" % planName}
        rsp = requests.post(bqnUrl + "/subscribers/" + c["ip"], headers=bqnHeaders, json=payload, auth=(args.user, args.password), verify=False)
        printResponseDetails(rsp) 




