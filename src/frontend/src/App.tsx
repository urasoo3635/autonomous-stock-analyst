import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import StockDetail from './pages/StockDetail'
import Layout from './components/Layout'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/stocks/:ticker" element={<StockDetail />} />
      </Routes>
    </Layout>
  )
}

export default App
