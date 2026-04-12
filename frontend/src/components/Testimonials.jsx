import { motion, useInView } from 'framer-motion'
import { useRef, useState, useEffect } from 'react'
import { Quote, Star, ChevronLeft, ChevronRight } from 'lucide-react'

const testimonials = [
    {
        name: 'Priya Sharma',
        role: 'CSE Graduate, Batch 2025',
        company: 'Software Engineer at Google',
        text: 'Nexus Institute transformed my career. The industry-aligned curriculum and amazing placement cell helped me land my dream job at Google. The professors here don\'t just teach — they mentor you for life.',
        rating: 5,
        avatar: 'PS',
        color: 'from-primary-500 to-accent-500',
    },
    {
        name: 'Rahul Krishnan',
        role: 'ECE Graduate, Batch 2024',
        company: 'Hardware Engineer at Intel',
        text: 'The VLSI and embedded systems labs are world-class. I got hands-on experience with real industry tools, which gave me a massive advantage during interviews. Proud to be a Nexus alumnus!',
        rating: 5,
        avatar: 'RK',
        color: 'from-accent-500 to-cyan-400',
    },
    {
        name: 'Ananya Reddy',
        role: 'CSE Graduate, Batch 2025',
        company: 'ML Engineer at Microsoft',
        text: 'The AI/ML specialization at Nexus is outstanding. The research opportunities and hackathons pushed me to build real projects that I showcased in my portfolio. Got placed at Microsoft with ₹42 LPA!',
        rating: 5,
        avatar: 'AR',
        color: 'from-purple-500 to-pink-400',
    },
    {
        name: 'Vikram Patel',
        role: 'ME Graduate, Batch 2024',
        company: 'Robotics Engineer at Tesla',
        text: 'The robotics and automation program is incredible. From CAD/CAM to 3D printing, every course prepared me for the cutting edge of mechanical engineering. The campus and facilities are truly world-class.',
        rating: 5,
        avatar: 'VP',
        color: 'from-orange-500 to-amber-400',
    },
    {
        name: 'Sneha Gupta',
        role: 'CE Graduate, Batch 2025',
        company: 'Structural Engineer at L&T',
        text: 'Nexus gave me a strong foundation in structural design and sustainable construction. The smart infrastructure lab is a gem. The institute\'s industry connections helped me start my career at L&T.',
        rating: 5,
        avatar: 'SG',
        color: 'from-emerald-500 to-teal-400',
    },
]

