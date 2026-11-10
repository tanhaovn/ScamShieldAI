from backend.app.ai.domain_intelligence import inspect_url, inspect_urls


def test_brand_subdomain_and_risky_tld_are_flagged():
    finding = inspect_url("http://vietcombank.login-secure-account.top/verify")
    assert finding is not None
    assert finding.score >= 40
    assert finding.level in {"review", "high"}
    assert len(finding.signals) >= 2


def test_normal_https_domain_stays_low():
    finding = inspect_url("https://example.com/docs")
    assert finding is not None
    assert finding.level == "low"


def test_duplicate_hosts_are_collapsed():
    findings = inspect_urls(["https://example.com/a", "https://example.com/b"])
    assert len(findings) == 1
