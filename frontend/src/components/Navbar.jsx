import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X, ShieldCheck } from 'lucide-react'

const navLinks = [
    { name: 'Home', href: '#home' },
    { name: 'Programs', href: '#courses' },
    { name: 'Campus', href: '#campus' },
    { name: 'Placement', href: '#placement' },
    { name: 'Admissions', href: '#admissions' },
]

export default function Navbar() {
    const [scrolled, setScrolled] = useState(false)
    const [mobileOpen, setMobileOpen] = useState(false)

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 50)
        window.addEventListener('scroll', handleScroll)
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    return (
        <motion.nav
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled
                ? 'glass-strong shadow-2xl shadow-black/30 py-4'
                : 'bg-transparent py-6'
                }`}
        >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between">
                    {/* Logo */}
                    <a href="#home" className="flex items-center gap-4 group">
                        <div className="relative">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center shadow-xl group-hover:scale-110 transition-transform duration-300">
                                <ShieldCheck className="w-7 h-7 text-accent-400" />
                            </div>
                            <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-accent-400 border-2 border-navy-950 flex items-center justify-center text-[8px] font-bold text-navy-950">
                                1
                            </div>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-xl font-heading font-extrabold text-white leading-tight tracking-tight">
                                Nexus 
                            </span>
                            <span className="text-[10px] tracking-[0.3em] uppercase text-accent-400 font-bold">
                                Category-1 University
                            </span>
                        </div>
                    </a>

                    {/* Desktop Nav */}
                    <div className="hidden md:flex items-center gap-2">
                        {navLinks.map((link) => (
                            <a
                                key={link.name}
                                href={link.href}
                                className="relative px-5 py-2 text-sm font-bold text-white/70 hover:text-white transition-all duration-300 group"
                            >
                                <span className="relative z-10">{link.name}</span>
                                <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-accent-400 group-hover:w-full transition-all duration-300 rounded-full" />
                            </a>
                        ))}
                    </div>

                    {/* CTA Button */}
                    <div className="hidden md:block">
                        <motion.a
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            href="#admissions"
                            className="inline-flex items-center px-8 py-3 text-sm font-bold text-white rounded-2xl bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-600 transition-all duration-500 shadow-xl shadow-primary-600/20"
                        >
                            Enquire Now
                        </motion.a>
                    </div>

                    {/* Mobile Toggle */}
                    <button
                        onClick={() => setMobileOpen(!mobileOpen)}
                        className="md:hidden w-12 h-12 flex items-center justify-center rounded-2xl glass text-white shadow-xl"
                        aria-label="Toggle menu"
                    >
                        {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            <AnimatePresence>
                {mobileOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="md:hidden overflow-hidden glass-strong mt-4 mx-4 rounded-3xl"
                    >
                        <div className="p-6 flex flex-col gap-3">
                            {navLinks.map((link) => (
                                <a
                                    key={link.name}
                                    href={link.href}
                                    onClick={() => setMobileOpen(false)}
                                    className="px-6 py-4 text-sm font-bold text-white/80 hover:text-white hover:bg-white/5 rounded-2xl transition-all"
                                >
                                    {link.name}
                                </a>
                            ))}
                            <a
                                href="#admissions"
                                onClick={() => setMobileOpen(false)}
                                className="mt-4 px-6 py-4 text-sm font-bold text-center text-white rounded-2xl bg-primary-600 shadow-xl shadow-primary-600/20"
                            >
                                Enquire Now
                            </a>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.nav>
    )
}
