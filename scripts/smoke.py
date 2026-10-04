"""Run the paired-reader StudioNet lifecycle against an existing deployment."""
import json
import os
import time

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet


ADDRESS = "0xd94E9C28EBbFD757b63A3eF975654C5890551Ee5"


def client(variable):
    key = os.environ.get(variable, "").strip()
    if not key:
        raise SystemExit(variable + " is required")
    account = create_account(account_private_key=key)
    return account, create_client(chain=studionet, account=account)


def send(api, method, args):
    tx = api.write_contract(address=ADDRESS, function_name=method, args=args)
    receipt = api.wait_for_transaction_receipt(
        transaction_hash=tx, wait_until="finalized", retries=180,
        interval=5000, full_transaction=True,
    )
    leader = (receipt.get("consensus_data", {}).get("leader_receipt") or [{}])[0]
    if receipt.get("result_name") != "MAJORITY_AGREE" or leader.get("execution_result") != "SUCCESS":
        raise RuntimeError(json.dumps(receipt, default=str))
    return str(tx)


author, author_api = client("AUTHOR_KEY")
reader_a, reader_a_api = client("READER_A_KEY")
reader_b, reader_b_api = client("READER_B_KEY")
rule_id = "AB-LIVE-" + str(int(time.time()))
transactions = {}
transactions["register"] = send(author_api, "register_rule", [
    rule_id, reader_a.address, reader_b.address, "Quiet-room access rule",
    "A member may enter the quiet room after hours when an active booking covers the full visit and no maintenance closure applies.",
    ["An active booking must cover the complete visit.", "A maintenance closure overrides every booking.", "After-hours entry is limited to registered members."],
    ["A registered member has a booking that ends ten minutes before the visit ends.", "A registered member has a complete booking during a posted maintenance closure."],
])
transactions["readingA"] = send(reader_a_api, "submit_reading", [
    rule_id,
    "Full-time coverage is mandatory and any maintenance closure blocks access.",
    [0, 1], ["DENY", "DENY"],
])
transactions["readingB"] = send(reader_b_api, "submit_reading", [
    rule_id,
    "A short booking gap is acceptable, but a maintenance closure still blocks access.",
    [0, 1], ["ALLOW", "DENY"],
])
transactions["compare"] = send(author_api, "compare_readings", [rule_id])
state = author_api.read_contract(address=ADDRESS, function_name="get_rule", args=[rule_id])
if state["state"] != "AMBIGUOUS" or 0 not in state["divergent_example_indexes"]:
    raise RuntimeError(json.dumps(state, default=str))
print(json.dumps({
    "ruleId": rule_id, "transactions": transactions,
    "state": state, "walletDisclosure": "All three wallets and examples are operator-controlled fixtures."
}, indent=2, default=str))

