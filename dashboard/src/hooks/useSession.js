import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

/**
 * useSession — the single source of truth for the auth state.
 * Listens to Supabase's auth state changes and returns the current session.
 */
export function useSession() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 1. Get the initial session on mount
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setLoading(false)
    })

    // 2. Subscribe to auth changes (login, logout, token refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session)
        setLoading(false)
      }
    )

    // Cleanup on unmount
    return () => subscription.unsubscribe()
  }, [])

  return { session, loading }
}
