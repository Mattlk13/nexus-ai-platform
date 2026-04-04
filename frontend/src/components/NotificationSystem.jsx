import React, { createContext, useContext, useState, useCallback } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { CheckCircle, XCircle, AlertTriangle, Info, Zap } from 'lucide-react';

const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  const notify = useCallback((notification) => {
    const { level, title, message, duration = 4000 } = notification;
    
    // Add to notifications list
    const newNotification = {
      id: Date.now(),
      level,
      title,
      message,
      timestamp: new Date().toISOString()
    };
    
    setNotifications(prev => [newNotification, ...prev].slice(0, 50)); // Keep last 50
    
    // Show toast
    const toastConfig = {
      duration,
      style: {
        background: getBackgroundColor(level),
        color: '#fff',
        borderRadius: '12px',
        padding: '16px',
        maxWidth: '500px'
      }
    };
    
    const icon = getIcon(level);
    
    toast.custom(
      (t) => (
        <div
          className={`${
            t.visible ? 'animate-enter' : 'animate-leave'
          } max-w-md w-full bg-slate-800 shadow-lg rounded-lg pointer-events-auto flex ring-1 ring-black ring-opacity-5`}
        >
          <div className="flex-1 w-0 p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                {icon}
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-white">
                  {title}
                </p>
                <p className="mt-1 text-sm text-slate-300">
                  {message}
                </p>
              </div>
            </div>
          </div>
          <div className="flex border-l border-slate-700">
            <button
              onClick={() => toast.dismiss(t.id)}
              className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-slate-400 hover:text-white focus:outline-none"
            >
              Close
            </button>
          </div>
        </div>
      ),
      toastConfig
    );
  }, []);

  const success = useCallback((title, message) => {
    notify({ level: 'success', title, message });
  }, [notify]);

  const error = useCallback((title, message) => {
    notify({ level: 'error', title, message });
  }, [notify]);

  const warning = useCallback((title, message) => {
    notify({ level: 'warning', title, message });
  }, [notify]);

  const info = useCallback((title, message) => {
    notify({ level: 'info', title, message });
  }, [notify]);

  const clearAll = useCallback(() => {
    setNotifications([]);
    toast.dismiss();
  }, []);

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        notify,
        success,
        error,
        warning,
        info,
        clearAll
      }}
    >
      {children}
      <Toaster
        position="top-right"
        toastOptions={{
          className: '',
          style: {
            background: '#1e293b',
            color: '#fff',
          },
        }}
      />
    </NotificationContext.Provider>
  );
};

// Helper functions
const getBackgroundColor = (level) => {
  switch (level) {
    case 'success':
      return 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
    case 'error':
      return 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
    case 'warning':
      return 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
    case 'info':
      return 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
    default:
      return 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)';
  }
};

const getIcon = (level) => {
  const className = "w-6 h-6";
  
  switch (level) {
    case 'success':
      return <CheckCircle className={`${className} text-green-400`} />;
    case 'error':
      return <XCircle className={`${className} text-red-400`} />;
    case 'warning':
      return <AlertTriangle className={`${className} text-yellow-400`} />;
    case 'info':
      return <Info className={`${className} text-blue-400`} />;
    default:
      return <Zap className={`${className} text-purple-400`} />;
  }
};

export default NotificationProvider;
