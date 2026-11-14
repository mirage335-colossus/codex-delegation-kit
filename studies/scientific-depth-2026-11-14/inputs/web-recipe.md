# Metered `web.run` recipe

The study owner supplies `allocations.json` in this directory. Its schema is
`{"total_cap": 640, "runs": {"run-id": 120, ...}}`. Per-run caps and the
total ceiling are enforced independently. Use the assigned run ID below. The meter counts
each item in `search_query`, `open`, `click`, `find`, and `screenshot`, including
items batched in one call. `response_length` does not consume an operation.

Copy this into `functions.exec` (raw JavaScript, no code fence). Set `run` and
`request` to the allocation and web request you intend to use. An admitted
ticket is required before `tools.web__run` is called; a denial exits without a
web call. The `finally` block records a returned result or an error, and a
returned response stores only its serialized character count as result
metadata.

```javascript
const root = "/home/user/___quick/p/_cur/codex-delegation-kit/studies/scientific-depth-2026-11-14";
const meter = root + "/tools/research_meter.py";
const run = "REPLACE_WITH_ASSIGNED_RUN_ID";
const request = {
  search_query: [{ q: "example query" }],
  response_length: "medium"
};

function shellQuote(value) {
  return "'" + String(value).replace(/'/g, "'\\''") + "'";
}
async function meterCommand(args) {
  return await tools.exec_command({
    cmd: ["python3", meter, ...args].map(shellQuote).join(" "),
    workdir: root,
    max_output_tokens: 1000
  });
}

const reserved = await meterCommand([
  "reserve", "--root", root, "--run", run,
  "--request-json", JSON.stringify(request)
]);
let ticket;
try {
  ticket = JSON.parse(reserved.output);
} catch (error) {
  throw new Error("Meter admission returned unreadable output: " + reserved.output);
}
if (reserved.exit_code !== 0 || ticket.admitted !== true) {
  text(JSON.stringify({ admitted: false, meter: ticket }));
} else {
  let status = "returned";
  let metadata;
  try {
    const response = await tools.web__run(ticket.request);
    const serialized = JSON.stringify(response);
    metadata = { serialized_characters: serialized.length };
    text(serialized);
  } catch (error) {
    status = "error";
    metadata = { error: String(error) };
    text(JSON.stringify({ web_error: String(error) }));
  } finally {
    const finished = await meterCommand([
      "finish", "--root", root, "--run", run, "--id", ticket.id,
      "--status", status, "--metadata-json", JSON.stringify(metadata)
    ]);
    text(JSON.stringify({ meter_finish_exit_code: finished.exit_code, meter_finish: finished.output }));
  }
}
```

The helper is cooperative accounting: it observes only calls wrapped this way.
It cannot prevent direct `web.run` use, authenticate the caller, establish that
all research calls were logged, or enforce the allocation outside this wrapper.
If `web.run` returns normally with an error-shaped result, the receipt is
`returned`; a thrown tool error is recorded as `error`. A process interruption
can leave a reservation in `reserved` status, while its operation allowance
remains consumed.
