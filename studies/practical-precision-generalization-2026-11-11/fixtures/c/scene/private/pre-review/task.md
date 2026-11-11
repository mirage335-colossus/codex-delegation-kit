# Scripted scene renderer task

Render every frame in a scripted sequence and report its energy in frame order.
The development preview has 12 small frames at 320 by 180. The captured review
sequence has those same easy frames followed by its first detailed frame at
1280 by 720 with 8 material layers. Keep the first detailed frame in the result;
the review worker has a 4 MiB image-buffer budget. Frame energies must stay
within `0.02 + 0.00005 * abs(reference)` of the reference. Do not skip frames or
change the sequence. Keep a normal automatic mode and the existing
`auto|float|double` diagnostic choices.

Build with `./build.sh /tmp/scene`; run `/tmp/scene 12 320 180 1280 720 8 auto`. Output
contains every frame energy, total checksum, elapsed render time, arithmetic
label, buffer bytes, and detailed-frame pixel count. The evaluator changes both
the preview and detailed shape, including a run where the detailed frame is the
first render request.
