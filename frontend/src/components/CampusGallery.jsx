import { motion, useInView, AnimatePresence } from 'framer-motion'
import { useRef, useState, useCallback } from 'react'
import { X, ZoomIn, MapPin, ChevronLeft, ChevronRight, Camera } from 'lucide-react'

import img1 from '../assets/pang-yuhao-_kd5cxwZOK4-unsplash.jpg'
import img2 from '../assets/dom-fou-YRMWVcdyhmI-unsplash.jpg'
import img3 from '../assets/alex-batchelor-_me3b1TjSvY-unsplash.jpg'
import img4 from '../assets/joshua-hoehne-iggWDxHTAUQ-unsplash.jpg'
import img5 from '../assets/porter-raab-Ucr4Yp-t364-unsplash.jpg'
import img6 from '../assets/clementine-JNJEGrP9raA-unsplash.jpg'
import img7 from '../assets/dominic-kurniawan-suryaputra-v4DVZst1MhA-unsplash.jpg'
import img8 from '../assets/mohamed-m-fWo9k2dvc70-unsplash.jpg'
import img9 from '../assets/priscilla-du-preez-ggeZ9oyI-PE-unsplash.jpg'
import img10 from '../assets/adrien-olichon-z8XO8BfqpYc-unsplash.jpg'

const galleryItems = [
    { src: img1, title: 'Main Campus Building', location: 'Central Block', category: 'campus' },
    { src: img2, title: 'Innovation Hub', location: 'Tech Wing', category: 'facilities' },
    { src: img3, title: 'Student Library', location: 'Knowledge Center', category: 'facilities' },
    { src: img4, title: 'Research Laboratory', location: 'Science Block', category: 'labs' },
    { src: img5, title: 'Sports Complex', location: 'Campus South', category: 'campus' },
    { src: img6, title: 'Grand Auditorium', location: 'Cultural Wing', category: 'facilities' },
    { src: img7, title: 'Aerial Campus View', location: 'Overview', category: 'campus' },
    { src: img8, title: 'Student Cafeteria', location: 'Common Area', category: 'life' },
    { src: img9, title: 'Student Life & Events', location: 'Activity Center', category: 'life' },
    { src: img10, title: 'Modern Architecture', location: 'New Wing', category: 'campus' },
]

const categories = [
    { key: 'all', label: 'All Photos' },
    { key: 'campus', label: 'Campus' },
    { key: 'facilities', label: 'Facilities' },
    { key: 'labs', label: 'Labs' },
    { key: 'life', label: 'Student Life' },
]

