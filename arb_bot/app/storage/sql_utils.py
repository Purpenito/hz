def split_sql_statements(sql_script: str) -> list[str]:
    statements: list[str] = []
    buffer: list[str] = []

    for line in sql_script.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            statement = "\n".join(buffer).strip()
            if statement:
                statements.append(statement)
            buffer.clear()

    tail = "\n".join(buffer).strip()
    if tail:
        statements.append(tail)

    return statements
