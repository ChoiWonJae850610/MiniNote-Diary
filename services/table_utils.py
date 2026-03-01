def read_table_data(table):
    rows = []
    for r in range(table.rowCount()):
        row = []
        empty = True
        for c in range(table.columnCount()):
            item = table.item(r, c)
            text = item.text() if item else ""
            if text:
                empty = False
            row.append(text)
        if not empty:
            rows.append(row)
    return rows