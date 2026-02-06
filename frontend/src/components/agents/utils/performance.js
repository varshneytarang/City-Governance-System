/**
 * Performance Optimization Utilities
 * Debouncing, throttling, memoization, lazy loading
 */

/**
 * Debounce function - delays execution until after wait time
 */
export const debounce = (func, wait = 300) => {
  let timeout
  
  const debounced = function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
  
  debounced.cancel = function() {
    clearTimeout(timeout)
  }
  
  return debounced
}

/**
 * Throttle function - limits execution to once per wait time
 */
export const throttle = (func, wait = 300) => {
  let inThrottle
  let lastRan
  
  return function(...args) {
    if (!inThrottle) {
      func(...args)
      lastRan = Date.now()
      inThrottle = true
      
      setTimeout(() => {
        inThrottle = false
      }, wait)
    }
  }
}

/**
 * Memoize function results
 */
export const memoize = (func, resolver) => {
  const cache = new Map()
  
  return function(...args) {
    const key = resolver ? resolver(...args) : JSON.stringify(args)
    
    if (cache.has(key)) {
      return cache.get(key)
    }
    
    const result = func(...args)
    cache.set(key, result)
    
    // Prevent memory leaks - limit cache size
    if (cache.size > 100) {
      const firstKey = cache.keys().next().value
      cache.delete(firstKey)
    }
    
    return result
  }
}

/**
 * Lazy load component with retry logic
 */
export const lazyWithRetry = (componentImport, retries = 3) => {
  return new Promise((resolve, reject) => {
    const attemptImport = (attemptsLeft) => {
      componentImport()
        .then(resolve)
        .catch((error) => {
          if (attemptsLeft === 1) {
            reject(error)
            return
          }
          
          console.warn(`Retry loading component (${attemptsLeft - 1} attempts left)`)
          
          // Exponential backoff
          const delay = (retries - attemptsLeft + 1) * 1000
          setTimeout(() => attemptImport(attemptsLeft - 1), delay)
        })
    }
    
    attemptImport(retries)
  })
}

/**
 * Request Animation Frame throttle
 */
export const rafThrottle = (func) => {
  let rafId = null
  
  return function(...args) {
    if (rafId !== null) return
    
    rafId = requestAnimationFrame(() => {
      func(...args)
      rafId = null
    })
  }
}

/**
 * Intersection Observer for lazy rendering
 */
export const createLazyObserver = (callback, options = {}) => {
  const defaultOptions = {
    root: null,
    rootMargin: '50px',
    threshold: 0.01,
    ...options
  }
  
  if (!('IntersectionObserver' in window)) {
    // Fallback for browsers without IntersectionObserver
    return {
      observe: () => callback(),
      disconnect: () => {},
      unobserve: () => {}
    }
  }
  
  return new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        callback(entry.target)
      }
    })
  }, defaultOptions)
}

/**
 * Virtual scroll helper for large lists
 */
export class VirtualScroller {
  constructor(options = {}) {
    this.itemHeight = options.itemHeight || 60
    this.containerHeight = options.containerHeight || 400
    this.overscan = options.overscan || 3
    this.items = options.items || []
  }
  
  getVisibleRange(scrollTop) {
    const start = Math.floor(scrollTop / this.itemHeight)
    const visibleCount = Math.ceil(this.containerHeight / this.itemHeight)
    const end = start + visibleCount
    
    return {
      start: Math.max(0, start - this.overscan),
      end: Math.min(this.items.length, end + this.overscan),
      offsetY: Math.max(0, start - this.overscan) * this.itemHeight
    }
  }
  
  getTotalHeight() {
    return this.items.length * this.itemHeight
  }
  
  updateItems(items) {
    this.items = items
  }
}

/**
 * Batch DOM updates
 */
export const batchDOMUpdates = (updates) => {
  return new Promise((resolve) => {
    requestAnimationFrame(() => {
      updates.forEach(update => update())
      resolve()
    })
  })
}

/**
 * Optimize images with lazy loading
 */
export const optimizeImage = (src, options = {}) => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    
    img.onload = () => resolve(img)
    img.onerror = reject
    
    if (options.lazy) {
      img.loading = 'lazy'
    }
    
    if (options.sizes) {
      img.sizes = options.sizes
    }
    
    if (options.srcset) {
      img.srcset = options.srcset
    }
    
    img.src = src
  })
}

