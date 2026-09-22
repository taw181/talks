

- Progress Towards a Reconfigurable Hybrid Tweezer Array of CaF and Rb 

Daniel Hoare Supervisors: Prof Michael Tarbutt, Prof Ben Sauer 8 July 2026 

- Motivation and Background 



0202 

## HYBRID ATOM-MOLECULE SYSTEM 

CaF qubit initialisation, entanglement, nondestructive readout mediated by a resonant dipole-dipole interaction with an auxiliary Rb Rydberg atom. 

CaF rich internal structure - rotational or hyperfine qubits Long coherence times ~ ms and s. 

Strong long-range Rydberg mediated interaction Resonant dipole-dipole interaction - Fast, highfidelity two-qubit gates - insensitive to thermal motion. 



C. Zhang and M. Tarbutt, “Quantum computation in a hybrid array of molecules and rydberg atoms,” PRX Quantum, vol. 3, no. 3, p. 030340, 2022. 









MOTIVATION AND BACKGROUND 

03 

OPTICAL TWEEZER ARRAY REQUIREMENTS 

- SMALL ARRAY SITE SPACING ~ 2.0 um Requires effective in-situ optical aberration correction to achieve diffraction-limited performance. UNIFORM TRAP DEPTHS ACROSS THE ARRAY For high-fidelity Rydberg excitation of Rb atoms. Requires precise intensity equalisation of the array. HIGH-SPEED PARALLEL TRANSPORT/REARRANGEMENT For generating near-deterministic defect-free arrays of CaF and Rb from stochastically loaded arrays. ATOMIC STATE PREPARATION AND MICROWAVE CONTROL For initialising Rb atomic qubits and demonstrating coherent quantum control. 



MOTIVATION AND BACKGROUND 

04 

## TALK OUTLINE 

Motiation and acground Generating Tweezer Arrays with Spatial Light Modulators Characterising the Array Using Rubidium Optimising the Array Using Rubidium High-Speed Parallel Rearrangement 

Current Efforts 



TALK OUTLINE 

05 

- Spatial Light Modulators and Generating Arrays 



0602 

## Spatial Light Modulators 





















Spatial Light Modulators and Generating Tweezer Arrays 

07 

Phase-Retrieval and Generating Phase Masks 

Phase retrieval problem - what phase mask approximately produces a desired intensity pattern. Weighted superposition of gratings algorithm. 

Iterative feedback for trap intensity equalisation. 



Each trap site has an associated position, weight, and phase. 























Spatial Light Modulators and Generating Tweezer Arrays 

08 

- Characterising the Array Using Rubidium 



0902 

## Loading Statistics 

Standard configuration - 16 x 16 array with a 4.0 um site spacing. Loading from a red-detuned molasses. 

Mean loading probability ~ 55% (limited by collisional blockade). Detection fidelity = 99.91%. 

### Individual Trap Site Photon Rate Histogram 

### Total Photon Rate Histogram 

Baseline imaging survival probability = 96.4% (20 ms exposure with molasses light). 



Characterising the Array 

10 

Loading Threshold, Atom Temperature, Trap Lifetime 



Vary the tweezer’s optical power and measure the loading probability. Saturates at 55% (collisional blockade). 

Mean loading threshold = 0.504 mW 

Switch off tweezer light for variable duration - measure recapture/survival probability - sample the atom’s thermal distribution. 

Optimised molasses temperature ~ 20 - 30 uK 

Trap lifetime = 3.6 s 

Limited by background gas collisions - vacuum pressure ~ 7E-10 mbar 



Characterising the Array 

11 

Trap Frequency Measurements 



Tweezer intensity modulation - parametric heating - measure mean survival probability. 

Along with optical power allows us to calculate trap depth and trap waist. 



Optimised trap depth = 224.87 uK 

Optimised trap waist = 0.992 um 



Characterising the Array 

12 

State Preparation and Microwave Control 

Prepare the Rb array in the F=2, mf=0 state. Drive coherent Rabi oscillations on the F=2, mf=0 to F=1, mf=0 transition. 





Characterising the Array 

13 

- Optimising the Array Using Rubidium 



1402 

In-Situ Aberration Correction 





Source: Patrick Y. Maeda, 2003, Zernike Polynomials and Their Use in Describing the Wavefront Aberrations of the Human Eye, Stanford, https:// acorn.stanford.edu/psych221/projects/2003/pmaeda/index.html 



Optimising the Array 

15 

## In-Situ Aberration Correction 

## Apply a trial Zernike polynomial. 

Correct optical aberrations / wavefront distortion to realise diffraction-limited performance - critical for minimising array site separation. 

Optical aberrations decomposed into weighted sums of Zernike polynomials. 

Vary the Zernike coefficient. Measure the mean radial trap frequency. Extract optimal coefficient value. Repeat for next Zernike polynomial. 





Optimising the Array 

15 

16 





Optimising the Array 

## In-Situ Aberration Correction 

Correction of Zernike modes Z5 to Z13. 

Increase in radial trap frequency from ~70 kHz to ~90 kHz. 25.9% increase in trap depth. Decrease in trap waist from ~1.3 um to 0.992 um. 29.6% decrease in loading threshold from 0.71 to 0.50 mW per tweezer. 









Optimising the Array 

17 





## In-Situ Trap Equalisation 

Equalise trap depths across the array - critical for high-fidelity gates and Rydberg excitation. Simple PI feedback of measured radial trap frequency distribution. Std dev. in radial trap frequency decrease from ~15% to 3%. Min/max ratio in radial trap frequency increase from ~50% to ~90%. 







