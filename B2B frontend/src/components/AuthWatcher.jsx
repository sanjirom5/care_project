import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const PROTECTED = ["/dashboard", "/products", "/orders", "/chat", "/profile"];

export default function AuthWatcher() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();

  useEffect(() => {
    const isProtected = PROTECTED.some(p => pathname === p || pathname.startsWith(p + "/"));
    if (isProtected && !token) navigate("/", { replace: true });
  }, [token, pathname, navigate]);

  return null;
}
