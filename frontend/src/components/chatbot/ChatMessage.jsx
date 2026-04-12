import { motion } from 'framer-motion'

export default function ChatMessage({ message, isBot }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className={`flex ${isBot ? 'justify-start' : 'justify-end'} mb-3`}
        >
            <div
                className={`max-w-[85%] px-4 py-3 text-sm leading-relaxed rounded-2xl ${isBot
                        ? 'bg-white/[0.06] text-white/90 rounded-bl-md border border-white/[0.06]'
                        : 'bg-gradient-to-r from-primary-600 to-primary-500 text-white rounded-br-md shadow-lg shadow-primary-600/20'
                    }`}
                style={{ whiteSpace: 'pre-line' }}
            >
                {message}
            </div>
        </motion.div>
    )
}
