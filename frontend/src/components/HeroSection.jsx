import { motion, AnimatePresence, useSpring, useTransform } from 'framer-motion'
import { useState, useEffect } from 'react'
import { ArrowRight, BookOpen, GraduationCap, Users, Trophy } from 'lucide-react'

import heroVideo from '../assets/14004543-uhd_3840_2160_60fps.mp4'

const slides = [
    {
        id: 1,
        title: 'Engineering the Future',
        subtitle: 'Empowering the next generation of innovators, creators, and technology leaders at Nexus.',
        badge: 'Category-1 University',
        gradient: 'from-navy-950/80 via-navy-950/40 to-transparent'
    },
    {
        id: 2,
        title: 'Admissions Open 2026-27',
        subtitle: 'Industry-driven education, advanced laboratories, and world-class engineering programs.',
        badge: 'NAAC A++ Accredited',
        gradient: 'from-navy-900/80 via-navy-900/40 to-transparent'
    },
    {
        id: 3,
        title: 'Learn from Experts. Build Skills.',
        subtitle: 'Transform your ideas into real-world solutions with cutting-edge engineering excellence.',
        badge: 'NIRF 53rd Ranked',
        gradient: 'from-slate-950/80 via-slate-950/40 to-transparent'
    }
]

const stats = [
    { label: 'Placements', value: 98, suffix: '%', icon: Trophy, color: 'text-accent-400' },
    { label: 'Alumni', value: 12000, suffix: '+', icon: Users, color: 'text-primary-400' },
    { label: 'Programs', value: 50, suffix: '+', icon: GraduationCap, color: 'text-emerald-400' },
    { label: 'Ranking', value: 99.9, suffix: '+', icon: Trophy, color: 'text-gold-400' }
]

function Counter({ value, suffix }) {
    const spring = useSpring(0, { stiffness: 40, damping: 20 })
    const display = useTransform(spring, (current) =>
        Math.floor(current).toLocaleString() + suffix
    )

    useEffect(() => {
        spring.set(value)
    }, [value, spring])

    return <motion.span>{display}</motion.span>
}

export default function HeroSection() {
    const [currentSlide, setCurrentSlide] = useState(0)

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentSlide((prev) => (prev + 1) % slides.length)
        }, 6000)
        return () => clearInterval(timer)
    }, [])

    return (
        <section id="home" className="relative min-h-[90vh] lg:min-h-screen flex items-center pt-20 overflow-hidden bg-navy-950">
            {/* Background Video and Overlays */}
            <div className="absolute inset-0 z-0">
                <video
                    autoPlay
                    muted
                    loop
                    playsInline
                    className="absolute inset-0 w-full h-full object-cover"
                >
                    <source src={heroVideo} type="video/mp4" />
                </video>
                
                {/* Fixed Dark Overlay */}
                <div className="absolute inset-0 bg-navy-950/60 z-[1]" />

                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentSlide}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 1.5, ease: 'easeInOut' }}
                        className="absolute inset-0 z-[2]"
                    >
                        <div className={`absolute inset-0 bg-gradient-to-r ${slides[currentSlide].gradient}`} />
                        
                        {/* Mosaic pattern overlay for texture */}
                        <div className="absolute inset-0 opacity-10 bg-checkered" />
                    </motion.div>
                </AnimatePresence>
            </div>

            <div className="relative z-[2] max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 w-full">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                    <div>
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={currentSlide}
                                initial={{ opacity: 0, x: -30 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 30 }}
                                transition={{ duration: 0.6, ease: 'easeOut' }}
                            >
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8"
                                >
                                    <span className="w-2 h-2 rounded-full bg-accent-400 animate-pulse" />
                                    <span className="text-xs font-semibold text-accent-400 tracking-wide uppercase">
                                        {slides[currentSlide].badge}
                                    </span>
                                </motion.div>

                                <h1 className="text-5xl sm:text-6xl md:text-7xl font-heading font-extrabold leading-[1.1] tracking-tight mb-6">
                                    {slides[currentSlide].title.split(' ').map((word, i) => (
                                        word === 'Future' || word === 'Experts' || word === 'Engineering' ?
                                            <span key={i} className="gradient-text">{word} </span> :
                                            word + ' '
                                    ))}
                                </h1>

                                <p className="text-lg sm:text-xl text-white/60 max-w-xl mb-10 leading-relaxed">
                                    {slides[currentSlide].subtitle}
                                </p>

                                <div className="flex flex-col sm:flex-row items-center gap-4">
                                    <a
                                        href="#admissions"
                                        className="w-full sm:w-auto group inline-flex items-center justify-center gap-2.5 px-8 py-4 text-base font-bold text-white rounded-2xl bg-gradient-to-r from-primary-600 to-primary-700 hover:scale-105 transition-all duration-300 shadow-xl shadow-primary-600/20"
                                    >
                                        Apply Now
                                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                    </a>
                                    <a
                                        href="#courses"
                                        className="w-full sm:w-auto group inline-flex items-center justify-center gap-2.5 px-8 py-4 text-base font-bold text-white/80 hover:text-white rounded-2xl glass hover:bg-white/5 transition-all duration-300"
                                    >
                                        <BookOpen className="w-4 h-4" />
                                        Programs
                                    </a>
                                </div>
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    {/* Stats Panel */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {stats.map((stat, i) => (
                            <motion.div
                                key={stat.label}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: 0.4 + (i * 0.1) }}
                                whileHover={{ y: -5, scale: 1.02 }}
                                className="glass rounded-3xl p-8 group border-white/5 hover:border-accent-400/20 transition-all duration-500"
                            >
                                <div className={`w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform ${stat.color}`}>
                                    <stat.icon className="w-6 h-6" />
                                </div>
                                <div className="text-4xl font-heading font-extrabold text-white mb-1">
                                    <Counter value={stat.value} suffix={stat.suffix} />
                                </div>
                                <div className="text-xs text-white/40 uppercase tracking-[0.2em] font-bold">
                                    {stat.label}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Scroll Indicator
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 2 }}
                className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3"
            >
                <div className="w-6 h-10 rounded-full border-2 border-white/10 flex justify-center p-1.5 overflow-hidden">
                    <motion.div
                        animate={{ y: [0, 15, 0] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                        className="w-1.5 h-1.5 rounded-full bg-primary-600"
                    />
                </div>
            </motion.div> */}
        </section>
    )
}
