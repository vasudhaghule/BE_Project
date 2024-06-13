import React, { useState } from "react";
import axios from "axios";
import "./App.css";
import Metrics from "./Metrics.tsx";

function App() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [emotionResult, setEmotionResult] = useState<string>("");
  const [showMetrics, setShowMetrics] = useState<boolean>(false);

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedImage(event.target.files[0]);
    }
  };

  const classifyEmotion = () => {
    const formData = new FormData();
    if (selectedImage) {
      formData.append("image", selectedImage);
      axios
        .post("http://127.0.0.1:5000/classify", formData)
        .then((response) => {
          console.log("response:", response);
          setEmotionResult(response.data[0].emotion);
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
  };

  const handleCloseMetrics = () => {
    setShowMetrics(false); // Hide Metrics page
  };

  return (
    <div className="container">
      <header>
        <h1>Emotion Recognition for Autistic Individuals</h1>
      </header>

      <div className="button-container">
        <button onClick={() => setShowMetrics(true)}>Show Metrics</button>
      </div>
      <div className="input-container">
        <input
          type="file"
          accept="image/*"
          id="fileInput"
          onChange={handleImageChange}
        />
        <label htmlFor="fileInput" className="custom-button">
          Select Image
        </label>
      </div>
      {selectedImage && (
        <div className="preview-container">
          <img
            src={URL.createObjectURL(selectedImage)}
            alt="Preview"
            className="preview-image"
          />
        </div>
      )}
      <div className="button-container">
        <button onClick={classifyEmotion}>Classify Emotion</button>
      </div>
      {emotionResult && (
        <div className="result">
          <p>Emotion: {emotionResult}</p>
        </div>
      )}
      {showMetrics && <Metrics onClose={handleCloseMetrics} />}
    </div>
  );
}

export default App;
