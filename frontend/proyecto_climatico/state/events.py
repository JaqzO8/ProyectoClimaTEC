"""Typed boundary for Reflex 0.9's decorator implemented through __new__.

Mypy treats EventNamespace.__new__ as a constructor and loses its EventCallback
return type. Keep the cast here so application handlers retain their arguments.
"""

from collections.abc import Callable
from typing import Any, cast

import reflex as rx
from reflex.event import EventCallback


def event[*Args](handler: Callable[[Any, *Args], Any]) -> EventCallback[*Args]:
    return cast(EventCallback[*Args], rx.event(handler))
