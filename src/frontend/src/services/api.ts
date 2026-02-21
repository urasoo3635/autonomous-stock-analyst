import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// --- 型定義 ---

export interface Stock {
  id: number
  ticker: string
  name: string
  sector: string | null
  market: string | null
  description: string | null
  is_active: boolean
}

export interface StockListResponse {
  stocks: Stock[]
  total: number
}

export interface StockPrice {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  adjusted_close: number | null
}

export interface StockPriceListResponse {
  ticker: string
  count: number
  prices: StockPrice[]
}

export interface TechnicalIndicator {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  sma_20: number | null
  sma_50: number | null
  sma_200: number | null
  rsi_14: number | null
  macd: number | null
  macd_hist: number | null
  macd_signal: number | null
  bb_upper: number | null
  bb_middle: number | null
  bb_lower: number | null
}

export interface SentimentResponse {
  text: string
  label: string
  score: number
}

export interface PredictionResponse {
  ticker: string
  target_days: number
  predicted_return: number
  confidence: number | null
}

export interface NewsArticle {
  title: string
  source: string
  published: string
  url: string
  summary: string
}

export interface NewsResponse {
  query: string
  count: number
  articles: NewsArticle[]
}

// --- API 呼び出し関数 ---

export const fetchStocks = async (): Promise<StockListResponse> => {
  const response = await api.get('/stocks')
  return response.data
}

export const createStock = async (ticker: string, name: string): Promise<Stock> => {
  const response = await api.post('/stocks', { ticker, name })
  return response.data
}

export const fetchStockPrices = async (ticker: string): Promise<StockPriceListResponse> => {
  const response = await api.post(`/stocks/${ticker}/fetch`, { period: '1y' })
  return response.data
}

export const getStockPrices = async (ticker: string, limit = 365): Promise<StockPriceListResponse> => {
  const response = await api.get(`/stocks/${ticker}/prices`, { params: { limit } })
  return response.data
}

export const getTechnicalIndicators = async (
  ticker: string,
  days = 90,
): Promise<TechnicalIndicator[]> => {
  const response = await api.get(`/analysis/${ticker}/technical`, { params: { days } })
  return response.data
}

export const predictPrice = async (
  ticker: string,
  targetDays = 30,
): Promise<PredictionResponse> => {
  const response = await api.post(`/analysis/${ticker}/predict`, null, {
    params: { target_days: targetDays },
  })
  return response.data
}

export const fetchNews = async (query: string, limit = 10): Promise<NewsResponse> => {
  const response = await api.get(`/news/${query}`, { params: { limit } })
  return response.data
}
