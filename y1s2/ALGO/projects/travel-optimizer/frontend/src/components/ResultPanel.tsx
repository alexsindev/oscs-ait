import { useState } from 'react';
import {
  ChevronDown, ChevronRight, ExternalLink, Navigation,
  Landmark, UtensilsCrossed, Building2, Trees, ShoppingBag, Music, MapPin,
} from 'lucide-react';
import type { Itinerary, Visit } from '../types';
import { DAY_COLORS } from './MapView';

interface Props {
  itinerary: Itinerary;
  hotelLat: number;
  hotelLng: number;
  activeDayIndex: number | null;
  onDayClick: (index: number | null) => void;
  onVisitClick: (lat: number, lng: number) => void;
}

// ── Category icons ─────────────────────────────────────────────────────────────

const CATEGORY_ICON: Record<string, React.ReactNode> = {
  Museum:        <Landmark size={12} />,
  Restaurant:    <UtensilsCrossed size={12} />,
  Landmark:      <Building2 size={12} />,
  Park:          <Trees size={12} />,
  Shopping:      <ShoppingBag size={12} />,
  Entertainment: <Music size={12} />,
};

function CategoryIcon({ category }: { category: string }) {
  return <span style={{ opacity: 0.7, display: 'flex', alignItems: 'center' }}>{CATEGORY_ICON[category] ?? <MapPin size={12} />}</span>;
}

// ── Google Maps URL builders ──────────────────────────────────────────────────

function visitMapsUrl(lat: number, lng: number, name: string): string {
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(name)}&query=${lat},${lng}`;
}

function dayRouteUrl(hotelLat: number, hotelLng: number, visits: Visit[]): string {
  if (visits.length === 0) return '';
  const origin = `${hotelLat},${hotelLng}`;
  const last = visits[visits.length - 1];
  const dest = `${last.lat},${last.lng}`;
  const midpoints = visits.slice(0, -1).slice(0, 8);
  let url =
    `https://www.google.com/maps/dir/?api=1` +
    `&origin=${origin}` +
    `&destination=${dest}` +
    `&travelmode=walking`;
  if (midpoints.length > 0)
    url += `&waypoints=${midpoints.map(v => `${v.lat},${v.lng}`).join('|')}`;
  return url;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function fmtTime(mins: number): string {
  const h = Math.floor(mins / 60) % 24;
  const m = mins % 60;
  const period = h >= 12 ? 'PM' : 'AM';
  const displayH = h === 0 ? 12 : h > 12 ? h - 12 : h;
  return `${displayH}:${String(m).padStart(2, '0')} ${period}`;
}

