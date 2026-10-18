"""Target authorization and owner declaration validation."""

from __future__ import annotations

from pathlib import Path

import yaml

from veylith.errors import AuthorizationMissingError
from veylith.models.project import OwnerDeclaration

AUTH_FILE_NAME = ".veylith.yaml"


def record_owner_declaration(
    project_root: Path,
    declared_by: str = "operator",
    scope: str = "authorized-security-evaluation",
) -> OwnerDeclaration:
    """Record an owner declaration file in the project root."""
    decl = OwnerDeclaration(
        declared_by=declared_by,
        scope=scope,
        authorized=True,
    )
    auth_file = project_root / AUTH_FILE_NAME
    data = {
        "schema_version": decl.schema_version,
        "owner_declaration": {
            "declared_by": decl.declared_by,
            "scope": decl.scope,
            "timestamp": decl.timestamp.isoformat(),
            "authorized": decl.authorized,
        },
    }
    with open(auth_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)
    return decl


def verify_owner_authorization(project_root: Path) -> OwnerDeclaration:
    """Verify that an owner authorization declaration is present and valid."""
    auth_file = project_root / AUTH_FILE_NAME
    if not auth_file.is_file():
        raise AuthorizationMissingError(
            f"No owner authorization declaration found at '{auth_file}'. "
            f"Run 'veylith init <path>' first to record target authorization."
        )

    try:
        with open(auth_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or "owner_declaration" not in data:
            raise AuthorizationMissingError(f"Malformed authorization file at '{auth_file}'.")

        decl_data = data["owner_declaration"]
        if not decl_data.get("authorized"):
            raise AuthorizationMissingError(
                "Target owner authorization is explicitly set to false."
            )

        return OwnerDeclaration(
            declared_by=decl_data["declared_by"],
            scope=decl_data["scope"],
            authorized=decl_data["authorized"],
        )
    except Exception as err:
        if isinstance(err, AuthorizationMissingError):
            raise
        raise AuthorizationMissingError(
            f"Failed to read authorization from '{auth_file}': {err}"
        ) from err
