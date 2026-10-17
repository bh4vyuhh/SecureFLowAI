-- Initial Seed Data for Security Policies
INSERT INTO security_policies (name, block_threshold, remediate_threshold, allow_threshold, whitelisted_domains, default_remediation_action, is_active, updated_at)
SELECT 'Global Banking Financial DLP Policy', 80, 45, 0, '@visa.com,@mastercard.com,clearinghouse.bank.org,swift.com,internal.bank.com', 'MASK', TRUE, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM security_policies WHERE name = 'Global Banking Financial DLP Policy');
