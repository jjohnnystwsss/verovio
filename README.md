# Verovio #4533 reproduction and validation

Code base: `bfbcec3c9a0c933aa832f779a5cc057285857d06` (`develop`).
Fix: `e12355d1df74b8c2439d0a84f7892afe598dfc25`.
These fixtures and scripts are review artifacts, kept outside the production patch per the repository instructions. The independently authored MEI fixtures and test drivers are available under LGPL-3.0-or-later, consistent with Verovio.

## Human reproduction

From a Verovio checkout, with this artifact directory downloaded as `/tmp/repro-4533`:

```sh
cmake -S cmake -B build/cli -DCMAKE_BUILD_TYPE=Debug
cmake --build build/cli --parallel 2
build/cli/verovio -r data -t timemap -o /tmp/repeat-timemap.json /tmp/repro-4533/consecutive-ends.mei
build/cli/verovio -r data -t midi -o /tmp/repeat-midi.mid /tmp/repro-4533/consecutive-ends.mei
```

Run the same commands on the base and fix revisions, saving output separately. The base Debug build aborts in `Object::InsertBefore` when the second ending tries to move a measure already reparented by the first strain. The fixed timemap contains `n1, n1-rend2, n2, n2-rend2` (or equivalent generated rendition IDs), with onsets 0, 2000, 4000, 6000 ms and final end at 8000 ms. MIDI has C4, C4, D4, D4 at four-quarter-note intervals. Existing MIDI encoding releases each note one tick before its boundary.

`cases.json` records expected original-note sequences for all 11 cases. The driver normalizes `-rend` suffixes. Every MEI fixture validates against the official MEI 5.1 CMN Relax NG schema (https://music-encoding.org/schema/5.1/mei-CMN.rng).

## Executed validation

Linux ARM64 GCC 14 Debug CLI, full native feature set. Native base is saved as `/verovio-baseline`; fixed as `/verovio-4533-fixed`. Data is `/verovio-src/data`; fixture root `/verovio-4533`. Drivers in `validation/` retain these actual paths. No core dumps were kept.

- Base timemap: 4 assertion aborts; leading-left-end wrong sequence; 6 controls pass.
- Fixed timemap: all 11 exact sequences, onset times and final times pass.
- Fixed native MIDI: all 11 decoded note-on pitches/times and note-off times pass (mido).
- Actual WebAssembly compiled from the fixed C++: all 11 timemaps pass, MIDI exports decode with all 11 pitch/timing checks passing. Emscripten 3.1.69, Node 20.19.2, `-O1 -DNDEBUG`, `NO_HUMDRUM_SUPPORT=ON`; this is not a browser UI test or the upstream release optimization matrix.
- 69 official MEI fixtures (barline/ending/expansion/repeats/repeatmark/section/midi/tie/slur): base and fixed complete timemap outputs identical under `--xml-id-seed 1`. Immutable external corpus blobs are listed in `validation/corpus-manifest.json`. This is a targeted CLI comparison, not the entire upstream regression runner.
- clang-format 22.1.8 and `git diff --check` pass.

Representative executed commands:

```sh
python3 /verovio-4533/matrix.py /verovio-baseline
python3 /verovio-4533/matrix.py /verovio-4533-fixed
python3 /verovio-4533/export-midi.py
node /verovio-4533/wasm-check.cjs /verovio-4533-wasm.js
python3 /verovio-corpus/compare.py
```

The first command intentionally fails on the original revision. Host mido verification was run on exported native and WASM MIDI directories using `check-midi.py` (the WASM run substitutes the directory). Raw outputs are in `validation/*.log`. Build/configure/link logs document the actual compilation. No external test data or generated SVG is included in the production code diff.