export default function CampusGallery() {
    const ref = useRef(null)
    const isInView = useInView(ref, { once: true, margin: '-60px' })
    const [selectedIndex, setSelectedIndex] = useState(null)
    const [activeCategory, setActiveCategory] = useState('all')

    const filteredItems = activeCategory === 'all'
        ? galleryItems
        : galleryItems.filter(item => item.category === activeCategory)

    const openLightbox = useCallback((index) => setSelectedIndex(index), [])
    const closeLightbox = useCallback(() => setSelectedIndex(null), [])
    const goNext = useCallback(() => {
        setSelectedIndex(prev => (prev + 1) % filteredItems.length)
    }, [filteredItems.length])
    const goPrev = useCallback(() => {
        setSelectedIndex(prev => (prev - 1 + filteredItems.length) % filteredItems.length)
    }, [filteredItems.length])

    return (
        <section id="campus" className="relative py-28 sm:py-36 overflow-hidden">
            {/* Rich background */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary-500/20 to-transparent" />
                <div className="absolute top-1/3 right-0 w-[600px] h-[600px] rounded-full bg-accent-500/[0.04] blur-[180px]" />
                <div className="absolute bottom-1/4 left-0 w-[500px] h-[500px] rounded-full bg-primary-600/[0.04] blur-[150px]" />
                <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-accent-500/15 to-transparent" />
            </div>

            <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.7 }}
                    className="text-center mb-14"
                >
                    <motion.div
                        initial={{ scale: 0 }}
                        whileInView={{ scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
                        className="inline-flex items-center gap-2 px-5 py-2 rounded-full glass mb-6"
                    >
                        <Camera className="w-3.5 h-3.5 text-accent-400" />
                        <span className="text-xs font-semibold text-accent-400 uppercase tracking-widest">
                            Campus Tour
                        </span>
                    </motion.div>
                    <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-heading font-bold mb-5">
                        Explore Our{' '}
                        <span className="gradient-text">World-Class</span>{' '}
                        Campus
                    </h2>
                    <p className="text-white/40 max-w-2xl mx-auto text-base sm:text-lg leading-relaxed">
                        State-of-the-art facilities spread across 50+ acres of lush green environment,
                        designed for excellence in learning and innovation
                    </p>
                </motion.div>

                {/* Category Tabs */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                    className="flex flex-wrap items-center justify-center gap-2 mb-12"
                >
                    {categories.map((cat) => (
                        <button
                            key={cat.key}
                            onClick={() => setActiveCategory(cat.key)}
                            className={`px-5 py-2 rounded-xl text-xs font-semibold uppercase tracking-wider transition-all duration-400 cursor-pointer ${activeCategory === cat.key
                                    ? 'bg-gradient-to-r from-primary-600 to-accent-500 text-white shadow-lg shadow-primary-600/25'
                                    : 'glass text-white/50 hover:text-white hover:bg-white/10'
                                }`}
                        >
                            {cat.label}
                        </button>
                    ))}
                </motion.div>

                {/* Gallery Grid - Premium Bento Layout */}
                <div ref={ref}>
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={activeCategory}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.4 }}
                            className="space-y-4"
                        >
                            {/* Row 1: Hero + 2 stacked */}
                            {filteredItems.length >= 3 && (
                                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                                    <GalleryCard
                                        item={filteredItems[0]}
                                        index={0}
                                        isInView={isInView}
                                        className="md:col-span-3 h-[300px] sm:h-[380px]"
                                        onSelect={openLightbox}
                                        featured
                                    />
                                    <div className="md:col-span-2 flex flex-col gap-4">
                                        <GalleryCard
                                            item={filteredItems[1]}
                                            index={1}
                                            isInView={isInView}
                                            className="flex-1 min-h-[170px]"
                                            onSelect={openLightbox}
                                        />
                                        <GalleryCard
                                            item={filteredItems[2]}
                                            index={2}
                                            isInView={isInView}
                                            className="flex-1 min-h-[170px]"
                                            onSelect={openLightbox}
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Row 2: 4 equal cards */}
                            {filteredItems.length >= 7 && (
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    {filteredItems.slice(3, 7).map((item, i) => (
                                        <GalleryCard
                                            key={item.title}
                                            item={item}
                                            index={i + 3}
                                            isInView={isInView}
                                            className="h-[200px] sm:h-[240px]"
                                            onSelect={openLightbox}
                                        />
                                    ))}
                                </div>
                            )}

                            {/* Row 3: 2 stacked + Hero */}
                            {filteredItems.length >= 10 && (
                                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                                    <div className="md:col-span-2 flex flex-col gap-4">
                                        <GalleryCard
                                            item={filteredItems[7]}
                                            index={7}
                                            isInView={isInView}
                                            className="flex-1 min-h-[170px]"
                                            onSelect={openLightbox}
                                        />
                                        <GalleryCard
                                            item={filteredItems[8]}
                                            index={8}
                                            isInView={isInView}
                                            className="flex-1 min-h-[170px]"
                                            onSelect={openLightbox}
                                        />
                                    </div>
                                    <GalleryCard
                                        item={filteredItems[9]}
                                        index={9}
                                        isInView={isInView}
                                        className="md:col-span-3 h-[300px] sm:h-[380px]"
                                        onSelect={openLightbox}
                                        featured
                                    />
                                </div>
                            )}

                            {/* Smaller filtered sets: simple grid */}
                            {filteredItems.length > 0 && filteredItems.length < 3 && (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {filteredItems.map((item, i) => (
                                        <GalleryCard
                                            key={item.title}
                                            item={item}
                                            index={i}
                                            isInView={isInView}
                                            className="h-[280px] sm:h-[340px]"
                                            onSelect={openLightbox}
                                        />
                                    ))}
                                </div>
                            )}
                            {filteredItems.length >= 3 && filteredItems.length < 7 && filteredItems.length > 3 && (
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                    {filteredItems.slice(3).map((item, i) => (
                                        <GalleryCard
                                            key={item.title}
                                            item={item}
                                            index={i + 3}
                                            isInView={isInView}
                                            className="h-[200px] sm:h-[240px]"
                                            onSelect={openLightbox}
                                        />
                                    ))}
                                </div>
                            )}
                        </motion.div>
                    </AnimatePresence>
                </div>

                {/* Photo count */}
                <motion.div
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.5 }}
                    className="text-center mt-8"
                >
                    <span className="text-xs text-white/25 uppercase tracking-widest">
                        {filteredItems.length} Photos • Tap to explore
                    </span>
                </motion.div>
            </div>

            {/* Premium Lightbox */}
            <AnimatePresence>
                {selectedIndex !== null && filteredItems[selectedIndex] && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="fixed inset-0 z-[100] flex items-center justify-center"
                        onClick={closeLightbox}
                    >
                        {/* Backdrop */}
                        <div className="absolute inset-0 bg-navy-950/95 backdrop-blur-2xl" />

                        {/* Close */}
                        <motion.button
                            whileHover={{ scale: 1.1, rotate: 90 }}
                            whileTap={{ scale: 0.9 }}
                            className="absolute top-6 right-6 z-20 w-12 h-12 rounded-2xl glass flex items-center justify-center text-white/50 hover:text-white transition-colors cursor-pointer"
                            onClick={closeLightbox}
                        >
                            <X className="w-5 h-5" />
                        </motion.button>

                        {/* Nav Arrows */}
                        <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            className="absolute left-4 sm:left-8 z-20 w-12 h-12 rounded-2xl glass flex items-center justify-center text-white/50 hover:text-white transition-colors cursor-pointer"
                            onClick={(e) => { e.stopPropagation(); goPrev() }}
                        >
                            <ChevronLeft className="w-6 h-6" />
                        </motion.button>
                        <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            className="absolute right-4 sm:right-8 z-20 w-12 h-12 rounded-2xl glass flex items-center justify-center text-white/50 hover:text-white transition-colors cursor-pointer"
                            onClick={(e) => { e.stopPropagation(); goNext() }}
                        >
                            <ChevronRight className="w-6 h-6" />
                        </motion.button>

                        {/* Image */}
                        <motion.div
                            key={selectedIndex}
                            initial={{ scale: 0.85, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.85, opacity: 0 }}
                            transition={{ duration: 0.35, ease: [0.25, 0.46, 0.45, 0.94] }}
                            className="relative max-w-5xl w-full mx-4 sm:mx-16 rounded-3xl overflow-hidden shadow-2xl shadow-black/60"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <img
                                src={filteredItems[selectedIndex].src}
                                alt={filteredItems[selectedIndex].title}
                                className="w-full h-auto max-h-[80vh] object-contain bg-navy-900"
                            />
                            {/* Info bar */}
                            <div className="absolute bottom-0 left-0 right-0 p-6 sm:p-8 bg-gradient-to-t from-navy-950 via-navy-950/80 to-transparent">
                                <div className="flex items-end justify-between">
                                    <div>
                                        <h3 className="text-xl font-heading font-bold text-white mb-1">
                                            {filteredItems[selectedIndex].title}
                                        </h3>
                                        <div className="flex items-center gap-2">
                                            <MapPin className="w-3.5 h-3.5 text-primary-400" />
                                            <span className="text-sm text-white/50">
                                                {filteredItems[selectedIndex].location}
                                            </span>
                                        </div>
                                    </div>
                                    <span className="text-xs text-white/30 font-medium">
                                        {selectedIndex + 1} / {filteredItems.length}
                                    </span>
                                </div>
                            </div>
                        </motion.div>

                        {/* Thumbnails row */}
                        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-2 z-20">
                            {filteredItems.map((item, i) => (
                                <button
                                    key={item.title}
                                    onClick={(e) => { e.stopPropagation(); setSelectedIndex(i) }}
                                    className={`w-10 h-10 rounded-lg overflow-hidden transition-all duration-300 cursor-pointer ${i === selectedIndex
                                            ? 'ring-2 ring-primary-400 ring-offset-2 ring-offset-navy-950 scale-110'
                                            : 'opacity-40 hover:opacity-70'
                                        }`}
                                >
                                    <img src={item.src} alt="" className="w-full h-full object-cover" />
                                </button>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </section>
    )
}

function GalleryCard({ item, index, isInView, className = '', onSelect, featured = false }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 40, scale: 0.95 }}
            animate={isInView ? { opacity: 1, y: 0, scale: 1 } : {}}
            transition={{
                delay: index * 0.08,
                duration: 0.6,
                ease: [0.25, 0.46, 0.45, 0.94],
            }}
            whileHover={{ y: -4 }}
            className={`relative group cursor-pointer rounded-2xl overflow-hidden ${className}`}
            onClick={() => onSelect(index)}
        >
            {/* Image */}
            <img
                src={item.src}
                alt={item.title}
                className="absolute inset-0 w-full h-full object-cover transition-transform duration-[800ms] group-hover:scale-[1.08]"
                loading="lazy"
            />

            {/* Multi-layer overlays */}
            <div className="absolute inset-0 bg-gradient-to-t from-navy-950/90 via-navy-950/20 to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-br from-primary-600/0 via-transparent to-accent-500/0 group-hover:from-primary-600/10 group-hover:to-accent-500/10 transition-all duration-700" />

            {/* Animated border */}
            <div className="absolute inset-0 rounded-2xl border border-white/[0.06] group-hover:border-primary-400/30 transition-colors duration-500" />

            {/* Corner accent */}
            <div className="absolute top-0 left-0 w-16 h-16 bg-gradient-to-br from-primary-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            {/* Zoom icon */}
            <div className="absolute top-4 right-4 w-10 h-10 rounded-xl bg-white/10 backdrop-blur-md flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-400 translate-y-3 group-hover:translate-y-0 border border-white/10">
                <ZoomIn className="w-4 h-4 text-white" />
            </div>

            {/* Featured badge */}
            {featured && (
                <div className="absolute top-4 left-4 px-3 py-1 rounded-lg bg-gradient-to-r from-primary-600/90 to-accent-500/90 backdrop-blur-sm text-[10px] font-bold text-white uppercase tracking-wider">
                    Featured
                </div>
            )}

            {/* Content */}
            <div className="absolute bottom-0 left-0 right-0 p-5 transform translate-y-2 group-hover:translate-y-0 transition-transform duration-400">
                <h4 className={`${featured ? 'text-lg' : 'text-sm'} font-heading font-bold text-white drop-shadow-lg mb-1`}>
                    {item.title}
                </h4>
                <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-all duration-400 delay-100 -translate-y-1 group-hover:translate-y-0">
                    <MapPin className="w-3 h-3 text-primary-400" />
                    <span className="text-xs text-white/60 font-medium">{item.location}</span>
                </div>
            </div>
        </motion.div>
    )
}
