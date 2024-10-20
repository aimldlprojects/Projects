// src/App.js

import React from 'react';
import './App.css';
import ChartComponent from './ChartComponent';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>My React Chart</h1>
        <ChartComponent />
      </header>
    </div>
  );
}

export default App;
