import torch, timm, io, os, re, requests
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from torchvision import transforms
from contextlib import asynccontextmanager
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# --- Configuration for Deployment ---
# The MODEL_URL will be set as an environment variable in Render
MODEL_URL = os.environ.get("MODEL_URL", "PASTE_YOUR_MODEL_URL_HERE")
# Render's free instances provide a temporary writable directory at /tmp
MODEL_DEST_PATH = Path("/tmp/model.pt") 
NUM_CLASSES = 132
IMG_SIZE = 224

ml_models = {}
CLASS_NAMES = [
    'Adristyrannus', 'Aleurocanthus spiniferus', 'Ampelophaga', 'Aphis citricola Vander Goot', 'Apolygus lucorum', 'Bactrocera tsuneonis', 'Beet spot flies', 'Black hairy', 'Brevipoalpus lewisi McGregor', 'Ceroplastes rubens', 'Chlumetia transversa', 'Chrysomphalus aonidum', 'Cicadella viridis', 'Cicadellidae', 'Colomerus vitis', 'Dacus dorsalis(Hendel)', 'Dasineura sp', 'Deporaus marginatus Pascoe', 'Erythroneura apicalis', 'Field Cricket', 'Fruit piercing moth', 'Gall fly', 'Icerya purchasi Maskell', 'Indigo caterpillar', 'Jute Stem Weevil', 'Jute aphid', 'Jute hairy', 'Jute red mite', 'Jute semilooper', 'Jute stem girdler', 'Jute stick insect', 'Lawana imitata Melichar', 'Leaf beetle', 'Limacodidae', 'Locust', 'Locustoidea', 'Lycorma delicatula', 'Mango flat beak leafhopper', 'Mealybug', 'Miridae', 'Nipaecoccus vastalor', 'Panonchus citri McGregor', 'Papilio xuthus', 'Parlatoria zizyphus Lucus', 'Phyllocnistis citrella Stainton', 'Phyllocoptes oleiverus ashmead', 'Pieris canidia', 'Pod borer', 'Polyphagotars onemus latus', 'Potosiabre vitarsis', 'Prodenia litura', 'Pseudococcus comstocki Kuwana', 'Rhytidodera bowrinii white', 'Rice Stemfly', 'Salurnis marginella Guerr', 'Scirtothrips dorsalis Hood', 'Spilosoma Obliqua', 'Sternochetus frigidus', 'Termite', 'Termite odontotermes (Rambur)', 'Tetradacus c Bactrocera minax', 'Thrips', 'Toxoptera aurantii', 'Toxoptera citricidus', 'Trialeurodes vaporariorum', 'Unaspis yanonensis', 'Viteus vitifoliae', 'Xylotrechus', 'Yellow Mite', 'alfalfa plant bug', 'alfalfa seed chalcid', 'alfalfa weevil', 'aphids', 'army worm', 'asiatic rice borer', 'beet army worm', 'beet fly', 'beet weevil', 'beetle', 'bird cherry-oataphid', 'black cutworm', 'blister beetle', 'bollworm', 'brown plant hopper', 'cabbage army worm', 'cerodonta denticornis', 'corn borer', 'corn earworm', 'cutworm', 'english grain aphid', 'fall armyworm', 'flax budworm', 'flea beetle', 'grain spreader thrips', 'grasshopper', 'green bug', 'grub', 'large cutworm', 'legume blister beetle', 'longlegged spider mite', 'lytta polita', 'meadow moth', 'mites', 'mole cricket', 'odontothrips loti', 'oides decempunctata', 'paddy stem maggot', 'parathrene regalis', 'peach borer', 'penthaleus major', 'red spider', 'rice gall midge', 'rice leaf caterpillar', 'rice leaf roller', 'rice leafhopper', 'rice shell pest', 'rice water weevil', 'sawfly', 'sericaorient alismots chulsky', 'small brown plant hopper', 'stem borer', 'tarnished plant bug', 'therioaphis maculata Buckton', 'wheat blossom midge', 'wheat phloeothrips', 'wheat sawfly', 'white backed plant hopper', 'white margined moth', 'whitefly', 'wireworm', 'yellow cutworm', 'yellow rice borer'
]

