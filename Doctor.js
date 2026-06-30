import React, { useState } from 'react';

function Doctor() {
  const [symptoms, setSymptoms] = useState('');
  const [cluster, setCluster] = useState('');

  const handleQuery = () => {
    // Mock cluster prediction based on symptoms
    if (symptoms.includes('fever')) setCluster('Cluster A');
    else setCluster('Cluster B');
  };

  return (
    <div>
      <h2>Doctor Portal</h2>
      <input
        type="text"
        placeholder="Enter patient symptoms"
        value={symptoms}
        onChange={(e) => setSymptoms(e.target.value)}
      />
      <button onClick={handleQuery}>Find Cluster</button>
      {cluster && <p>Patient belongs to: {cluster}</p>}
    </div>
  );
}

export default Doctor;
