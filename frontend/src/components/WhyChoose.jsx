import { motion } from 'framer-motion'
import { Microscope, Users, BookOpen, Briefcase, Award, TrendingUp } from 'lucide-react'

const features = [
    {
        icon: Microscope,
        title: 'Advanced Laboratories',
        description: 'Over 150+ high-tech laboratories and specialized research centers for hands-on innovation.',
        color: 'from-blue-600 to-primary-600'
    },
    {
        icon: Users,
        title: 'Experienced Faculty',
        description: 'Mentorship from industry veterans and PhD holders with high impact factor research.',
        color: 'from-accent-400 to-blue-500'
    },
    {
        icon: BookOpen,
        title: 'Industry Curriculum',
        description: 'Academic syllabus co-designed with global tech giants ensuring immediate employability.',
        color: 'from-indigo-600 to-primary-600'
    },
    {
        icon: Briefcase,
        title: 'Placement Excellence',
        description: 'Annual placement drives with 500+ recruiting partners and significant LPA packages.',
        color: 'from-primary-700 to-primary-900'
    }
]

export default function WhyChoose() {
    return (
        <section id="placement" className="relative py-28 sm:py-36 overflow-hidden bg-navy-950/50">
            {/* Background pattern */}
            <div className="absolute inset-0 opacity-30 bg-checkered" />

            <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
                    <div>
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass mb-8 text-accent-400 text-[10px] font-bold uppercase tracking-widest border-accent-400/20"
                        >
                            <Award className="w-3 h-3" />
                            Academic Excellence Since 1987
                        </motion.div>
                        <motion.h2
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.1 }}
                            className="text-4xl sm:text-5xl font-heading font-extrabold text-white mb-8 leading-tight"
                        >
                            Shaping Global Professionals via <span className="gradient-text">Practical Learning</span>
                        </motion.h2>
                        <motion.p
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.2 }}
                            className="text-white/40 text-lg mb-12 leading-relaxed"
                        >
                            Ranked 53rd among Universities in India by NIRF 2024, Nexus provides a vibrant environment for intellectual growth and career transformation.
                        </motion.p>

                        <div className="grid grid-cols-2 gap-6">
                            <motion.div
                                initial={{ opacity: 0, scale: 0.9 }}
                                whileInView={{ opacity: 1, scale: 1 }}
                                viewport={{ once: true }}
                                className="glass p-6 rounded-3xl"
                            >
                                <div className="text-3xl font-heading font-black text-white mb-1">A++</div>
                                <div className="text-[10px] text-white/30 uppercase tracking-widest font-bold">NAAC Accreditation</div>
                            </motion.div>
                            <motion.div
                                initial={{ opacity: 0, scale: 0.9 }}
                                whileInView={{ opacity: 1, scale: 1 }}
                                viewport={{ once: true }}
                                transition={{ delay: 0.1 }}
                                className="glass p-6 rounded-3xl"
                            >
                                <div className="text-3xl font-heading font-black text-accent-400 mb-1">91%</div>
                                <div className="text-[10px] text-white/30 uppercase tracking-widest font-bold">Placement Rate</div>
                            </motion.div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        {features.map((feature, i) => (
                            <motion.div
                                key={feature.title}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                whileHover={{ y: -6, rotate: 1 }}
                                className="group p-8 rounded-[2.5rem] glass border-white/5 hover:border-accent-400/20 transition-all duration-500"
                            >
                                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6 shadow-xl group-hover:scale-110 transition-transform duration-500 p-3.5`}>
                                    <feature.icon className="w-full h-full text-white" />
                                </div>
                                <h3 className="text-lg font-heading font-bold text-white mb-3 group-hover:text-accent-400 transition-colors">
                                    {feature.title}
                                </h3>
                                <p className="text-sm text-white/30 leading-relaxed group-hover:text-white/50 transition-colors">
                                    {feature.description}
                                </p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    )
}
