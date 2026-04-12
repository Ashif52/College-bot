import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send } from 'lucide-react'

export default function ChatInput({ onSend, placeholder = 'Type a message...' }) {
    const [text, setText] = useState('')

    const handleSubmit = (e) => {
        e.preventDefault()
        if (text.trim()) {
            onSend(text.trim())
            setText('')
        }
    }

    return (
        <form onSubmit={handleSubmit} className="flex items-center gap-2 p-3 border-t border-white/5">
            <input
                type="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder={placeholder}
                className="flex-1 px-4 py-2.5 text-sm text-white bg-white/[0.04] rounded-xl border border-white/[0.06] placeholder-white/30 focus:outline-none focus:border-primary-500/40 focus:bg-white/[0.06] transition-all duration-200"
            />
            <motion.button
                type="submit"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                disabled={!text.trim()}
                className="w-10 h-10 rounded-xl bg-gradient-to-r from-primary-600 to-primary-500 flex items-center justify-center text-white disabled:opacity-30 disabled:cursor-not-allowed transition-opacity duration-200 cursor-pointer shrink-0"
            >
                <Send className="w-4 h-4" />
            </motion.button>
        </form>
    )
}
