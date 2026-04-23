import { motion } from 'framer-motion'
import { Cpu, Zap, Settings, Building, ArrowUpRight, CheckCircle2 } from 'lucide-react'

const courses = [
    {
        id: 'cse',
        title: 'Computer Science & Engineering',
        icon: Cpu,
        duration: '4 Years',
        fee: '₹1.8L',
        total: '₹7.2L',
        tags: ['AI/ML', 'Cloud', 'Cyber Security'],
        description: 'Focus on Data Structures, AI, IoT, Robotics, and Blockchain Technology.',
        color: 'from-blue-600 to-cyan-500'
    },
    {
        id: 'ece',
        title: 'Electronics & Communication',
        icon: Zap,
        duration: '4 Years',
        fee: '₹1.6L',
        total: '₹6.4L',
        tags: ['VLSI', 'Embedded', 'Signal'],
        description: 'Digital Electronics, Signal Processing, and Data Science specializations.',
        color: 'from-accent-500 to-blue-500'
    },
    {
        id: 'mech',
        title: 'Mechanical Engineering',
        icon: Settings,
        duration: '4 Years',
        fee: '₹1.4L',
        total: '₹5.6L',
        tags: ['Robotics', 'CAD/CAM', 'Thermal'],
        description: 'Machine Design, Manufacturing Tech, and Automation systems.',
        color: 'from-primary-600 to-indigo-500'
    },
    {
        id: 'civil',
        title: 'Civil Engineering',
        icon: Building,
        duration: '4 Years',
        fee: '₹1.3L',
        total: '₹5.2L',
        tags: ['Smart Cities', 'Structures', 'Geo'],
        description: 'Structural Engineering, Construction Tech, and Smart Infrastructure.',
        color: 'from-indigo-600 to-primary-600'
    }
]

export default function CourseCards() {
    return (
        <section id="courses" className="relative py-28 sm:py-36 overflow-hidden">
            {/* Background decorative elements */}
            <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-primary-600/5 blur-[150px] rounded-full pointer-events-none" />

            <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="text-center mb-16">
                    <motion.span
                        initial={{ opacity: 0, y: 10 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-block px-4 py-1.5 rounded-full glass text-xs font-bold text-accent-400 uppercase tracking-widest mb-6"
                    >
                        Academic Excellence
                    </motion.span>
                    <motion.h2
                        initial={{ opacity: 0, y: 10 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-3xl sm:text-4xl md:text-5xl font-heading font-bold mb-6"
                    >
                        Premier Engineering{' '}
                        <span className="gradient-text">Programs</span>
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 10 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                        className="text-white/40 max-w-2xl mx-auto text-base sm:text-lg"
                    >
                        Empowering students with industry-aligned curriculum and hands-on laboratory experience
                    </motion.p>
                </div>

                {/* Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {courses.map((course, i) => (
                        <motion.div
                            key={course.id}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: '-50px' }}
                            transition={{ delay: i * 0.15, duration: 0.6 }}
                            whileHover={{ y: -8 }}
                            className="group relative glass rounded-[2.5rem] p-8 sm:p-10 transition-all duration-500 hover:shadow-2xl hover:shadow-primary-600/10"
                        >
                            <div className="flex flex-wrap items-start justify-between gap-6 mb-8">
                                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${course.color} flex items-center justify-center p-4 shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all duration-500`}>
                                    <course.icon className="w-full h-full text-white" />
                                </div>
                                <div className="text-right">
                                    <div className="text-2xl font-heading font-bold text-white">{course.fee}</div>
                                    <div className="text-xs text-white/30 font-medium uppercase tracking-widest">per annum</div>
                                </div>
                            </div>

                            <h3 className="text-2xl font-heading font-bold text-white mb-3 group-hover:text-accent-400 transition-colors">
                                {course.title}
                            </h3>
                            <p className="text-white/40 mb-6 leading-relaxed group-hover:text-white/60 transition-colors">
                                {course.description}
                            </p>

                            <div className="flex flex-wrap gap-2 mb-8">
                                {course.tags.map(tag => (
                                    <span key={tag} className="px-3 py-1 rounded-lg bg-white/5 text-[10px] font-bold text-primary-300 border border-white/5 uppercase tracking-wider">
                                        {tag}
                                    </span>
                                ))}
                            </div>

                            <div className="flex items-center justify-between pt-8 border-t border-white/5">
                                <div className="flex items-center gap-2">
                                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                                    <span className="text-sm font-semibold text-white/70">{course.duration} Program</span>
                                </div>
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    className="flex items-center gap-2 text-sm font-bold text-accent-400 group/btn"
                                >
                                    Details
                                    <ArrowUpRight className="w-4 h-4 group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform" />
                                </motion.button>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    )
}
