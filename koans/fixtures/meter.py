"""A tiny module whose body runs on first import."""

loads = 1
value = "original"


def publish(new_value: str) -> None:
    global value
    value = new_value