export default function Testimonials() {
    const ref = useRef(null)
    const isInView = useInView(ref, { once: true, margin: '-80px' })
    const [activeIndex, setActiveIndex] = useState(0)
    const [isAutoPlaying, setIsAutoPlaying] = useState(true)

    useEffect(() => {
        if (!isAutoPlaying) return
        const interval = setInterval(() => {
            setActiveIndex((prev) => (prev + 1) % testimonials.length)
        }, 5000)
        return () => clearInterval(interval)
    }, [isAutoPlaying])

    const goTo = (index) => {
        setActiveIndex(index)
        setIsAutoPlaying(false)
        setTimeout(() => setIsAutoPlaying(true), 10000)
    }

    const goPrev = () => goTo((activeIndex - 1 + testimonials.length) % testimonials.length)
    const goNext = () => goTo((activeIndex + 1) % testimonials.length)

    const current = testimonials[activeIndex]

    return (
        <section className="relative py-24 sm:py-32 overflow-hidden">
            {/* Background */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 right-1/4 w-[600px] h-[600px] rounded-full bg-primary-600/5 blur-[150px]" />
                <div className="absolute bottom-1/3 left-0 w-[400px] h-[400px] rounded-full bg-accent-500/5 blur-[120px]" />
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
                        Student Voices
                    </span>
                    <h2 className="text-3xl sm:text-4xl md:text-5xl font-heading font-bold mb-4">
                        What Our Alumni{' '}
                        <span className="gradient-text">Say</span>
                    </h2>
                    <p className="text-white/40 max-w-xl mx-auto text-base sm:text-lg">
                        Real stories from graduates who shaped their careers at Nexus Institute
                    </p>
                </motion.div>

                {/* Testimonial Card */}
                <div ref={ref} className="max-w-3xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={isInView ? { opacity: 1, y: 0 } : {}}
                        transition={{ duration: 0.6 }}
                        className="relative"
                    >
                        {/* Main testimonial */}
                        <div className="glass rounded-3xl p-8 sm:p-10 relative overflow-hidden">
                            {/* Decorative quote */}
                            <div className="absolute top-6 right-6 opacity-5">
                                <Quote className="w-24 h-24 text-white" />
                            </div>

                            <motion.div
                                key={activeIndex}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                transition={{ duration: 0.4 }}
                            >
                                {/* Stars */}
                                <div className="flex items-center gap-1 mb-6">
                                    {Array.from({ length: current.rating }).map((_, i) => (
                                        <Star key={i} className="w-4 h-4 text-gold-400 fill-gold-400" />
                                    ))}
                                </div>

                                {/* Quote text */}
                                <p className="text-base sm:text-lg text-white/70 leading-relaxed mb-8 relative z-10">
                                    "{current.text}"
                                </p>

                                {/* Author */}
                                <div className="flex items-center gap-4">
                                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${current.color} flex items-center justify-center text-sm font-bold text-white shrink-0`}>
                                        {current.avatar}
                                    </div>
                                    <div>
                                        <h4 className="text-sm font-heading font-semibold text-white">
                                            {current.name}
                                        </h4>
                                        <p className="text-xs text-white/40">{current.role}</p>
                                        <p className="text-xs text-primary-400 font-medium mt-0.5">{current.company}</p>
                                    </div>
                                </div>
                            </motion.div>
                        </div>

                        {/* Navigation */}
                        <div className="flex items-center justify-between mt-6">
                            <div className="flex items-center gap-2">
                                {testimonials.map((_, i) => (
                                    <button
                                        key={i}
                                        onClick={() => goTo(i)}
                                        className={`h-1.5 rounded-full transition-all duration-300 cursor-pointer ${i === activeIndex
                                            ? 'w-8 bg-gradient-to-r from-primary-500 to-accent-500'
                                            : 'w-1.5 bg-white/20 hover:bg-white/30'
                                            }`}
                                    />
                                ))}
                            </div>
                            <div className="flex items-center gap-2">
                                <motion.button
                                    whileHover={{ scale: 1.1 }}
                                    whileTap={{ scale: 0.9 }}
                                    onClick={goPrev}
                                    className="w-10 h-10 rounded-xl glass flex items-center justify-center text-white/40 hover:text-white transition-colors cursor-pointer"
                                >
                                    <ChevronLeft className="w-5 h-5" />
                                </motion.button>
                                <motion.button
                                    whileHover={{ scale: 1.1 }}
                                    whileTap={{ scale: 0.9 }}
                                    onClick={goNext}
                                    className="w-10 h-10 rounded-xl glass flex items-center justify-center text-white/40 hover:text-white transition-colors cursor-pointer"
                                >
                                    <ChevronRight className="w-5 h-5" />
                                </motion.button>
                            </div>
                        </div>
                    </motion.div>

                    {/* Mini avatars preview */}
                    <div className="flex items-center justify-center gap-3 mt-10">
                        {testimonials.map((t, i) => (
                            <motion.button
                                key={t.name}
                                onClick={() => goTo(i)}
                                whileHover={{ scale: 1.15 }}
                                className={`w-10 h-10 rounded-xl bg-gradient-to-br ${t.color} flex items-center justify-center text-[10px] font-bold text-white transition-all duration-300 cursor-pointer ${i === activeIndex
                                    ? 'ring-2 ring-primary-400/50 ring-offset-2 ring-offset-navy-950 scale-110'
                                    : 'opacity-40 hover:opacity-70'
                                    }`}
                            >
                                {t.avatar}
                            </motion.button>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    )
}
