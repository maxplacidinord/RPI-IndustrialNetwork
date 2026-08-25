from drive_monitor.decode import decode_status_word, scaled, signed_word


def test_status_word_decodes_only_set_bits() -> None:
    assert decode_status_word((1 << 0) | (1 << 3) | (1 << 7)) == [
        "ready_to_switch_on",
        "fault",
        "warning",
    ]


def test_signed_process_word() -> None:
    assert signed_word(0x7FFF) == 32767
    assert signed_word(0xFFFF) == -1


def test_scaling() -> None:
    assert scaled(1234, 0.01) == 12.34
    assert scaled(None, 0.01) is None

