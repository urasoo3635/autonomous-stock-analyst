import { useParams } from 'react-router-dom'

const StockDetail = () => {
  const { ticker } = useParams<{ ticker: string }>()

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">{ticker} の詳細（開発中）</h1>
      </div>
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 min-h-[400px] flex items-center justify-center">
        <p className="text-gray-500">チャート実装予定地</p>
      </div>
    </div>
  )
}

export default StockDetail
