import test from "node:test";
import assert from "node:assert/strict";
import { recommendSongs } from "./recommendations.js";

const songs = [
  { id: "old", title: "Antiga", artist: "A", chords: "C G", youtube_url: "https://youtu.be/x" },
  { id: "recent", title: "Recente", artist: "B", chords: "D A" },
  { id: "new", title: "Nova", artist: "C", chords: "" },
];

test("prioritizes songs not used recently", () => {
  const result = recommendSongs({
    songs,
    referenceDate: "2026-09-29",
    scales: [
      { id: "s1", status: "published", date: "2026-05-01", setlist: [{ song_id: "old" }] },
      { id: "s2", status: "published", date: "2026-09-24", setlist: [{ song_id: "recent" }] },
    ],
  });
  assert.notEqual(result[0].song.id, "recent");
  assert.ok(result.findIndex((x) => x.song.id === "recent") > 0);
});

test("ignores draft and future scales when building history", () => {
  const result = recommendSongs({
    songs: [songs[2]],
    referenceDate: "2026-09-29",
    scales: [
      { id: "draft", status: "draft", date: "2026-09-20", setlist: [{ song_id: "new" }] },
      { id: "future", status: "published", date: "2026-10-10", setlist: [{ song_id: "new" }] },
    ],
  });
  assert.equal(result[0].daysSince, null);
  assert.match(result[0].reasons[0], /Ainda não foi usada/);
});

test("does not suggest songs already selected for the scale", () => {
  const result = recommendSongs({ songs, selectedIds: ["old", "new"], referenceDate: "2026-09-29" });
  assert.deepEqual(result.map((x) => x.song.id), ["recent"]);
});

test("can exclude the scale currently being edited from its own history", () => {
  const result = recommendSongs({
    songs: [songs[0]],
    referenceDate: "2026-09-29",
    excludeScaleId: "current",
    scales: [{ id: "current", status: "published", date: "2026-09-29", setlist: [{ song_id: "old" }] }],
  });
  assert.equal(result[0].daysSince, null);
});
