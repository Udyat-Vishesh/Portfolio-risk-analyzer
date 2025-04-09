import React, { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');

    const handleSearch = () => {
        console.log("Search clicked:", query);
          };

            return (
                <div className="app">
                      <h1 className="title">Portfolio Risk Analyzer</h1>
                            <div className="search-container">
                                    <input
                                              type="text"
                                                        placeholder="Search stock, ETF or crypto..."
                                                                  value={query}
                                                                            onChange={(e) => setQuery(e.target.value)}
                                                                                      className="search-input"
                                                                                              />
                                                                                                      <button className="search-button" onClick={handleSearch}>Search</button>
                                                                                                            </div>
                                                                                                                </div>
                                                                                                                  );
                                                                                                                  }

                                                                                                                  export default App;
                                                                                                                  