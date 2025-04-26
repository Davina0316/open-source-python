# tests/test_mail_ai_integration_to_tmp.py
import logging
from pathlib import Path

import pytest

import hw4_integration.src.main as mail_module


class DummyGmailClient:
    """A dymmy gmail client class for testing, mocking some of the methods."""

    def __init__(self) -> None:
        """Init dummy client."""
        self._connected = False
    def connect(self) -> bool:
        """Connect stub."""
        self._connected = True
        return True
    def get_emails_list(self, mailbox: str, limit: int) -> list[dict[str, str]]:
        """Get dummy email list."""
        return [{"id": "m1"}, {"id": "m2"}][:limit]
    def get_email_content(self, mail_id: str) -> dict[str, str]:
        """Get dummy email content."""
        return {"body": f"body_of_{mail_id}"}

def test_writes_spam_csv_into_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)

    # 1) cd into a temp directory
    monkeypatch.chdir(tmp_path)

    # 2) patch the imports in hw4_integration.main
    monkeypatch.setattr(mail_module, "GmailClientImpl", DummyGmailClient)
    def ret_088(x: str) -> float:
        return len(x) * 0 + 0.88

    monkeypatch.setattr(mail_module, "get_spam_probability", ret_088)

    # 3) run end-to-end
    integration = mail_module.MailAiIntegration()
    assert integration.connect() is True

    bodies, ids = integration.crawl_get_email_content(limit=2)
    integration.analyze_and_write_csv(bodies, ids)

    # 4) assert that spam_results.csv lives in tmp_path
    out_file = tmp_path / "spam_results.csv"
    assert out_file.exists()

    lines = out_file.read_text().splitlines()
    assert lines[0] == "mail_id,Pct_spam"
    # "body_of_m1" is 11 chars → 11 * 0.01 = 0.11 → rounded to 0.11
    assert lines[1] == "m1,0.88"
    assert lines[2] == "m2,0.88"
