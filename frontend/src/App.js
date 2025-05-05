import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);

  const handleSearch = async (e) => {
    const value = e.target.value;
    setQuery(value);

    if (value.trim() === '') {
      setSuggestions([]);
      return;
    }

    try {
      const response = await axios.get(`https://your-backend-url.onrender.com/search?q=${value}`);
      setSuggestions(response.data || []);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      setSuggestions([]);
    }
  };

  return (
    <div className="App">
      <h1>Stock Portfolio Risk Analyzer</h1>
      <input
        type="text"
        placeholder="Enter stock names"
        value={query}
        onChange={handleSearch}
      />
      {suggestions.length > 0 && (
        <ul className="suggestion-list">
          {suggestions.map((s, index) => (
            <li key={index}>{s}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;