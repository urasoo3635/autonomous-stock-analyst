import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface Stock {
  id: number
  ticker: str
  name: str
  sector: str | null
  market: str | null
  description: str | null
}

export interface StockListResponse {
  stocks: Stock[]
  total: number
}

// API Functions
export const fetchStocks = async (): Promise<StockListResponse> => {
  const response = await api.get('/stocks')
  return response.data
}

export const createStock = async (ticker: string, name: string): Promise<Stock> => {
  const response = await api.post('/stocks', { ticker, name })
  return response.data
}
