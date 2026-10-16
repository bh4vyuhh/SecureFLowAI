import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "ai-service"))

from app.engine.factory import get_dlp_engine

engine = get_dlp_engine()

print("=" * 60)
print("TESTING SECUREFLOW AI CALIBRATED DLP ENGINE")
print("=" * 60)

# Test 1: Clean contract / bulletin
with open("data/demo_samples/demo_clean_contract.txt", "r") as f:
    clean_text = f.read()
r1 = engine.scan(clean_text)
print(f"1. Clean Bulletin  -> Tier: {r1.tier} | Risk: {r1.risk_score}% | Action: {r1.action} | Entities: {len(r1.entities)}")
assert r1.action == "ALLOW", f"Clean contract should be ALLOW, got {r1.action}"
assert r1.risk_score < 45, f"Clean contract risk should be < 45, got {r1.risk_score}"

# Test 2: Standard office utility bill
bill = """
MUMBAI ELECTRICITY SUPPLY AND TRANSPORT UNDERTAKING
CONSUMER BILL INVOICE FOR MONTHLY UTILITY CONSUMPTION
Consumer Name: Rajesh Sharma
Address: Flat 402, Greenfield Heights, Andheri West, Mumbai
Total Amount Due: INR 3,450.00
Due Date: 25-OCT-2026
"""
r2 = engine.scan(bill)
print(f"2. Electricity Bill -> Tier: {r2.tier} | Risk: {r2.risk_score}% | Action: {r2.action} | Entities: {len(r2.entities)}")
assert r2.action == "ALLOW", f"Electricity bill should be ALLOW, got {r2.action}"
assert r2.risk_score < 45, f"Electricity bill risk should be < 45, got {r2.risk_score}"

# Test 3: Wire Transfer Leak (IBAN + SWIFT)
leak_wire = """
CONFIDENTIAL WIRE TRANSFER
Beneficiary Account IBAN: DE89370400440532013000
Bank SWIFT BIC: CHASUS33XXX
Amount: $450,000.00 USD
"""
r3 = engine.scan(leak_wire)
print(f"3. Leaked Wire     -> Tier: {r3.tier} | Risk: {r3.risk_score}% | Action: {r3.action} | Entities: {[e.entity_type for e in r3.entities]}")
assert r3.action == "BLOCK", f"Wire leak should be BLOCK, got {r3.action}"
assert r3.risk_score >= 80, f"Wire leak risk should be >= 80, got {r3.risk_score}"

# Test 4: Credit Card Leak
leak_card = "Customer payment records: Card Number 4012-8888-8888-1881 CVV: 891 Exp: 12/28"
r4 = engine.scan(leak_card)
print(f"4. Leaked Card     -> Tier: {r4.tier} | Risk: {r4.risk_score}% | Action: {r4.action} | Entities: {[e.entity_type for e in r4.entities]}")
assert r4.action == "BLOCK", f"Card leak should be BLOCK, got {r4.action}"
assert r4.risk_score >= 80, f"Card leak risk should be >= 80, got {r4.risk_score}"

# Test 5: API Key Leak
leak_key = "Production environment config: API_KEY=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
r5 = engine.scan(leak_key)
print(f"5. Leaked API Key  -> Tier: {r5.tier} | Risk: {r5.risk_score}% | Action: {r5.action} | Entities: {[e.entity_type for e in r5.entities]}")
assert r5.action == "BLOCK", f"Key leak should be BLOCK, got {r5.action}"

print("=" * 60)
print("ALL DLP CALIBRATION TESTS PASSED WITH 100% ACCURACY!")
print("=" * 60)
