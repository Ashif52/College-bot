import { motion, useInView } from 'framer-motion'
import { useRef, useState } from 'react'
import { User, Phone, Mail, Send, Loader2, CheckCircle2, GraduationCap, FileText, Calendar, Shield } from 'lucide-react'
import { submitLead, triggerAutoCall } from '../api/lead'

const steps = [
    { icon: FileText, title: 'Fill Application', desc: 'Complete the online form' },
    { icon: Calendar, title: 'Entrance Exam', desc: 'Take the aptitude test' },
    { icon: GraduationCap, title: 'Counseling', desc: 'Attend admission counseling' },
    { icon: Shield, title: 'Enrollment', desc: 'Confirm your seat' },
]

export default function AdmissionsSection() {
    const ref = useRef(null)
    const isInView = useInView(ref, { once: true, margin: '-100px' })
    const [formData, setFormData] = useState({ name: '', phone: '', email: '' })
    const [submitting, setSubmitting] = useState(false)
    const [submitted, setSubmitted] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setSubmitting(true)
        try {
            await submitLead(formData)
            await triggerAutoCall(formData.phone)
            setSubmitted(true)
        } catch {
            // handle error
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <section id="admissions" className="relative py-24 sm:py-32 overflow-hidden">
            {/* Background */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-1/2 left-0 w-[600px] h-[600px] rounded-full bg-primary-600/5 blur-[150px]" />
                <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] rounded-full bg-accent-500/5 blur-[120px]" />
            </div>

            <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <span className="inline-block px-4 py-1.5 rounded-full glass text-xs font-medium text-gold-400 uppercase tracking-widest mb-4">
                        Admissions 2026-27
                    </span>
                    <h2 className="text-3xl sm:text-4xl md:text-5xl font-heading font-bold mb-4">
                        Begin Your{' '}
                        <span className="gradient-text">Journey</span>
                    </h2>
                    <p className="text-white/40 max-w-xl mx-auto text-base sm:text-lg">
                        Simple 4-step admission process designed to help you secure your future
                    </p>
                </motion.div>

                {/* Process Steps */}
                <motion.div
                    ref={ref}
                    className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16"
                >
                    {steps.map((step, i) => (
                        <motion.div
                            key={step.title}
                            initial={{ opacity: 0, y: 30 }}
                            animate={isInView ? { opacity: 1, y: 0 } : {}}
                            transition={{ delay: i * 0.15, duration: 0.5 }}
                            className="relative glass rounded-2xl p-5 text-center group"
                        >
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform duration-300">
                                <step.icon className="w-6 h-6 text-primary-400" />
                            </div>
                            <div className="absolute -top-3 -left-1 w-7 h-7 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-[11px] font-bold text-white shadow-lg">
                                {i + 1}
                            </div>
                            <h4 className="text-sm font-heading font-semibold text-white mb-1">{step.title}</h4>
                            <p className="text-xs text-white/40">{step.desc}</p>
                        </motion.div>
                    ))}
                </motion.div>

                {/* Application Form */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="max-w-xl mx-auto"
                >
                    <div className="glass rounded-2xl p-8">
                        {submitted ? (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="text-center py-8"
                            >
                                <CheckCircle2 className="w-14 h-14 text-green-400 mx-auto mb-4" />
                                <h3 className="text-xl font-heading font-bold text-white mb-2">Application Received! 🎉</h3>
                                <p className="text-sm text-white/40">Our admissions counselor will contact you shortly.</p>
                            </motion.div>
                        ) : (
                            <>
                                <h3 className="text-lg font-heading font-semibold text-white mb-6 text-center">
                                    Quick Application
                                </h3>
                                <form onSubmit={handleSubmit} className="space-y-4">
                                    <div className="relative">
                                        <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                                        <input
                                            type="text"
                                            value={formData.name}
                                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                            placeholder="Full Name"
                                            required
                                            className="w-full pl-12 pr-4 py-3.5 text-sm text-white bg-white/[0.04] border border-white/[0.06] rounded-xl placeholder-white/30 focus:outline-none focus:border-primary-500/40 focus:bg-white/[0.06] transition-all"
                                        />
                                    </div>
                                    <div className="relative">
                                        <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                                        <input
                                            type="tel"
                                            value={formData.phone}
                                            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                            placeholder="Phone Number"
                                            required
                                            className="w-full pl-12 pr-4 py-3.5 text-sm text-white bg-white/[0.04] border border-white/[0.06] rounded-xl placeholder-white/30 focus:outline-none focus:border-primary-500/40 focus:bg-white/[0.06] transition-all"
                                        />
                                    </div>
                                    <div className="relative">
                                        <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                                        <input
                                            type="email"
                                            value={formData.email}
                                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                            placeholder="Email Address"
                                            required
                                            className="w-full pl-12 pr-4 py-3.5 text-sm text-white bg-white/[0.04] border border-white/[0.06] rounded-xl placeholder-white/30 focus:outline-none focus:border-primary-500/40 focus:bg-white/[0.06] transition-all"
                                        />
                                    </div>
                                    <motion.button
                                        type="submit"
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        disabled={submitting}
                                        className="w-full py-3.5 text-sm font-semibold text-white rounded-xl bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-accent-500 transition-all duration-500 shadow-lg shadow-primary-600/30 flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
                                    >
                                        {submitting ? (
                                            <>
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                                Submitting...
                                            </>
                                        ) : (
                                            <>
                                                <Send className="w-4 h-4" />
                                                Submit Application
                                            </>
                                        )}
                                    </motion.button>
                                </form>
                            </>
                        )}
                    </div>
                </motion.div>
            </div>
        </section>
    )
}
