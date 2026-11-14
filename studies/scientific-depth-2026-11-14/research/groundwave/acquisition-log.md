# Read-only NTIA LFMF source acquisition

Authorized GitHub connector acquisition calls (up to 25); run was bounded to the official public NTIA implementation and study-only output. Calls used `mcp__codex_apps__github_fetch` / `github_fetch_file`; every returned normally. No repository writes or package installation occurred.

## Repository identity and exact requests

1. `github_fetch(url="https://api.github.com/repos/NTIA/LFMF")` — returned public repo metadata; default branch `main`, C++, described as NTIA/ITS LF/MF propagation model for 0.01–30MHz over smooth Earth, antenna heights <50m.
2. `github_fetch(url="https://api.github.com/repos/NTIA/LFMF/branches/main")` — returned commit `57886e9d0a29fd8f04a6416dc3f782322f5a3589`, committed 2025-01-23; associated tree `e916a266bd47be343c3ea764da916aee192dca62`.
3. `github_fetch(url="https://api.github.com/repos/NTIA/LFMF/git/trees/57886e9d0a29fd8f04a6416dc3f782322f5a3589?recursive=1")` — returned full non-truncated recursive tree, `truncated=false`.
4. `github_fetch_file(repository_full_name="NTIA/LFMF",path="include/LFMF.h",ref="57886e9d0a29fd8f04a6416dc3f782322f5a3589")` — returned text successfully; this header was fetched once more in the next batch.

The next batch made one `github_fetch_file` call per listed path, all with the same repository and pinned `ref` above. All returned text successfully. The first batch was `LICENSE.md`, `include/LFMF.h`, `src/Airy.cpp`, `src/FlatEarthCurveCorrection.cpp`, `src/LFMF.cpp`, `src/ResidueSeries.cpp`, `src/ReturnCodes.cpp`, `src/ValidateInputs.cpp`, `src/WiRoot.cpp`, and `src/wofz.cpp`. The first artifact-write loop saved LICENSE then stopped on a JavaScript `TextEncoder is not defined` error; it was not an acquisition failure. A second batch refetched the nine remaining files; all were saved. The selected tree blob identifiers and sizes are:

| Path | Git blob SHA | Bytes |
|---|---|---:|
| `LICENSE.md` | `add8ca72cfcd6b2b2451ff2486fb89fa86685ea0` | 2,086 |
| `include/LFMF.h` | `d3641d86736361e04c2dc8297ebd5bdd80b2dc47` | 7,446 |
| `src/Airy.cpp` | `e49429cf136ec94d745cdb0276017bf89b3a4e07` | 46,690 |
| `src/FlatEarthCurveCorrection.cpp` | `f578ebaa67db0dcbe6e2ce4de199640f8efbd2fa` | 4,641 |
| `src/LFMF.cpp` | `d3f7fbba729af9d7ae8dcf4d59caa40982c132dc` | 7,369 |
| `src/ResidueSeries.cpp` | `67d44c38df9a7ac911c73522e223765a74abcbe5` | 4,005 |
| `src/ReturnCodes.cpp` | `05dfcf19ef1d741351ea4adab1497aa4761bbf1d` | 3,058 |
| `src/ValidateInputs.cpp` | `1b4176aeded69e029a2c6bd14a8f34efbbad9f66` | 2,267 |
| `src/WiRoot.cpp` | `d887f8e39b2048627373fee012946e8047021b32` | 10,952 |
| `src/wofz.cpp` | `8f80f8b5593158efc410864dbed04ef613809730` | 6,749 |

Two additional exact calls inspected the standalone build metadata: `github_fetch_file(repository_full_name="NTIA/LFMF",path="src/CMakeLists.txt",ref="57886e9d0a29fd8f04a6416dc3f782322f5a3589")` and the same with `path="CMakeLists.txt"`. Both returned text successfully (tree blobs `db86ec92f08f65bf547d1dce8339fc4badfb3bb2`/1,835 bytes and `3879a298b096d15881519a7e5d4f1f45ef734e72`/8,061 bytes respectively). They established the exact source list and project version 1.1; the CMake system itself was not run.

Total connector acquisition calls: 25/25. No failed connector calls. Official ITU software table identifies the P.368 C++ product as authoritative/integral software version 10; its link was attempted through metered web and returned an unsupported ZIP-content-type error. NTIA/LFMF is the official model source cited by ITU, acquired above through the separately authorized read-only GitHub connector. See `tmp/LFMF/LICENSE.md`; no product code is included in pumpModem.

The official-table link click targeted `https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Software%20Products/R19-WP3L-C-0072%21P2%21ZIP-E.zip`; web returned an internal fetch error, HTTP-like status 400, `Unsupported content-type: application/x-zip-compressed`. A separate metered direct open of the P.368-10 PDF timed out. Opening `https://ntia.github.io/LFMF/` later returned “URL ... is not accessible via this tool.” These tool-content limitations do not imply the software or recommendation is unavailable; P.368 text/current status and ITU's software listing were accessible, and the same official NTIA model source was successfully fetched via the authorized connector. The groundwave web run used 78/140 operations by completion, with no thrown web-tool errors recorded; error-shaped results were returned normally and recorded by the meter.

## Desk executable

Only the source and license files listed above were copied under `tmp/LFMF/`; `model_sweep.cpp` is an original thin caller of the public API. It uses g++ 14.2.0 with the upstream C++11-compatible source and compile definitions copied from upstream CMake metadata (`LIBRARY_NAME="LFMF"`, `LIBRARY_VERSION="1.1"`). No upstream build system, test suite or dependencies were invoked. The first standalone compile stopped because those two compile definitions were omitted; no model call/assertion occurred. After adding the definitions, compile and execution completed successfully. See `model_sweep.cpp` and `model_sweep.txt` for exact inputs and output.
