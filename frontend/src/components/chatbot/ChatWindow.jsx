import { useState, useRef, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import { X, Bot, Sparkles } from 'lucide-react'
import ChatMessage from './ChatMessage'
import ChatOptions from './ChatOptions'
import ChatInput from './ChatInput'
import LeadForm from './LeadForm'
import { submitLead, triggerAutoCall } from '../../api/lead'

const WELCOME_MESSAGE = `Hi 👋\nI'm EduBot, your college admissions assistant.\n\nI can help you with:\n• Admissions\n• Fees\n• Courses\n• Placement\n• Scholarships\n\nWhat would you like to know?`

const MAIN_OPTIONS = ['Admissions', 'Fees', 'Courses', 'Placement', 'Scholarships', 'Request Call']

const BOT_RESPONSES = {
    Admissions: {
        text: `Our engineering programs include:\n\n🖥️ Computer Science\n📡 Electronics & Communication\n⚙️ Mechanical\n🏗️ Civil Engineering\n\nWould you like to receive a call from our admissions team?`,
        options: ['Yes, Request Call', 'No, Thanks', '← Main Menu'],
    },
    Fees: {
        text: `Here's our fee structure (per year):\n\n💻 CSE — ₹1,50,000\n📡 ECE — ₹1,35,000\n⚙️ ME — ₹1,20,000\n🏗️ CE — ₹1,10,000\n\nScholarships available for merit students!\n\nWould you like to know more?`,
        options: ['Scholarships', 'Request Call', '← Main Menu'],
    },
    Courses: {
        text: `We offer 4-year B.Tech programs in:\n\n1. Computer Science Engineering\n   — AI/ML, Full Stack, Cloud, Cybersecurity\n2. Electronics & Communication\n   — VLSI, IoT, 5G, Embedded Systems\n3. Mechanical Engineering\n   — Robotics, CAD/CAM, 3D Printing\n4. Civil Engineering\n   — Smart Infra, Green Building\n\nWant details on any specific program?`,
        options: ['CSE Details', 'ECE Details', 'Request Call', '← Main Menu'],
    },
    Placement: {
        text: `Our placement highlights:\n\n📊 98% Placement Rate\n💰 ₹78L Highest Package\n🏢 500+ Recruiting Partners\n🌍 Top companies: Google, Microsoft, TCS, Infosys, Amazon\n\nWould you like our placement team to contact you?`,
        options: ['Yes, Request Call', 'No, Thanks', '← Main Menu'],
    },
    Scholarships: {
        text: `Scholarship options available:\n\n🏅 Merit Scholarship — Up to 100% tuition waiver\n🎯 Sports Scholarship — 50% fee concession\n📚 Need-Based Aid — Financial assistance\n🌟 First Rank Holders — Full scholarship\n\nWant to check your eligibility?`,
        options: ['Request Call', '← Main Menu'],
    },
    'Request Call': {
        text: `Great! I'll need a few details to connect you with our admissions counselor. 📞`,
        showLeadForm: true,
    },
    'Yes, Request Call': {
        text: `Perfect! Let me collect your details to arrange a callback. 📞`,
        showLeadForm: true,
    },
    'No, Thanks': {
        text: `No problem! Feel free to explore more. What else can I help you with? 😊`,
        options: MAIN_OPTIONS,
    },
    '← Main Menu': {
        text: `Sure! What would you like to know? 😊`,
        options: MAIN_OPTIONS,
    },
    'CSE Details': {
        text: `Computer Science Engineering (B.Tech)\n\n⏱ Duration: 4 Years\n💰 Fee: ₹1,50,000/year\n\nSpecializations:\n• Artificial Intelligence & Machine Learning\n• Full Stack Web Development\n• Cloud Computing & DevOps\n• Cybersecurity\n\nTop recruiters: Google, Microsoft, Amazon, Flipkart\n\nWant to apply or talk to an advisor?`,
        options: ['Request Call', '← Main Menu'],
    },
    'ECE Details': {
        text: `Electronics & Communication Engineering (B.Tech)\n\n⏱ Duration: 4 Years\n💰 Fee: ₹1,35,000/year\n\nSpecializations:\n• VLSI Design\n• Embedded Systems\n• IoT & Sensor Networks\n• 5G Technologies\n\nTop recruiters: Qualcomm, Intel, Texas Instruments\n\nWant to apply or talk to an advisor?`,
        options: ['Request Call', '← Main Menu'],
    },
}

export default function ChatWindow({ onClose }) {
    const [messages, setMessages] = useState([])
    const [currentOptions, setCurrentOptions] = useState(MAIN_OPTIONS)
    const [showLeadForm, setShowLeadForm] = useState(false)
    const [isTyping, setIsTyping] = useState(false)
    const messagesEndRef = useRef(null)

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [])

    useEffect(() => {
        // Welcome message with typing effect
        setIsTyping(true)
        const timer = setTimeout(() => {
            setMessages([{ text: WELCOME_MESSAGE, isBot: true }])
            setIsTyping(false)
        }, 800)
        return () => clearTimeout(timer)
    }, [])

    useEffect(() => {
        scrollToBottom()
    }, [messages, showLeadForm, isTyping, scrollToBottom])

    const handleOptionSelect = (option) => {
        // Add user message
        setMessages((prev) => [...prev, { text: option, isBot: false }])
        setCurrentOptions([])
        setShowLeadForm(false)

        // Simulate typing
        setIsTyping(true)
        setTimeout(() => {
            const response = BOT_RESPONSES[option]
            if (response) {
                setMessages((prev) => [...prev, { text: response.text, isBot: true }])
                if (response.showLeadForm) {
                    setShowLeadForm(true)
                    setCurrentOptions([])
                } else {
                    setCurrentOptions(response.options || MAIN_OPTIONS)
                }
            } else {
                setMessages((prev) => [
                    ...prev,
                    { text: `I'm not sure about that. Let me connect you with our team!`, isBot: true },
                ])
                setCurrentOptions(MAIN_OPTIONS)
            }
            setIsTyping(false)
        }, 600 + Math.random() * 400)
    }

    const handleFreeText = (text) => {
        setMessages((prev) => [...prev, { text, isBot: false }])
        setCurrentOptions([])
        setIsTyping(true)

        setTimeout(() => {
            const lowerText = text.toLowerCase()
            let matched = false

            const keywords = {
                admission: 'Admissions',
                fee: 'Fees',
                course: 'Courses',
                program: 'Courses',
                placement: 'Placement',
                job: 'Placement',
                scholarship: 'Scholarships',
                call: 'Request Call',
                contact: 'Request Call',
            }

            for (const [keyword, responseKey] of Object.entries(keywords)) {
                if (lowerText.includes(keyword)) {
                    const response = BOT_RESPONSES[responseKey]
                    setMessages((prev) => [...prev, { text: response.text, isBot: true }])
                    if (response.showLeadForm) {
                        setShowLeadForm(true)
                    } else {
                        setCurrentOptions(response.options || MAIN_OPTIONS)
                    }
                    matched = true
                    break
                }
            }

            if (!matched) {
                setMessages((prev) => [
                    ...prev,
                    {
                        text: `Thanks for your question! I can help you with Admissions, Fees, Courses, Placement, and Scholarships. Please select an option below, or request a call to speak with our team directly.`,
                        isBot: true,
                    },
                ])
                setCurrentOptions(MAIN_OPTIONS)
            }
            setIsTyping(false)
        }, 800)
    }

    const handleLeadSubmit = async (formData) => {
        const response = await submitLead(formData)
        if (response.success) {
            await triggerAutoCall(formData.phone)
        }
        setShowLeadForm(false)
        setMessages((prev) => [
            ...prev,
            {
                text: `Thank you, ${formData.name}! 🎉\n\nOur admission counselor will contact you shortly at ${formData.phone}.\n\nIs there anything else I can help you with?`,
                isBot: true,
            },
        ])
        setCurrentOptions(MAIN_OPTIONS)
    }

    const handleLeadCancel = () => {
        setShowLeadForm(false)
        setMessages((prev) => [
            ...prev,
            { text: `No problem! What else can I help with? 😊`, isBot: true },
        ])
        setCurrentOptions(MAIN_OPTIONS)
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className="fixed bottom-24 right-4 sm:right-6 w-[360px] max-w-[calc(100vw-2rem)] z-50 rounded-2xl overflow-hidden shadow-2xl shadow-black/40"
            style={{
                background: 'linear-gradient(180deg, rgba(12,20,69,0.98) 0%, rgba(5,10,31,0.99) 100%)',
                border: '1px solid rgba(255,255,255,0.08)',
            }}
        >
            {/* Header */}
            <div className="relative px-5 py-4 border-b border-white/5">
                <div className="absolute inset-0 bg-gradient-to-r from-primary-600/20 to-accent-500/10" />
                <div className="relative flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                                <Bot className="w-5 h-5 text-white" />
                            </div>
                            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-green-400 border-2 border-navy-900" />
                        </div>
                        <div>
                            <div className="flex items-center gap-1.5">
                                <span className="text-sm font-heading font-semibold text-white">EduBot</span>
                                <Sparkles className="w-3 h-3 text-gold-400" />
                            </div>
                            <span className="text-[10px] text-white/40">Admissions AI • Online</span>
                        </div>
                    </div>
                    <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={onClose}
                        className="w-8 h-8 rounded-lg hover:bg-white/5 flex items-center justify-center text-white/40 hover:text-white transition-colors cursor-pointer"
                    >
                        <X className="w-4 h-4" />
                    </motion.button>
                </div>
            </div>

            {/* Messages */}
            <div className="h-[380px] overflow-y-auto p-4 space-y-1 scrollbar-thin">
                {messages.map((msg, i) => (
                    <ChatMessage key={i} message={msg.text} isBot={msg.isBot} />
                ))}

                {/* Typing indicator */}
                {isTyping && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-1 px-4 py-3 w-fit rounded-2xl rounded-bl-md bg-white/[0.06] border border-white/[0.06]"
                    >
                        <div className="w-2 h-2 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </motion.div>
                )}

                {/* Options */}
                {!isTyping && currentOptions.length > 0 && (
                    <ChatOptions options={currentOptions} onSelect={handleOptionSelect} />
                )}

                {/* Lead Form */}
                {!isTyping && showLeadForm && (
                    <LeadForm onSubmit={handleLeadSubmit} onCancel={handleLeadCancel} />
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            {!showLeadForm && <ChatInput onSend={handleFreeText} placeholder="Ask about admissions..." />}
        </motion.div>
    )
}
