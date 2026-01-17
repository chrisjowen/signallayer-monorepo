from datetime import timedelta
from typing import TYPE_CHECKING

import inject

from ....common.dummy_service import DummyService
from ...lib.decorators import configured_activity

if TYPE_CHECKING:
    from ...lib.decorators.activity import ExecutableActivity

@configured_activity(
    name="say_hello",
    start_to_close_timeout=timedelta(seconds=10),
)
@inject.params(service=DummyService)
async def say_hello(name: str, service: DummyService) -> str:
    """A simple hello activity using an injected service."""
    return service.get_greeting(name)

# Help the IDE resolve the complex signature formed by double decorators
if TYPE_CHECKING:
    # This explicitly tells the IDE that say_hello takes a str and returns a str
    # when called/executed, hiding the injected service argument.
    say_hello: ExecutableActivity[[str], str]
