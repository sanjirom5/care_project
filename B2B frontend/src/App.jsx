import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";
import TopBar from "./components/TopBar";
import AuthWatcher from "./components/AuthWatcher";

import LoginPage    from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import Dashboard    from "./pages/Dashboard";
import Products     from "./pages/Products";
import Orders       from "./pages/Orders";
import OrderDetails from "./pages/OrderDetails";
import Chat         from "./pages/Chat";
import ProfilePage  from "./pages/ProfilePage";
import AboutPage    from "./pages/AboutPage";

function Layout({ children }) {
  return (
    <div className="app-layout">
      <TopBar />
      <main className="main-content">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AuthWatcher />
        <Routes>
          {/* Auth pages — no topbar */}
          <Route path="/"         element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* App pages — with topbar */}
          <Route path="/dashboard"    element={<Layout><Dashboard /></Layout>} />
          <Route path="/products"     element={<Layout><Products /></Layout>} />
          <Route path="/orders"       element={<Layout><Orders /></Layout>} />
          <Route path="/orders/:id"   element={<Layout><OrderDetails /></Layout>} />
          <Route path="/chat"         element={<Layout><Chat /></Layout>} />
          <Route path="/profile"      element={<Layout><ProfilePage /></Layout>} />
          <Route path="/about"        element={<Layout><AboutPage /></Layout>} />

          {/* Fallback */}
          <Route path="*" element={<LoginPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
