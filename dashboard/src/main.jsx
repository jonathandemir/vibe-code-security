import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ClerkProvider } from '@clerk/clerk-react'
import { dark } from '@clerk/themes'
import './index.css'
import App from './App.jsx'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

const Root = () => {
  if (!PUBLISHABLE_KEY) {
    // Dev fallback: render without auth if key is not loaded yet
    // Restart the dev server after adding .env.local to fix this
    console.warn('VibeGuard: VITE_CLERK_PUBLISHABLE_KEY not found. Auth is disabled. Restart the dev server after setting up .env.local')
    return <App />
  }
  return (
    <ClerkProvider
      publishableKey={PUBLISHABLE_KEY}
      appearance={{
        baseTheme: dark,
        variables: {
          colorPrimary: '#7B61FF',
          colorBackground: '#12121E',
          colorText: '#F0EFF4',
          colorInputBackground: '#1A1A2E',
          colorInputText: '#F0EFF4',
          borderRadius: '0.75rem',
        },
      }}
    >
      <App />
    </ClerkProvider>
  )
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Root />
  </StrictMode>,
)
