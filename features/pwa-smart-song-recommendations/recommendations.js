const DAY = 86400000;

function asDate(value) {
  if (!value) return null;
  const date = new Date(String(value).slice(0, 10) + "T12:00:00");
  return Number.isNaN(date.getTime()) ? null : date;
}

function daysBetween(from, to) {
  return Math.max(0, Math.round((to.getTime() - from.getTime()) / DAY));
}

function songCompleteness(song) {
  let score = 0;
  if (String(song?.chords || "").trim()) score += 14;
  else if (song?.cifra_saved || song?.cifra_club_chords) score += 8;
  if (String(song?.youtube_url || "").trim()) score += 7;
  if (String(song?.tone || "").trim()) score += 3;
  return score;
}

export function recommendSongs({
  songs = [],
  scales = [],
  referenceDate,
  selectedIds = [],
  excludeScaleId = "",
  limit = 6,
} = {}) {
  const reference = asDate(referenceDate) || new Date();
  const selected = new Set(selectedIds.filter(Boolean));
  const history = new Map();

  for (const scale of scales) {
    if (!scale || scale.id === excludeScaleId || scale.status !== "published") continue;
    const date = asDate(scale.date);
    if (!date || date > reference) continue;
    for (const item of scale.setlist || []) {
      const id = item?.song_id;
      if (!id) continue;
      const current = history.get(id) || { plays: 0, lastDate: null, recent30: 0, recent60: 0 };
      current.plays += 1;
      if (!current.lastDate || date > current.lastDate) current.lastDate = date;
      const age = daysBetween(date, reference);
      if (age <= 30) current.recent30 += 1;
      if (age <= 60) current.recent60 += 1;
      history.set(id, current);
    }
  }

  return songs
    .filter((song) => song?.id && !selected.has(song.id))
    .map((song) => {
      const stats = history.get(song.id) || { plays: 0, lastDate: null, recent30: 0, recent60: 0 };
      const daysSince = stats.lastDate ? daysBetween(stats.lastDate, reference) : null;
      let score = songCompleteness(song);

      if (daysSince === null) score += 58;
      else if (daysSince >= 120) score += 48;
      else if (daysSince >= 75) score += 40;
      else if (daysSince >= 45) score += 30;
      else if (daysSince >= 30) score += 18;
      else if (daysSince >= 15) score += 6;
      else score -= 35;

      score -= Math.min(stats.recent30 * 16 + Math.max(0, stats.recent60 - stats.recent30) * 7, 45);
      score -= Math.min(Math.max(0, stats.plays - 5) * 2, 12);

      const reasons = [];
      if (daysSince === null) reasons.push("Ainda não foi usada");
      else if (daysSince >= 45) reasons.push(`Última vez há ${daysSince} dias`);
      else if (daysSince >= 15) reasons.push(`Há ${daysSince} dias sem tocar`);
      else reasons.push(`Tocada há ${daysSince} dias`);

      if (String(song.chords || "").trim()) reasons.push("Cifra completa");
      else if (song.cifra_saved || song.cifra_club_chords) reasons.push("Cifra pronta");
      if (String(song.youtube_url || "").trim()) reasons.push("YouTube pronto");

      return {
        song,
        score,
        plays: stats.plays,
        daysSince,
        reasons: reasons.slice(0, 3),
      };
    })
    .sort((a, b) => b.score - a.score || (b.daysSince ?? 9999) - (a.daysSince ?? 9999) || String(a.song.title || "").localeCompare(String(b.song.title || "")))
    .slice(0, Math.max(0, limit));
}
