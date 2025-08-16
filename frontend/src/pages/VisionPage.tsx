import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Camera, Upload, Loader2, MapPin, Info } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

const VisionPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      const reader = new FileReader()
      reader.onload = () => setPreview(reader.result as string)
      reader.readAsDataURL(file)
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return

    setIsLoading(true)
    try {
      // Demo mode - simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Mock result
      setResult({
        landmarks: [
          {
            name: 'Monumen Nasional (Monas)',
            description: 'Monumen setinggi 132 meter yang menjadi simbol kemerdekaan Indonesia, terletak di Jakarta Pusat',
            location: 'Jakarta Pusat, DKI Jakarta',
            category: 'monument',
            confidence: 0.92
          }
        ],
        summary: 'Teridentifikasi Monumen Nasional (Monas), landmark ikonik Jakarta yang merupakan simbol kemerdekaan Indonesia',
        ai_source: 'demo',
        confidence: 0.92
      })
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDemoAnalysis = () => {
    setResult({
      landmarks: [
        {
          name: 'Candi Borobudur',
          description: 'Candi Buddha terbesar di dunia dan Situs Warisan Dunia UNESCO',
          location: 'Magelang, Jawa Tengah',
          category: 'temple',
          confidence: 0.95
        }
      ],
      summary: 'Teridentifikasi Candi Borobudur, salah satu keajaiban dunia dan warisan budaya Indonesia',
      ai_source: 'demo',
      confidence: 0.95
    })
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
              Analisis Foto Landmark
            </h1>
            <p className="text-xl text-gray-600">
              Upload foto landmark untuk mendapatkan informasi detail tentang tempat wisata
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Upload Section */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Camera className="mr-2 h-5 w-5" />
                  Upload Foto
                </CardTitle>
                <CardDescription>
                  Pilih foto landmark atau tempat wisata untuk dianalisis
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* File Input */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-2">
                      Klik untuk upload foto atau drag & drop
                    </p>
                    <p className="text-sm text-gray-500">
                      Format: JPG, PNG, WebP (Max 5MB)
                    </p>
                  </label>
                </div>

                {/* Preview */}
                {preview && (
                  <div className="space-y-4">
                    <img
                      src={preview}
                      alt="Preview"
                      className="w-full h-64 object-cover rounded-lg"
                    />
                    <Button
                      onClick={handleAnalyze}
                      disabled={isLoading}
                      className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Menganalisis...
                        </>
                      ) : (
                        <>
                          <Camera className="mr-2 h-4 w-4" />
                          Analisis Foto
                        </>
                      )}
                    </Button>
                  </div>
                )}

                {/* Demo Button */}
                <div className="pt-4 border-t">
                  <Button
                    onClick={handleDemoAnalysis}
                    variant="outline"
                    className="w-full"
                  >
                    <Info className="mr-2 h-4 w-4" />
                    Coba Demo Analisis
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Result Section */}
            <div>
              {result ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-4"
                >
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <MapPin className="mr-2 h-5 w-5" />
                        Hasil Analisis
                      </CardTitle>
                      <CardDescription>
                        Confidence Score: {(result.confidence * 100).toFixed(1)}%
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="p-4 bg-blue-50 rounded-lg">
                          <p className="text-sm text-blue-800 mb-2">Ringkasan:</p>
                          <p className="text-blue-900">{result.summary}</p>
                        </div>

                        {result.landmarks.map((landmark: any, index: number) => (
                          <div key={index} className="border rounded-lg p-4">
                            <div className="flex items-start justify-between mb-2">
                              <h3 className="font-semibold text-lg">{landmark.name}</h3>
                              <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded-full">
                                {(landmark.confidence * 100).toFixed(1)}%
                              </span>
                            </div>
                            
                            <p className="text-gray-600 mb-2">{landmark.description}</p>
                            
                            {landmark.location && (
                              <div className="flex items-center text-sm text-gray-500 mb-2">
                                <MapPin className="h-4 w-4 mr-1" />
                                {landmark.location}
                              </div>
                            )}
                            
                            {landmark.category && (
                              <span className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">
                                {landmark.category}
                              </span>
                            )}
                          </div>
                        ))}

                        <div className="text-xs text-gray-500 text-center">
                          Powered by {result.ai_source} AI
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ) : (
                <Card className="h-full flex items-center justify-center">
                  <CardContent className="text-center py-12">
                    <Camera className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500 mb-4">
                      Upload foto landmark untuk melihat hasil analisis
                    </p>
                    <p className="text-sm text-gray-400">
                      AI akan mengidentifikasi tempat wisata dan memberikan informasi detail
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>

          {/* Tips Section */}
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>Tips untuk Hasil Terbaik</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="space-y-2">
                  <h4 className="font-medium">📸 Kualitas Foto:</h4>
                  <ul className="space-y-1 text-gray-600">
                    <li>• Gunakan pencahayaan yang baik</li>
                    <li>• Pastikan landmark terlihat jelas</li>
                    <li>• Hindari foto yang blur atau gelap</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">🎯 Sudut Pengambilan:</h4>
                  <ul className="space-y-1 text-gray-600">
                    <li>• Ambil dari sudut yang menunjukkan ciri khas</li>
                    <li>• Sertakan konteks sekitar jika memungkinkan</li>
                    <li>• Fokus pada detail arsitektur yang unik</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}

export default VisionPage