function fmtDuration(mins: number): string {
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function ResultPanel({
  itinerary, hotelLat, hotelLng, activeDayIndex, onDayClick, onVisitClick,
}: Props) {
  const [expandedDays, setExpandedDays] = useState<Set<number>>(new Set());

  function toggleCollapse(di: number) {
    setExpandedDays(prev => {
      const next = new Set(prev);
      if (next.has(di)) next.delete(di); else next.add(di);
      return next;
    });
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

      {/* Summary cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 8, textAlign: 'center' }}>
        {[
          { label: 'Attractions', value: itinerary.total_attractions },
          { label: 'Total Cost',  value: `$${itinerary.total_cost.toFixed(2)}` },
          { label: 'Satisfaction', value: itinerary.total_satisfaction.toFixed(2) },
        ].map(({ label, value }) => (
          <div key={label} style={{
            background: 'var(--bg-4)', border: '1px solid var(--border)', borderRadius: 8, padding: '8px 4px',
          }}>
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-1)' }}>{value}</div>
            <div style={{ fontSize: 11, color: 'var(--text-4)', marginTop: 2 }}>{label}</div>
          </div>
        ))}
      </div>

      <div style={{ fontSize: 11, color: 'var(--text-3)', textAlign: 'right' }}>
        {itinerary.algorithm.toUpperCase()} · {itinerary.computation_ms.toFixed(0)} ms ·{' '}
        <span style={{ color: 'var(--text-4)' }}>click day to highlight · click stop to zoom</span>
      </div>

      {/* Day cards */}
      {itinerary.days.map((day, di) => {
        const color = DAY_COLORS[di % DAY_COLORS.length];
        const isActive = activeDayIndex === di;
        const isCollapsed = !expandedDays.has(di);
        const mapsUrl = dayRouteUrl(hotelLat, hotelLng, day.visits);

        return (
          <div key={day.day} style={{
            border: `1.5px solid ${isActive ? color : color + '30'}`,
            borderRadius: 10, overflow: 'hidden', transition: 'border-color .2s',
          }}>

            {/* Header row 1 — title + Maps route */}
            <div style={{
              background: isActive ? color : color + 'cc',
              color: 'white', padding: '7px 12px',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8,
            }}>
              <span
                onClick={() => { toggleCollapse(di); onDayClick(isActive ? null : di); }}
                style={{ fontWeight: 700, fontSize: 13, cursor: 'pointer', userSelect: 'none', display: 'flex', alignItems: 'center', gap: 6, flex: 1 }}
              >
                {isCollapsed
                  ? <ChevronRight size={14} strokeWidth={2.5} />
                  : <ChevronDown size={14} strokeWidth={2.5} />}
                Day {day.day}
              </span>

              {mapsUrl && (
                <a
                  href={mapsUrl} target="_blank" rel="noopener noreferrer"
                  onClick={e => e.stopPropagation()}
                  title="Open full day route in Google Maps"
                  style={{
                    display: 'inline-flex', alignItems: 'center', gap: 4,
                    background: 'rgba(255,255,255,0.2)', border: '1px solid rgba(255,255,255,0.4)',
                    borderRadius: 6, padding: '3px 8px', fontSize: 11, fontWeight: 600,
                    color: 'white', textDecoration: 'none', flexShrink: 0, transition: 'background .15s',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.35)')}
                  onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.2)')}
                >
                  <Navigation size={11} /> Route
                </a>
              )}
            </div>

            {/* Header row 2 — stats */}
            <div
              onClick={() => { toggleCollapse(di); onDayClick(isActive ? null : di); }}
              style={{
                background: isActive ? color + 'dd' : color + 'aa',
                color: 'white', padding: '4px 12px',
                fontSize: 11, cursor: 'pointer',
              }}
            >
              {day.visits.length} stops · ${day.total_cost.toFixed(2)} · {fmtDuration(day.total_travel_time)} travel
            </div>

            {/* Visits */}
            {!isCollapsed && (day.visits.length === 0 ? (
              <div style={{ padding: '10px 12px', color: 'var(--text-4)', fontSize: 12 }}>No visits scheduled</div>
            ) : (
              day.visits.map((v, vi) => (
                <div
                  key={vi}
                  style={{
                    display: 'flex', alignItems: 'flex-start', gap: 10,
                    padding: '8px 12px', cursor: 'pointer',
                    borderBottom: vi < day.visits.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                    transition: 'background .1s',
                  }}
                  onClick={() => onVisitClick(v.lat, v.lng)}
                  onMouseEnter={e => (e.currentTarget.style.background = 'var(--bg-5)')}
                  onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                >
                  {/* Number badge */}
                  <div style={{
                    width: 22, height: 22, flexShrink: 0, background: color,
                    borderRadius: '50%', display: 'flex', alignItems: 'center',
                    justifyContent: 'center', color: 'white', fontSize: 11, fontWeight: 700, marginTop: 1,
                  }}>
                    {vi + 1}
                  </div>

                  {/* Name + time */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontSize: 13, fontWeight: 600, color: 'var(--text-1)',
                      whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                      display: 'flex', alignItems: 'center', gap: 5,
                    }}>
                      <CategoryIcon category={v.category} />
                      {v.name}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 2 }}>
                      {fmtTime(v.arrival_time)} – {fmtTime(v.departure_time)}
                      {v.fee > 0 && <span> · ${v.fee.toFixed(2)}</span>}
                    </div>
                  </div>

                  {/* Preference + Maps link */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4, flexShrink: 0 }}>
                    <span style={{ fontSize: 11, color: 'var(--text-3)' }}>
                      {(v.preference * 100).toFixed(0)}%
                    </span>
                    <a
                      href={visitMapsUrl(v.lat, v.lng, v.name)}
                      target="_blank" rel="noopener noreferrer"
                      onClick={e => e.stopPropagation()}
                      title={`Open ${v.name} in Google Maps`}
                      style={{
                        display: 'inline-flex', alignItems: 'center', gap: 3,
                        fontSize: 10, color: '#4285F4', textDecoration: 'none',
                        fontWeight: 600, padding: '2px 5px',
                        border: '1px solid #4285F440', borderRadius: 4,
                        transition: 'background .1s',
                      }}
                      onMouseEnter={e => (e.currentTarget.style.background = '#4285F415')}
                      onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                    >
                      <ExternalLink size={10} /> Maps
                    </a>
                  </div>
                </div>
              ))
            ))}
          </div>
        );
      })}
    </div>
  );
}
