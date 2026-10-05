"""Project pinned upstream INSERT columns onto LonelyIce's current world schema."""
import argparse
import re
from pathlib import Path


def split_sql(text, delimiter):
    parts, start, quote, depth, index = [], 0, None, 0, 0
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                if index + 1 < len(text) and text[index + 1] == quote:
                    index += 2
                    continue
                quote = None
        elif char in "'\"`":
            quote = char
        elif text.startswith("--", index):
            newline = text.find("\n", index)
            index = len(text) if newline < 0 else newline + 1
            continue
        elif text.startswith("/*", index):
            end = text.find("*/", index + 2)
            if end < 0:
                raise ValueError("Unterminated SQL comment")
            index = end + 2
            continue
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == delimiter and depth == 0:
            parts.append(text[start:index])
            start = index + 1
        index += 1
    parts.append(text[start:])
    return parts


def adapt(text):
    # Source is pinned; fail on unexpected trainer data instead of silently losing it.
    header = re.compile(r"((?:INSERT|REPLACE)\s+INTO\s+`?(\w+)`?)\s*\(([^)]+)\)\s*VALUES\s*(.*)", re.I | re.S)
    text = text.replace("`id1`", "`id`")
    result = []
    for statement in split_sql(text, ";"):
        if re.search(r"UPDATE\s+`?item_template`?\s+SET", statement, re.I):
            statement = re.sub(r"\bStatsCount\s*=\s*\d+\s*,", "", statement, flags=re.I)
        select = re.search(r"((?:INSERT|REPLACE)\s+INTO\s+`?item_template`?)\s*\(([^)]+)\)\s*SELECT\s+(.*?)\s+FROM\s+(.*)", statement, re.I | re.S)
        if select:
            columns = [column.strip(" \r\n\t`") for column in select[2].split(",")]
            expressions = split_sql(select[3], ",")
            if len(columns) != len(expressions):
                raise ValueError("INSERT SELECT column count mismatch")
            kept = [index for index, name in enumerate(columns) if name.lower() != "statscount"]
            source = re.sub(r"\s+ON DUPLICATE KEY UPDATE.*", "", select[4], flags=re.I | re.S)
            result.append(statement[:select.start()] + select[1] + " (" +
                          ", ".join("`" + columns[index] + "`" for index in kept) + ") SELECT " +
                          ", ".join(expressions[index] for index in kept) + " FROM " + source)
            continue
        match = header.search(statement)
        if not match or match[2].lower() not in ("item_template", "creature_template", "creature"):
            result.append(statement)
            continue
        table = match[2].lower()
        columns = [column.strip(" \r\n\t`") for column in match[3].split(",")]
        renamed = table == "creature" and any(name.lower() == "id1" for name in columns)
        if renamed:
            columns = ["id" if name.lower() == "id1" else name for name in columns]
        obsolete = {"statscount"} if table == "item_template" else {"id2", "id3"} if table == "creature" else {
            "scale", "trainer_type", "trainer_spell", "trainer_class", "trainer_race",
            "mechanic_immune_mask", "spell_school_immune_mask",
        }
        removed = [index for index, name in enumerate(columns) if name.lower() in obsolete]
        if not removed and not renamed:
            result.append(statement)
            continue
        kept = [index for index in range(len(columns)) if index not in removed]
        rows, immunities = [], []
        source_rows = re.sub(r"(?m)^\s*--[^\n]*", "", match[4])
        for row in split_sql(source_rows, ","):
            row = row.strip()
            if not row:
                continue
            if not row.startswith("(") or not row.endswith(")"):
                raise ValueError("Unexpected VALUES row: " + row[:100])
            values = [value.strip() for value in split_sql(row[1:-1], ",")]
            if len(values) != len(columns):
                raise ValueError(f"{table}: {len(values)} values for {len(columns)} columns")
            if table == "creature":
                for index in removed:
                    if int(values[index]) != 0:
                        raise ValueError("Nonzero alternate spawn requires creature_multispawn migration")
            if table == "creature_template":
                data = {name.lower(): values[index] for index, name in enumerate(columns)}
                for name in ("trainer_type", "trainer_spell", "trainer_class", "trainer_race"):
                    if name in data and int(data[name]) != 0:
                        raise ValueError(f"Unsupported trainer field {name}={data[name]}")
                mechanics = int(data.get("mechanic_immune_mask", "0"))
                school = int(data.get("spell_school_immune_mask", "0"))
                entry = int(data["entry"])
                immunity_id = entry if mechanics or school else 0
                values.append(str(immunity_id))
                if immunity_id:
                    immunities.append(f"({entry}, {school}, {mechanics}, '', '', 'Mythic Plus custom NPC')")
            rows.append("(" + ", ".join(values[index] for index in kept) +
                        (", " + values[-1] if table == "creature_template" else "") + ")")
        names = [columns[index] for index in kept]
        if table == "creature_template":
            names.append("CreatureImmunitiesId")
        replacement = match[1] + " (" + ", ".join("`" + name + "`" for name in names) + ") VALUES\n"
        replacement += ",\n".join(rows)
        result.append(statement[:match.start()] + replacement)
        if immunities:
            result.append("\nREPLACE INTO creature_immunities (ID, SchoolMask, MechanicsMask, Effects, Auras, Comment) VALUES\n" + ",\n".join(immunities))
    return ";".join(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    options = parser.parse_args()
    scripts = sorted((options.directory / "sql/db-world").rglob("*.sql"))
    if not scripts:
        raise ValueError("No world SQL scripts found in " + str(options.directory))
    for path in scripts:
        path.write_text(adapt(path.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    print(f"Adapted {len(scripts)} world SQL files in {options.directory}")
