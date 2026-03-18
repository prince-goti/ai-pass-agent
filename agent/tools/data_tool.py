import pandas as pd
import io

def run_data_tool(csv_bytes: bytes) -> dict:
    try:
        df = pd.read_csv(io.BytesIO(csv_bytes))
        metrics = {
            "columns": list(df.columns),
            "row_count": len(df),
            "summary": df.describe(include="all").fillna("").to_dict(),
            "preview": df.head(5).to_dict(orient="records")
        }
        return {"status": "success", "metrics": metrics}
    except Exception as e:
        return {"status": "error", "error": str(e)} 