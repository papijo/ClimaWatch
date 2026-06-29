"use client";

import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { RISK_HEX } from "@/lib/risk";
import type { StateItem } from "@/lib/api";

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN ?? "";

const NIGERIA_CENTER: [number, number] = [8.6753, 9.082];
const NIGERIA_ZOOM = 5.5;

interface MapProps {
  className?: string;
  states?: StateItem[];
  onStateClick?: (stateId: string) => void;
}

export default function Map({ className = "w-full h-[600px]", states, onStateClick }: MapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/light-v11",
      center: NIGERIA_CENTER,
      zoom: NIGERIA_ZOOM,
    });

    map.addControl(new mapboxgl.NavigationControl(), "top-right");
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !states?.length) return;

    states.forEach((state) => {
      const color = RISK_HEX[state.current_risk_level] ?? RISK_HEX.LOW;

      const marker = new mapboxgl.Marker({ color })
        .setLngLat([state.longitude, state.latitude])
        .setPopup(
          new mapboxgl.Popup({ offset: 25 }).setHTML(
            `<div style="font-family:sans-serif"><strong>${state.name}</strong><br/><span style="color:${color}">${state.current_risk_level}</span></div>`
          )
        )
        .addTo(map);

      marker.getElement().addEventListener("click", () => {
        onStateClick?.(state.id);
      });
    });
  }, [states, onStateClick]);

  return <div ref={containerRef} className={className} />;
}
