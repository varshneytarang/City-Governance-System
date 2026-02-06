/**
 * Smart Message Parser
 * Extracts locations, keywords, and intent from user messages
 */

// Common location patterns
const LOCATION_PATTERNS = [
  /\b(?:in|at|near|around|on)\s+([\w\s]+(?:street|road|avenue|ave|blvd|boulevard|lane|drive|district|area|zone|sector|park|building|facility))/gi,
  /\b([\w\s]+(?:street|road|avenue|ave|blvd|boulevard|lane|drive|district|area|zone|sector|park|building|facility))/gi,
  /\b(?:zip|zipcode|postal code)\s*:?\s*(\d{5}(?:-\d{4})?)/gi,
  /\b(north|south|east|west|central|downtown)\s+([\w\s]+)/gi
]

// Common city landmarks/areas
const COMMON_LOCATIONS = [
  'downtown', 'central', 'north district', 'south district', 
  'east district', 'west district', 'industrial area', 'residential area',
  'commercial zone', 'city center', 'main street', 'market area'
]

// Urgency keywords
const URGENCY_KEYWORDS = {
  emergency: ['emergency', 'urgent', 'critical', 'immediately', 'asap', 'help', 'danger', 'crisis'],
  high: ['soon', 'quickly', 'important', 'priority', 'serious'],
  normal: ['when possible', 'sometime', 'eventually', 'planning', 'future']
}

// Agent-specific keywords
const AGENT_KEYWORDS = {
  water: [
    'water', 'pipeline', 'leak', 'pressure', 'supply', 'quality', 'contamination',
    'meter', 'valve', 'pump', 'reservoir', 'treatment', 'sewage', 'drain'
  ],
  fire: [
    'fire', 'smoke', 'flames', 'burning', 'hazmat', 'rescue', 'inspection',
    'hydrant', 'extinguisher', 'safety', 'evacuation', 'alarm'
  ],
  engineering: [
    'road', 'bridge', 'construction', 'repair', 'infrastructure', 'pothole',
    'traffic', 'street', 'sidewalk', 'pavement', 'project', 'design'
  ],
  health: [
    'health', 'disease', 'infection', 'vaccine', 'inspection', 'restaurant',
    'food', 'sanitary', 'outbreak', 'medical', 'clinic', 'hospital'
  ],
  finance: [
    'budget', 'cost', 'payment', 'revenue', 'expense', 'audit', 'funds',
    'allocation', 'forecast', 'tax', 'billing', 'financial'
  ],
  sanitation: [
    'waste', 'garbage', 'trash', 'recycling', 'cleaning', 'disposal',
    'collection', 'dump', 'sanitation', 'litter', 'sweep'
  ]
}

/**
 * Extract locations from message text
 */
export const extractLocations = (message) => {
  const locations = new Set()
  
  // Try each pattern
  LOCATION_PATTERNS.forEach(pattern => {
    const matches = [...message.matchAll(pattern)]
    matches.forEach(match => {
      const location = match[1] || match[0]
      if (location) {
        locations.add(location.trim().toLowerCase())
      }
    })
  })
  
  // Check for common locations
  const lowerMessage = message.toLowerCase()
  COMMON_LOCATIONS.forEach(location => {
    if (lowerMessage.includes(location)) {
      locations.add(location)
    }
  })
  
  return Array.from(locations)
}

/**
 * Detect urgency level from message
 */
export const detectUrgency = (message) => {
  const lowerMessage = message.toLowerCase()
  
  // Check emergency keywords first
  if (URGENCY_KEYWORDS.emergency.some(keyword => lowerMessage.includes(keyword))) {
    return { level: 'emergency', score: 3 }
  }
  
  // Check high priority
  if (URGENCY_KEYWORDS.high.some(keyword => lowerMessage.includes(keyword))) {
    return { level: 'high', score: 2 }
  }
  
  // Check normal/low priority
  if (URGENCY_KEYWORDS.normal.some(keyword => lowerMessage.includes(keyword))) {
    return { level: 'normal', score: 1 }
  }
  
  // Default to normal if no keywords found
  return { level: 'normal', score: 1 }
}

