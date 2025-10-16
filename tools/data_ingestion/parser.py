import os
import pandas as pd
import json

def handle_file_upload(file, save_dir, metadata_path):
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, file.filename)
    file.save(file_path)

    meta = {"file": file.filename, "columns": [], "rows": 0, "type": None}

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file_path)
            meta.update({
                "columns": df.columns.tolist(),
                "rows": len(df),
                "type": "csv"
            })
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(file_path)
            meta.update({
                "columns": df.columns.tolist(),
                "rows": len(df),
                "type": "excel"
            })
        elif file.filename.endswith(".db"):
            meta["type"] = "database"
        else:
            meta["type"] = "unknown"
    except Exception as e:
        meta["error"] = str(e)

    with open(metadata_path, "w") as f:
        json.dump(meta, f, indent=4)
    return meta
