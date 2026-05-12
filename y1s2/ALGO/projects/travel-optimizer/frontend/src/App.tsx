import { useState, useEffect, useCallback, useRef } from 'react';
import {
  Map, MapPin, Crosshair, LocateFixed, Layers, Cpu, Zap, Sparkles,
  SlidersHorizontal, Play, BarChart2, X, ChevronLeft, ChevronRight,
  GripHorizontal, DollarSign, Clock, Calendar,
} from 'lucide-react';
import type { Attraction, Itinerary } from './types';
import { fetchDataset, optimize } from './api';
import MapView from './components/MapView';
import ResultPanel from './components/ResultPanel';
import './App.css';

const DATASETS = ['small', 'medium', 'large', 'bangkok_real', 'hard'];

const DATASET_LABELS: Record<string, string> = {
  small: 'Small (15)',
  medium: 'Medium (75)',
  large: 'Large (300)',
  bangkok_real: 'Bangkok Real (150)',
  hard: 'Hard — adversarial (100)',
};

export default function App() {
  // ── Form state ──────────────────────────────────────────────────────────────
  const [hotelLat, setHotelLat] = useState(13.7563);
  const [hotelLng, setHotelLng] = useState(100.5018);
  const [datasetName, setDatasetName] = useState('medium');
  const [algorithm, setAlgorithm] = useState<'greedy' | 'sa'>('sa');
  const [numDays, setNumDays] = useState(2);
  const [dailyTimeBudget, setDailyTimeBudget] = useState(600);
  const [dailyBudget, setDailyBudget] = useState(100);
  const [startTime, setStartTime] = useState(540);
  const [saSeed, setSaSeed] = useState(42);

  // ── Map / result state ──────────────────────────────────────────────────────
  const [attractions, setAttractions] = useState<Attraction[]>([]);
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPickingHotel, setIsPickingHotel] = useState(false);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [gpsError, setGpsError] = useState<string | null>(null);
  const [activeDayIndex, setActiveDayIndex] = useState<number | null>(null);
  const [focusPoint, setFocusPoint] = useState<{ lat: number; lng: number; zoom?: number } | null>(null);

  // ── Sidebar state ───────────────────────────────────────────────────────────
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isDesktop, setIsDesktop] = useState(() => window.innerWidth >= 768);
  const sidebarRef = useRef<HTMLElement>(null);
  const handleRef = useRef<HTMLDivElement>(null);

  // Kept in refs so the imperative touch listeners always see current values
  const sidebarOpenRef = useRef(sidebarOpen);
  useEffect(() => { sidebarOpenRef.current = sidebarOpen; }, [sidebarOpen]);

  // ── Responsive sidebar initialisation ───────────────────────────────────────
  useEffect(() => {
    const mq = window.matchMedia('(min-width: 768px)');
    setSidebarOpen(mq.matches);
    setIsDesktop(mq.matches);
    const handler = (e: MediaQueryListEvent) => {
      setIsDesktop(e.matches);
      setSidebarOpen(e.matches);
    };
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  // ── Load dataset ────────────────────────────────────────────────────────────
  useEffect(() => {
    setItinerary(null);
    fetchDataset(datasetName)
      .then(setAttractions)
      .catch(() => setError(`Could not load dataset "${datasetName}"`));
  }, [datasetName]);

  // ── Handlers ────────────────────────────────────────────────────────────────
  const handleHotelPick = useCallback((lat: number, lng: number) => {
    setHotelLat(lat);
    setHotelLng(lng);
    setIsPickingHotel(false);
  }, []);

  const handleGps = useCallback(() => {
    if (!navigator.geolocation) {
      setGpsError('Geolocation not supported by this browser.');
      return;
    }
    setGpsLoading(true);
    setGpsError(null);
    navigator.geolocation.getCurrentPosition(
      pos => {
        setHotelLat(pos.coords.latitude);
        setHotelLng(pos.coords.longitude);
        setGpsLoading(false);
      },
      err => {
        setGpsError(`GPS error: ${err.message}`);
        setGpsLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }, []);

  const handleOptimize = async () => {
    setLoading(true);
    setError(null);
    setItinerary(null);
    try {
      const result = await optimize({
        dataset_name: datasetName,
        hotel_lat: hotelLat,
        hotel_lng: hotelLng,
        num_days: numDays,
        daily_time_budget: dailyTimeBudget,
        total_budget: dailyBudget * numDays,
        start_time: startTime,
        algorithm,
        sa_seed: saSeed,
      });
      setItinerary(result);
      setActiveDayIndex(null);
      setFocusPoint(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Optimization failed');
    } finally {
      setLoading(false);
    }
  };

  // ── Mobile swipe gesture (imperative, non-passive so Chrome doesn't hijack) ──
  useEffect(() => {
    const handle = handleRef.current;
    const sidebar = sidebarRef.current;
    if (!handle || !sidebar) return;

    let startY = 0;
    let delta = 0;

    function onStart(e: TouchEvent) {
      startY = e.touches[0].clientY;
      delta = 0;
      sidebar!.classList.add('sidebar--dragging');
    }

    function onMove(e: TouchEvent) {
      e.preventDefault(); // blocks Chrome scroll hijack — only works with passive:false
      delta = e.touches[0].clientY - startY;
      const HANDLE_H = 56;
      const closedOffset = sidebar!.offsetHeight - HANDLE_H;
      const t = sidebarOpenRef.current
        ? Math.max(0, Math.min(closedOffset, delta))          // open → drag down
        : Math.max(0, Math.min(closedOffset, closedOffset + delta)); // closed → drag up
      sidebar!.style.transform = `translateY(${t}px)`;
    }

    function onEnd() {
      sidebar!.classList.remove('sidebar--dragging');
      sidebar!.style.transform = '';
      const THRESHOLD = 60;
      if (sidebarOpenRef.current) {
        if (delta > THRESHOLD) setSidebarOpen(false);
      } else {
        if (delta < -THRESHOLD) setSidebarOpen(true);
      }
    }

    handle.addEventListener('touchstart', onStart, { passive: true });
    handle.addEventListener('touchmove',  onMove,  { passive: false }); // ← critical
    handle.addEventListener('touchend',   onEnd,   { passive: true });

    return () => {
      handle.removeEventListener('touchstart', onStart);
      handle.removeEventListener('touchmove',  onMove);
      handle.removeEventListener('touchend',   onEnd);
    };
  // Re-attach when desktop/mobile switches so handleRef is live
  }, [isDesktop]);

  // ── Derived ─────────────────────────────────────────────────────────────────
  const attractionPins = attractions.map(a => ({
    id: a.id,
    lat: a.location.lat,
    lng: a.location.lng,
    name: a.name,
    category: a.category,
  }));

  const sidebarClass = [
    'sidebar',
    isDesktop ? (sidebarOpen ? '' : 'sidebar--closed') : (sidebarOpen ? 'sidebar--open-mobile' : ''),
  ].filter(Boolean).join(' ');

  return (
    <div className="app">
      {/* Mobile backdrop */}
      {!isDesktop && sidebarOpen && (
        <div className="sidebar-backdrop" onClick={() => setSidebarOpen(false)} />
      )}

      {/* ── Sidebar ───────────────────────────────────────────────────────── */}
      <aside className={sidebarClass} ref={sidebarRef}>
        <div className="sidebar-inner">

          {/* Mobile swipe handle — always visible at bottom */}
          {!isDesktop && (
            <div
              ref={handleRef}
              className="sidebar-handle"
              onClick={() => setSidebarOpen(p => !p)}
            >
              <GripHorizontal size={18} className="grip-icon" />
              <span className="handle-label">Itinerary Planner</span>
            </div>
          )}

          <div className="sidebar-header">
            <div className="sidebar-logo"><Map size={22} strokeWidth={1.75} /></div>
            <div style={{ flex: 1 }}>
              <div className="sidebar-title">Itinerary Optimizer</div>
              <div className="sidebar-sub">Bangkok Tourism Planner</div>
            </div>
            {/* Desktop: collapse button lives here in the header */}
            {isDesktop && (
              <button className="icon-btn" onClick={() => setSidebarOpen(false)} title="Collapse sidebar">
                <ChevronLeft size={18} />
              </button>
            )}
            {/* Mobile: close (snap down) */}
            {!isDesktop && (
              <button className="icon-btn" onClick={() => setSidebarOpen(false)}>
                <X size={18} />
              </button>
            )}
          </div>

          <div className="form-body">

            {/* Hotel Location */}
            <section className="form-section">
              <label className="section-label"><MapPin size={11} /> Hotel Location</label>
              <div className="coord-row">
                <div className="coord-field">
                  <span className="coord-tag">Lat</span>
                  <input
                    type="number" step="0.0001" value={hotelLat}
                    onChange={e => setHotelLat(parseFloat(e.target.value))}
                    className="coord-input"
                  />
                </div>
                <div className="coord-field">
                  <span className="coord-tag">Lng</span>
                  <input
                    type="number" step="0.0001" value={hotelLng}
                    onChange={e => setHotelLng(parseFloat(e.target.value))}
                    className="coord-input"
                  />
                </div>
              </div>
              <div style={{ display: 'flex', gap: 6 }}>
                <button
                  className={`pick-btn ${isPickingHotel ? 'pick-btn--active' : ''}`}
                  style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}
                  onClick={() => setIsPickingHotel(p => !p)}
                >
                  {isPickingHotel
                    ? <><X size={13} /> Cancel</>
                    : <><Crosshair size={13} /> Pick from map</>}
                </button>
                <button
                  className="pick-btn"
                  style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}
                  onClick={handleGps}
                  disabled={gpsLoading}
                >
                  <LocateFixed size={13} className={gpsLoading ? 'spin' : ''} />
                  {gpsLoading ? 'Locating…' : 'Use GPS'}
                </button>
              </div>
              {gpsError && <div className="error-box" style={{ fontSize: 11 }}>{gpsError}</div>}
            </section>

            {/* Dataset */}
            <section className="form-section">
              <label className="section-label"><Layers size={11} /> Attraction Dataset</label>
              <select
                className="form-select"
                value={datasetName}
                onChange={e => setDatasetName(e.target.value)}
              >
                {DATASETS.map(d => (
                  <option key={d} value={d}>{DATASET_LABELS[d] ?? d}</option>
                ))}
              </select>
              <div className="hint">{attractions.length} attractions loaded</div>
            </section>

            {/* Algorithm */}
            <section className="form-section">
              <label className="section-label"><Cpu size={11} /> Algorithm</label>
              <div className="radio-group">
                {(['greedy', 'sa'] as const).map(alg => (
                  <label key={alg} className={`radio-card ${algorithm === alg ? 'radio-card--active' : ''}`}>
                    <input
                      type="radio" name="algorithm" value={alg}
                      checked={algorithm === alg}
                      onChange={() => setAlgorithm(alg)}
                      style={{ display: 'none' }}
                    />
                    <span className="radio-title" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      {alg === 'greedy' ? <Zap size={13} /> : <Sparkles size={13} />}
                      {alg === 'greedy' ? 'Greedy' : 'Simulated Annealing'}
                    </span>
                    <span className="radio-desc">
                      {alg === 'greedy' ? 'Fast, deterministic' : 'Better quality, ~0.4 s'}
                    </span>
                  </label>
                ))}
              </div>
              {algorithm === 'sa' && (
                <div className="inline-field" style={{ marginTop: 8 }}>
                  <label className="inline-label">Random seed</label>
                  <input
                    type="number" min={0} max={9999} value={saSeed}
                    onChange={e => setSaSeed(parseInt(e.target.value))}
                    className="inline-input"
                  />
                </div>
              )}
            </section>

            {/* Parameters */}
            <section className="form-section">
              <label className="section-label"><SlidersHorizontal size={11} /> Parameters</label>

              <div className="inline-field">
                <label className="inline-label" style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <Calendar size={13} /> Days
                </label>
                <select className="inline-select" value={numDays} onChange={e => setNumDays(+e.target.value)}>
                  {[1, 2, 3, 5, 7].map(d => <option key={d} value={d}>{d} day{d > 1 ? 's' : ''}</option>)}
                </select>
              </div>

              <div className="slider-field">
                <div className="slider-header">
                  <label className="inline-label" style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                    <Clock size={13} /> Daily time budget
                  </label>
                  <span className="slider-value">{(dailyTimeBudget / 60).toFixed(1)} h</span>
                </div>
                <input
                  type="range" min={240} max={720} step={30} value={dailyTimeBudget}
                  onChange={e => setDailyTimeBudget(+e.target.value)}
                  className="slider"
                />
                <div className="slider-ticks"><span>4 h</span><span>8 h</span><span>12 h</span></div>
              </div>

              <div className="inline-field">
                <label className="inline-label" style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <DollarSign size={13} /> Budget / day
                  <span style={{ fontWeight: 400, color: 'var(--text-4)', marginLeft: 4 }}>
                    = ${dailyBudget * numDays} total
                  </span>
                </label>
                <div className="dollar-input">
                  <span className="dollar-sign">$</span>
                  <input
                    type="number" min={0} step={10} value={dailyBudget}
                    onChange={e => setDailyBudget(+e.target.value)}
                    className="dollar-inner"
                  />
                </div>
              </div>

              <div className="slider-field">
                <div className="slider-header">
                  <label className="inline-label">Start time</label>
                  <span className="slider-value">{fmtTime(startTime)}</span>
                </div>
                <input
                  type="range" min={360} max={720} step={30} value={startTime}
                  onChange={e => setStartTime(+e.target.value)}
                  className="slider"
                />
                <div className="slider-ticks"><span>6 AM</span><span>9 AM</span><span>12 PM</span></div>
              </div>
            </section>

            {/* Submit */}
            {error && <div className="error-box">{error}</div>}
            <button
              className="optimize-btn"
              onClick={handleOptimize}
              disabled={loading || attractions.length === 0}
            >
              {loading
                ? <span className="spinner" />
                : <><Play size={16} /> Optimize Itinerary</>}
            </button>

            {/* Results */}
            {itinerary && (
              <section className="form-section result-section">
                <label className="section-label"><BarChart2 size={11} /> Results</label>
                <ResultPanel
                  itinerary={itinerary}
                  hotelLat={hotelLat}
                  hotelLng={hotelLng}
                  activeDayIndex={activeDayIndex}
                  onDayClick={setActiveDayIndex}
                  onVisitClick={(lat, lng) => setFocusPoint({ lat, lng, zoom: 17 })}
                />
              </section>
            )}
          </div>
        </div>{/* /sidebar-inner */}
      </aside>

      {/* Desktop expand button — only shown when sidebar is collapsed */}
      {isDesktop && !sidebarOpen && (
        <button className="sidebar-expand-btn" onClick={() => setSidebarOpen(true)} title="Expand sidebar">
          <ChevronRight size={18} />
        </button>
      )}

      {/* ── Map ──────────────────────────────────────────────────────────── */}
      <main className="map-area">
        <MapView
          hotelLat={hotelLat}
          hotelLng={hotelLng}
          itinerary={itinerary}
          attractions={attractionPins}
          isPickingHotel={isPickingHotel}
          onHotelPick={handleHotelPick}
          activeDayIndex={activeDayIndex}
          focusPoint={focusPoint}
        />
      </main>
    </div>
  );
}

function fmtTime(mins: number): string {
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  const ampm = h < 12 ? 'AM' : 'PM';
  return `${h % 12 || 12}:${m.toString().padStart(2, '0')} ${ampm}`;
}
