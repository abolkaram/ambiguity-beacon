"""Deploy the exact repository contract to StudioNet."""
import json
import os
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet


def main():
    key = os.environ.get("GENLAYER_PRIVATE_KEY", "").strip()
    if not key:
        raise SystemExit("GENLAYER_PRIVATE_KEY is required")
    source = (Path(__file__).parents[1] / "contracts" / "contract.py").read_text(encoding="utf-8")
    account = create_account(account_private_key=key)
    client = create_client(chain=studionet, account=account)
    tx_hash = client.deploy_contract(code=source, args=[])
    print("deployment_tx=" + str(tx_hash), flush=True)
    receipt = client.wait_for_transaction_receipt(
        transaction_hash=tx_hash, wait_until="finalized", retries=180,
        interval=5000, full_transaction=True,
    )
    leader = (receipt.get("consensus_data", {}).get("leader_receipt") or [{}])[0]
    print(json.dumps({
        "transaction": str(tx_hash),
        "address": receipt.get("data", {}).get("contract_address") or receipt.get("to_address"),
        "consensus": receipt.get("result_name"),
        "execution": leader.get("execution_result"),
        "wallet": account.address,
    }, default=str), flush=True)


if __name__ == "__main__":
    main()

