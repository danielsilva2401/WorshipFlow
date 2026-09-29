import React, { useMemo } from "react";
import { Plus, Sparkles } from "lucide-react";
import { recommendSongs } from "./recommendations";

export default function SongRecommendations({
  songs,
  scales,
  referenceDate,
  selectedIds,
  excludeScaleId,
  onAdd,
}) {
  const suggestions = useMemo(
    () =>
      recommendSongs({
        songs,
        scales,
        referenceDate,
        selectedIds,
        excludeScaleId,
        limit: 6,
      }),
    [songs, scales, referenceDate, selectedIds, excludeScaleId],
  );

  if (!songs?.length) return null;

  return (
    <section className="smart-song-suggestions">
      <div className="smart-song-head">
        <span className="smart-song-icon"><Sparkles size={18} /></span>
        <div className="grow">
          <h3>SUGESTÕES PARA ESTA ESCALA</h3>
          <p className="muted">
            Baseado no histórico das escalas, tempo desde a última execução e músicas que já estão prontas no WorshipFlow.
          </p>
        </div>
        <span className="count">{suggestions.length}</span>
      </div>

      {suggestions.length ? (
        <div className="smart-song-grid">
          {suggestions.map(({ song, plays, reasons }) => (
            <article className="smart-song-card" key={song.id}>
              <div className="grow">
                <strong>{song.title}</strong>
                <small>{song.artist}{song.tone ? ` · Tom ${song.tone}` : ""}</small>
                <div className="smart-song-reasons">
                  {reasons.map((reason) => <span key={reason}>{reason}</span>)}
                  {plays > 0 && <span>{plays}x no histórico</span>}
                </div>
              </div>
              <button type="button" className="smart-song-add" onClick={() => onAdd(song)}>
                <Plus size={16} /> Adicionar
              </button>
            </article>
          ))}
        </div>
      ) : (
        <p className="muted smart-song-empty">
          Todas as músicas disponíveis já foram adicionadas a esta escala.
        </p>
      )}
    </section>
  );
}
