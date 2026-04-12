import { motion } from 'framer-motion'
import { GraduationCap, Mail, Phone, MapPin, Facebook, Twitter, Instagram, Linkedin, Youtube, ArrowUp } from 'lucide-react'

const quickLinks = [
    { name: 'About Us', href: '#' },
    { name: 'Admissions', href: '#admissions' },
    { name: 'Courses', href: '#courses' },
    { name: 'Placements', href: '#placement' },
    { name: 'Research', href: '#' },
    { name: 'Campus Life', href: '#' },
]

const programs = [
    { name: 'Computer Science', href: '#courses' },
    { name: 'Electronics & Communication', href: '#courses' },
    { name: 'Mechanical Engineering', href: '#courses' },
    { name: 'Civil Engineering', href: '#courses' },
    { name: 'Data Science', href: '#courses' },
    { name: 'Artificial Intelligence', href: '#courses' },
]

const socials = [
    { icon: Facebook, href: '#', label: 'Facebook' },
    { icon: Twitter, href: '#', label: 'Twitter' },
    { icon: Instagram, href: '#', label: 'Instagram' },
    { icon: Linkedin, href: '#', label: 'LinkedIn' },
    { icon: Youtube, href: '#', label: 'YouTube' },
]

export default function Footer() {
    const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' })

    return (
        <footer id="contact" className="relative border-t border-white/5">
            {/* Background */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[300px] rounded-full bg-primary-600/5 blur-[150px]" />
            </div>

            <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Main footer content */}
                <div className="py-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
                    {/* Brand */}
                    <div className="lg:col-span-1">
                        <a href="#home" className="flex items-center gap-3 mb-5">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                                <GraduationCap className="w-6 h-6 text-white" />
                            </div>
                            <div className="flex flex-col">
                                <span className="text-lg font-heading font-bold text-white leading-tight">Nexus Institute</span>
                                <span className="text-[10px] tracking-[0.2em] uppercase text-primary-300/60 font-medium">of Technology</span>
                            </div>
                        </a>
                        <p className="text-sm text-white/40 leading-relaxed mb-6">
                            Empowering the next generation of engineers with industry-driven education and cutting-edge research.
                        </p>
                        <div className="flex items-center gap-3">
                            {socials.map((social) => (
                                <a
                                    key={social.label}
                                    href={social.href}
                                    aria-label={social.label}
                                    className="w-9 h-9 rounded-lg glass flex items-center justify-center text-white/40 hover:text-white hover:bg-primary-500/20 transition-all duration-300"
                                >
                                    <social.icon className="w-4 h-4" />
                                </a>
                            ))}
                        </div>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h4 className="text-sm font-heading font-semibold text-white mb-5 uppercase tracking-wider">Quick Links</h4>
                        <ul className="space-y-3">
                            {quickLinks.map((link) => (
                                <li key={link.name}>
                                    <a href={link.href} className="text-sm text-white/40 hover:text-primary-300 transition-colors duration-300">
                                        {link.name}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Programs */}
                    <div>
                        <h4 className="text-sm font-heading font-semibold text-white mb-5 uppercase tracking-wider">Programs</h4>
                        <ul className="space-y-3">
                            {programs.map((link) => (
                                <li key={link.name}>
                                    <a href={link.href} className="text-sm text-white/40 hover:text-primary-300 transition-colors duration-300">
                                        {link.name}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Contact Info */}
                    <div>
                        <h4 className="text-sm font-heading font-semibold text-white mb-5 uppercase tracking-wider">Contact Us</h4>
                        <ul className="space-y-4">
                            <li className="flex items-start gap-3">
                                <MapPin className="w-4 h-4 text-primary-400 shrink-0 mt-0.5" />
                                <span className="text-sm text-white/40">
                                    123 Innovation Drive, Tech City, Tamil Nadu - 600119
                                </span>
                            </li>
                            <li className="flex items-center gap-3">
                                <Phone className="w-4 h-4 text-primary-400 shrink-0" />
                                <span className="text-sm text-white/40">+91 44 2650 1234</span>
                            </li>
                            <li className="flex items-center gap-3">
                                <Mail className="w-4 h-4 text-primary-400 shrink-0" />
                                <span className="text-sm text-white/40">admissions@nexusinstitute.edu</span>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Bottom bar */}
                <div className="py-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <p className="text-xs text-white/30">
                        © 2026 Nexus Institute of Technology. All rights reserved.
                    </p>
                    <div className="flex items-center gap-6">
                        <a href="#" className="text-xs text-white/30 hover:text-white/50 transition-colors">Privacy Policy</a>
                        <a href="#" className="text-xs text-white/30 hover:text-white/50 transition-colors">Terms of Service</a>
                    </div>
                </div>
            </div>

            {/* Scroll to top */}
            <motion.button
                onClick={scrollToTop}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                className="fixed bottom-24 right-6 w-11 h-11 rounded-xl bg-gradient-to-br from-primary-600 to-primary-500 flex items-center justify-center shadow-lg shadow-primary-600/30 z-40 hover:shadow-primary-500/50 transition-shadow"
                aria-label="Scroll to top"
            >
                <ArrowUp className="w-5 h-5 text-white" />
            </motion.button>
        </footer>
    )
}
