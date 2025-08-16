import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Calendar, MapPin, DollarSign, Users, Clock, Loader2 } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

const PlanPage: React.FC = () => {
  const [formData, setFormData] = useState({
    destination: '',
    duration: 3,
    budget: 'sedang',
    preferences: [] as string[]
  })
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const budgetOptions = [
    { value: 'murah', label: 'Hemat (< 500rb/hari)', icon: '💰' },
    { value: 'sedang', label: 'Sedang (500rb - 1jt/hari)', icon: '💳' },
    { value: 'mahal', label: 'Premium (> 1jt/hari)', icon: '💎' }
  ]

  const preferenceOptions = [
    { value: 'halal', label: 'Makanan Halal', icon: '🥘' },
    { value: 'vegetarian', label: 'Vegetarian', icon: '🥗' },
    { value: 'accessibility', label: 'Aksesibilitas', icon: '♿' },
    { value: 'family_friendly', label: 'Ramah Keluarga', icon: '👨‍👩‍👧‍👦' }
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // Demo mode - simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Mock result
      setResult({
        title: `Perjalanan ${formData.duration} Hari ke ${formData.destination}`,
        destination: formData.destination,
        duration_days: formData.duration,
        daily_routes: Array.from({ length: formData.duration }, (_, i) => ({
          day: i + 1,
          date: new Date(Date.now() + i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          activities: [
            {
              time: '09:00',
              activity: `Eksplorasi ${formData.destination} - Hari ${i + 1}`,
              location: formData.destination,
              description: 'Kunjungi tempat wisata populer dan nikmati kuliner lokal',
              estimated_cost: formData.budget === 'murah' ? 200000 : formData.budget === 'sedang' ? 400000 : 800000
            }
          ],
          estimated_cost: formData.budget === 'murah' ? 300000 : formData.budget === 'sedang' ? 600000 : 1200000
        })),
        cost_estimate: {
          total: formData.duration * (formData.budget === 'murah' ? 300000 : formData.budget === 'sedang' ? 600000 : 1200000),
          currency: 'IDR'
        },
        ai_source: 'demo',
        confidence: 0.9
      })
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-4xl mx-auto"
        >
          <div className="text-center mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
              Rencanakan Perjalanan Anda
            </h1>
            <p className="text-xl text-gray-600">
              Buat itinerary perjalanan yang sempurna dengan bantuan AI
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Form */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="mr-2 h-5 w-5" />
                  Detail Perjalanan
                </CardTitle>
                <CardDescription>
                  Isi informasi perjalanan Anda untuk mendapatkan rekomendasi terbaik
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Destination */}
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      <MapPin className="inline mr-1 h-4 w-4" />
                      Destinasi
                    </label>
                    <Input
                      type="text"
                      placeholder="Contoh: Bandung, Yogyakarta, Bali"
                      value={formData.destination}
                      onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                      required
                    />
                  </div>

                  {/* Duration */}
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      <Clock className="inline mr-1 h-4 w-4" />
                      Durasi Perjalanan
                    </label>
                    <select
                      className="w-full p-2 border border-gray-300 rounded-md"
                      value={formData.duration}
                      onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) })}
                    >
                      {[1, 2, 3, 4, 5, 6, 7].map(day => (
                        <option key={day} value={day}>
                          {day} Hari
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Budget */}
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      <DollarSign className="inline mr-1 h-4 w-4" />
                      Range Budget
                    </label>
                    <div className="grid grid-cols-1 gap-2">
                      {budgetOptions.map(option => (
                        <label key={option.value} className="flex items-center p-3 border rounded-md cursor-pointer hover:bg-gray-50">
                          <input
                            type="radio"
                            name="budget"
                            value={option.value}
                            checked={formData.budget === option.value}
                            onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                            className="mr-3"
                          />
                          <span className="mr-2">{option.icon}</span>
                          <span>{option.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Preferences */}
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      <Users className="inline mr-1 h-4 w-4" />
                      Preferensi Khusus
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {preferenceOptions.map(option => (
                        <label key={option.value} className="flex items-center p-2 border rounded-md cursor-pointer hover:bg-gray-50">
                          <input
                            type="checkbox"
                            value={option.value}
                            checked={formData.preferences.includes(option.value)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setFormData({
                                  ...formData,
                                  preferences: [...formData.preferences, option.value]
                                })
                              } else {
                                setFormData({
                                  ...formData,
                                  preferences: formData.preferences.filter(p => p !== option.value)
                                })
                              }
                            }}
                            className="mr-2"
                          />
                          <span className="mr-1">{option.icon}</span>
                          <span className="text-sm">{option.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <Button
                    type="submit"
                    disabled={isLoading || !formData.destination}
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Membuat Rencana...
                      </>
                    ) : (
                      'Buat Rencana Perjalanan'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Result */}
            <div>
              {result ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-4"
                >
                  <Card>
                    <CardHeader>
                      <CardTitle>{result.title}</CardTitle>
                      <CardDescription>
                        Total Estimasi: {formatCurrency(result.cost_estimate.total)}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {result.daily_routes.map((day: any) => (
                          <div key={day.day} className="border rounded-lg p-4">
                            <h3 className="font-semibold mb-2">
                              Hari {day.day} - {new Date(day.date).toLocaleDateString('id-ID')}
                            </h3>
                            {day.activities.map((activity: any, idx: number) => (
                              <div key={idx} className="flex items-start space-x-3 mb-2">
                                <span className="text-sm font-medium text-blue-600 min-w-[50px]">
                                  {activity.time}
                                </span>
                                <div className="flex-1">
                                  <p className="font-medium">{activity.activity}</p>
                                  <p className="text-sm text-gray-600">{activity.description}</p>
                                  <p className="text-sm text-green-600">
                                    Estimasi: {formatCurrency(activity.estimated_cost)}
                                  </p>
                                </div>
                              </div>
                            ))}
                            <div className="mt-2 pt-2 border-t">
                              <p className="text-sm font-medium">
                                Total Hari {day.day}: {formatCurrency(day.estimated_cost)}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ) : (
                <Card className="h-full flex items-center justify-center">
                  <CardContent className="text-center py-12">
                    <Calendar className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500">
                      Isi form di sebelah kiri untuk membuat rencana perjalanan Anda
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default PlanPage
