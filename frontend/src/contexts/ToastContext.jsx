import React, { createContext, useContext, useState, useCallback } from 'react';

const ToastContext = createContext(null);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((type, title, message) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const success = useCallback((title, message) => addToast('success', title, message), [addToast]);
  const warning = useCallback((title, message) => addToast('warning', title, message), [addToast]);
  const danger = useCallback((title, message) => addToast('danger', title, message), [addToast]);
  const info = useCallback((title, message) => addToast('info', title, message), [addToast]);

  return (
    <ToastContext.Provider value={{ success, warning, danger, info, toasts }}>
      {children}
    </ToastContext.Provider>
  );
};

export const useToast = () => useContext(ToastContext);
export default ToastContext;