/**
 * Preload critical resources
 */
export const preloadResource = (url, type = 'fetch') => {
  const link = document.createElement('link')
  link.rel = 'preload'
  link.href = url
  link.as = type
  
  document.head.appendChild(link)
}

/**
 * Measure performance
 */
export class PerformanceMonitor {
  constructor(name) {
    this.name = name
    this.marks = {}
    this.measures = {}
  }
  
  start(label = 'default') {
    const markName = `${this.name}-${label}-start`
    this.marks[label] = { start: markName }
    
    if (window.performance && window.performance.mark) {
      performance.mark(markName)
    } else {
      this.marks[label].startTime = Date.now()
    }
  }
  
  end(label = 'default') {
    const markName = `${this.name}-${label}-end`
    
    if (!this.marks[label]) {
      console.warn(`No start mark found for ${label}`)
      return null
    }
    
    this.marks[label].end = markName
    
    if (window.performance && window.performance.mark) {
      performance.mark(markName)
      
      const measureName = `${this.name}-${label}`
      performance.measure(measureName, this.marks[label].start, markName)
      
      const measure = performance.getEntriesByName(measureName)[0]
      this.measures[label] = measure.duration
      
      return measure.duration
    } else {
      const duration = Date.now() - this.marks[label].startTime
      this.measures[label] = duration
      return duration
    }
  }
  
  getMeasures() {
    return { ...this.measures }
  }
  
  clear() {
    if (window.performance && window.performance.clearMarks) {
      Object.values(this.marks).forEach(mark => {
        if (mark.start) performance.clearMarks(mark.start)
        if (mark.end) performance.clearMarks(mark.end)
      })
    }
    
    this.marks = {}
    this.measures = {}
  }
}

/**
 * Request Idle Callback wrapper with fallback
 */
export const requestIdleCallback = (callback, options = {}) => {
  if ('requestIdleCallback' in window) {
    return window.requestIdleCallback(callback, options)
  } else {
    // Fallback for browsers without requestIdleCallback
    const timeout = options.timeout || 1000
    return setTimeout(() => {
      callback({
        didTimeout: false,
        timeRemaining: () => 50
      })
    }, timeout)
  }
}

/**
 * Cancel Idle Callback wrapper
 */
export const cancelIdleCallback = (id) => {
  if ('cancelIdleCallback' in window) {
    window.cancelIdleCallback(id)
  } else {
    clearTimeout(id)
  }
}

/**
 * Web Worker helper for heavy computations
 */
export const runInWorker = (func, ...args) => {
  return new Promise((resolve, reject) => {
    const blob = new Blob([`
      self.onmessage = function(e) {
        const func = ${func.toString()};
        const result = func(...e.data);
        self.postMessage(result);
      }
    `], { type: 'application/javascript' })
    
    const worker = new Worker(URL.createObjectURL(blob))
    
    worker.onmessage = (e) => {
      resolve(e.data)
      worker.terminate()
    }
    
    worker.onerror = (error) => {
      reject(error)
      worker.terminate()
    }
    
    worker.postMessage(args)
  })
}

/**
 * Cache with expiration
 */
export class ExpiringCache {
  constructor(ttl = 5 * 60 * 1000) { // 5 minutes default
    this.cache = new Map()
    this.ttl = ttl
  }
  
  set(key, value) {
    const expiresAt = Date.now() + this.ttl
    this.cache.set(key, { value, expiresAt })
  }
  
  get(key) {
    const item = this.cache.get(key)
    
    if (!item) return null
    
    if (Date.now() > item.expiresAt) {
      this.cache.delete(key)
      return null
    }
    
    return item.value
  }
  
  has(key) {
    return this.get(key) !== null
  }
  
  clear() {
    this.cache.clear()
  }
  
  cleanup() {
    const now = Date.now()
    for (const [key, item] of this.cache.entries()) {
      if (now > item.expiresAt) {
        this.cache.delete(key)
      }
    }
  }
}

export default {
  debounce,
  throttle,
  memoize,
  lazyWithRetry,
  rafThrottle,
  createLazyObserver,
  VirtualScroller,
  batchDOMUpdates,
  optimizeImage,
  preloadResource,
  PerformanceMonitor,
  requestIdleCallback,
  cancelIdleCallback,
  runInWorker,
  ExpiringCache
}
