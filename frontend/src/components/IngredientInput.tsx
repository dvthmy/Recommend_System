import React, { useState, useRef } from 'react';
import { Ingredient } from '../types';
import { Box, Button, TextField, Typography, Chip, IconButton, CircularProgress } from '@mui/material';
import './IngredientInput.css';

interface IngredientInputProps {
  onIngredientsSubmit: (ingredients: Ingredient[]) => void;
}

const IngredientInput: React.FC<IngredientInputProps> = ({ onIngredientsSubmit }) => {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [textInput, setTextInput] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [isProcessingImage, setIsProcessingImage] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (textInput.trim()) {
      const newIngredients = textInput
        .split(',')
        .map(item => item.trim())
        .filter(item => item.length > 0)
        .map(item => ({ name: item, source: 'text' as const }));
      
      setIngredients(prev => [...prev, ...newIngredients]);
      setTextInput('');
    }
  };

  const handleImageUpload = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      setIsProcessingImage(true);
      const reader = new FileReader();
      reader.onload = (e) => {
        const imageUrl = e.target?.result as string;
        setUploadedImage(imageUrl);
        
        // Simulate AI image processing (in real app, you'd call an AI service)
        setTimeout(() => {
          const mockIngredients = [
            'tomatoes', 'onions', 'garlic', 'basil', 'olive oil'
          ].map(item => ({ name: item, source: 'image' as const }));
          
          setIngredients(prev => [...prev, ...mockIngredients]);
          setIsProcessingImage(false);
        }, 2000);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleImageUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleImageUpload(e.target.files[0]);
    }
  };

  const removeIngredient = (index: number) => {
    setIngredients(prev => prev.filter((_, i) => i !== index));
  };

  const handleGetSuggestions = () => {
    if (ingredients.length === 0) {
      alert('Please add some ingredients first!');
      return;
    }
    onIngredientsSubmit(ingredients);
  };

  return (
<Box className="ingredient-input-container" sx={{ width: '100%', p: 6, bgcolor: '#f9f9f9', fontFamily: "'Inter', sans-serif", fontWeight: 500, fontSize: '16px' }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, fontSize: '18px' }}>Your Ingredients</Typography>
      <Typography variant="subtitle1" gutterBottom sx={{ mb: 4 }}>Upload images or enter your ingredients to get personalized recipe suggestions</Typography>

      <Box className="input-methods" sx={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {/* Image Upload Section */}
        <Box className="input-section">
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, fontSize: '16px', mb: 2 }}>
            Upload Ingredient Images
          </Typography>
          <Box
            className={`image-upload-area ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            sx={{
              border: '2px dashed',
              borderColor: dragActive ? 'primary.main' : 'grey.400',
              borderRadius: 1.5,
              p: 3,
              textAlign: 'center',
              cursor: 'pointer',
              position: 'relative'
            }}
          >
            {uploadedImage ? (
              <Box sx={{ position: 'relative' }}>
                <img src={uploadedImage} alt="Uploaded ingredients" style={{ maxWidth: '100%', borderRadius: 12 }} />
                {isProcessingImage && (
                  <Box sx={{
                    position: 'absolute',
                    top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(255,255,255,0.7)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: 12
                  }}>
                    <CircularProgress />
                    <Typography>Analyzing ingredients...</Typography>
                  </Box>
                )}
              </Box>
            ) : (
              <Box>
                <Typography>Drag and drop images here or click to browse</Typography>
                <Typography variant="caption">Supports JPG, PNG, WebP</Typography>
              </Box>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
          </Box>
        </Box>

        {/* Text Input Section */}
        <Box className="input-section">
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, fontSize: '16px', mb: 2 }}>
            Enter Your Ingredients
          </Typography>
          <form onSubmit={handleTextSubmit} className="text-input-form" style={{ display: 'flex', gap: 12 }}>
            <TextField
              fullWidth
              variant="outlined"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="e.g.: tomatoes, onions, garlic (separated by commas)"
              sx={{ borderRadius: 1.5 }}
            />
            <Button type="submit" variant="contained" color="primary" sx={{ borderRadius: 1.5, fontWeight: 600 }}>Add</Button>
          </form>
        </Box>
      </Box>

      {/* Ingredients List */}
      {ingredients.length > 0 && (
        <Box className="ingredients-list" sx={{ mt: 6 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, fontSize: '16px' }}>Your Ingredients ({ingredients.length})</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {ingredients.map((ingredient, index) => (
              <Chip
                key={index}
                label={ingredient.name}
                onDelete={() => removeIngredient(index)}
                deleteIcon={<IconButton size="small">×</IconButton>}
                color={ingredient.source === 'image' ? 'primary' : 'default'}
                sx={{ borderRadius: 1.5 }}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Get Suggestions Button */}
      <Box className="action-section" sx={{ mt: 6, textAlign: 'center' }}>
        <Button
          onClick={handleGetSuggestions}
          variant="contained"
          color="primary"
          disabled={ingredients.length === 0}
          sx={{ borderRadius: 1.5, fontWeight: 600 }}
        >
          Get Recipe Suggestions ({ingredients.length} ingredients)
        </Button>
      </Box>
    </Box>
  );
};

export default IngredientInput;
