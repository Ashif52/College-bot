import { motion } from 'framer-motion'

export default function ChatOptions({ options, onSelect }) {
    if (!options || options.length === 0) return null

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="flex flex-wrap gap-2 mb-3 pl-1"
        >
            {options.map((option) => (
                <motion.button
                    key={option}
                    whileHover={{ scale: 1.04 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => onSelect(option)}
                    className="px-4 py-2 text-xs font-semibold text-primary-300 bg-primary-500/10 hover:bg-primary-500/20 border border-primary-500/20 hover:border-primary-400/40 rounded-xl transition-all duration-200 cursor-pointer"
                >
                    {option}
                </motion.button>
            ))}
        </motion.div>
    )
}
