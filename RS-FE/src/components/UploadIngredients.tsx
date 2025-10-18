import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { Ingredient } from '../types';
import './UploadIngredients.css';

const UploadIngredients: React.FC = () => {
  const navigate = useNavigate();
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [detectedIngredients, setDetectedIngredients] = useState<Ingredient[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzingMethod, setAnalyzingMethod] = useState<'local' | 'gpt' | null>(null);
  const [manualIngredient, setManualIngredient] = useState('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setUploadedFiles(prev => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
    },
    multiple: true,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const analyzeImagesWithLocalModel = async () => {
    if (uploadedFiles.length === 0) return;

    setIsAnalyzing(true);
    setAnalyzingMethod('local');
    
    try {
      // Call local model API
      const formData = new FormData();
      uploadedFiles.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('http://localhost:8000/detect-local', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze images with local model');
      }

      const result = await response.json();
      const ingredients: Ingredient[] = result.detections.map((detection: any) => ({
        name: detection.label || `Ingredient ${detection.cls}`,
        source: 'image'
      }));
      
      setDetectedIngredients(ingredients);
    } catch (error) {
      console.error('Error analyzing with local model:', error);
      // Fallback to mock data
      const mockIngredients: Ingredient[] = [
        { name: 'Tomatoes', source: 'image' },
        { name: 'Onions', source: 'image' },
        { name: 'Garlic', source: 'image' },
        { name: 'Beef', source: 'image' },
        { name: 'Cilantro', source: 'image' },
        { name: 'Bell Peppers', source: 'image' }
      ];
      setDetectedIngredients(mockIngredients);
    } finally {
      setIsAnalyzing(false);
      setAnalyzingMethod(null);
    }
  };

  const analyzeImagesWithGPT = async () => {
    if (uploadedFiles.length === 0) return;

    setIsAnalyzing(true);
    setAnalyzingMethod('gpt');
    
    try {
      // Call GPT API
      const formData = new FormData();
      uploadedFiles.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('http://localhost:8000/detect-gpt', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze images with GPT');
      }

      const result = await response.json();
      const ingredients: Ingredient[] = result.ingredients.map((ingredient: string) => ({
        name: ingredient,
        source: 'image'
      }));
      
      setDetectedIngredients(ingredients);
    } catch (error) {
      console.error('Error analyzing with GPT:', error);
      // Fallback to mock data
      const mockIngredients: Ingredient[] = [
        { name: 'Tomatoes', source: 'image' },
        { name: 'Onions', source: 'image' },
        { name: 'Garlic', source: 'image' },
        { name: 'Beef', source: 'image' },
        { name: 'Cilantro', source: 'image' },
        { name: 'Bell Peppers', source: 'image' }
      ];
      setDetectedIngredients(mockIngredients);
    } finally {
      setIsAnalyzing(false);
      setAnalyzingMethod(null);
    }
  };

  const addManualIngredient = () => {
    if (manualIngredient.trim()) {
      const newIngredient: Ingredient = {
        name: manualIngredient.trim(),
        source: 'text'
      };
      setDetectedIngredients(prev => [...prev, newIngredient]);
      setManualIngredient('');
    }
  };

  const removeIngredient = (index: number) => {
    setDetectedIngredients(prev => prev.filter((_, i) => i !== index));
  };

  const editIngredient = (index: number, newName: string) => {
    setDetectedIngredients(prev => 
      prev.map((ingredient, i) => 
        i === index ? { ...ingredient, name: newName } : ingredient
      )
    );
  };

  const proceedToSuggestions = () => {
    if (detectedIngredients.length > 0) {
      // Save ingredients to localStorage for recommendations
      localStorage.setItem('uploadedIngredients', JSON.stringify(detectedIngredients));
      navigate('/suggestions');
    }
  };

  return (
    <div className="upload-container">
      <div className="container">
        <div className="upload-header">
          <h1>Upload Ingredient Photos</h1>
          <p>Upload photos of your ingredients so AI can suggest suitable dishes</p>
        </div>

        <div className="upload-content">
          {/* Upload Zone */}
          <div className="upload-section">
            <div
              {...getRootProps()}
              className={`upload-zone ${isDragActive ? 'active' : ''}`}
            >
              <input {...getInputProps()} />
              <div className="upload-icon">
              </div>
              <h3>
                {isDragActive
                  ? 'Drop images here...'
                  : 'Drag and drop images or click to select'}
              </h3>
              <p>Supported: JPG, PNG, GIF, BMP, WebP (max 10MB)</p>
            </div>

            {/* File Preview */}
            {uploadedFiles.length > 0 && (
              <div className="file-preview">
                <h4>Uploaded Images ({uploadedFiles.length})</h4>
                <div className="file-grid">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="file-item">
                      <img
                        src={URL.createObjectURL(file)}
                        alt={file.name}
                        className="file-image"
                      />
                      <button
                        className="remove-file"
                        onClick={() => removeFile(index)}
                        aria-label="Remove image"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Analyze Buttons */}
            {uploadedFiles.length > 0 && (
              <div className="analyze-section">
                <h4>Choose analysis method:</h4>
                <div className="analyze-buttons">
                  <button
                    className="btn btn-primary btn-lg"
                    onClick={() => analyzeImagesWithLocalModel()}
                    disabled={isAnalyzing}
                  >
                    {isAnalyzing && analyzingMethod === 'local' ? (
                      <>
                        <span className="loading-spinner"></span>
                        Analyzing with local AI...
                      </>
                    ) : (
                      <>
                        Analyze with Local AI
                      </>
                    )}
                  </button>
                  <button
                    className="btn btn-outline btn-lg"
                    onClick={() => analyzeImagesWithGPT()}
                    disabled={isAnalyzing}
                  >
                    {isAnalyzing && analyzingMethod === 'gpt' ? (
                      <>
                        <span className="loading-spinner"></span>
                        Analyzing with GPT...
                      </>
                    ) : (
                      <>
                        Analyze with GPT API
                      </>
                    )}
                  </button>
                </div>
                <p className="analyze-description">
                  <strong>Local AI:</strong> Fast, free, works offline<br/>
                  <strong>GPT API:</strong> More accurate, requires internet connection
                </p>
              </div>
            )}
          </div>

          {/* Detected Ingredients */}
          {detectedIngredients.length > 0 && (
            <div className="ingredients-section">
              <h3>Detected Ingredients</h3>
              <div className="ingredients-list">
                {detectedIngredients.map((ingredient, index) => (
                  <div key={index} className="ingredient-item">
                    <span className="ingredient-icon">
                    </span>
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
                    Add ingredient manually
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
    </div>
  );
};

export default UploadIngredients;
