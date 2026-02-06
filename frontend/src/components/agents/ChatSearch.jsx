import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, X, ChevronDown, ChevronUp } from 'lucide-react'

/**
 * Chat Search Component
 * Search and navigate through chat messages
 */
const ChatSearch = ({ messages, onResultClick, isOpen, onClose }) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [currentResultIndex, setCurrentResultIndex] = useState(-1)

  // Search messages when query changes
  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSearchResults([])
      setCurrentResultIndex(-1)
      return
    }

    const query = searchQuery.toLowerCase()
    const results = messages
      .map((msg, index) => ({ ...msg, originalIndex: index }))
      .filter(msg => 
        msg.content.toLowerCase().includes(query) ||
        (msg.type && msg.type.toLowerCase().includes(query))
      )
    
    setSearchResults(results)
    setCurrentResultIndex(results.length > 0 ? 0 : -1)
  }, [searchQuery, messages])

  // Navigate to previous result
  const gotoPrevious = () => {
    if (searchResults.length === 0) return
    const newIndex = currentResultIndex > 0 ? currentResultIndex - 1 : searchResults.length - 1
    setCurrentResultIndex(newIndex)
    onResultClick && onResultClick(searchResults[newIndex])
  }

  // Navigate to next result
  const gotoNext = () => {
    if (searchResults.length === 0) return
    const newIndex = currentResultIndex < searchResults.length - 1 ? currentResultIndex + 1 : 0
    setCurrentResultIndex(newIndex)
    onResultClick && onResultClick(searchResults[newIndex])
  }

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (e.shiftKey) {
        gotoPrevious()
      } else {
        gotoNext()
      }
    } else if (e.key === 'Escape') {
      handleClose()
    }
  }

  const handleClose = () => {
    setSearchQuery('')
    setSearchResults([])
    setCurrentResultIndex(-1)
    onClose && onClose()
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="bg-white border-b border-gray-200 p-3 shadow-sm"
      >
        <div className="flex items-center gap-2">
          {/* Search Icon */}
          <Search size={16} className="text-gray-400" />
          
          {/* Search Input */}
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search messages..."
            className="flex-1 px-2 py-1 text-sm border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            autoFocus
          />
          
          {/* Results Counter */}
          {searchResults.length > 0 && (
            <div className="flex items-center gap-1 text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded">
              <span className="font-semibold">{currentResultIndex + 1}</span>
              <span>/</span>
              <span>{searchResults.length}</span>
            </div>
          )}
          
          {/* Navigation Buttons */}
          {searchResults.length > 0 && (
            <div className="flex items-center gap-1">
              <button
                onClick={gotoPrevious}
                className="p-1 rounded hover:bg-gray-100 transition-colors"
                title="Previous result (Shift+Enter)"
              >
                <ChevronUp size={16} className="text-gray-600" />
              </button>
              <button
                onClick={gotoNext}
                className="p-1 rounded hover:bg-gray-100 transition-colors"
                title="Next result (Enter)"
              >
                <ChevronDown size={16} className="text-gray-600" />
              </button>
            </div>
          )}
          
          {/* Close Button */}
          <button
            onClick={handleClose}
            className="p-1 rounded hover:bg-gray-100 transition-colors"
            title="Close (Esc)"
          >
            <X size={16} className="text-gray-600" />
          </button>
        </div>
        
        {/* No Results Message */}
        {searchQuery.trim().length >= 2 && searchResults.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-2 text-xs text-gray-500 italic"
          >
            No messages found for "{searchQuery}"
          </motion.div>
        )}
        
        {/* Search Tips */}
        {searchQuery.trim().length === 0 && (
          <div className="mt-2 text-xs text-gray-500">
            Type to search • <kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs">Enter</kbd> next • <kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs">Shift+Enter</kbd> previous
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  )
}

export default ChatSearch