Optimising the Array 

18 

## In-Situ Trap Equalisation 

Equalise trap depths across the array - critical for high-fidelity gates and Rydberg excitation. 

Simple PI feedback of measured radial trap frequency distribution. Std dev. in radial trap frequency decrease from ~15% to 3%. Min/max ratio in radial trap frequency increase from ~50% to ~90%. 







Optimising the Array 

19 

- High-Speed Parallel Rearrangement 



2002 

## Tweezer Array Rearrangement 

Stochastic loading of Rb (~55%) and CaF (~30%). 

High-speed parallel rearrangement for neardeterministic defect-free arrays in arbitrary geometries. 

Pre-calculate initial and final array phase masks using full phase-retrieval algorithm (5 sec). 

Intermediate phase masks calculated by linearly interpolating trap weights, phases, positions. Map occupied trap sites to final trap sites using an efficient sorting algorithm (e.g. Hungarian, Jonker-Volgenant algorithms). 

Knottnerus, Ivo, et al. "Parallel assembly of neutral atom arrays with an SLM using linear phase interpolation." SciPost Physics 19.4 (2025): 118. 













Array Rearrangement 

21 

## Tweezer Array Rearrangement 

Load and image tweezer array (20 ms exposure). 

Process image and extract occupancy mask of array (2 ms). 

Map occupied trap sites to final trap sites using JV sorting algorithm (<1ms). Switch off unoccupied and excess trap sites. 

Interpolate, calculate ( next phase mask + upload phase mask to SLM (in parallel, ~ 1.8 ms per frame, typ. 20 ms total rearrangement time). 













Array Rearrangement 

22 

23 





Array Rearrangement 

Tweezer Array Rearrangement 





Initial array - 16x16 5.0um spacing Mean filling fraction ~ 55% 



<!-- Start of picture text -->
Final array - 10x10 5.0um spacing<br>Mean filling fraction ~ 94%<br><!-- End of picture text -->

Final array - 10x10 5.0um spacing Mean filling fraction ~ 94% 



Array Rearrangement 

24 

Tweezer Array Rearrangement 









<!-- Start of picture text -->
Max. step size ~ 1.0 um<br>Rearrangement ‘speed’ = 1.88 ms<br>per frame<br>12.2 frames per sequence, 22.9 ms<br>total rearrangement time<br>Loss dominated by lifetime + imaging<br>loss.<br>Rearrangement ‘efficiency’ ~ 98%.<br><!-- End of picture text -->

Max. step size ~ 1.0 um Rearrangement ‘speed’ = 1.88 ms per frame 12.2 frames per sequence, 22.9 ms total rearrangement time Loss dominated by lifetime + imaging loss. Rearrangement ‘efficiency’ ~ 98%. 



Array Rearrangement 

25 

## Dense Arrays 

For two-qubit hybrid gates need small trap site separation ~ 2.0 um for highfidelity operations. 

Challenges: 

Interference of tweezer light, deep offplane traps, reduces detection fidelity. Interference between neighbouring trap sites, distorts trap potential. Rearrangement linear interpolation method breaks down for small site spacing. 

5.0 um site spacing 

3.0 um site spacing 





Array Rearrangement 

26 

## Dense Arrays 

For two-qubit hybrid gates need small trap site separation ~ 2.0 um for highfidelity operations. 

Challenges: 

Interference of tweezer light, deep offplane traps, reduces detection fidelity. Interference between neighbouring trap sites, distorts trap potential. Rearrangement linear interpolation method breaks down for small site spacing. 



## 3.0 um site spacing 



Array Rearrangement 

27 

## Dense Arrays 

For two-qubit hybrid gates need small trap site separation ~ 2.0 um for highfidelity operations. 

Challenges: 

Interference of tweezer light, deep offplane traps which can efficiently trap, reduces detection fidelity. Interference between neighbouring trap sites, distorts trap potential. Rearrangement linear interpolation method breaks down for small site spacing. 

## 2.0 um site spacing - CCD image of array 





Array Rearrangement 

28 

# Current Efforts 



2902 

## Trapping CaF Molecules 

- CaF blue MOT ~ 2.5 - 3.0 x 10⁴ molecules at ~ 60 uK. 

Optical pumping, magnetic trapping of CaF and transport to the tweezer chamber. Transfer into a blue MOT in the tweezer chamber. Load CaF into 852 nm tweezer array from blue MOT. 

- Rydberg Excitation 780 nm + 480 nm - two-photon Rydberg excitation to 60s. 297 nm -  direct single-photon Rydberg excitation to 59p. 





Current Efforts 

30 

## Second Wavelength Tweezer Array 

Set up a second high-speed SLM for generating an array which is selectively attractive to CaF Small site spacing of ~ 1.0 um between CaF and Rb without interference. Species selective trapping. 

Electric Field Control Replace internal mount - install Faraday shielding and electrodes. Tuning the Rb Rydberg energy separation to match the CaF rotational energy separation for a resonant dipole interaction. 





Current Efforts 

31 

# Thank You 



3202 

## THE TEAM 



Prof. Michael Tarbutt 



Prof. Ben Sauer Prof. Stefan Truppe 





## CaF Team 









Joe Cox 

Joe Vagge Qinshu Lyu 

Dr. Jonas Rodewald 

## Tweezer Team 









<!-- Start of picture text -->
Dr. Kai Voges<br><!-- End of picture text -->

Dr. Thomas Walker Dr. Chi Zhang 



33 

