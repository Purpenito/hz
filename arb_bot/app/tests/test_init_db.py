from app.storage.sql_utils import split_sql_statements


def test_split_sql_statements_handles_multiple_blocks():
    sql = """
    -- comment
    CREATE TABLE a (id INT);

    CREATE TABLE b (id INT);
    """
    parts = split_sql_statements(sql)
    assert len(parts) == 2
    assert parts[0].startswith("CREATE TABLE a")
    assert parts[1].startswith("CREATE TABLE b")