class PestNameRequest(BaseModel):
    pest_name: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- Loading models ---")
    load_dotenv()
    
    # Configure Gemini API
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        ml_models["gemini_model"] = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini API configured successfully.")
    except Exception as e:
        print(f"❌ ERROR: Could not configure Gemini API. Is GEMINI_API_KEY secret set? Error: {e}")
        ml_models["gemini_model"] = None

    # Download the model from the URL if it doesn't exist
    if not MODEL_DEST_PATH.exists():
        print(f"Model not found at {MODEL_DEST_PATH}. Downloading from URL...")
        try:
            with requests.get(MODEL_URL, stream=True) as r:
                r.raise_for_status()
                with open(MODEL_DEST_PATH, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print("Model downloaded successfully.")
        except Exception as e:
            print(f"❌ ERROR: Failed to download model: {e}")

    # Load the local classification model
    model = timm.create_model('convnext_tiny_in22k', pretrained=False, num_classes=NUM_CLASSES)
    try:
        model.load_state_dict(torch.load(MODEL_DEST_PATH, map_location=torch.device('cpu')))
    except FileNotFoundError:
        print(f"ERROR: Local pest classifier not found at {MODEL_DEST_PATH}")
        ml_models["pest_classifier"] = None
        yield
        return
        
    device = torch.device("cpu") # Render's free tier uses CPU
    model.to(device); model.eval()
    ml_models["pest_classifier"] = model
    ml_models["device"] = device
    ml_models["class_names"] = CLASS_NAMES
    print(f"--- Models loaded successfully on device: {device} ---")
    
    yield
    
    ml_models.clear()

app = FastAPI(title="Pest Classification API", lifespan=lifespan)

# Allow all origins for simplicity, can be locked down later
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

data_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

@app.get("/")
def home():
    return {"message": "API is running."}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # ... (predict logic is the same)
    if not ml_models.get("pest_classifier"): raise HTTPException(status_code=500, detail="Model is not loaded.")
    contents = await file.read(); image = Image.open(io.BytesIO(contents)).convert("RGB")
    image_tensor = data_transforms(image).unsqueeze(0).to(ml_models["device"])
    with torch.no_grad():
        outputs = ml_models["pest_classifier"](image_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        top3_conf, top3_indices = torch.topk(probabilities, 3)
    predictions = [{"class_name": ml_models["class_names"][idx], "confidence": round(conf.item(), 4)} for idx, conf in zip(top3_indices, top3_conf)]
    return {"filename": file.filename, "predictions": predictions}

@app.post("/recommend")
async def recommend(request: PestNameRequest):
    # ... (recommend logic is the same)
    gemini_model = ml_models.get("gemini_model")
    if not gemini_model: raise HTTPException(status_code=500, detail="Gemini model not available.")
    pest_name = request.pest_name.replace('_', ' ').title()
    prompt = f"..." # (shortened for brevity)
    response = await gemini_model.generate_content_async(prompt)
    text = response.text
    def parse_section(header, content):
        try:
            section_content = re.search(f'# {header}\n(.*?)(?=\n# |$)', content, re.DOTALL).group(1).strip()
            lines = [line.strip() for line in section_content.split('\n') if line.strip()]
            def clean_line(line): return line.strip('-* ').replace('**', '')
            if header == "CHEMICAL SOLUTIONS":
                solutions = []
                for line in lines:
                    if "CRITICAL DISCLAIMER" in line.upper(): continue
                    cleaned = clean_line(line)
                    parts = cleaned.split(':', 1)
                    if len(parts) == 2: pesticide, notes = parts[0].strip(), parts[1].strip()
                    else: pesticide, notes = cleaned, "Consult packaging for detailed information."
                    solutions.append({"pesticide": pesticide, "dosage": "As per local guidelines", "notes": notes})
                return solutions
            else: return [clean_line(line) for line in lines]
        except: return []
    response_payload = {
        "pest_name": pest_name,
        "pest_info": re.search(r'# PEST INFO\n(.*?)(?=\n# |$)', text, re.DOTALL).group(1).strip() if re.search(r'# PEST INFO\n(.*?)(?=\n# |$)', text, re.DOTALL) else "Information not available.",
        "ipm_solutions": parse_section("IPM SOLUTIONS", text),
        "chemical_solutions": parse_section("CHEMICAL SOLUTIONS", text),
        "prevention_tips": parse_section("PREVENTION TIPS", text),
    }
    return response_payload

