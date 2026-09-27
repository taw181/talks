# Slides plan

The deck as it stands. Order lives in `talk/deck.txt`; each heading below is
one slide class in `talk/aion_slides.py`. "Clicks" = stops at each `beat()`;
"loops" = each stage/hold loops until the click.

# intro

## TitleSlide
Blue MOT video in the background (ping-pong loop, veiled), AION logo top left,
Imperial logo top right. Title: A prototype differential atom interferometer
for fundamental physics. Thomas Walker, University of Freiburg, 2026.

## ContentsSlide
Outline, numbered:
1. Atom interferometry
2. Gravitational waves
3. Dark matter
4. Our prototype device
5. Future plans

# 1. atom interferometry
One clock, then two sharing a laser so its noise cancels.

## SinglePhotonMachZehnderSlide (clicks)
pi/2 - pi - pi/2 driven by single photons, beside the two-level system it
drives; the atom arrives as |g, p>, kets on each leg as it is drawn.

## ClockPhaseTermsSlide (clicks)
"The interferometer is a clock": hands per arm, phases phi_n under each pulse,
the null (both arms spend equal time in |e>). Then Phi = Phi_interferometer +
Phi_laser, with the laser term circled as the one the gradiometer cancels.

## GradiometerSlide (clicks)
Two interferometers, one baseline, one laser: two clocks reading the same.
Ends on what the difference is made of.

# 2. gravitational waves

## BlackHoleMergerSlide (no stops)
Flat sheet, two holes dent it, inspiral, merger, ringdown, settled sheet.

## MergerOnSensitivityPlotSlide (clicks)
Merger on the left, its signal crossing LIGO's band on the right.

## SensitivityLandscapeSlide (clicks)
LIGO and one merger, the other mergers, LISA, ET, the gap between them, then
AION-km filling it. No AEDGE.

## GradiometerGWStretchSlide (clicks)
The wave drawn as a stretching baseline (proper-distance picture), h(t) above.

# 3. dark matter

## DarkMatterScaleSlide (loops)
An ultralight dark-matter wave laid across the Earth, out to the Moon, out to
the Sun; and so, in the lab.

## DarkMatterFieldSlide (loops)
What the field is (one classical wave at its Compton frequency), then what it
does to a clock: couplings walk the Sr clock transition up and down (level
diagram at double size).

## DarkMatterPhaseSlide (clicks)
ClockPhase's geometry with the field through it: the arms are excited over
different windows, the hands no longer come back together, Phi != 0.

# 4. our prototype device

## AIONCollabSlide
The AION collaboration: UK map + logo, click, baseline image beside it.

## ChamberSlide
Chamber photo with the window called out; two cartoon clouds ~2 mm apart,
click, "<< 1 km".

## AIONChambersSlide
The same chamber at each AION site (captioned figure).

## CoolingSequenceSlide (loops per stage)
Oven feeding a 2D MOT, pushed stream into the 3D MOT; blue MOT, modulated red
MOT, narrowband red MOT, with level scheme and timeline.

## DipoleTrapLoadingSlide (loops per stage)
Upper dipole trap, lower dipole trap (1064 nm horizontal, 813 nm vertical),
spin polarisation.

## ExperimentSequenceSlide (no stops)
The shot on a timeline beside the imaging video (centred, no level scheme),
from the blue MOT (red MOT handover at 54 ms) to the loaded lower trap.

## VelocitySlicingSlide (loops per step)
Thermal velocity spread, 698 nm pi pulse, 461 nm push, what is left.

## SignalInjectionSlide (loops per stage)
Two clouds one above the other, one clock laser through both, a light-shift
beam on the upper cloud alone.

## LightShiftSignalSlide (clicks)
Gradiometer with the off-resonant beam across the upper cloud during the
first leg: the null breaks. Readout by two 461 nm imaging pulses (S then P),
ending on the camera image of the two clouds.

## LaserNoiseLissajousSlide (clicks)
Measured DAI fringes: low-laser-noise run full size, shrunk to the top panel,
high-laser-noise run below, both onto one Lissajous ellipse.

## AllanDeviationSlide
Allan deviation built up: standard quantum limit, + low-noise run, + noisy run.

## ExtractedSignalSlide
Fig. 5a redrawn: each injected frequency recovered where it was put.

# 5. future plans

## FuturePlansSlide
Section title "5. Future plans".

## Aion10BeecroftSlide
AION-10 at Oxford: stairwell photo, click, Beecroft building cutaway beside it
(no shaft image).

## AICECernSlide
AICE figure with the PX46 shaft's 150 m depth marked.

## LargeMomentumTransferSlide (no stops)
A ladder of single-photon kicks separating the arms by N hbar k.

## LMTMachZehnderSlide (clicks)
LMT Mach-Zehnder (after Rudolph et al. Fig. 1c): beam splitter, mirror, beam
splitter with pi/2 and pi labels; then the enclosed area vs the dashed N = 1
one, Phi propto N k sin^2(omega T/2).

## LMTResultsSlide
Upper/lower Lissajous ellipses from 1 to 71 LMT pulses.

# outro

## OutroSlide
Thank you for listening! Sr lab team photo on the left; Oliver Buchmüller (PI)
and AION logo over the AION collaboration photo on the right.
