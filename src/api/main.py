# src/api/main.py

import torch, timm, io, os, pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Import CORS
from pydantic import BaseModel
from PIL import Image
from torchvision import transforms
from contextlib import asynccontextmanager

# --- Configuration ---
MODEL_PATH = "../../models/convnext_pestopia_LLRD_best.pt" 
PESTICIDE_DATA_PATH = "../../data/Pesticides.csv"
NUM_CLASSES = 132
IMG_SIZE = 224

ml_models = {}
CLASS_NAMES = [ # Full list of class names...
    'Adristyrannus', 'Aleurocanthus spiniferus', 'Ampelophaga', 'Aphis citricola Vander Goot', 'Apolygus lucorum', 'Bactrocera tsuneonis', 'Beet spot flies', 'Black hairy', 'Brevipoalpus lewisi McGregor', 'Ceroplastes rubens', 'Chlumetia transversa', 'Chrysomphalus aonidum', 'Cicadella viridis', 'Cicadellidae', 'Colomerus vitis', 'Dacus dorsalis(Hendel)', 'Dasineura sp', 'Deporaus marginatus Pascoe', 'Erythroneura apicalis', 'Field Cricket', 'Fruit piercing moth', 'Gall fly', 'Icerya purchasi Maskell', 'Indigo caterpillar', 'Jute Stem Weevil', 'Jute aphid', 'Jute hairy', 'Jute red mite', 'Jute semilooper', 'Jute stem girdler', 'Jute stick insect', 'Lawana imitata Melichar', 'Leaf beetle', 'Limacodidae', 'Locust', 'Locustoidea', 'Lycorma delicatula', 'Mango flat beak leafhopper', 'Mealybug', 'Miridae', 'Nipaecoccus vastalor', 'Panonchus citri McGregor', 'Papilio xuthus', 'Parlatoria zizyphus Lucus', 'Phyllocnistis citrella Stainton', 'Phyllocoptes oleiverus ashmead', 'Pieris canidia', 'Pod borer', 'Polyphagotars onemus latus', 'Potosiabre vitarsis', 'Prodenia litura', 'Pseudococcus comstocki Kuwana', 'Rhytidodera bowrinii white', 'Rice Stemfly', 'Salurnis marginella Guerr', 'Scirtothrips dorsalis Hood', 'Spilosoma Obliqua', 'Sternochetus frigidus', 'Termite', 'Termite odontotermes (Rambur)', 'Tetradacus c Bactrocera minax', 'Thrips', 'Toxoptera aurantii', 'Toxoptera citricidus', 'Trialeurodes vaporariorum', 'Unaspis yanonensis', 'Viteus vitifoliae', 'Xylotrechus', 'Yellow Mite', 'alfalfa plant bug', 'alfalfa seed chalcid', 'alfalfa weevil', 'aphids', 'army worm', 'asiatic rice borer', 'beet army worm', 'beet fly', 'beet weevil', 'beetle', 'bird cherry-oataphid', 'black cutworm', 'blister beetle', 'bollworm', 'brown plant hopper', 'cabbage army worm', 'cerodonta denticornis', 'corn borer', 'corn earworm', 'cutworm', 'english grain aphid', 'fall armyworm', 'flax budworm', 'flea beetle', 'grain spreader thrips', 'grasshopper', 'green bug', 'grub', 'large cutworm', 'legume blister beetle', 'longlegged spider mite', 'lytta polita', 'meadow moth', 'mites', 'mole cricket', 'odontothrips loti', 'oides decempunctata', 'paddy stem maggot', 'parathrene regalis', 'peach borer', 'penthaleus major', 'red spider', 'rice gall midge', 'rice leaf caterpillar', 'rice leaf roller', 'rice leafhopper', 'rice shell pest', 'rice water weevil', 'sawfly', 'sericaorient alismots chulsky', 'small brown plant hopper', 'stem borer', 'tarnished plant bug', 'therioaphis maculata Buckton', 'wheat blossom midge', 'wheat phloeothrips', 'wheat sawfly', 'white backed plant hopper', 'white margined moth', 'whitefly', 'wireworm', 'yellow cutworm', 'yellow rice borer'
]

class PestNameRequest(BaseModel):
    pest_name: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- Loading model and data ---")
    model = timm.create_model('convnext_tiny_in22k', pretrained=False, num_classes=NUM_CLASSES)
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
        pesticide_df = pd.read_csv(PESTICIDE_DATA_PATH)
        pesticide_df.columns = ['Pest_Name', 'Pesticides']
        ml_models["pesticide_data"] = pesticide_df.set_index('Pest_Name').to_dict()['Pesticides']
    except FileNotFoundError as e:
        print(f"ERROR: Could not find a required file: {e}")
        ml_models["pest_classifier"] = None
        yield
        return
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device); model.eval()
    ml_models["pest_classifier"] = model
    ml_models["device"] = device
    ml_models["class_names"] = CLASS_NAMES
    print(f"--- Model and data loaded successfully on device: {device} ---")
    yield
    ml_models.clear()

app = FastAPI(title="Pest Classification API", lifespan=lifespan)

# --- CORRECTED CORS Middleware ---
# We have added the addresses your Vite server is using.
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080", # Added for your Vite server
    "http://192.168.29.88:8080" # Added for network access
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

@app.get("/")
def home():
    return {"message": "API is running. Go to /docs for interface."}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not ml_models.get("pest_classifier"):
        raise HTTPException(status_code=500, detail="Model is not loaded.")
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")
    image_tensor = data_transforms(image).unsqueeze(0).to(ml_models["device"])
    with torch.no_grad():
        outputs = ml_models["pest_classifier"](image_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        top3_conf, top3_indices = torch.topk(probabilities, 3)
    predictions = [{"class_name": ml_models["class_names"][idx], "confidence": round(conf.item(), 4)} for idx, conf in zip(top3_indices, top3_conf)]
    return {"filename": file.filename, "predictions": predictions}

@app.post("/recommend")
async def recommend(request: PestNameRequest):
    pest_name = request.pest_name
    mock_recommendations = {
        "bollworm": {
            "pest_name": "Bollworm",
            "pest_info": "The cotton bollworm is a highly destructive pest...",
            "ipm_solutions": ["Introduce natural predators like Trichogramma wasps.", "Use pheromone traps."],
            "chemical_solutions": [{"pesticide": ml_models["pesticide_data"].get(pest_name, "N/A"), "dosage": "As per label", "notes": "Follow safety guidelines."}],
            "prevention_tips": ["Practice crop rotation.", "Ensure timely sowing."]
        }
    }
    recommendation = mock_recommendations.get(pest_name.lower())
    if not recommendation:
        return {
            "pest_name": pest_name.replace('_', ' ').title(),
            "pest_info": "No detailed information available for this pest.",
            "ipm_solutions": ["Monitor crop regularly.", "Consult local agricultural extension for advice."],
            "chemical_solutions": [{"pesticide": ml_models["pesticide_data"].get(pest_name, "Consult expert"), "dosage": "N/A", "notes": "N/A"}],
            "prevention_tips": ["Maintain good field sanitation."]
        }
    return recommendation
