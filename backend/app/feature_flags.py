FEATURE_FLAGS = {
"use_phone_number": False,
}


def is_enabled(flag_name: str) -> bool:
    return FEATURE_FLAGS.get(flag_name, False)