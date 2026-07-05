import { useEffect, useRef } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import type { StateItem } from '../lib/api'

const RISK_HEX: Record<string, string> = {
  LOW: '#22c55e',
  MODERATE: '#eab308',
  HIGH: '#f97316',
  CRITICAL: '#ef4444',
  UNKNOWN: '#6b7280',
}

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN ?? ''
if (MAPBOX_TOKEN) {
  mapboxgl.accessToken = MAPBOX_TOKEN
}

const NIGERIA_CENTER: [number, number] = [8.6753, 9.082]

interface Props {
  states: StateItem[]
  onStateClick: (state: StateItem) => void
  className?: string
}

export default function AdminMap({ states, onStateClick, className = '' }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<mapboxgl.Map | null>(null)
  const markersRef = useRef<mapboxgl.Marker[]>([])
  const onClickRef = useRef(onStateClick)

  useEffect(() => {
    onClickRef.current = onStateClick
  }, [onStateClick])

  useEffect(() => {
    if (!containerRef.current || mapRef.current || !MAPBOX_TOKEN) return
    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: NIGERIA_CENTER,
      zoom: 5.1,
      attributionControl: false,
    })
    map.addControl(new mapboxgl.NavigationControl({ showCompass: false }), 'top-right')
    mapRef.current = map
    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !states.length) return

    markersRef.current.forEach((m) => m.remove())
    markersRef.current = []

    const addMarkers = () => {
      states.forEach((state) => {
        if (!state.latitude || !state.longitude) return
        const color = RISK_HEX[state.current_risk_level] ?? RISK_HEX.UNKNOWN

        const el = document.createElement('div')
        el.style.cssText = [
          'width:11px',
          'height:11px',
          'border-radius:50%',
          `background:${color}`,
          'border:2px solid rgba(255,255,255,0.2)',
          `box-shadow:0 0 10px ${color}60`,
          'cursor:pointer',
          'transition:transform 0.1s',
        ].join(';')
        el.addEventListener('mouseenter', () => { el.style.transform = 'scale(1.5)' })
        el.addEventListener('mouseleave', () => { el.style.transform = 'scale(1)' })
        el.addEventListener('click', () => onClickRef.current(state))

        const marker = new mapboxgl.Marker({ element: el })
          .setLngLat([state.longitude, state.latitude])
          .setPopup(
            new mapboxgl.Popup({ offset: 14, closeButton: false })
              .setHTML(
                `<div style="font-family:system-ui,sans-serif;padding:2px 0">
                  <strong style="font-size:13px">${state.name}</strong>
                  <br/>
                  <span style="color:${color};font-size:11px;font-weight:600">${state.current_risk_level}</span>
                </div>`
              )
          )
          .addTo(map)

        markersRef.current.push(marker)
      })
    }

    if (map.loaded()) {
      addMarkers()
    } else {
      map.once('load', addMarkers)
    }

    return () => {
      markersRef.current.forEach((m) => m.remove())
      markersRef.current = []
    }
  }, [states])

  if (!MAPBOX_TOKEN) {
    return (
      <div className={`flex items-center justify-center bg-zinc-800/50 text-zinc-500 text-sm ${className}`}>
        Add VITE_MAPBOX_TOKEN to enable the map
      </div>
    )
  }

  return <div ref={containerRef} className={className} />
}
