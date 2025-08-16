import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { MessageCircle, Send, Mic, MicOff, Bot, User, Loader2 } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
  suggestions?: string[]
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: 'Halo! Saya AI Travel Guide. Saya siap membantu Anda merencanakan perjalanan wisata di Indonesia. Anda bisa bertanya tentang destinasi, budget, transportasi, atau apa saja seputar wisata. Ada yang ingin Anda tanyakan?',
      timestamp: new Date(),
      suggestions: [
        'Rekomendasi tempat wisata di Bali',
        'Budget untuk liburan 3 hari di Yogyakarta',
        'Transportasi dari Jakarta ke Bandung'
      ]
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (message: string = inputMessage) => {
    if (!message.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Demo mode - simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Mock AI response
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: generateMockResponse(message),
        timestamp: new Date(),
        suggestions: [
          'Tanyakan tentang kuliner lokal',
          'Info transportasi umum',
          'Rekomendasi hotel budget'
        ]
      }

      setMessages(prev => [...prev, aiResponse])
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateMockResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase()
    
    if (lowerMessage.includes('bali')) {
      return 'Bali memiliki banyak tempat wisata menarik! Beberapa yang populer: Uluwatu (sunset di tebing), Tanah Lot (pura di atas batu karang), Ubud (sawah terasering dan budaya), Kuta/Seminyak (pantai dan surfing), dan Nusa Penida (pemandangan alam yang menakjubkan). Budget untuk 3-4 hari sekitar 2-4 juta rupiah tergantung akomodasi dan aktivitas yang dipilih.'
    }
    
    if (lowerMessage.includes('yogyakarta') || lowerMessage.includes('jogja')) {
      return 'Yogyakarta adalah kota budaya yang kaya! Wajib dikunjungi: Candi Borobudur (sunrise terbaik), Candi Prambanan, Keraton Yogyakarta, Malioboro Street untuk belanja dan kuliner, Taman Sari (bekas kolam pemandian raja). Jangan lupa coba gudeg, bakpia, dan wedang ronde. Budget 3 hari sekitar 1-2 juta rupiah sudah cukup nyaman.'
    }
    
    if (lowerMessage.includes('jakarta') || lowerMessage.includes('bandung')) {
      return 'Rute Jakarta-Bandung sangat populer! Transportasi: kereta api (3 jam, 60-150rb), bus (4-5 jam, 30-80rb), atau mobil pribadi (3-4 jam tol). Di Bandung bisa kunjungi Tangkuban Perahu, Jalan Braga, factory outlets, dan nikmati udara sejuk. Kuliner wajib: batagor, siomay, surabi, dan bandrek.'
    }
    
    if (lowerMessage.includes('budget') || lowerMessage.includes('biaya')) {
      return 'Budget wisata Indonesia bervariasi tergantung destinasi dan gaya perjalanan:\n\n💰 Hemat: 200-500rb/hari (homestay, warung, transportasi umum)\n💳 Sedang: 500rb-1jt/hari (hotel 3*, restoran, mix transport)\n💎 Premium: 1jt+/hari (hotel 4-5*, fine dining, private transport)\n\nTips hemat: booking early, paket tour, makan di warung lokal, gunakan transportasi umum.'
    }
    
    return 'Terima kasih atas pertanyaannya! Saya siap membantu dengan informasi wisata Indonesia. Bisa Anda spesifikkan lebih detail tentang destinasi, durasi perjalanan, atau aspek tertentu yang ingin Anda ketahui? Saya akan berikan rekomendasi yang sesuai dengan kebutuhan Anda.'
  }

  const handleVoiceInput = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      const recognition = new SpeechRecognition()
      
      recognition.lang = 'id-ID'
      recognition.continuous = false
      recognition.interimResults = false

      recognition.onstart = () => {
        setIsListening(true)
      }

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setInputMessage(transcript)
        setIsListening(false)
      }

      recognition.onerror = () => {
        setIsListening(false)
      }

      recognition.onend = () => {
        setIsListening(false)
      }

      recognition.start()
    } else {
      alert('Browser Anda tidak mendukung speech recognition')
    }
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
              Chat dengan AI Travel Guide
            </h1>
            <p className="text-xl text-gray-600">
              Tanyakan apa saja seputar wisata Indonesia
            </p>
          </div>

          <Card className="h-[600px] flex flex-col">
            <CardHeader className="border-b">
              <CardTitle className="flex items-center">
                <MessageCircle className="mr-2 h-5 w-5" />
                Percakapan
              </CardTitle>
              <CardDescription>
                Gunakan teks atau suara untuk bertanya
              </CardDescription>
            </CardHeader>

            {/* Messages */}
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start space-x-2 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      message.type === 'user' 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-purple-500 text-white'
                    }`}>
                      {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                    </div>
                    
                    <div className={`rounded-lg p-3 ${
                      message.type === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-white border shadow-sm'
                    }`}>
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      <p className={`text-xs mt-1 ${
                        message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {message.timestamp.toLocaleTimeString('id-ID', { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </p>
                      
                      {message.suggestions && (
                        <div className="mt-3 space-y-1">
                          <p className="text-xs text-gray-500 mb-2">Saran pertanyaan:</p>
                          {message.suggestions.map((suggestion, index) => (
                            <button
                              key={index}
                              onClick={() => handleSendMessage(suggestion)}
                              className="block w-full text-left text-xs bg-gray-50 hover:bg-gray-100 p-2 rounded border transition-colors"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2">
                    <div className="w-8 h-8 rounded-full bg-purple-500 text-white flex items-center justify-center">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="bg-white border shadow-sm rounded-lg p-3">
                      <div className="flex items-center space-x-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-gray-500">AI sedang mengetik...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </CardContent>

            {/* Input */}
            <div className="border-t p-4">
              <div className="flex space-x-2">
                <div className="flex-1 relative">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Ketik pertanyaan Anda..."
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    disabled={isLoading}
                  />
                </div>
                
                <Button
                  onClick={handleVoiceInput}
                  disabled={isLoading || isListening}
                  variant="outline"
                  size="icon"
                  className={isListening ? 'bg-red-50 border-red-200' : ''}
                >
                  {isListening ? (
                    <MicOff className="h-4 w-4 text-red-500" />
                  ) : (
                    <Mic className="h-4 w-4" />
                  )}
                </Button>
                
                <Button
                  onClick={() => handleSendMessage()}
                  disabled={isLoading || !inputMessage.trim()}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              
              {isListening && (
                <p className="text-sm text-red-500 mt-2 text-center">
                  🎤 Mendengarkan... Silakan bicara
                </p>
              )}
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}

export default ChatPage
