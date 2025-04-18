import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [stocks, setStocks] = useState([]);
  const [stockInput, setStockInput] = useState('');
  const [stockSuggestions, setStockSuggestions] = useState([]);

  // Fetch stock suggestions from API (or use a static list initially)
  const fetchStockSuggestions = async (query) => {
    if (query.length > 2) {
      const response = await fetch(`https://api.example.com/search?query=${query}`); // Replace with real API
      const data = await response.json();
      setStockSuggestions(data);
    } else {
      setStockSuggestions([]);
    }
  };

  const handleInputChange = (event) => {
    setStockInput(event.target.value);
    fetchStockSuggestions(event.target.value);
  };

  const handleStockSelect = (stock) => {
    setStockInput(stock.name);  // Assuming stock has a 'name' property
    setStockSuggestions([]);
  };

  useEffect(() => {
    // Initialize with some data or on app load
    // e.g., fetch initial stock data
  }, []);

  return (
    <div className="App">
      <h1>Stock Portfolio Risk Analyzer</h1>
      
      <div className="search-container">
        <input 
          type="text" 
          value={stockInput} 
          onChange={handleInputChange} 
          placeholder="Enter stock names" 
        />
        {stockSuggestions.length > 0 && (
          <ul className="suggestions-list">
            {stockSuggestions.map((stock, index) => (
              <li key={index} onClick={() => handleStockSelect(stock)}>
                {stock.name}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div className="stock-list">
        {/* Render selected stocks, portfolio or other data here */}
      </div>
    </div>
  );
}

export default App;
