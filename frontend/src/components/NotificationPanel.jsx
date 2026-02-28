import React, { useState, useEffect } from 'react';
import { 
  Bell, Check, AlertCircle, Clock, CheckCircle2, 
  AlertTriangle, Info, X 
} from 'lucide-react';

// Simple UI component replacements
const Card = ({ children, className = '' }) => <div className={`bg-white rounded-lg shadow ${className}`}>{children}</div>;
const CardHeader = ({ children, className = '' }) => <div className={`p-6 border-b ${className}`}>{children}</div>;
const CardTitle = ({ children, className = '' }) => <h2 className={`text-xl font-bold text-gray-900 ${className}`}>{children}</h2>;
const CardContent = ({ children, className = '' }) => <div className={`p-6 ${className}`}>{children}</div>;
const Badge = ({ children, variant = 'default', className = '' }) => (
  <span className={`px-2 py-1 text-xs rounded-full ${variant === 'outline' ? 'border border-gray-300 bg-white' : ''} ${className}`}>
    {children}
  </span>
);
const Button = ({ children, variant = 'default', size = 'default', className = '', onClick, disabled }) => {
  const baseClasses = 'rounded transition inline-flex items-center justify-center';
  const variantClasses = variant === 'outline' 
    ? 'border border-gray-300 bg-white hover:bg-gray-50 text-gray-700'
    : variant === 'ghost'
    ? 'hover:bg-gray-100 text-gray-700'
    : 'bg-blue-600 hover:bg-blue-700 text-white';
  const sizeClasses = size === 'sm' ? 'px-2 py-1 text-sm' : size === 'icon' ? 'p-2' : 'px-4 py-2';
  return (
    <button 
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${className}`} 
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};
const ScrollArea = ({ children, className = '' }) => <div className={`overflow-auto ${className}`}>{children}</div>;

/**
 * Notification Panel Component
 * 
 * Shows department notifications with real-time updates
 */
export default function NotificationPanel({ department }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showPanel, setShowPanel] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (department) {
      fetchNotifications();
      fetchUnreadCount();
      
      // Poll for new notifications every 30 seconds
      const interval = setInterval(() => {
        fetchNotifications();
        fetchUnreadCount();
      }, 30000);
      
      return () => clearInterval(interval);
    }
  }, [department]);

  const fetchNotifications = async () => {
    try {
      const response = await fetch(
        `/api/task-orchestration/departments/${department}/notifications?limit=50`
      );
      const data = await response.json();
      setNotifications(data);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  const fetchUnreadCount = async () => {
    try {
      const response = await fetch(
        `/api/task-orchestration/departments/${department}/notifications/unread-count`
      );
      const data = await response.json();
      setUnreadCount(data.unread_count);
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await fetch(`/api/task-orchestration/notifications/${notificationId}/read`, {
        method: 'POST'
      });
      
      // Update local state
      setNotifications(notifications.map(n => 
        n.notification_id === notificationId 
          ? { ...n, read_at: new Date().toISOString(), status: 'read' }
          : n
      ));
      
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    setLoading(true);
    try {
      const unreadNotifications = notifications.filter(n => !n.read_at);
      
      await Promise.all(
        unreadNotifications.map(n => 
          fetch(`/api/task-orchestration/notifications/${n.notification_id}/read`, {
            method: 'POST'
          })
        )
      );
      
      setNotifications(notifications.map(n => ({
        ...n,
        read_at: n.read_at || new Date().toISOString(),
        status: 'read'
      })));
      
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    } finally {
      setLoading(false);
    }
  };

  const getNotificationIcon = (type) => {
    const icons = {
      'task_ready': <CheckCircle2 size={20} className="text-green-500" />,
      'dependency_completed': <Check size={20} className="text-blue-500" />,
      'deadline_reminder': <Clock size={20} className="text-amber-500" />,
      'approval_needed': <AlertCircle size={20} className="text-purple-500" />,
      'task_blocked': <AlertTriangle size={20} className="text-red-500" />,
      'workflow_completed': <CheckCircle2 size={20} className="text-green-600" />,
      'info': <Info size={20} className="text-blue-500" />
    };
    return icons[type] || icons['info'];
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'low': 'border-gray-300 bg-gray-50',
      'medium': 'border-blue-300 bg-blue-50',
      'high': 'border-orange-300 bg-orange-50',
      'urgent': 'border-red-400 bg-red-100'
    };
    return colors[priority] || colors['medium'];
  };

  const formatTime = (dateString) => {
    if (!dateString) return 'Just now';
    
    const date = new Date(dateString);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000); // seconds
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
    
    return date.toLocaleDateString();
  };

  return (
    <>
      {/* Notification Bell Button */}
      <div className="relative">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowPanel(!showPanel)}
          className="relative"
        >
          <Bell size={18} />
          {unreadCount > 0 && (
            <Badge className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center bg-red-500 text-white text-xs">
              {unreadCount > 99 ? '99+' : unreadCount}
            </Badge>
          )}
        </Button>
      </div>

      {/* Notification Panel */}
      {showPanel && (
        <div className="fixed right-4 top-16 w-96 max-h-[80vh] z-50 shadow-2xl">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bell size={20} />
                  <CardTitle className="text-lg">Notifications</CardTitle>
                  {unreadCount > 0 && (
                    <Badge className="bg-red-500 text-white">
                      {unreadCount}
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {unreadCount > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={markAllAsRead}
                      disabled={loading}
                      className="text-xs"
                    >
                      Mark all read
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowPanel(false)}
                  >
                    <X size={16} />
                  </Button>
                </div>
              </div>
            </CardHeader>
            
            <ScrollArea className="h-[60vh]">
              <CardContent className="space-y-2 pt-0">
                {notifications.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Bell size={32} className="mx-auto mb-2 text-gray-300" />
                    <p className="text-sm">No notifications</p>
                  </div>
                ) : (
                  notifications.map((notification) => (
                    <div
                      key={notification.notification_id}
                      className={`
                        p-3 border-l-4 rounded cursor-pointer transition
                        ${getPriorityColor(notification.priority)}
                        ${notification.read_at ? 'opacity-60' : 'font-medium'}
                      `}
                      onClick={() => {
                        if (!notification.read_at) {
                          markAsRead(notification.notification_id);
                        }
                        if (notification.action_url) {
                          window.location.href = notification.action_url;
                        }
                      }}
                    >
                      <div className="flex items-start gap-3">
                        {getNotificationIcon(notification.notification_type)}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <Badge variant="outline" className="text-xs mb-1">
                              {notification.notification_type.replace('_', ' ')}
                            </Badge>
                            <span className="text-xs text-gray-500">
                              {formatTime(notification.sent_at)}
                            </span>
                          </div>
                          <p className="text-sm text-gray-800 whitespace-pre-wrap break-words">
                            {notification.message}
                          </p>
                          {notification.action_url && (
                            <Button
                              variant="link"
                              size="sm"
                              className="text-xs p-0 h-auto mt-2"
                            >
                              View Details →
                            </Button>
                          )}
                        </div>
                        {!notification.read_at && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-1" />
                        )}
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </ScrollArea>
          </Card>
        </div>
      )}
      
      {/* Backdrop */}
      {showPanel && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowPanel(false)}
        />
      )}
    </>
  );
}
