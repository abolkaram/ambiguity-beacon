from conftest import CONTRACT


CLAUSES = [
    "Members may reserve a shared room for community activities.",
    "Commercial activity requires prior written approval from the steward.",
]
EXAMPLES = [
    "A resident hosts a free neighborhood language exchange.",
    "A tutor charges attendees for a workshop in the shared room.",
]


def setup_rule(vm, deploy, owner, reader_a, reader_b):
    vm.sender = owner
    contract = deploy(CONTRACT)
    contract.register_rule(
        "room-policy", "0x" + reader_a.hex(), "0x" + reader_b.hex(),
        "Shared room use policy",
        "Community activities are welcome, while commercial activity requires prior written approval from the designated steward.",
        CLAUSES, EXAMPLES,
    )
    return contract


def submit_pair(vm, contract, reader_a, reader_b):
    vm.sender = reader_a
    contract.submit_reading("room-policy", "Free community gatherings are allowed, but any paid event needs written steward approval.", [0, 1], ["ALLOW", "DENY"])
    vm.sender = reader_b
    contract.submit_reading("room-policy", "Community purpose is enough for access, including paid educational workshops run for residents.", [0, 1], ["ALLOW", "ALLOW"])


def mock_compare(vm, clause="[1]", example="[1]", equivalent=False):
    vm.mock_llm(r".*Ambiguity Beacon comparison.*", '{"equivalent":' + str(equivalent).lower() + ',"divergent_clause_indexes":' + clause + ',"divergent_example_indexes":' + example + '}')


def test_two_readings_reach_ready_state(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = setup_rule(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    submit_pair(direct_vm, contract, direct_bob, direct_charlie)
    assert contract.get_rule("room-policy")["state"] == "READY"


def test_material_fork_is_indexed(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = setup_rule(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    submit_pair(direct_vm, contract, direct_bob, direct_charlie)
    mock_compare(direct_vm)
    contract.compare_readings("room-policy")
    result = contract.get_rule("room-policy")
    assert result["state"] == "AMBIGUOUS"
    assert result["divergent_clause_indexes"] == [1]
    assert result["divergent_example_indexes"] == [1]


def test_objective_example_difference_cannot_be_omitted(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = setup_rule(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    submit_pair(direct_vm, contract, direct_bob, direct_charlie)
    mock_compare(direct_vm, example="[]")
    with direct_vm.expect_revert("objective example divergence omitted"):
        contract.compare_readings("room-policy")


def test_validator_rejects_forged_equivalence(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = setup_rule(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    submit_pair(direct_vm, contract, direct_bob, direct_charlie)
    mock_compare(direct_vm)
    record = contract.rules["ROOM-POLICY"]
    result = contract._compare(record)
    assert direct_vm.run_validator(leader_result=result) is True
    forged = {"equivalent": True, "divergent_clause_indexes": [], "divergent_example_indexes": []}
    assert direct_vm.run_validator(leader_result=forged) is False


def test_clarification_must_preserve_and_resolve(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = setup_rule(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    submit_pair(direct_vm, contract, direct_bob, direct_charlie)
    mock_compare(direct_vm)
    contract.compare_readings("room-policy")
    direct_vm.clear_mocks()
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r".*Ambiguity Beacon clarification review.*", '{"preserves_boundary":true,"resolves_all":true}')
    contract.clarify("room-policy", "Community activities without participant fees are allowed. Any event charging admission, tuition, sales, or service fees is commercial and requires written steward approval before reservation.")
    result = contract.get_rule("room-policy")
    assert result["state"] == "CLARIFIED"
    assert result["revision"] == 1


def test_roles_must_be_separated(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT)
    with direct_vm.expect_revert("three separated roles"):
        contract.register_rule("bad", "0x" + direct_bob.hex(), "0x" + direct_bob.hex(), "Duplicate readers", "A sufficiently detailed policy rule that can be interpreted in more than one way.", CLAUSES, EXAMPLES)
