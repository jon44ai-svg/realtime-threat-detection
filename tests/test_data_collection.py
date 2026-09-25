from threat_detection.data_collection import ALLOWED_LABELS, MAX_UPLOAD_BYTES, _safe_header


def test_collection_limits_and_labels() -> None:
    assert MAX_UPLOAD_BYTES == 5 * 1024 * 1024
    assert {"empty", "gun", "knife", "blunt_object"} <= ALLOWED_LABELS
    assert _safe_header("a\r\nb", 10) == "a  b"
