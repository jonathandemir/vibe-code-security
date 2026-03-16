import React from 'react'
import { Auth } from '@supabase/auth-ui-react'
import { ThemeSupa } from '@supabase/auth-ui-shared'
import { supabase } from '../lib/supabase'

/**
 * VouchAuthView — the login/signup screen.
 * Shown when the user is not authenticated (e.g. on the /dashboard page).
 */
export default function VouchAuthView() {
  return (
    <div className="min-h-screen bg-[#0A0A14] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-[#7B61FF]/10 border border-[#7B61FF]/20 mb-4 mx-auto">
            <svg className="w-7 h-7 text-[#7B61FF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-[#F0EFF4]">Welcome to Vouch</h1>
          <p className="text-neutral-400 mt-2 text-sm">The Stripe for App-Security. Sign in to start scanning.</p>
        </div>

        {/* Supabase Auth UI */}
        <div className="glass-panel p-6 rounded-2xl border border-white/5">
          <Auth
            supabaseClient={supabase}
            appearance={{
              theme: ThemeSupa,
              variables: {
                default: {
                  colors: {
                    brand: '#7B61FF',
                    brandAccent: '#6A50E0',
                    brandButtonText: 'white',
                    defaultButtonBackground: '#1A1A2E',
                    defaultButtonBackgroundHover: '#252539',
                    defaultButtonBorder: 'rgba(255,255,255,0.08)',
                    defaultButtonText: '#F0EFF4',
                    dividerBackground: 'rgba(255,255,255,0.08)',
                    inputBackground: '#0A0A14',
                    inputBorder: 'rgba(255,255,255,0.08)',
                    inputBorderHover: '#7B61FF',
                    inputBorderFocus: '#7B61FF',
                    inputText: '#F0EFF4',
                    inputLabelText: '#9CA3AF',
                    inputPlaceholder: '#4B5563',
                    messageText: '#F0EFF4',
                    messageTextDanger: '#F87171',
                    anchorTextColor: '#7B61FF',
                    anchorTextHoverColor: '#6A50E0',
                  },
                  radii: {
                    borderRadiusButton: '0.75rem',
                    buttonBorderRadius: '0.75rem',
                    inputBorderRadius: '0.75rem',
                  },
                  fonts: {
                    bodyFontFamily: `'Inter', sans-serif`,
                    buttonFontFamily: `'Inter', sans-serif`,
                    inputFontFamily: `'Inter', sans-serif`,
                    labelFontFamily: `'Inter', sans-serif`,
                  },
                },
              },
            }}
            providers={['github', 'google']}
            redirectTo={`${window.location.origin}/dashboard`}
          />
        </div>

        <p className="text-center text-xs text-neutral-600 mt-6">
          By signing up, you agree to our <a href="/legal" className="text-[#7B61FF]/70 hover:text-[#7B61FF]">Terms of Service</a>.
        </p>
      </div>
    </div>
  )
}
