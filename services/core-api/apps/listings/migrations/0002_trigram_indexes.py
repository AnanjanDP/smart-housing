from django.db import migrations

COLUMNS = ("title", "city", "state", "address")


def create_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    for column in COLUMNS:
        schema_editor.execute(
            f"CREATE INDEX IF NOT EXISTS listings_listing_{column}_trgm "
            f"ON listings_listing USING gin ({column} gin_trgm_ops)"
        )


def drop_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    for column in COLUMNS:
        schema_editor.execute(f"DROP INDEX IF EXISTS listings_listing_{column}_trgm")


class Migration(migrations.Migration):
    """Trigram indexes used by the search service's typo-tolerant search."""

    dependencies = [("listings", "0001_initial")]
    operations = [migrations.RunPython(create_indexes, drop_indexes)]
