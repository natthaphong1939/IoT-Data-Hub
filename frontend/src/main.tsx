import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import AlertComponent from './component/Alert.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AlertComponent />
    <main className="max-w-[1920px] m-auto min-h-screen bg-gray-200 p-4">
      <h1 className='mb-4'>Room</h1>
      <App />
    </main>
  </StrictMode>,
)