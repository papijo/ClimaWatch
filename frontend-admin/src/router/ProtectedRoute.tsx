import { Navigate, Outlet } from 'react-router-dom'
import { getToken, isAdmin } from '../lib/auth'

export default function ProtectedRoute() {
  if (!getToken() || !isAdmin()) {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}
