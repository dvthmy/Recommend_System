import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useNavigate } from "react-router-dom";
import { Ingredient } from "../types";
import "./UploadIngredients.css";

const UploadIngredients: React.FC = () => {
  const navigate = useNavigate();
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [detectedIngredients, setDetectedIngredients] = useState<Ingredient[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [manualIngredient, setManualIngredient] = useState("");

  // 🧾 Handle file upload
  const onDrop = useCallback((acceptedFiles: File[]) => {
    setUploadedFiles((prev) => [...prev, ...acceptedFiles]);
    setErrorMessage(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpeg", ".jpg", ".png", ".webp"] },
    multiple: true,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const removeFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  // 🔍 Call FastAPI detect endpoint
  const analyzeImages = async () => {
  if (uploadedFiles.length === 0) return;

  setIsAnalyzing(true);
  setErrorMessage(null);

  try {
    const formData = new FormData();
    uploadedFiles.forEach((file) => formData.append("files", file));

    const response = await fetch("http://localhost:8000/detect/", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to analyze images");
    }

    const result = await response.json();

    // ✅ Check returned data
    if (!result.ingredients || result.ingredients.length === 0) {
      throw new Error("No ingredients detected");
    }

    const uniqueIngredients = Array.from(new Set(result.ingredients)).sort();
    const ingredients: Ingredient[] = uniqueIngredients.map((name) => ({
      name: String(name),
      source: "image" as const,
    }));

    setDetectedIngredients(ingredients);
  } catch (error) {
    console.error("❌ API detect error:", error);

    // ⚠️ Fallback mock data when API fails
    const mockIngredients: Ingredient[] = [
      { name: "Tomatoes", source: "image" },
      { name: "Onions", source: "image" },
      { name: "Garlic", source: "image" },
      { name: "Beef", source: "image" },
      { name: "Cilantro", source: "image" },
      { name: "Bell Peppers", source: "image" },
    ];

    setDetectedIngredients(mockIngredients);
    setErrorMessage("⚠️ API not responded.");
  } finally {
    setIsAnalyzing(false);
  }
};


  // ➕ Add manual ingredient
  const addManualIngredient = () => {
    if (manualIngredient.trim()) {
      const newIngredient: Ingredient = {
        name: manualIngredient.trim(),
        source: "text",
      };
      setDetectedIngredients((prev) => [...prev, newIngredient]);
      setManualIngredient("");
    }
  };

  // 🗑️ Remove ingredient
  const removeIngredient = (index: number) => {
    setDetectedIngredients((prev) => prev.filter((_, i) => i !== index));
  };

  // ✏️ Edit ingredient name
  const editIngredient = (index: number, newName: string) => {
    setDetectedIngredients((prev) =>
      prev.map((ingredient, i) =>
        i === index ? { ...ingredient, name: newName } : ingredient
      )
    );
  };

  // ⏭️ Proceed to next page
  const proceedToSuggestions = () => {
    if (detectedIngredients.length > 0) {
      localStorage.setItem("uploadedIngredients", JSON.stringify(detectedIngredients));
      navigate("/suggestions");
    }
  };

  return (
    <div className="upload-container">
      <div className="container">
        <div className="upload-header">
          <h1>Upload Ingredient Photos</h1>
          <p>Upload your ingredient photos — AI will detect and list them below</p>
        </div>

        {/* 🖼 Upload Zone */}
        <div {...getRootProps()} className={`upload-zone ${isDragActive ? "active" : ""}`}>
          <input {...getInputProps()} />
          <h3>{isDragActive ? "Drop images here..." : "Drag or click to upload images"}</h3>
          <p>Supported: JPG, PNG, WebP — Max 10MB each</p>
        </div>

        {/* 📷 File Preview */}
        {uploadedFiles.length > 0 && (
          <div className="file-preview">
            <h4>Uploaded Images ({uploadedFiles.length})</h4>
            <div className="file-grid">
              {uploadedFiles.map((file, i) => (
                <div key={i} className="file-item">
                  <img
                    src={URL.createObjectURL(file)}
                    alt={file.name}
                    className="file-image"
                  />
                  <button
                    className="remove-file"
                    onClick={() => removeFile(i)}
                    aria-label="Remove image"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 🔍 Analyze Button */}
        {uploadedFiles.length > 0 && (
          <button
            className="btn btn-primary analyze-btn"
            onClick={analyzeImages}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? "Analyzing..." : "Detect Ingredients"}
          </button>
        )}

        {/* ⚠️ Error */}
        {errorMessage && <p className="error-text">{errorMessage}</p>}

        {/* 🧾 Detected Ingredients */}
        {detectedIngredients.length > 0 && (
          <div className="ingredients-section">
            <h3>Detected Ingredients</h3>
            <div className="ingredients-list">
              {detectedIngredients.map((ingredient, index) => (
                <div key={index} className="ingredient-item">
                  <input
                    type="text"
                    value={ingredient.name}
                    onChange={(e) => editIngredient(index, e.target.value)}
                    className="ingredient-input"
                  />
                  <button
                    className="remove-ingredient"
                    onClick={() => removeIngredient(index)}
                    aria-label="Remove ingredient"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>

            {/* Manual Add Ingredient */} 
            <div className="manual-ingredient">
                <div className="form-group">
                  <label htmlFor="manual-ingredient" className="form-label">
                    Add ingredient
                  </label>
                  <div className="input-group">
                    <input
                      id="manual-ingredient"
                      type="text"
                      value={manualIngredient}
                      onChange={(e) => setManualIngredient(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addManualIngredient()}
                      placeholder="Enter ingredient name..."
                      className="form-input"
                    />
                    <button
                      className="btn btn-outline"
                      onClick={addManualIngredient}
                      disabled={!manualIngredient.trim()}
                    >
                      Add
                    </button>
                  </div>
                </div>
              </div>

            {/* Proceed Button */}
              <div className="proceed-section">
                <button
                  className="btn btn-primary btn-lg"
                  onClick={proceedToSuggestions}
                >
                  View Dish Suggestions
                </button>
              </div>
            </div>
        )}
      </div>
    </div>
  );
};

export default UploadIngredients;
