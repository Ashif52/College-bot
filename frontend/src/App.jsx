import Navbar from './components/Navbar'
import HeroSection from './components/HeroSection'
import StatsCounter from './components/StatsCounter'
import WhyChoose from './components/WhyChoose'
import CourseCards from './components/CourseCards'
import CampusGallery from './components/CampusGallery'
import Testimonials from './components/Testimonials'
import AdmissionsSection from './components/AdmissionsSection'
import Footer from './components/Footer'
import ChatbotWidget from './components/chatbot/ChatbotWidget'

export default function App() {
  return (
    <div className="min-h-screen bg-navy-950 text-white font-sans selection:bg-accent-400/30">
      <Navbar />
      <main>
        <HeroSection />
        <StatsCounter />
        <WhyChoose />
        <CourseCards />
        <CampusGallery />
        <Testimonials />
        <AdmissionsSection />
      </main>
      <Footer />

      {/* High-Fidelity Chatbot with XState & Twilio Voice */}
      <ChatbotWidget />
    </div>
  )
}
