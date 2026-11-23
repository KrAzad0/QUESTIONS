#!/usr/bin/env python3
"""Publish 10 deterministic, original, solved Physics practice questions each day.

Only Python standard library; no third-party API, scraping, copied PYQs or tokens.
Uses Asia/Kolkata for today's date. A dated file is never overwritten.
Every subject has three rotating concept families with date-seeded parameters.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import math
import random
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
SUBJECTS = [
    "Mathematical Physics",
    "Classical Mechanics",
    "Electromagnetic Theory",
    "Quantum Mechanics",
    "Statistical Physics",
    "Optics",
    "Atomic Physics",
    "Solid State",
    "Nuclear Physics",
    "Electronics and Experimental Physics",
]
EXAM_TAGS = [
    "JAM / GATE", "TIFR / CSIR", "GATE", "TIFR / CSIR",
    "CSIR", "JAM", "GATE / CSIR", "GATE", "JAM / CSIR", "GATE / JAM",
]


def rng_for(day: dt.date, subject: str) -> random.Random:
    digest = hashlib.sha256((day.isoformat() + ":" + subject).encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


def make_math(r, v):
    if v == 0:
        a, b = r.randint(4, 11), r.randint(1, 3)
        return ("Symmetric-matrix diagonalization",
                f"A = [[{a},{b}],[{b},{a}]]. Find both eigenvalues and normalized eigenvectors.",
                f"First calculate det(A - λI) = ({a} - λ)^2 - {b}^2 = 0. "
                f"Therefore λ = {a}+{b} = {a+b} or {a}-{b} = {a-b}. "
                "The eigenvector for the larger eigenvalue is (1,1)/sqrt(2); "
                "the smaller has (1,-1)/sqrt(2). These vectors are orthogonal and unit length.")
    if v == 1:
        a, b, c = r.randint(1, 4), r.randint(1, 4), r.randint(1, 4)
        x, z = r.randint(1, 3), r.randint(1, 3)
        value = (2*a+b)*x+2*c*z
        return ("Vector divergence",
                f"For F = ({a}x^2, {b}xy, {c}z^2), evaluate div F at (x,y,z)=({x},0,{z}).",
                f"Use div F = ∂F_x/∂x + ∂F_y/∂y + ∂F_z/∂z "
                f"= {2*a}x + {b}x + {2*c}z = {2*a+b}x + {2*c}z. "
                f"Substitution gives ({2*a+b})({x}) + ({2*c})({z}) = **{value}**. "
                "The derivative of xy with respect to y is x, not y.")
    n = r.randint(1, 6)
    a = n*n
    return ("Gaussian integral",
            f"Evaluate I = integral from -infinity to infinity of exp(-{a} x^2) dx.",
            f"Start with the known Gaussian integral ∫exp(-u²)du=sqrt(pi). "
            f"Set u={n}x, so dx=du/{n}. Thus I=sqrt(pi)/{n}. "
            "Dimensional check: if x has dimensions of length, the coefficient of x² must have reciprocal-length-squared units.")


def make_mechanics(r, v):
    if v == 0:
        m1, m2 = r.randint(1, 4), r.randint(5, 9)
        return ("Atwood machine",
                f"Two ideal masses m1={m1} kg and m2={m2} kg hang over a frictionless massless pulley. "
                "Find acceleration as a multiple of g and the string tension as a multiple of g (in kg*g units).",
                f"Write m2*g - T = m2*a and T - m1*g = m1*a. "
                f"Adding gives a=({m2}-{m1})/({m2}+{m1}) g = "
                f"**{m2-m1}/{m2+m1} g**. "
                f"Insert into T=m1(g+a) to get T=2*m1*m2/(m1+m2) g = "
                f"**{2*m1*m2}/{m1+m2} g**. "
                "Check the heavier mass accelerates downward with a<g.")
    if v == 1:
        L = r.randint(2, 6)
        return ("Stability of a central-force orbit",
                f"For V(r)=-k/r, m=k=1 in consistent units and angular momentum L={L}, "
                "find the circular-orbit radius and determine radial stability.",
                "The effective potential is V_eff=L²/(2mr²)-k/r. "
                "Differentiate: V_eff'=-L²/(mr³)+k/r². "
                f"At its stationary point r0=L²/(mk)={L}²=**{L*L}**. "
                "Next V_eff''(r0)=k/r0³>0; the effective potential has a minimum, "
                "so small radial disturbances oscillate rather than grow.")
    speed = r.choice([10, 20, 30])
    height = speed*speed//20
    return ("Conservation of mechanical energy",
            f"A particle slides without friction from rest through a vertical drop h={height} m. "
            "With g=10 m/s², what is its speed at the bottom?",
            f"Mechanical energy conservation gives m*g*h=(1/2)m*v². "
            f"Thus v=sqrt(2gh)=sqrt(2*10*{height})=**{speed} m/s**. "
            "The mass cancels; this holds only when nonconservative work is absent.")


def make_em(r, v):
    if v == 0:
        electric = 3*r.randint(1, 7)
        return ("Vacuum EM wave",
                f"A vacuum plane wave has peak electric field E0={electric} V/m. Find its B-field amplitude; use c=3.0e8 m/s.",
                "Maxwell's equations imply E0=c B0 for a plane wave in vacuum. "
                f"Thus B0={electric}/(3.0e8)=**{electric/3e8:.2e} T**. "
                "E, B and the propagation direction are mutually perpendicular.")
    if v == 1:
        u = r.randint(1, 5)
        return ("Series capacitance",
                f"Two ideal capacitors C1={2*u} microfarad and C2={3*u} microfarad are in series. Determine C_eq.",
                f"In series, 1/C_eq=1/C1+1/C2. Equivalently, "
                f"C_eq=C1*C2/(C1+C2)=({2*u}*{3*u})/({2*u}+{3*u}) "
                f"= **{6*u/5:.2f} microfarad**. "
                "The equivalent is less than the smaller capacitor.")
    kappa = r.randint(2, 6)
    energy = kappa*r.randint(2, 6)
    return ("Dielectric inserted at fixed charge",
            f"An isolated charged parallel-plate capacitor initially stores U0={energy} mJ. "
            f"A dielectric with relative permittivity k={kappa} completely fills the gap. "
            "Find the new energy, assuming no charge leaks.",
            "Isolated means Q is fixed. With dielectric C'=kC, "
            f"U'=Q²/(2C')=U0/k={energy}/{kappa}=**{energy/kappa:.1f} mJ**. "
            "Warning: fixed voltage would give a different energy change.")


def make_qm(r, v):
    if v == 0:
        n = r.randint(2, 6)
        return ("Infinite square well energy",
                f"A particle is in the nth eigenstate n={n} of a one-dimensional infinite square well. Find E_n/E_1.",
                "Solve the boundary-value problem ψ(0)=ψ(L)=0; allowed wave numbers are k_n=n*pi/L. "
                f"E_n=ħ²k_n²/(2m), so E_n/E_1=n²={n}²=**{n*n}**. "
                "It is the boundary condition, not the classical potential energy, that quantizes E.")
    if v == 1:
        p = r.randint(1, 4)
        R = 1/(2*p+1)**2
        return ("Quantum potential step; flux ratio",
                f"A particle of energy E>V0 encounters a 1D upward step. "
                f"If transmitted and incident wave numbers satisfy k2/k1={p}/{p+1}, "
                "find reflection and transmission probabilities.",
                "Continuity of ψ and ψ' gives r=(k1-k2)/(k1+k2). "
                f"Here r=(1-{p}/{p+1})/(1+{p}/{p+1})=1/{2*p+1}. "
                f"So R=|r|²=**1/{(2*p+1)**2}** (≈{R:.4f}), "
                f"T=1-R=**{1-R:.4f}**. "
                "Probability transmission includes the velocity/flux factor, unlike |t|² alone.")
    n = r.randint(0, 5)
    return ("Harmonic oscillator uncertainties",
            f"For the nth stationary oscillator state with n={n}, express Δx Δp in multiples of ħ.",
            "For each number state, <x>=<p>=0, "
            "<x²>=(n+1/2)ħ/(mω), and <p²>=(n+1/2)mħω. "
            f"Therefore Δx Δp=(n+1/2)ħ=**{n+0.5:g} ħ**. "
            "The ground state n=0 saturates Heisenberg; excited stationary states do not.")


def make_stat(r, v):
    if v == 0:
        n = r.randint(2, 7)
        return ("Two-level canonical probabilities",
                "A nondegenerate two-level system has energies 0 and Delta. "
                f"At temperature T, exp(-Delta/(kB T))=1/{n}. Find the excited probability and mean energy.",
                f"Z=1+exp(-beta Delta)=1+1/{n}=({n+1})/{n}. "
                f"P_exc=(1/{n})/Z=**1/{n+1}**. "
                f"Mean U=0*P_ground+Delta*P_exc=**Delta/{n+1}**. "
                "Partition functions normalize Boltzmann weights.")
    if v == 1:
        n = r.randint(3, 12)
        return ("Entropy from multiplicity",
                f"A system has N={n} independent, equally probable two-state degrees of freedom. "
                "Find the entropy in units of kB.",
                f"The multiplicity is Omega=2^N=2^{n}. "
                f"Boltzmann entropy S=kB ln(Omega)=kB ln(2^{n})=**{n} kB ln 2**. "
                "Assumes all 2^N states are accessible and equiprobable.")
    n = r.randint(1, 6)
    return ("Equipartition and heat capacity",
            f"Find the internal energy and constant-volume heat capacity for {n} moles of a classical monatomic ideal gas.",
            f"Each atom has three translational quadratic degrees of freedom. "
            f"U=(3/2)nRT=**{1.5*n:g} RT**, so C_V=(∂U/∂T)_V="
            f"**{1.5*n:g} R**. "
            "Rotations and vibrations of structureless monatomic particles do not contribute.")


def make_optics(r, v):
    if v == 0:
        degrees = r.choice([30, 45, 60])
        factor = {30:"3/4",45:"1/2",60:"1/4"}[degrees]
        return ("Polarization: Malus' law",
                f"Linearly polarized light of intensity I0 passes through an analyzer whose axis is {degrees} degrees to the input polarization. Find I/I0.",
                f"Malus' law gives I/I0=cos²({degrees} degrees)=**{factor}**. "
                "A perpendicular analyzer blocks the ideal beam; a parallel analyzer transmits its full intensity.")
    if v == 1:
        wavelength = r.choice([500, 600, 700])
        distance = r.randint(1, 3)
        separation = r.choice([0.2, 0.3, 0.4])
        fringe = wavelength*distance*0.001/separation
        return ("Young double-slit interference",
                f"For wavelength {wavelength} nm, screen distance {distance} m, and slit separation "
                f"{separation} mm, find the small-angle fringe spacing in mm.",
                "For d << D, β=λD/d. Converting all dimensions, "
                f"β={wavelength}*{distance}*0.001/{separation} mm="
                f"**{fringe:.3f} mm**. "
                "Fringe separation grows with wavelength and distance, decreases with slit spacing.")
    ratio = r.choice(["1", "sqrt(3)"])
    angle = 45 if ratio=="1" else 60
    return ("Brewster angle",
            f"Light travels from n1=1 into a medium of refractive index n2={ratio}. Find the Brewster angle.",
            "For nonmagnetic lossless media, tan(theta_B)=n2/n1. "
            f"Here tan(theta_B)={ratio}, hence theta_B=**{angle} degrees**. "
            "At this incidence, the reflected p-polarized amplitude vanishes.")


def make_atomic(r, v):
    if v == 0:
        ni = r.randint(3, 7)
        energy = 13.6*(1/4-1/(ni*ni))
        return ("Hydrogen photon emission",
                f"A hydrogen electron transitions from n_i={ni} to n_f=2. Find emitted photon energy in eV (ignore fine structure).",
                "Hydrogen bound-state energies are E_n=-13.6/n² eV. "
                f"E_gamma=E_i-E_f=13.6(1/2²-1/{ni}²)="
                f"**{energy:.4f} eV**. Emission energy is positive because the final bound level is lower.")
    if v == 1:
        ell = r.randint(1, 4)
        m = r.randint(-ell, ell)
        return ("Angular momentum eigenvalues",
                f"For a simultaneous eigenstate |l,m> with l={ell}, m={m}, "
                "give L² and Lz eigenvalues in ħ units.",
                "The defining eigenvalue equations are L²|l,m>=ħ² l(l+1)|l,m> and Lz|l,m>=ħ m|l,m>. "
                f"So **L²={ell*(ell+1)} ħ²** and **Lz={m} ħ**. "
                "Note the magnitude squared is not (Lz)².")
    valid = r.choice([True, False])
    initial = "(l=2,m=0)"
    final = "(l=1,m=1)" if valid else "(l=2,m=1)"
    return ("Electric-dipole selection rules",
            f"Is the atomic electric-dipole transition {initial} to {final} allowed by orbital angular-momentum selection rules?",
            "E1 transitions have Δl=±1 and Δm=0,±1 (subject to additional state restrictions). "
            + ("Here Δl=-1 and Δm=+1: **allowed by these selection rules**."
               if valid else "Here Δl=0, even though Δm=+1: **forbidden in the electric-dipole approximation**.") )


def make_solid(r, v):
    if v == 0:
        lattice = r.choice(["SC", "BCC", "FCC"])
        size = r.choice([0.30, 0.40, 0.50])
        if lattice == "SC":
            value, rule = size, "a"
        elif lattice == "BCC":
            value, rule = size*math.sqrt(3)/2, "sqrt(3)*a/2"
        else:
            value, rule = size/math.sqrt(2), "a/sqrt(2)"
        return ("Nearest-neighbor spacing",
                f"A {lattice} cubic crystal has lattice parameter a={size:.2f} nm. Find its nearest-neighbor distance.",
                f"The nearest-neighbor geometric relation for {lattice} is d={rule}. "
                f"Numerically, d=**{value:.4f} nm**. "
                "Use cube edges (SC), body diagonal (BCC), or face diagonal (FCC), respectively.")
    if v == 1:
        d = r.choice([0.20, 0.30, 0.40])
        return ("Bragg diffraction",
                f"First-order X-ray diffraction occurs from lattice planes with d={d:.2f} nm "
                f"using wavelength λ={d:.2f} nm. Find the Bragg angle θ.",
                "Bragg's law is nλ=2d sinθ. With n=1 and λ=d, sinθ=1/2, "
                "so **θ=30 degrees**. The measured diffractometer scattering angle is often 2θ=60 degrees.")
    factor = r.choice([8, 27, 64])
    ratio = round(factor**(2/3))
    return ("Fermi energy density scaling",
            f"The number density of a three-dimensional free-electron gas increases by a factor of {factor}. "
            "By what factor does its Fermi energy change?",
            "For a spin-1/2 3D free-electron gas, k_F is proportional to n^(1/3), "
            "so E_F=ħ²k_F²/(2m) is proportional to n^(2/3). "
            f"The factor is {factor}^(2/3)=**{ratio}**.")


def make_nuclear(r, v):
    if v == 0:
        half = r.randint(2, 9)
        count = r.randint(2, 5)
        return ("Radioactive decay",
                f"A sample has half-life {half} days. What fraction remains after {half*count} days?",
                "N(t)=N0*2^(-t/T_half). "
                f"Here t/T_half={half*count}/{half}={count}. "
                f"The surviving fraction is **1/{2**count}**. "
                "This is the number of undecayed nuclei, not the fraction that decayed.")
    if v == 1:
        factor = r.choice([8, 27, 64])
        return ("Nuclear radius scaling",
                f"Two nuclei have mass numbers A and {factor}A. Find the ratio of their radii R2/R1.",
                "Empirically R≈r0*A^(1/3), reflecting approximately constant nuclear density. "
                f"Hence R2/R1=({factor}A/A)^(1/3)=**{round(factor**(1/3))}**.")
    defect = r.randint(1, 9)/1000
    return ("Mass defect and Q-value",
            f"An exothermic nuclear reaction has initial-minus-final mass defect Δm={defect:.3f} u. "
            "Find the released energy in MeV using 1 u*c²=931.5 MeV.",
            "Energy conservation relates mass loss to kinetic/radiation energy via Q=Δm c². "
            f"Q={defect:.3f}*931.5=**{defect*931.5:.4f} MeV**. "
            "The positive sign denotes energy release.")


def make_electronics(r, v):
    if v == 0:
        n = r.randint(2, 7)
        return ("Parallel resistors",
                f"Two ideal resistors of R1={2*n} ohm and R2={3*n} ohm are parallel. Find their equivalent resistance.",
                "Current adds across equal voltage: 1/R_eq=1/R1+1/R2. "
                f"Therefore R_eq=R1 R2/(R1+R2)={2*n}*{3*n}/({2*n}+{3*n})="
                f"**{6*n/5:.2f} ohm**. It must be below the smaller branch resistance.")
    if v == 1:
        rin = r.randint(1, 4)
        gain = r.randint(2, 8)
        vin = r.choice([0.1, 0.2, 0.5])
        return ("Ideal inverting op-amp",
                f"An ideal inverting op-amp has Rin={rin} kilo-ohm and Rf={gain*rin} kilo-ohm. "
                f"With Vin={vin:.1f} V, find the closed-loop gain and Vout.",
                f"For negative feedback, Vout/Vin=-Rf/Rin=-{gain*rin}/{rin}=**-{gain}**. "
                f"Thus Vout=-{gain}*{vin:.1f}=**{-gain*vin:.2f} V**. "
                "This presumes sufficient output headroom and an ideal op-amp.")
    resistance, capacitance = r.randint(2, 9), r.randint(2, 9)
    return ("RC time constant",
            f"A simple RC charging circuit has R={resistance} kilo-ohm and C={capacitance} microfarad. "
            "Find the time constant in milliseconds.",
            "τ=RC. Since (1 kilo-ohm)(1 microfarad)=1 millisecond, "
            f"τ={resistance}*{capacitance}=**{resistance*capacitance} ms**. "
            "Charging from zero reaches 1-e^(-1)≈63.2% of the final capacitor voltage at t=τ.")


MAKERS = [make_math, make_mechanics, make_em, make_qm, make_stat,
          make_optics, make_atomic, make_solid, make_nuclear, make_electronics]


def phase_for(day: dt.date) -> str:
    if day < dt.date(2026, 12, 1):
        return "Foundation diagnostic: identify missing prerequisites"
    if day <= dt.date(2026, 12, 12):
        return "TIFR GS sprint: conceptual depth, then official TIFR PYQs"
    if day == dt.date(2026, 12, 13):
        return "TIFR exam day: optional light warm-up only; prioritize rest and logistics"
    if day <= dt.date(2026, 12, 26):
        return "CSIR-NET sprint: analytical Part C, negative-mark discipline"
    if day == dt.date(2026, 12, 27):
        return "CSIR-NET exam day: optional light warm-up only"
    return "GATE PH + IIT JAM PH: numerical precision, aptitude and timed PYQs"


def build(day: dt.date) -> str:
    lines = [
        f"# Ten original solved Physics questions — {day.isoformat()}",
        "",
        f"**Phase:** {phase_for(day)}",
        "",
        "> These are **original parameterized practice problems**, not official PYQs. "
        "Some concept families recur while numbers and cases change; "
        "use official papers separately for past-question practice.",
        "",
        "**Workflow:** attempt all ten without reading solutions; allow ~75–100 minutes, "
        "then review and record errors. On official exam dates, this is optional.",
        "",
    ]
    for i, (subject, maker) in enumerate(zip(SUBJECTS, MAKERS), 1):
        r = rng_for(day, subject)
        variant = (day.toordinal() + i) % 3
        topic, question, solution = maker(r, variant)
        lines.extend([
            f"## Q{i}. {subject} — {topic}",
            "",
            f"**Practice style:** {EXAM_TAGS[i-1]}",
            "",
            f"**Question.** {question}",
            "",
            "<details><summary><strong>Show worked solution</strong></summary>",
            "",
            solution,
            "",
            "</details>",
            "",
        ])
    lines.extend([
        "---", "",
        "## Review checklist",
        "",
        "- [ ] I attempted every question before opening answers.",
        "- [ ] I checked units and limiting cases where appropriate.",
        "- [ ] I recorded each error: concept / algebra / interpretation / time.",
        "- [ ] I scheduled re-solves at +2 days and +7 days.",
        "- [ ] I practised corresponding **official** exam PYQs.",
        "",
        "[Full plan](../docs/2027-ROADMAP.md) · "
        "[Resources and official PYQs](../docs/RESOURCES.md) · "
        "[Tracker](../docs/TRACKER.md)",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="YYYY-MM-DD; defaults to today's date in Asia/Kolkata")
    parser.add_argument("--stdout", action="store_true", help="Print instead of writing a file")
    args = parser.parse_args()
    day = (dt.date.fromisoformat(args.date) if args.date
           else dt.datetime.now(ZoneInfo("Asia/Kolkata")).date())
    doc = build(day)
    if args.stdout:
        print(doc)
        return
    target = ROOT / "questions" / f"{day.isoformat()}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        print(f"Existing dated sheet preserved: {target}")
        return
    target.write_text(doc, encoding="utf-8")
    print(f"Created: {target} (10 solved original questions)")


if __name__ == "__main__":
    main()
