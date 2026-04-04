import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation, Navigate } from "react-router-dom";
import LoginPage from "@/pages/LoginPage";
import SetupPage from "@/pages/SetupPage";
import AuthCallback from "@/pages/AuthCallback";
import OMDashboard from "@/pages/OMDashboard";
import OpenClawInfo from "@/pages/OpenClawInfo";
import OpenClawControlUI from "@/pages/OpenClawControlUI";
import OpenClawChat from "@/pages/OpenClawChat";
import OpenClawLogs from "@/pages/OpenClawLogs";
import OpenClawAutonomous from "@/pages/OpenClawAutonomous";
import OpenClawDashboard from "@/pages/OpenClawDashboard";
import OpenClawTUI from "@/pages/OpenClawTUI";
import OpenClawSettings from "@/pages/OpenClawSettings";
import CreatorHub from "@/pages/CreatorHub";
import HybridIntegrationsHub from "@/pages/HybridIntegrationsHub";
import { Toaster } from "@/components/ui/sonner";
import { NotificationProvider } from "@/components/NotificationSystem";

// REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH

function AppRouter() {
  const location = useLocation();
  
  // Check URL fragment (not query params) for session_id - MUST be synchronous
  // This runs BEFORE ProtectedRoute to prevent race conditions
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }
  
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<SetupPage />} />
      <Route path="/dashboard" element={<OpenClawDashboard />} />
      <Route path="/maintenance" element={<OMDashboard />} />
      <Route path="/creator-hub" element={<CreatorHub />} />
      <Route path="/hybrid-ai" element={<HybridIntegrationsHub />} />
      <Route path="/openclaw-info" element={<OpenClawInfo />} />
      <Route path="/openclaw-control" element={<OpenClawControlUI />} />
      <Route path="/openclaw-chat" element={<OpenClawChat />} />
      <Route path="/openclaw-logs" element={<OpenClawLogs />} />
      <Route path="/openclaw-autonomous" element={<OpenClawAutonomous />} />
      <Route path="/openclaw-tui" element={<OpenClawTUI />} />
      <Route path="/openclaw-settings" element={<OpenClawSettings />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <NotificationProvider>
      <div className="App dark">
        <Toaster data-testid="global-toaster" richColors position="top-center" />
        <BrowserRouter>
          <AppRouter />
        </BrowserRouter>
      </div>
    </NotificationProvider>
  );
}

export default App;
