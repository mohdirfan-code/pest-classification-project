Agricultural Pest Classification & Recommendation SystemThis project is an AI-powered web application designed to help farmers identify agricultural pests from images and receive treatment recommendations. It leverages a state-of-the-art deep learning model for accurate pest classification and provides a user-friendly interface for analysis.🚀 FeaturesAI-Powered Pest Classification: Upload an image of a pest to get an instant identification from a highly accurate model.Detailed Pest Information: Access information about the identified pest's lifecycle and the damage it causes.Treatment Recommendations: Receive a list of both organic/IPM and chemical solutions for the identified pest.Prevention Strategies: Get actionable tips to prevent future infestations.Modern, Responsive UI: A clean and intuitive web interface built with React and Tailwind CSS.🛠️ Technology StackFrontend: React.js, Vite, Tailwind CSSBackend: Python, FastAPI, UvicornAI Model: PyTorch, timm (ConvNeXt-T architecture)Experimentation: Kaggle Notebooks, Weights & Biases⚙️ How to Run LocallyPrerequisitesPython 3.10+Node.js and npm1. Backend Setup# Navigate to the API directory
cd src/api

# Install Python dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn main:app --reload
The backend will be running at http://127.0.0.1:8000.2. Frontend Setup# Navigate to the frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Run the frontend development server
npm run dev
The frontend will open in your browser, typically at http://localhost:5173.