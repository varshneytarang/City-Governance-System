import React from 'react'
import { motion } from 'framer-motion'
import { Activity, AlertTriangle, Wrench, CheckCircle, Droplets, TrendingUp } from 'lucide-react'

/**
 * Quick action buttons for common agent queries
 * Provides one-click shortcuts for frequent operations
 */
const QuickActions = ({ agentType, onActionClick, agentColor = '#3b82f6' }) => {
  // Define quick actions per agent type
  const getQuickActions = () => {
    switch (agentType) {
      case 'water':
        return [
          {
            label: 'Check Capacity',
            type: 'capacity_query',
            defaultLocation: 'Downtown',
            icon: Activity,
            description: 'Check water capacity and availability'
          },
          {
            label: 'Report Emergency',
            type: 'emergency_response',
            defaultLocation: 'Downtown',
            icon: AlertTriangle,
            description: 'Report water emergency'
          },
          {
            label: 'Schedule Maintenance',
            type: 'maintenance_request',
            defaultLocation: 'Downtown',
            icon: Wrench,
            description: 'Schedule maintenance work'
          },
          {
            label: 'Quality Check',
            type: 'water_quality_check',
            defaultLocation: 'Downtown',
            icon: CheckCircle,
            description: 'Request water quality test'
          }
        ]

      case 'fire':
        return [
          {
            label: 'Fire Emergency',
            type: 'fire_emergency',
            defaultLocation: 'Downtown',
            icon: AlertTriangle,
            description: 'Report fire emergency'
          },
          {
            label: 'Fire Inspection',
            type: 'fire_inspection',
            defaultLocation: 'Downtown',
            icon: CheckCircle,
            description: 'Schedule fire safety inspection'
          },
          {
            label: 'Safety Assessment',
            type: 'fire_safety_assessment',
            defaultLocation: 'Downtown',
            icon: Activity,
            description: 'Request safety assessment'
          }
        ]

      case 'engineering':
        return [
          {
            label: 'Project Planning',
            type: 'project_planning',
            defaultLocation: 'Downtown',
            icon: Activity,
            description: 'Start project planning'
          },
          {
            label: 'Infrastructure Check',
            type: 'infrastructure_assessment',
            defaultLocation: 'Downtown',
            icon: CheckCircle,
            description: 'Assess infrastructure status'
          },
          {
            label: 'Road Repair',
            type: 'road_repair',
            defaultLocation: 'Downtown',
            icon: Wrench,
            description: 'Request road repair'
          }
        ]

      case 'health':
        return [
          {
            label: 'Health Inspection',
            type: 'health_inspection',
            defaultLocation: 'Downtown',
            icon: CheckCircle,
            description: 'Schedule health inspection'
          },
          {
            label: 'Disease Outbreak',
            type: 'disease_outbreak',
            defaultLocation: 'Downtown',
            icon: AlertTriangle,
            description: 'Report disease outbreak'
          },
          {
            label: 'Vaccination Campaign',
            type: 'vaccination_campaign',
            defaultLocation: 'Downtown',
            icon: Activity,
            description: 'Plan vaccination campaign'
          }
        ]

      case 'finance':
        return [
          {
            label: 'Budget Approval',
            type: 'budget_approval',
            defaultLocation: 'Downtown',
            icon: CheckCircle,
            description: 'Request budget approval'
          },
          {
            label: 'Cost Estimation',
            type: 'cost_estimation',
            defaultLocation: 'Downtown',
            icon: TrendingUp,
            description: 'Get cost estimate'
          },
          {
            label: 'Financial Audit',
            type: 'financial_audit',
            defaultLocation: 'Downtown',
            icon: Activity,
            description: 'Schedule financial audit'
          }
        ]

      case 'sanitation':
        return [
          {
            label: 'Waste Collection',
            type: 'waste_collection',
            defaultLocation: 'Downtown',
            icon: Activity,
            description: 'Schedule waste collection'
          },
          {
            label: 'Street Cleaning',
            type: 'street_cleaning',
            defaultLocation: 'Downtown',
            icon: Wrench,
            description: 'Request street cleaning'
          },
          {
            label: 'Sanitation Inspection',
            type: 'sanitation_inspection',
            defaultLocation: 'Downtown',
            icon: CheckCircle,
            description: 'Schedule inspection'
          }
        ]

      default:
        return []
    }
  }

  const actions = getQuickActions()

  return (
    <div className="p-4 border-b border-gray-100 bg-gray-50/50">
      <h3 className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-3">
        Quick Actions
      </h3>
      <div className="grid grid-cols-2 gap-2">
        {actions.map((action, index) => {
          const Icon = action.icon
          return (
            <motion.button
              key={action.type}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => onActionClick(action)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white border border-gray-200 hover:border-gray-300 transition-all text-left group hover:shadow-sm"
              title={action.description}
            >
              <div 
                className="p-1.5 rounded-md flex-shrink-0"
                style={{ backgroundColor: `${agentColor}15` }}
              >
                <Icon size={14} style={{ color: agentColor }} />
              </div>
              <span className="text-xs font-medium text-gray-700 group-hover:text-gray-900">
                {action.label}
              </span>
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}

export default QuickActions
