import { useEffect, useRef } from 'react';
import {
  MapContainer, TileLayer, Marker, Popup, Polyline,
  useMap, useMapEvents, ScaleControl,
} from 'react-leaflet';
import L from 'leaflet';
import type { Itinerary, DayPlan } from '../types';
import 'leaflet/dist/leaflet.css';

// ── Constants ─────────────────────────────────────────────────────────────────

export const DAY_COLORS = [
  '#2563EB', '#059669', '#D97706', '#DC2626',
  '#7C3AED', '#DB2777', '#0891B2',
];

// Category initial letters for ghost pins
const CATEGORY_LETTER: Record<string, string> = {
  Museum: 'M', Restaurant: 'R', Landmark: 'L',
  Park: 'P', Shopping: 'S', Entertainment: 'E',
};

// ── Icon factories ─────────────────────────────────────────────────────────────

function makeNumberedIcon(num: number, color: string, opacity = 1) {
  return L.divIcon({
    className: '',
    html: `<div style="
      width:30px;height:30px;background:${color};
      border:2.5px solid white;border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      color:white;font-weight:700;font-size:12px;
      box-shadow:0 2px 6px rgba(0,0,0,0.35);font-family:sans-serif;
      opacity:${opacity};transition:opacity .2s;
    ">${num}</div>`,
    iconSize: [30, 30], iconAnchor: [15, 15],
  });
}

function makeHotelIcon(dragging = false) {
  // Inline SVG bed icon — no emoji, crisp at all DPIs
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M2 20v-8a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v8"/>
    <path d="M4 10V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4"/>
    <path d="M12 10v4"/><path d="M2 18h20"/>
  </svg>`;
  return L.divIcon({
    className: '',
    html: `<div style="
      width:38px;height:38px;background:#1e293b;
      border:3px solid white;border-radius:10px;
      display:flex;align-items:center;justify-content:center;
      box-shadow:0 3px 8px rgba(0,0,0,0.45);
      cursor:${dragging ? 'grabbing' : 'grab'};
    ">${svg}</div>`,
    iconSize: [38, 38], iconAnchor: [19, 19],
  });
}

// ── Auto-resize: calls invalidateSize whenever the map container resizes ──────

function MapResizer() {
  const map = useMap();
  useEffect(() => {
    const container = map.getContainer();
    const observer = new ResizeObserver(() => map.invalidateSize());
    observer.observe(container);
    return () => observer.disconnect();
  }, [map]);
  return null;
}

// ── Inner map components (must live inside MapContainer) ──────────────────────

interface ControllerProps {
  hotelLat: number; hotelLng: number;
  isPickingHotel: boolean;
  onHotelPick: (lat: number, lng: number) => void;
}
function MapController({ hotelLat, hotelLng, isPickingHotel, onHotelPick }: ControllerProps) {
  const map = useMap();
  useEffect(() => { map.setView([hotelLat, hotelLng], map.getZoom()); }, [hotelLat, hotelLng]);
  useMapEvents({ click(e) { if (isPickingHotel) onHotelPick(e.latlng.lat, e.latlng.lng); } });
  return null;
}

function FitBounds({ itinerary, hotelLat, hotelLng }: { itinerary: Itinerary | null; hotelLat: number; hotelLng: number }) {
  const map = useMap();
  const prevRef = useRef<string>('');
  useEffect(() => {
    if (!itinerary) return;
    const key = JSON.stringify(itinerary.days.map(d => d.visits.length));
    if (key === prevRef.current) return;
    prevRef.current = key;
    const pts: [number, number][] = [
      [hotelLat, hotelLng],
      ...itinerary.days.flatMap(d => d.visits.map(v => [v.lat, v.lng] as [number, number])),
    ];
    if (pts.length > 1) map.fitBounds(pts, { padding: [50, 50], maxZoom: 14 });
  }, [itinerary]);
  return null;
}

