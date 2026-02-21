import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'
import {
  getTechnicalIndicators,
  fetchStockPrices,
  fetchNews,
  predictPrice,
} from '../services/api'
import { ArrowLeft, RefreshCw, TrendingUp, TrendingDown, Newspaper } from 'lucide-react'

const sentimentColor = (label: string) => {
  if (label === 'positive') return 'text-green-600 bg-green-50'
  if (label === 'negative') return 'text-red-600 bg-red-50'
  return 'text-gray-600 bg-gray-50'
}

const StockDetail = () => {
  const { ticker } = useParams<{ ticker: string }>()
  const [chartDays, setChartDays] = useState<30 | 90 | 180>(90)

  const tickerStr = ticker ?? ''

  // テクニカル指標取得
  const { data: indicators, isLoading: loadingChart, refetch: refetchChart } = useQuery({
    queryKey: ['technical', tickerStr, chartDays],
    queryFn: () => getTechnicalIndicators(tickerStr, chartDays),
    enabled: !!tickerStr,
  })

  // データ取得（fetch）
  const fetchMutation = useMutation({
    mutationFn: () => fetchStockPrices(tickerStr),
    onSuccess: () => refetchChart(),
  })

  // ニュース取得
  const { data: news } = useQuery({
    queryKey: ['news', tickerStr],
    queryFn: () => fetchNews(tickerStr, 5),
    enabled: !!tickerStr,
  })

  // 株価予測
  const {
    data: prediction,
    isLoading: loadingPred,
    refetch: refetchPred,
  } = useQuery({
    queryKey: ['prediction', tickerStr],
    queryFn: () => predictPrice(tickerStr, 30),
    enabled: !!tickerStr,
    staleTime: 1000 * 60 * 60, // 1h キャッシュ
  })

  // チャートデータ: closeとSMA20/50
  const chartData = indicators?.map((d) => ({
    date: d.date,
    close: Number(d.close?.toFixed(2)),
    sma20: d.sma_20 != null ? Number(d.sma_20.toFixed(2)) : null,
    sma50: d.sma_50 != null ? Number(d.sma_50.toFixed(2)) : null,
    rsi: d.rsi_14 != null ? Number(d.rsi_14.toFixed(1)) : null,
    volume: d.volume,
  })) ?? []

  const latest = chartData[chartData.length - 1]
  const prev = chartData[chartData.length - 2]
  const priceChange =
    latest && prev ? ((latest.close - prev.close) / prev.close) * 100 : null

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center gap-4">
        <Link to="/" className="text-gray-500 hover:text-gray-800">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">{tickerStr}</h1>
        {priceChange != null && (
          <div
            className={`flex items-center gap-1 text-sm font-semibold px-2 py-1 rounded ${
              priceChange >= 0 ? 'text-green-700 bg-green-50' : 'text-red-700 bg-red-50'
            }`}
          >
            {priceChange >= 0 ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            {priceChange >= 0 ? '+' : ''}
            {priceChange.toFixed(2)}%
          </div>
        )}
        <div className="ml-auto flex gap-2">
          <button
            onClick={() => fetchMutation.mutate()}
            disabled={fetchMutation.isPending}
            className="flex items-center gap-1 text-sm px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${fetchMutation.isPending ? 'animate-spin' : ''}`} />
            データ更新
          </button>
        </div>
      </div>

      {/* 期間セレクタ */}
      <div className="flex gap-2">
        {([30, 90, 180] as const).map((d) => (
          <button
            key={d}
            onClick={() => setChartDays(d)}
            className={`px-3 py-1 text-sm rounded-lg transition ${
              chartDays === d
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            {d}日
          </button>
        ))}
      </div>

      {/* --- 株価チャート --- */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h2 className="text-base font-semibold text-gray-700 mb-4">株価チャート</h2>
        {loadingChart ? (
          <div className="h-64 flex items-center justify-center text-gray-400">読み込み中...</div>
        ) : chartData.length === 0 ? (
          <div className="h-64 flex flex-col items-center justify-center gap-2 text-gray-400">
            <p>データがありません</p>
            <button
              onClick={() => fetchMutation.mutate()}
              className="text-blue-600 underline text-sm"
            >
              データを取得する
            </button>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11 }}
                tickFormatter={(v) => v.slice(5)} // MM-DD 表示
              />
              <YAxis yAxisId="price" domain={['auto', 'auto']} width={70} tick={{ fontSize: 11 }} />
              <YAxis yAxisId="volume" orientation="right" hide />
              <Tooltip
                contentStyle={{ borderRadius: 8, border: '1px solid #e5e7eb' }}
                formatter={(v: number) => v?.toLocaleString()}
              />
              <Legend />
              <Bar yAxisId="volume" dataKey="volume" fill="#e5e7eb" opacity={0.4} name="出来高" />
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="close"
                stroke="#2563eb"
                dot={false}
                strokeWidth={2}
                name="終値"
              />
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="sma20"
                stroke="#f59e0b"
                dot={false}
                strokeWidth={1.5}
                strokeDasharray="4 2"
                name="SMA20"
              />
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="sma50"
                stroke="#10b981"
                dot={false}
                strokeWidth={1.5}
                strokeDasharray="4 2"
                name="SMA50"
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* --- RSI チャート --- */}
      {chartData.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-base font-semibold text-gray-700 mb-1">RSI (14)</h2>
          <p className="text-xs text-gray-400 mb-4">30以下: 売られ過ぎ / 70以上: 買われ過ぎ</p>
          <ResponsiveContainer width="100%" height={120}>
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(v) => v.slice(5)} />
              <YAxis domain={[0, 100]} ticks={[30, 50, 70]} width={30} tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ borderRadius: 8 }} />
              <Line
                type="monotone"
                dataKey="rsi"
                stroke="#8b5cf6"
                dot={false}
                strokeWidth={1.5}
                name="RSI"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* --- 株価予測 --- */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-base font-semibold text-gray-700 mb-4">30日間 株価予測</h2>
          {loadingPred ? (
            <p className="text-gray-400 text-sm">予測計算中... (しばらくお待ちください)</p>
          ) : prediction ? (
            <div className="space-y-3">
              <div
                className={`text-4xl font-bold ${
                  prediction.predicted_return >= 0 ? 'text-green-600' : 'text-red-500'
                }`}
              >
                {prediction.predicted_return >= 0 ? '+' : ''}
                {(prediction.predicted_return * 100).toFixed(2)}%
              </div>
              <p className="text-xs text-gray-400">
                ※ 過去データに基づく参考値です。投資判断の根拠には使わないでください。
              </p>
              <button
                onClick={() => refetchPred()}
                className="text-xs text-blue-600 hover:underline"
              >
                再計算する
              </button>
            </div>
          ) : (
            <p className="text-gray-400 text-sm">データが不十分です（最低100日分必要）</p>
          )}
        </div>

        {/* --- ニュース --- */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center gap-2 mb-4">
            <Newspaper className="w-4 h-4 text-gray-500" />
            <h2 className="text-base font-semibold text-gray-700">関連ニュース</h2>
          </div>
          {news?.articles && news.articles.length > 0 ? (
            <ul className="space-y-3">
              {news.articles.map((article, i) => (
                <li key={i} className="border-b border-gray-50 pb-3 last:border-0">
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-medium text-blue-700 hover:underline line-clamp-2"
                  >
                    {article.title}
                  </a>
                  <p className="text-xs text-gray-400 mt-1">
                    {article.source} · {article.published?.slice(0, 16)}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400 text-sm">ニュースが見つかりません</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default StockDetail
