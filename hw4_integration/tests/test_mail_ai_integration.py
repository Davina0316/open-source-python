"""Test integration-level tests for MailAiIntegration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from hw4_integration.src.main import MailAiIntegration
from inbox_impl.src.inbox_impl._impl import GmailClientImpl as RealGmailClientImpl

if TYPE_CHECKING:
    # Only used for type hint
    from pathlib import Path
    from unittest.mock import MagicMock

    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture(autouse=True)
def stub_gmail(
    monkeypatch: MonkeyPatch,
    mocker: MockerFixture,
) -> Any:
    """Replace GmailClientImpl with a fake object for unit-level tests."""
    fake_client: Any = mocker.MagicMock(name="FakeGmailClient")
    fake_client.connect.return_value = True
    fake_client.get_emails_list.return_value = [{"id": "1"}]
    fake_client.get_email_content.return_value = {"body": "hello world"}

    monkeypatch.setattr(
        "hw4_integration.src.main.GmailClientImpl",
        lambda: fake_client,
        raising=True,
    )
    return fake_client


@pytest.fixture
def integration() -> MailAiIntegration:
    """Provide a fresh instance for each test."""
    return MailAiIntegration()


def test_connect_success(
    integration: MailAiIntegration,
    stub_gmail: Any,
) -> None:
    """`connect()` returns True and calls Gmail once."""
    result: bool = integration.connect()
    assert result is True
    stub_gmail.connect.assert_called_once()


def test_crawl_get_email_content(
    integration: MailAiIntegration,
    stub_gmail: Any,
) -> None:
    """Should fetch exactly the bodies and IDs returned by the fake client, and should propagate the `limit` argument unchanged."""
    bodies: list[str]
    ids: list[str]
    bodies, ids = integration.crawl_get_email_content(limit=5)

    assert bodies == ["hello world"]
    assert ids == ["1"]
    stub_gmail.get_emails_list.assert_called_once_with(
        mailbox="INBOX", limit=5,
    )
    stub_gmail.get_email_content.assert_called_once_with("1")


def test_analyze_and_write_csv(
    integration: MailAiIntegration,
    monkeypatch: MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    """Test the flow of analyzaiton and write to csv.

    `analyze_and_write_csv` should
    • call `get_spam_probability` once per message body;
    • round the value to two decimals;
    • forward the resulting list of dicts to `write_spam_results`.
    """
    fake_spam_prob: MagicMock = mocker.MagicMock(return_value=0.87654321)
    captured: dict[str, list[dict[str, float]]] = {}

    def fake_writer(rows: list[dict[str, float]]) -> None:
        captured["rows"] = rows

    monkeypatch.setattr(
        "hw4_integration.src.main.get_spam_probability",
        fake_spam_prob,
        raising=True,
    )
    monkeypatch.setattr(
        "hw4_integration.src.main.write_spam_results",
        fake_writer,
        raising=True,
    )

    integration.analyze_and_write_csv(["body text"], ["abc123"])

    fake_spam_prob.assert_called_once_with("body text")
    assert captured["rows"] == [{"mail_id": "abc123", "Pct_spam": 0.88}]


# ---------- Integration tests ---------- #

def test_crawl_no_emails_returns_empty(
    monkeypatch: MonkeyPatch,
) -> None:
    """When the inbox is empty, crawl_get_email_content returns empty lists."""
    class EmptyGmail(RealGmailClientImpl):
        def connect(self) -> bool:
            return True
        def get_emails_list(self, mailbox: str = "INBOZ", limit: int = 10) -> list[dict[str, Any]]:
            return []

    monkeypatch.setattr(
        "hw4_integration.src.main.GmailClientImpl",
        lambda: EmptyGmail(),
        raising=True,
    )
    integration = MailAiIntegration()

    bodies, ids = integration.crawl_get_email_content(limit=3)
    assert bodies == []
    assert ids == []


def test_crawl_skips_malformed_entries(
    monkeypatch: MonkeyPatch,
) -> None:
    """Entries without 'id' or with empty body should be skipped."""
    class MalformedGmail(RealGmailClientImpl):
        def connect(self) -> bool:
            return True
        def get_emails_list(self, mailbox: str = "INBOX", limit: int = 10) -> list[dict[str, Any]]:
            return [{}, {"id": "good"}]
        def get_email_content(self, mail_id: str) -> dict[str, Any]:
            return {"body": ""} if mail_id == "" else {"body": "valid body"}

    monkeypatch.setattr(
        "hw4_integration.src.main.GmailClientImpl",
        lambda: MalformedGmail(),
        raising=True,
    )
    integration = MailAiIntegration()

    bodies, ids = integration.crawl_get_email_content(limit=2)
    assert bodies == ["valid body"]
    assert ids == ["good"]


def test_crawl_handles_exceptions_and_logs(monkeypatch: MonkeyPatch) -> None:
    """If Gmail client raises during crawl, we catch and return empty lists."""
    class ErrorGmail(RealGmailClientImpl):
        def connect(self) -> bool:
            return True
        def get_emails_list(self, mailbox: str = "INBOX", limit: int = 10) -> list[dict[str, Any]]:
            msg = "Fetch failed: " + mailbox + ", limit: " + str(limit)
            raise RuntimeError(msg)

    monkeypatch.setattr(
        "hw4_integration.src.main.GmailClientImpl",
        lambda: ErrorGmail(),
        raising=True,
    )
    integration = MailAiIntegration()

    bodies, ids = integration.crawl_get_email_content(limit=1)
    assert bodies == []
    assert ids == []


def test_analyze_continues_on_spam_errors_and_writes(tmp_path: Path,
                                                   monkeypatch: MonkeyPatch) -> None:
    """analyze_and_write_csv should skip on spam detection errors, but still write valid rows."""
    # change cwd for CSV output
    monkeypatch.chdir(tmp_path)

    # stub spam probability: first call fails, second succeeds
    class FlakySpam:
        count = 0
        def __call__(self, body:str) -> float:
            FlakySpam.count += 1
            if FlakySpam.count == 1:
                msg = "AI Failure: " + body
                raise ValueError(msg)
            return 0.3333

    monkeypatch.setattr(
        "hw4_integration.src.main.get_spam_probability",
        FlakySpam(),
        raising=True,
    )

    # run analysis with two entries
    integration = MailAiIntegration()
    bodies = ["bad body", "good body"]
    ids = ["bad1", "good1"]
    integration.analyze_and_write_csv(bodies, ids)

    # verify CSV has only one successful row
    csv_file = tmp_path / "spam_results.csv"
    assert csv_file.exists()
    lines = csv_file.read_text().splitlines()
    assert lines[0] == "mail_id,Pct_spam"
    assert lines[1] == "good1,0.33"
