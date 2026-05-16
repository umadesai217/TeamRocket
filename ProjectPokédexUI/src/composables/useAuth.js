import { supabase } from '../lib/supabase.js'
import { useAppState } from './useAppState.js'
import { useLibraryStore } from './useLibraryStore.js'

export function useAuth() {
  const { setScreen, currentUser, activeScreen, resetButtons } = useAppState()
  const { loadLibrary, loadScans, loadSetsCatalog } = useLibraryStore()

  function loadUserData() {
    loadLibrary()
    loadScans()
    loadSetsCatalog()
  }

  // ---Check for an existing session on app load---
  async function checkSession() {
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.user) {
      currentUser.value = session.user
      setScreen(null)
      loadUserData()
    } else {
      // ---Show welcome screen first, then slide into login---
      setScreen('welcome')
      setTimeout(() => {
        if (activeScreen.value === 'welcome') setScreen('login')
      }, 2500)
    }
  }

  // ---Boot sequence: shown after a fresh login---
  function _bootSequence(user) {
    currentUser.value = user   // triggers app brightening transition immediately
    setScreen('booting')
    loadUserData()
    setTimeout(() => {
      if (activeScreen.value === 'booting') setScreen('default')
    }, 2000)
  }

  // ---Sign in with email + password----
  async function login(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
    _bootSequence(data.user)
  }

  // ---Create a new account---
  // NOTE: disable "Enable email confirmations" in Supabase Auth settings so
  // the user is logged in immediately after signup without an email click.
  async function signup(email, password) {
    const { data, error } = await supabase.auth.signUp({ email, password })
    if (error) throw error
    if (data.session) {
      _bootSequence(data.user)
    }
    return data
  }

  // ---Sign out (instant)---
  async function logout() {
    await supabase.auth.signOut()
    currentUser.value = null
    setScreen('login')
  }

  // ---Boot-down sequence: dims app first, then enters login---
  async function bootDown() {
    resetButtons()                    // deactivate all buttons before dimming
    await supabase.auth.signOut()
    setScreen('default')                   // clear screen during the dim transition
    currentUser.value = null          // triggers 2s dim CSS transition immediately
    setTimeout(() => {
      if (!currentUser.value) setScreen('login')
    }, 2000)
  }

  return { checkSession, login, signup, logout, bootDown }
}
