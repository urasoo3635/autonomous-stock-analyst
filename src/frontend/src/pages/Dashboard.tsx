import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchStocks, createStock } from '../services/api'
import { Plus, ArrowRight, TrendingUp } from 'lucide-react'

const Dashboard = () => {
  const queryClient = useQueryClient()
  const [ticker, setTicker] = useState('')
  const [name, setName] = useState('')
  const [isOpen, setIsOpen] = useState(false)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['stocks'],
    queryFn: fetchStocks,
  })

  const mutation = useMutation({
    mutationFn: (newStock: { ticker: string; name: string }) =>
      createStock(newStock.ticker, newStock.name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stocks'] })
      setIsOpen(false)
      setTicker('')
      setName('')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (ticker && name) {
      mutation.mutate({ ticker, name })
    }
  }

  if (isLoading) return <div className="text-center py-10">読み込み中...</div>
  if (isError) return <div className="text-center py-10 text-red-500">エラーが発生しました</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">ダッシュボード</h1>
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          <Plus className="w-4 h-4" />
          銘柄登録
        </button>
      </div>

      {isOpen && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6">
          <form onSubmit={handleSubmit} className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">銘柄コード</label>
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                placeholder="例: 7203.T"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">銘柄名</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="例: トヨタ自動車"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="bg-gray-900 text-white px-6 py-2 rounded-lg hover:bg-gray-800 transition disabled:opacity-50"
            >
              {mutation.isPending ? '登録中...' : '登録'}
            </button>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data?.stocks.map((stock) => (
          <Link
            key={stock.id}
            to={`/stocks/${stock.ticker}`}
            className="block bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition group"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <span className="inline-block px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded mb-2">
                  {stock.ticker}
                </span>
                <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition">
                  {stock.name}
                </h3>
              </div>
              <div className="p-2 bg-blue-50 rounded-full group-hover:bg-blue-100 transition">
                <TrendingUp className="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <div className="flex justify-between items-center text-sm text-gray-500 mt-4 pt-4 border-t border-gray-100">
              <span>詳細を見る</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
            </div>
          </Link>
        ))}
      </div>

      {data?.stocks.length === 0 && (
        <div className="text-center py-20 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
          <p className="text-gray-500">登録された銘柄はありません</p>
        </div>
      )}
    </div>
  )
}

export default Dashboard
