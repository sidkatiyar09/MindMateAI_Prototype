from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uvicorn, os, shutil
from notebook_gen import generate_notebook, safe_filename

app = FastAPI()
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV allowed")
    out_path = os.path.join(DATA_DIR, file.filename)
    with open(out_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"msg":"saved", "path": out_path}

@app.post("/generate-notebook/")
async def gen_notebook(project_name: str):
    nb_name = safe_filename(project_name)+".ipynb"
    nb_path = os.path.join(DATA_DIR, nb_name)
    # pick up mood_logs.csv if exists
    csv = os.path.join(DATA_DIR, "mood_logs.csv")
    csv_use = csv if os.path.exists(csv) else None
    generate_notebook(nb_path, project_name, csv_use)
    return {"notebook": nb_path}

@app.get("/download/{fname}")
def download(fname: str):
    p = os.path.join(DATA_DIR, fname)
    if os.path.exists(p):
        return FileResponse(p)
    raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
