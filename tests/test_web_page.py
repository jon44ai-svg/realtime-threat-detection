"""Smoke check for the hostable web page payload."""

from threat_detection.web.app import _PAGE


def test_page_has_stream_endpoint() -> None:
    assert 'src="/stream"' in _PAGE
    assert 'id="status"' in _PAGE
