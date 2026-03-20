def process_claim(merchant, tribe):
    issued = merchant.issue_claim()
    if not issued:
        return None

    is_true = merchant.claim_is_true()
    validated = tribe.validate_claim(is_true)
    return is_true, validated