function FocusPoint({ point }: { point: { lat: number; lng: number; zoom?: number } | null }) {
  const map = useMap();
  useEffect(() => {
    if (point) map.setView([point.lat, point.lng], point.zoom ?? 16, { animate: true });
  }, [point]);
  return null;
}

// ── Legend overlay ────────────────────────────────────────────────────────────

function Legend({ itinerary }: { itinerary: Itinerary | null }) {
  if (!itinerary || itinerary.days.every(d => d.visits.length === 0)) return null;
  return (
    <div style={{
      position: 'absolute', bottom: 28, right: 10, zIndex: 1000,
      background: 'rgba(11,18,33,0.88)', backdropFilter: 'blur(6px)',
      border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: 8, padding: '8px 10px',
      boxShadow: '0 4px 16px rgba(0,0,0,0.5)', fontSize: 12,
      display: 'flex', flexDirection: 'column', gap: 4,
    }}>
      {itinerary.days.filter(d => d.visits.length > 0).map((d, di) => (
        <div key={d.day} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{
            width: 12, height: 12, borderRadius: '50%',
            background: DAY_COLORS[di % DAY_COLORS.length], flexShrink: 0,
          }} />
          <span style={{ color: '#f1f5f9', fontWeight: 500 }}>Day {d.day}</span>
          <span style={{ color: '#94a3b8' }}>· {d.visits.length} stops</span>
        </div>
      ))}
    </div>
  );
}

// ── Main MapView ───────────────────────────────────────────────────────────────

export interface AttractionPin {
  id: number; lat: number; lng: number; name: string; category: string;
}

interface Props {
  hotelLat: number; hotelLng: number;
  itinerary: Itinerary | null;
  attractions: AttractionPin[];
  isPickingHotel: boolean;
  onHotelPick: (lat: number, lng: number) => void;
  activeDayIndex: number | null;
  focusPoint: { lat: number; lng: number; zoom?: number } | null;
}

