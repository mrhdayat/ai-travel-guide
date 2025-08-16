import React from 'react'
import { Link } from 'react-router-dom'
import { Brain, Heart, Mail, Building2, Phone, Globe } from 'lucide-react'

const Footer: React.FC = () => {
  return (
    <footer className="border-t bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-6">
            <div className="flex items-center space-x-3">
              <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center shadow-lg">
                <Brain className="h-7 w-7 text-white" />
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  AI Travel Guide
                </span>
                <span className="text-xs text-gray-500 font-medium">Enterprise Edition</span>
              </div>
            </div>
            <p className="text-sm text-gray-600 leading-relaxed">
              Platform AI enterprise untuk industri pariwisata Indonesia.
              Mengintegrasikan IBM watsonx dengan teknologi machine learning terdepan.
            </p>
          </div>

          {/* Solutions */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-gray-800">Platform Features</h3>
            <ul className="space-y-3 text-sm">
              <li>
                <Link to="/plan" className="text-gray-600 hover:text-blue-600 transition-colors flex items-center">
                  Smart Trip Planner
                </Link>
              </li>
              <li>
                <Link to="/vision" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Computer Vision AI
                </Link>
              </li>
              <li>
                <Link to="/chat" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Conversational AI
                </Link>
              </li>
              <li>
                <span className="text-gray-600">Real-time Analytics</span>
              </li>
            </ul>
          </div>

          {/* Enterprise */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-gray-800">Enterprise Solutions</h3>
            <ul className="space-y-3 text-sm text-gray-600">
              <li>IBM watsonx Integration</li>
              <li>Multi-modal AI Processing</li>
              <li>Enterprise Security</li>
              <li>24/7 Support</li>
              <li>Custom Implementation</li>
              <li>API Integration</li>
            </ul>
          </div>

          {/* Contact */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-gray-800">Contact IBM Jakarta</h3>
            <div className="space-y-3">
              <a
                href="mailto:ibm.jakarta@ibm.com"
                className="flex items-center space-x-2 text-sm text-gray-600 hover:text-blue-600 transition-colors"
              >
                <Mail className="h-4 w-4" />
                <span>ibm.jakarta@ibm.com</span>
              </a>
              <a
                href="tel:+62-21-5795-7000"
                className="flex items-center space-x-2 text-sm text-gray-600 hover:text-blue-600 transition-colors"
              >
                <Phone className="h-4 w-4" />
                <span>+62-21-5795-7000</span>
              </a>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Building2 className="h-4 w-4" />
                <span>Jakarta, Indonesia</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-6 md:space-y-0">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <span>Built with</span>
              <Heart className="h-4 w-4 text-red-500" />
              <span>for IBM Jakarta Partnership</span>
            </div>

            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <span>© 2024 AI Travel Guide</span>
              <span>•</span>
              <span>Enterprise Demo</span>
              <span>•</span>
              <span>IBM Partner Solution</span>
            </div>
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="text-center">
            <p className="text-xs text-gray-500 leading-relaxed">
              <strong>Technology Stack:</strong> React + TypeScript + Tailwind CSS + FastAPI +
              <span className="text-blue-600 font-semibold"> IBM watsonx</span> +
              Hugging Face + Replicate + PostgreSQL + Docker
            </p>
            <div className="mt-3 flex justify-center items-center space-x-4">
              <div className="flex items-center space-x-2 text-xs text-gray-500">
                <Globe className="h-3 w-3" />
                <span>Enterprise-grade Infrastructure</span>
              </div>
              <span className="text-gray-300">•</span>
              <div className="flex items-center space-x-2 text-xs text-gray-500">
                <Building2 className="h-3 w-3" />
                <span>ISO 27001 Certified</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
