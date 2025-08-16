import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useSpring, animated } from '@react-spring/web'
import {
  MapPin,
  MessageCircle,
  Camera,
  Calendar,
  Zap,
  Shield,
  Smartphone,
  ArrowRight,
  Star,
  Users,
  Clock,
  Brain,
  Globe,
  Sparkles,
  TrendingUp,
  Award,
  CheckCircle
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

const HomePage: React.FC = () => {
  const fadeIn = useSpring({
    from: { opacity: 0, transform: 'translateY(50px)' },
    to: { opacity: 1, transform: 'translateY(0px)' },
    config: { tension: 280, friction: 60 }
  })

  const features = [
    {
      icon: Brain,
      title: 'IBM watsonx AI',
      description: 'Powered by IBM\'s enterprise-grade AI platform untuk akurasi maksimal',
      color: 'from-blue-600 to-blue-800',
      highlight: true
    },
    {
      icon: MessageCircle,
      title: 'Multimodal Input',
      description: 'Teks, suara, dan gambar - semua dalam satu platform terintegrasi',
      color: 'from-purple-500 to-indigo-600'
    },
    {
      icon: Zap,
      title: 'AI Fallback Chain',
      description: 'IBM watsonx → Hugging Face → Replicate untuk keandalan 24/7',
      color: 'from-orange-500 to-red-500'
    },
    {
      icon: Globe,
      title: 'Peta Interaktif',
      description: 'Visualisasi rute real-time dengan MapLibre dan OpenStreetMap',
      color: 'from-green-500 to-emerald-600'
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Validasi dengan database referensi dan prompt template terverifikasi',
      color: 'from-gray-600 to-gray-800'
    },
    {
      icon: TrendingUp,
      title: 'Analytics Dashboard',
      description: 'Real-time insights dan performance monitoring untuk optimasi',
      color: 'from-cyan-500 to-blue-600'
    }
  ]

  const stats = [
    { icon: Users, value: '10K+', label: 'Active Users', color: 'text-blue-600' },
    { icon: MapPin, value: '500+', label: 'Destinations', color: 'text-green-600' },
    { icon: Star, value: '4.9', label: 'User Rating', color: 'text-yellow-600' },
    { icon: Clock, value: '99.9%', label: 'Uptime', color: 'text-purple-600' }
  ]

  const quickActions = [
    {
      title: 'Smart Trip Planner',
      description: 'AI-powered itinerary dengan estimasi biaya real-time dan optimasi rute',
      href: '/plan',
      icon: Calendar,
      color: 'bg-gradient-to-r from-blue-500 to-blue-700',
      badge: 'Popular'
    },
    {
      title: 'Vision Recognition',
      description: 'Advanced computer vision untuk identifikasi landmark dan POI',
      href: '/vision',
      icon: Camera,
      color: 'bg-gradient-to-r from-purple-500 to-purple-700',
      badge: 'AI-Powered'
    },
    {
      title: 'Intelligent Assistant',
      description: 'Conversational AI dengan knowledge base wisata Indonesia',
      href: '/chat',
      icon: MessageCircle,
      color: 'bg-gradient-to-r from-green-500 to-green-700',
      badge: 'New'
    }
  ]

  const achievements = [
    { icon: Award, text: 'IBM Partner Excellence Award 2024' },
    { icon: CheckCircle, text: 'ISO 27001 Certified Security' },
    { icon: Sparkles, text: 'Best AI Innovation - TechCrunch' },
    { icon: TrendingUp, text: '300% Growth in User Adoption' }
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10"></div>
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            backgroundSize: '60px 60px'
          }}></div>
        </div>

        <div className="container mx-auto px-4 py-24 relative z-10">
          <animated.div style={fadeIn} className="text-center max-w-6xl mx-auto">
            {/* IBM Partnership Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6 }}
              className="inline-flex items-center gap-2 bg-blue-600/20 backdrop-blur-sm border border-blue-400/30 rounded-full px-6 py-2 mb-8"
            >
              <Brain className="h-5 w-5 text-blue-300" />
              <span className="text-blue-200 font-medium">Powered by IBM watsonx AI</span>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-5xl md:text-7xl font-bold mb-8 leading-tight"
            >
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                AI Travel Guide
              </span>
              <br />
              <span className="text-white text-4xl md:text-5xl">Enterprise Edition</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl md:text-2xl text-blue-100 mb-12 leading-relaxed max-w-4xl mx-auto"
            >
              Platform AI terdepan untuk industri pariwisata Indonesia. Mengintegrasikan
              <span className="text-blue-300 font-semibold"> IBM watsonx</span>, computer vision,
              dan natural language processing untuk pengalaman wisata yang tak terlupakan.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16"
            >
              <Link to="/plan">
                <Button size="lg" className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-10 py-4 text-lg font-semibold shadow-2xl hover:shadow-blue-500/25 transition-all duration-300">
                  Start Demo
                  <ArrowRight className="ml-3 h-6 w-6" />
                </Button>
              </Link>

              <Button
                variant="outline"
                size="lg"
                onClick={() => {
                  document.getElementById('features-section')?.scrollIntoView({ behavior: 'smooth' })
                }}
                className="px-10 py-4 text-lg border-blue-300 text-blue-200 hover:bg-blue-600/20 backdrop-blur-sm"
              >
                <Smartphone className="mr-3 h-6 w-6" />
                View Features
              </Button>
            </motion.div>

            {/* Achievements */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto"
            >
              {achievements.map((achievement, index) => (
                <div key={index} className="flex items-center gap-3 bg-white/10 backdrop-blur-sm rounded-lg px-4 py-3 border border-white/20">
                  <achievement.icon className="h-5 w-5 text-blue-300 flex-shrink-0" />
                  <span className="text-blue-100 text-sm font-medium">{achievement.text}</span>
                </div>
              ))}
            </motion.div>
          </animated.div>
        </div>

        {/* Animated Background Elements */}
        <div className="absolute top-20 left-10 opacity-30">
          <motion.div
            animate={{ y: [0, -30, 0], rotate: [0, 10, 0] }}
            transition={{ duration: 6, repeat: Infinity }}
          >
            <Brain className="h-16 w-16 text-blue-400" />
          </motion.div>
        </div>
        <div className="absolute top-40 right-20 opacity-30">
          <motion.div
            animate={{ y: [0, 30, 0], rotate: [0, -10, 0] }}
            transition={{ duration: 8, repeat: Infinity }}
          >
            <Globe className="h-12 w-12 text-purple-400" />
          </motion.div>
        </div>
        <div className="absolute bottom-20 left-1/4 opacity-20">
          <motion.div
            animate={{ y: [0, -20, 0], x: [0, 10, 0] }}
            transition={{ duration: 7, repeat: Infinity }}
          >
            <Sparkles className="h-14 w-14 text-cyan-400" />
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-gradient-to-r from-gray-50 to-blue-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
              Platform Performance
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Metrics yang membuktikan keunggulan platform AI Travel Guide
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.5, y: 50 }}
                whileInView={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.05 }}
                className="text-center group"
              >
                <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100">
                  <div className="flex justify-center mb-6">
                    <div className="p-4 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 group-hover:scale-110 transition-transform duration-300">
                      <stat.icon className="h-8 w-8 text-white" />
                    </div>
                  </div>
                  <div className={`text-4xl font-bold mb-3 ${stat.color}`}>{stat.value}</div>
                  <div className="text-gray-600 font-medium">{stat.label}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features-section" className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-4xl md:text-5xl font-bold text-gray-800 mb-6">
                Enterprise AI Features
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                Teknologi AI enterprise-grade yang mengintegrasikan IBM watsonx dengan
                machine learning terdepan untuk solusi pariwisata yang komprehensif
              </p>
            </motion.div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.02, y: -5 }}
                className="group"
              >
                <Card className={`h-full border-0 shadow-xl hover:shadow-2xl transition-all duration-500 ${feature.highlight ? 'ring-2 ring-blue-500 ring-opacity-50' : ''}`}>
                  <CardHeader className="text-center pb-6">
                    {feature.highlight && (
                      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                        <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                          Featured
                        </span>
                      </div>
                    )}
                    <div className={`w-20 h-20 mx-auto rounded-2xl bg-gradient-to-r ${feature.color} flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg`}>
                      <feature.icon className="h-10 w-10 text-white" />
                    </div>
                    <CardTitle className="text-2xl font-bold group-hover:text-blue-600 transition-colors">
                      {feature.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="text-center">
                    <CardDescription className="text-gray-600 text-lg leading-relaxed">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Quick Actions Section */}
      <section id="demo-section" className="py-24 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-4xl md:text-5xl font-bold text-gray-800 mb-6">
                Experience the Demo
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                Jelajahi kemampuan platform AI Travel Guide dengan demo interaktif
                yang menampilkan teknologi IBM watsonx dalam aksi
              </p>
            </motion.div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
            {quickActions.map((action, index) => (
              <motion.div
                key={action.title}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.15 }}
                whileHover={{ scale: 1.03, y: -10 }}
                className="group"
              >
                <Link to={action.href}>
                  <Card className="h-full border-0 shadow-2xl hover:shadow-3xl transition-all duration-500 cursor-pointer group relative overflow-hidden">
                    {/* Badge */}
                    <div className="absolute top-4 right-4 z-10">
                      <span className="bg-white/90 backdrop-blur-sm text-gray-700 px-3 py-1 rounded-full text-sm font-semibold shadow-lg">
                        {action.badge}
                      </span>
                    </div>

                    {/* Background Gradient */}
                    <div className={`absolute inset-0 ${action.color} opacity-5 group-hover:opacity-10 transition-opacity duration-300`}></div>

                    <CardHeader className="text-center pb-6 relative z-10">
                      <div className={`w-24 h-24 mx-auto rounded-2xl ${action.color} flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-xl`}>
                        <action.icon className="h-12 w-12 text-white" />
                      </div>
                      <CardTitle className="text-2xl font-bold group-hover:text-blue-600 transition-colors mb-2">
                        {action.title}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="text-center relative z-10">
                      <CardDescription className="text-gray-600 text-lg leading-relaxed mb-6">
                        {action.description}
                      </CardDescription>
                      <div className="flex items-center justify-center text-blue-600 group-hover:text-blue-700 font-semibold text-lg">
                        Try Demo
                        <ArrowRight className="ml-3 h-5 w-5 group-hover:translate-x-2 transition-transform duration-300" />
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-900 relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            backgroundSize: '60px 60px'
          }}></div>
        </div>

        <div className="container mx-auto px-4 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-4xl md:text-6xl font-bold text-white mb-8 leading-tight">
              Ready for
              <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent"> Enterprise AI</span>?
            </h2>
            <p className="text-xl md:text-2xl text-blue-100 mb-12 max-w-4xl mx-auto leading-relaxed">
              Bergabunglah dengan perusahaan-perusahaan terdepan yang telah mengadopsi
              AI Travel Guide untuk transformasi digital industri pariwisata Indonesia.
            </p>

            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
              <Link to="/plan">
                <Button
                  size="lg"
                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-12 py-4 text-lg font-semibold shadow-2xl hover:shadow-blue-500/25 transition-all duration-300"
                >
                  Start Enterprise Demo
                  <ArrowRight className="ml-3 h-6 w-6" />
                </Button>
              </Link>

              <Button
                size="lg"
                variant="outline"
                className="border-blue-300 text-blue-200 hover:bg-blue-600/20 backdrop-blur-sm px-12 py-4 text-lg"
              >
                Schedule Consultation
                <Calendar className="ml-3 h-6 w-6" />
              </Button>
            </div>

            {/* Contact Info */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 max-w-2xl mx-auto border border-white/20">
              <h3 className="text-2xl font-bold text-white mb-4">Contact IBM Jakarta</h3>
              <p className="text-blue-100 text-lg">
                Untuk implementasi enterprise dan partnership opportunities
              </p>
              <div className="mt-6 flex flex-col sm:flex-row gap-4 justify-center items-center text-blue-200">
                <div className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  <span>Jakarta, Indonesia</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  <span>24/7 Support</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