export default function MapView({
  hotelLat, hotelLng, itinerary, attractions,
  isPickingHotel, onHotelPick, activeDayIndex, focusPoint,
}: Props) {
  const visitedIds = new Set(itinerary?.days.flatMap(d => d.visits.map(v => v.attraction_id)));

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      {isPickingHotel && (
        <div style={{
          position: 'absolute', top: 12, left: '50%', transform: 'translateX(-50%)',
          zIndex: 1000, background: 'rgba(11,18,33,0.92)', backdropFilter: 'blur(6px)',
          border: '1px solid rgba(255,255,255,0.12)', color: '#f1f5f9',
          padding: '8px 18px', borderRadius: 8, fontSize: 14, fontWeight: 600,
          boxShadow: '0 4px 16px rgba(0,0,0,0.5)', pointerEvents: 'none',
        }}>
          📍 Click on the map to set hotel location
        </div>
      )}

      <Legend itinerary={itinerary} />

      <MapContainer
        center={[hotelLat, hotelLng]}
        zoom={13}
        style={{ width: '100%', height: '100%' }}
      >
        {/* Esri World Imagery — satellite base */}
        <TileLayer
          attribution='Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community'
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          maxZoom={19}
        />
        {/* Esri English label overlay — stays English at all zoom levels */}
        <TileLayer
          attribution=""
          url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
          maxZoom={19}
          opacity={0.9}
        />
        <ScaleControl position="bottomleft" />

        <MapResizer />
        <MapController hotelLat={hotelLat} hotelLng={hotelLng} isPickingHotel={isPickingHotel} onHotelPick={onHotelPick} />
        <FitBounds itinerary={itinerary} hotelLat={hotelLat} hotelLng={hotelLng} />
        <FocusPoint point={focusPoint} />

        {/* Draggable hotel marker */}
        <Marker
          position={[hotelLat, hotelLng]}
          icon={makeHotelIcon()}
          draggable
          eventHandlers={{ dragend(e) { const { lat, lng } = e.target.getLatLng(); onHotelPick(lat, lng); } }}
        >
          <Popup>
            <strong>🏨 Hotel</strong><br />
            <span style={{ color: '#94a3b8', fontSize: 12 }}>
              {hotelLat.toFixed(5)}, {hotelLng.toFixed(5)}<br />
              Drag to reposition
            </span>
          </Popup>
        </Marker>

        {/* Unvisited ghost pins */}
        {itinerary && attractions.filter(a => !visitedIds.has(a.id)).map(a => (
          <Marker
            key={`ghost-${a.id}`}
            position={[a.lat, a.lng]}
            icon={L.divIcon({
              className: '',
              html: `<div style="
                width:18px;height:18px;background:#94a3b8;
                border:2px solid white;border-radius:50%;
                display:flex;align-items:center;justify-content:center;
                font-size:8px;font-weight:700;color:#1e293b;opacity:0.5;
                font-family:sans-serif;
              ">${CATEGORY_LETTER[a.category] ?? '?'}</div>`,
              iconSize: [18, 18], iconAnchor: [9, 9],
            })}
          >
            <Popup>
              <strong>{a.name}</strong><br />
              <span style={{ color: '#94a3b8', fontSize: 12 }}>{a.category} · not scheduled</span>
            </Popup>
          </Marker>
        ))}

        {/* Per-day routes and markers */}
        {itinerary?.days.map((day, di) => {
          const color = DAY_COLORS[di % DAY_COLORS.length];
          const isActive = activeDayIndex === null || activeDayIndex === di;
          const opacity = isActive ? 1 : 0.2;
          const routePts: [number, number][] = [
            [hotelLat, hotelLng],
            ...day.visits.map(v => [v.lat, v.lng] as [number, number]),
          ];

          return (
            <span key={`day-${day.day}`}>
              <Polyline
                positions={routePts}
                pathOptions={{ color, weight: 3, opacity: isActive ? 0.8 : 0.1, dashArray: '7 5' }}
              />
              {day.visits.map((v, vi) => (
                <Marker
                  key={`v-${day.day}-${vi}`}
                  position={[v.lat, v.lng]}
                  icon={makeNumberedIcon(vi + 1, color, opacity)}
                >
                  <Popup>
                    <div style={{ minWidth: 200 }}>
                      <div style={{
                        background: color, color: 'white',
                        borderRadius: '6px 6px 0 0',
                        margin: '-8px -8px 8px', padding: '6px 10px',
                        fontWeight: 700,
                      }}>
                        Day {day.day} · Stop {vi + 1}
                      </div>
                      <strong>{v.name}</strong><br />
                      <span style={{ color: '#94a3b8', fontSize: 12 }}>{v.category}</span><br />
                      <span style={{ fontSize: 12 }}>
                        {fmtTime(v.arrival_time)} → {fmtTime(v.departure_time)}
                      </span><br />
                      <span style={{ fontSize: 12 }}>
                        Fee: ${v.fee.toFixed(2)} · Preference: {(v.preference * 100).toFixed(0)}%
                      </span>
                      <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                        <a
                          href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(v.name)}&query=${v.lat},${v.lng}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: 'inline-flex', alignItems: 'center', gap: 5,
                            fontSize: 12, color: '#4285F4', fontWeight: 600,
                            textDecoration: 'none',
                          }}
                        >
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="#4285F4">
                            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
                            <circle cx="12" cy="9" r="2.5" fill="white"/>
                          </svg>
                          Open in Google Maps ↗
                        </a>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </span>
          );
        })}
      </MapContainer>
    </div>
  );
}

function fmtTime(mins: number): string {
  const h = Math.floor(mins / 60) % 24;
  const m = mins % 60;
  const period = h >= 12 ? 'PM' : 'AM';
  const displayH = h === 0 ? 12 : h > 12 ? h - 12 : h;
  return `${displayH}:${String(m).padStart(2, '0')} ${period}`;
}
