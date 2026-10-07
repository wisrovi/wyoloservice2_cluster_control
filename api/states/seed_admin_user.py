"""WPipe state that guarantees the default operator account exists."""

from typing import Any

from wpipe import step

from backend.auth import seed_default_admin
from dto.api_startup_context import ApiStartupContext


@step(
    name="SeedAdminUser",
    version="v1.0",
    description="Create the default admin operator in Redis when missing.",
    tags=["auth"],
)
class SeedAdminUser:
    """Seeds the default administrator credentials when Redis is reachable."""

    def __call__(self, data: dict[str, Any]) -> dict[str, Any]:
        """Run the admin seeding routine if Redis answered the health probe.

        Args:
            data: Current pipeline context as a dictionary.

        Returns:
            dict[str, Any]: The updated context.
        """
        ctx = ApiStartupContext(**data)
        if ctx.redis_ok:
            seed_default_admin()
            ctx.admin_seeded = True
        else:
            print("[SeedAdminUser] Skipped: Redis is not reachable (retried on API lifespan).")
        return ctx.model_dump()
