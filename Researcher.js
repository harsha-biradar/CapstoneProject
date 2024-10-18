import React, { useState } from 'react';

function Researcher() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);

  const handleQuery = () => {
    // Mock patient similarity search
    setResult(`Similarity score between patients for "${query}": 0.85`);
  };

  return (
    <div>
      <h2>Researcher Portal</h2>
      <input
        type="text"
        placeholder="Enter query for research"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleQuery}>Search</button>
      {result && <p>{result}</p>}
    </div>
  );
}

export default Researcher;
