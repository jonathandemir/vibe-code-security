import React, { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("Vouch UI Error Caught:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', color: '#F87171', backgroundColor: '#0A0A14', minHeight: '100vh', fontFamily: 'monospace' }}>
          <h2 style={{ fontSize: '24px', marginBottom: '20px' }}>React App Crashed 💥</h2>
          <p>This is exactly why you got a blank screen. Please copy the error below and send it to the AI Agent:</p>
          <pre style={{ backgroundColor: '#000', padding: '20px', borderRadius: '8px', overflowX: 'auto', marginTop: '20px' }}>
            {this.state.error && this.state.error.toString()}
            <br/><br/>
            {this.state.error && this.state.error.stack}
          </pre>
          <button 
            onClick={() => window.location.replace('/')} 
            style={{ marginTop: '30px', padding: '10px 20px', backgroundColor: '#7B61FF', color: 'white', borderRadius: '8px', border: 'none', cursor: 'pointer' }}
          >
            Reload App
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
