You are a mechanical design engineer. Do NOT use any tools, code, files, search, or calculators — answer from your own knowledge and reasoning only, in a single reply.

## Request (from the user, verbatim)
"울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야"
(= "Make it so the phone doesn't shake even on bumpy roads, as light as possible. I'll 3D print it.")

## Product and fixed conditions
- One-piece bicycle phone mount, PETG, FDM printed, 100 % infill.
- Clamps a handlebar of diameter 31.8 mm. Phone (any phone, width 64–90 mm, thickness 6–14 mm, ≤ 290 g with case) is held tilted so a seated rider can see it.
- Total moving mass carried by the mount: phone + gripping parts ≈ 311 g.
- Phone must also not deflect much when the user taps the screen.
- Phone generates heat (navigation); the mount should not trap it.

## Coordinate system (mm) — phone-aligned frame, already tilted 35° about the handlebar axis
- Handlebar axis = y axis, centred at x = 0, z = 0. Handlebar bore radius 16.1 (keep empty).
- x = along the phone length (phone bottom edge at x = −10, top edge up to x = 150).
- z = normal to the phone screen. Phone BACK face sits at z = 30; phone occupies z = 30…44 (keep empty).
- y = across the phone width; design is symmetric about y = 0; usable y range −40…+40.
- Design box you may fill: x −24…152, y −40…40, z −36…30 (outside the bore and the phone).

## Parts that are ALREADY fixed (you must connect to them; they are added automatically, do not redraw)
- Clamp ring around the bore, r 16.1–20.6, |y| < 10, plus bolt ears below the bar.
- Side-jaw housing (holds spring jaws for phone sides): x 55…75, z 18…30, full width y −42…42.
- Bottom hook (holds phone bottom edge): x −16…−10, |y| < 15, z 24…47.
- Top rail (for sliding top hook): x 102…150, |y| < 10, z 12…24.
- Top back pad: x 126…140, |y| < 16, z 24…30.

Your job: design the structure that connects the clamp to these fixed parts (and any back plate you want under the phone), so that the request is met.

## Output format (exactly this, one JSON block)
```json
{"criteria": {"vibration_target": "...your own criterion...", "shock": "...", "thermal": "...", "other": "..."},
 "primitives": [
   {"type":"box","min":[x,y,z],"max":[x,y,z]},
   {"type":"rod","p0":[x,y,z],"p1":[x,y,z],"r":R},
   {"type":"cyl_y","center_xz":[x,z],"r":R,"y":[y0,y1]},
   {"type":"box","min":[...],"max":[...],"op":"sub"}
 ],
 "predicted": {"mass_g": ..., "f1_hz": ..., "max_shake_vs_handlebar": ..., "peak_stress_mpa": ..., "phone_temp_rise_c": ...}}
```
- "add" is default; "op":"sub" removes material. Use at most 25 primitives.
- State your own criteria (how you decide it is "not shaking", what shock, etc.) and your own predictions.
- Keep the explanation outside the JSON short (≤ 8 lines).
