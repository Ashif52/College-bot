import { motion, useInView, useMotionValue, useTransform, animate } from 'framer-motion'
import { useRef, useEffect, useState } from 'react'
import { GraduationCap, Building2, Trophy, Users, Globe, Handshake, TrendingUp } from 'lucide-react'

const stats = [
    { icon: GraduationCap, value: 12000, suffix: '+', label: 'Students Enrolled', color: 'from-primary-500 to-primary-400', shadowColor: 'rgba(99, 102, 241, 0.3)' },
    { icon: Building2, value: 500, suffix: '+', label: 'Recruiting Partners', color: 'from-accent-500 to-cyan-400', shadowColor: 'rgba(14, 165, 233, 0.3)' },
    { icon: Trophy, value: 98, suffix: '%', label: 'Placement Rate', color: 'from-gold-400 to-gold-500', shadowColor: 'rgba(251, 191, 36, 0.3)' },
    { icon: Users, value: 200, suffix: '+', label: 'Expert Faculty', color: 'from-purple-500 to-purple-400', shadowColor: 'rgba(168, 85, 247, 0.3)' },
    { icon: Globe, value: 15, suffix: '+', label: 'International Tie-ups', color: 'from-emerald-500 to-teal-400', shadowColor: 'rgba(16, 185, 129, 0.3)' },
    { icon: Handshake, value: 78, suffix: 'L', prefix: '₹', label: 'Highest Package', color: 'from-orange-500 to-amber-400', shadowColor: 'rgba(249, 115, 22, 0.3)' },
]

function AnimatedNumber({ value, prefix = '', suffix = '', isInView }) {
    const [displayValue, setDisplayValue] = useState(0)

    useEffect(() => {
        if (!isInView) return

        const duration = 2200
        const start = 0
        const startTime = Date.now()

        const easeOutQuart = (t) => 1 - Math.pow(1 - t, 4)

        const timer = setInterval(() => {
            const elapsed = Date.now() - startTime
            const progress = Math.min(elapsed / duration, 1)
            const easedProgress = easeOutQuart(progress)
            const current = Math.floor(start + (value - start) * easedProgress)
            setDisplayValue(current)

            if (progress >= 1) clearInterval(timer)
        }, 16)

        return () => clearInterval(timer)
    }, [isInView, value])

    const formatNumber = (num) => {
        if (num >= 1000) {
            return (num / 1000).toFixed(num % 1000 === 0 ? 0 : 1) + 'K'
        }
        return num.toString()
    }

    return (
        <span>
            {prefix}{formatNumber(displayValue)}{suffix}
        </span>
    )
}

export default function StatsCounter() {
    const ref = useRef(null)
    const isInView = useInView(ref, { once: true, margin: '-50px' })

    return (
        <section className="relative py-24 sm:py-28 overflow-hidden">
            {/* Rich background */}
            <div className="absolute inset-0">
                <div className="absolute inset-0 bg-gradient-to-b from-navy-950 via-navy-900/50 to-navy-950" />
                <div className="absolute inset-0 bg-gradient-to-r from-primary-600/[0.06] via-transparent to-accent-500/[0.06]" />
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary-500/30 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-accent-500/25 to-transparent" />
                {/* Floating glow orbs */}
                <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-[300px] h-[300px] rounded-full bg-primary-600/[0.06] blur-[120px] animate-float" />
                <div className="absolute top-1/2 right-1/4 -translate-y-1/2 w-[250px] h-[250px] rounded-full bg-accent-500/[0.05] blur-[100px] animate-float-reverse" />
            </div>

            <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" ref={ref}>
                {/* Section Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-xs font-semibold text-primary-300 uppercase tracking-widest mb-4">
                        <TrendingUp className="w-3.5 h-3.5" />
                        Our Impact
                    </span>
                    <h2 className="text-3xl sm:text-4xl md:text-5xl font-heading font-bold">
                        Numbers That Speak{' '}
                        <span className="gradient-text">Excellence</span>
                    </h2>
                </motion.div>

                {/* Stats Grid */}
                <motion.div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-5">
                    {stats.map((stat, i) => (
                        <motion.div
                            key={stat.label}
                            initial={{ opacity: 0, y: 40, scale: 0.9 }}
                            animate={isInView ? { opacity: 1, y: 0, scale: 1 } : {}}
                            transition={{ delay: i * 0.1, duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
                            whileHover={{ y: -8, scale: 1.05 }}
                            className="relative text-center group cursor-default"
                        >
                            {/* Glass card */}
                            <div className="glass rounded-2xl p-6 h-full relative overflow-hidden transition-shadow duration-500"
                                style={{ boxShadow: `0 0 0 rgba(0,0,0,0)` }}
                            >
                                {/* Hover glow */}
                                <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                                    style={{
                                        background: `radial-gradient(circle at 50% 0%, ${stat.shadowColor}, transparent 70%)`,
                                    }}
                                />

                                {/* Icon */}
                                <div className={`relative w-14 h-14 rounded-2xl bg-gradient-to-br ${stat.color} flex items-center justify-center mx-auto mb-4 group-hover:scale-110 group-hover:rotate-6 transition-all duration-400`}
                                    style={{ boxShadow: `0 8px 25px -5px ${stat.shadowColor}` }}
                                >
                                    <stat.icon className="w-7 h-7 text-white" />
                                </div>

                                {/* Number */}
                                <div className="relative text-2xl sm:text-3xl font-heading font-extrabold text-white mb-2">
                                    <AnimatedNumber
                                        value={stat.value}
                                        prefix={stat.prefix}
                                        suffix={stat.suffix}
                                        isInView={isInView}
                                    />
                                </div>

                                {/* Label */}
                                <div className="relative text-[11px] text-white/40 uppercase tracking-wider font-semibold group-hover:text-white/60 transition-colors duration-300">
                                    {stat.label}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </motion.div>
            </div>
        </section>
    )
}