/**
 * Extract relevant keywords for an agent
 */
export const extractKeywords = (message, agentType) => {
  const keywords = []
  const lowerMessage = message.toLowerCase()
  const agentKeywords = AGENT_KEYWORDS[agentType] || []
  
  agentKeywords.forEach(keyword => {
    if (lowerMessage.includes(keyword)) {
      keywords.push(keyword)
    }
  })
  
  return keywords
}

/**
 * Parse message and extract all relevant information
 */
export const parseMessage = (message, agentType) => {
  return {
    original: message,
    locations: extractLocations(message),
    urgency: detectUrgency(message),
    keywords: extractKeywords(message, agentType),
    length: message.length,
    wordCount: message.split(/\s+/).length,
    hasQuestion: message.includes('?'),
    sentiment: detectSentiment(message)
  }
}

/**
 * Simple sentiment detection
 */
const detectSentiment = (message) => {
  const positive = ['thank', 'thanks', 'great', 'good', 'excellent', 'appreciate', 'helpful']
  const negative = ['bad', 'poor', 'terrible', 'angry', 'frustrated', 'disappointed', 'useless']
  
  const lowerMessage = message.toLowerCase()
  const positiveCount = positive.filter(word => lowerMessage.includes(word)).length
  const negativeCount = negative.filter(word => lowerMessage.includes(word)).length
  
  if (positiveCount > negativeCount) return 'positive'
  if (negativeCount > positiveCount) return 'negative'
  return 'neutral'
}

/**
 * Get smart suggestions based on partial input
 */
export const getSmartSuggestions = (input, agentType, recentMessages = []) => {
  const suggestions = []
  const lowerInput = input.toLowerCase().trim()
  
  if (lowerInput.length < 2) return suggestions
  
  // Common question starters
  const questionStarters = [
    'What is the status of',
    'Can you help me with',
    'I need information about',
    'How do I request',
    'When will',
    'Where can I find'
  ]
  
  // Agent-specific templates
  const templates = {
    water: [
      'Check water quality in',
      'Report a water leak at',
      'Water pressure issues in',
      'Request pipeline inspection for',
      'What is the water supply schedule for'
    ],
    fire: [
      'Request fire safety inspection for',
      'Report a fire hazard at',
      'Schedule fire drill for',
      'Check fire hydrant status at',
      'Request fire safety training'
    ],
    engineering: [
      'Report a pothole on',
      'Request road repair for',
      'Bridge inspection needed at',
      'Construction permit status for',
      'Traffic signal issue at'
    ],
    health: [
      'Request restaurant inspection for',
      'Report health concern at',
      'Vaccination schedule for',
      'Public health advisory about',
      'Food safety compliance check'
    ],
    finance: [
      'Budget allocation for',
      'Cost estimate for',
      'Payment status for',
      'Financial report for',
      'Revenue forecast for'
    ],
    sanitation: [
      'Waste collection schedule for',
      'Report missed pickup at',
      'Request special waste disposal',
      'Street cleaning needed at',
      'Recycling program information'
    ]
  }
  
  // Match question starters
  questionStarters.forEach(starter => {
    if (starter.toLowerCase().startsWith(lowerInput)) {
      suggestions.push(starter)
    }
  })
  
  // Match agent-specific templates
  const agentTemplates = templates[agentType] || []
  agentTemplates.forEach(template => {
    if (template.toLowerCase().includes(lowerInput)) {
      suggestions.push(template)
    }
  })
  
  // Add location-based suggestions
  if (lowerInput.includes('in') || lowerInput.includes('at')) {
    COMMON_LOCATIONS.forEach(location => {
      suggestions.push(`${input} ${location}`)
    })
  }
  
  return suggestions.slice(0, 5) // Return top 5 suggestions
}

export default {
  parseMessage,
  extractLocations,
  detectUrgency,
  extractKeywords,
  getSmartSuggestions
}
