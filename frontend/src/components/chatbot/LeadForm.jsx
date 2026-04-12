import { useState } from 'react'
import { motion } from 'framer-motion'
import { User, Phone, Mail, Loader2, CheckCircle2 } from 'lucide-react'

export default function LeadForm({ onSubmit, onCancel }) {
    const [step, setStep] = useState(0)
    const [formData, setFormData] = useState({ name: '', phone: '', email: '' })
    const [submitting, setSubmitting] = useState(false)
    const [done, setDone] = useState(false)

    const fields = [
        { key: 'name', icon: User, label: 'Please enter your full name', placeholder: 'Your full name', type: 'text' },
        { key: 'phone', icon: Phone, label: 'Please enter your phone number', placeholder: '+91 9876543210', type: 'tel' },
        { key: 'email', icon: Mail, label: 'Please enter your email', placeholder: 'you@example.com', type: 'email' },
    ]

    const currentField = fields[step]

    const handleNext = async (e) => {
        e.preventDefault()
        const value = formData[currentField.key]
        if (!value.trim()) return

        if (step < fields.length - 1) {
            setStep(step + 1)
        } else {
            setSubmitting(true)
            try {
                await onSubmit(formData)
                setDone(true)
            } catch {
                // handle error
            } finally {
                setSubmitting(false)
            }
        }
    }

    if (done) {
        return (
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-4 text-center"
            >
                <CheckCircle2 className="w-10 h-10 text-green-400 mx-auto mb-3" />
                <p className="text-sm text-white/80 font-medium">
                    Thank you! 🎉
                </p>
                <p className="text-xs text-white/40 mt-1">
                    Our admission counselor will contact you shortly.
                </p>
            </motion.div>
        )
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4"
        >
            {/* Progress */}
            <div className="flex items-center gap-1 mb-4">
                {fields.map((_, i) => (
                    <div
                        key={i}
                        className={`flex-1 h-1 rounded-full transition-colors duration-300 ${i <= step ? 'bg-gradient-to-r from-primary-500 to-accent-500' : 'bg-white/10'
                            }`}
                    />
                ))}
            </div>

            <p className="text-xs text-white/60 mb-3">{currentField.label}</p>

            <form onSubmit={handleNext} className="flex gap-2">
                <div className="flex-1 relative">
                    <currentField.icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                    <input
                        type={currentField.type}
                        value={formData[currentField.key]}
                        onChange={(e) => setFormData({ ...formData, [currentField.key]: e.target.value })}
                        placeholder={currentField.placeholder}
                        className="w-full pl-10 pr-3 py-2.5 text-sm text-white bg-white/[0.04] border border-white/[0.06] rounded-xl placeholder-white/30 focus:outline-none focus:border-primary-500/40 transition-all"
                        autoFocus
                        required
                    />
                </div>
                <motion.button
                    type="submit"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    disabled={submitting}
                    className="px-5 py-2.5 text-xs font-semibold text-white rounded-xl bg-gradient-to-r from-primary-600 to-primary-500 disabled:opacity-50 cursor-pointer shrink-0"
                >
                    {submitting ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : step < fields.length - 1 ? (
                        'Next'
                    ) : (
                        'Submit'
                    )}
                </motion.button>
            </form>

            <button
                onClick={onCancel}
                className="mt-3 text-[10px] text-white/30 hover:text-white/50 transition-colors cursor-pointer"
            >
                Cancel
            </button>
        </motion.div>
    )
}
